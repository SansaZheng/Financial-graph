#!/usr/bin/env python3
"""Explicit, pinned HF assets. No implicit whole-repo download or deletion."""
import argparse
import csv
import hashlib
import itertools
import json
import os
import platform
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

MANIFEST = Path(__file__).resolve().parents[1] / 'assets/manifest.json'
BLOCKED = {'.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules', '.ssh'}


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def relative(value):
    p = PurePosixPath(value)
    if not value or not p.parts or p.is_absolute() or '..' in p.parts or '\\' in value or any(x in BLOCKED for x in p.parts):
        raise ValueError('Unsafe asset path')
    return p


def under(root, value):
    root = Path(root).resolve()
    p = root.joinpath(*relative(value).parts)
    if not p.resolve().is_relative_to(root): raise ValueError('Asset path escapes root')
    return p


def load_manifest(path=MANIFEST):
    m = json.loads(Path(path).read_text())
    if m.get('schema_version') != 1: raise ValueError('Unknown manifest schema')
    seen = set()
    for a in m['assets']:
        if a['id'] in seen: raise ValueError('Duplicate asset ID')
        seen.add(a['id'])
        if a['repo_type'] not in ['dataset', 'model']: raise ValueError('Invalid repo type')
        if a['status'] == 'published':
            if not a.get('repo_id') or not re.fullmatch('[0-9a-f]{40}', a.get('revision') or ''):
                raise ValueError('Published assets require full immutable HF commit SHA')
        if a['repo_type']=='model':
            if not re.fullmatch('[0-9a-f]{40}', a.get('code_revision') or ''): raise ValueError('Model requires code commit')
            if not a.get('dataset_revisions') or any(not re.fullmatch('[0-9a-f]{40}', d.get('revision') or '') for d in a['dataset_revisions']): raise ValueError('Model requires pinned dataset revisions')
            if not a.get('random_seeds') or not a.get('configuration') or not a.get('evaluation'): raise ValueError('Model requires seeds, configuration and metrics paths')
            for f in a['files']:
                if Path(f['path']).suffix in ['.pt','.pth','.ckpt','.safetensors','.bin','.pkl','.joblib']:
                    if not f.get('roles') or not set(f['roles']) <= {'best','final','recovery'}: raise ValueError('Select best/final/recovery checkpoints explicitly')
        paths = set(); local_paths = set()
        for f in a['files']:
            relative(f['path']); relative(f['local_path'])
            if f['path'] in paths or f['local_path'] in local_paths: raise ValueError('Duplicate file path')
            paths.add(f['path']); local_paths.add(f['local_path'])
            if not re.fullmatch('[0-9a-f]{64}', f['sha256']): raise ValueError('Missing SHA256')
            if not isinstance(f['bytes'], int) or f['bytes'] < 0: raise ValueError('Invalid size')
    return m


def choose(m, name, files=None, published=True):
    a = next((a for a in m['assets'] if a['id'] == name), None)
    if a is None: raise ValueError('Unknown asset ID')
    if published and a['status'] != 'published': raise ValueError('Asset not uploaded and pinned yet; see migration status')
    selected = a['files'] if not files else [f for f in a['files'] if f['path'] in files]
    if files and set(files) != {f['path'] for f in selected}: raise ValueError('Requested file is not in manifest')
    if not selected: raise ValueError('No files selected')
    return a, selected


def verify_file(path, f):
    if not path.is_file() or path.stat().st_size != f['bytes'] or digest(path) != f['sha256']:
        raise ValueError('Integrity mismatch: ' + f['path'])


def remote_guard(allow_local):
    if platform.system() == 'Darwin' and not allow_local:
        raise ValueError('Mac downloads/streaming disabled by default; use remote CQ execution or explicit --allow-local')


def configure_tls():
    # Use administrator-installed OS roots, never disable TLS or trust a downloaded certificate.
    bundle=os.getenv('FG_CA_BUNDLE') or os.getenv('REQUESTS_CA_BUNDLE')
    if not bundle and platform.system()=='Linux' and Path('/etc/ssl/certs/ca-certificates.crt').is_file():
        bundle='/etc/ssl/certs/ca-certificates.crt'
    if bundle:
        if not Path(bundle).is_file(): raise ValueError('Configured CA bundle does not exist')
        os.environ['REQUESTS_CA_BUNDLE']=bundle
        os.environ.setdefault('SSL_CERT_FILE',bundle)
    return bundle


def configure_cache(cache):
    if not cache: raise ValueError('--cache-root or FG_CACHE_ROOT required; use a project-owned remote path')
    p = Path(cache).expanduser().resolve(); p.mkdir(parents=True, exist_ok=True)
    os.environ['HF_HUB_CACHE'] = str(p / 'hub')
    os.environ['HF_XET_CACHE'] = str(p / 'xet')
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    return p


def fetch(a, files, root, cache, allow_local=False):
    remote_guard(allow_local)
    from huggingface_hub import hf_hub_download
    results = []
    for f in files:
        dest = under(Path(root) / a['id'], f['local_path'])
        if dest.exists(): verify_file(dest, f)
        else:
            src = Path(hf_hub_download(a['repo_id'], f['path'], repo_type=a['repo_type'], revision=a['revision'], cache_dir=str(cache / 'hub')))
            verify_file(src, f)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Preserve cache objects: never modify hardlinks or cached files in place.
            fd, tmpname = tempfile.mkstemp(prefix='.asset-', dir=dest.parent); os.close(fd)
            tmp = Path(tmpname)
            try:
                shutil.copyfile(src, tmp); verify_file(tmp, f); os.replace(tmp, dest)
            finally:
                if tmp.exists(): tmp.unlink()  # only our temporary transfer file
        results.append({'path':str(dest), 'sha256':f['sha256'], 'bytes':f['bytes']})
    return {'asset':a['id'], 'revision':a['revision'], 'status':'verified', 'files':results}


def account_audit():
    from huggingface_hub import HfApi, get_token
    if not get_token(): return {'authenticated':False, 'quota':'unknown: login required'}
    api = HfApi(); u = api.whoami()
    namespaces = [u['name']] + [o['name'] for o in u.get('orgs', [])]
    repos = []
    for ns in namespaces:
        for kind, fn in [('dataset', api.list_datasets), ('model', api.list_models)]:
            for r in fn(author=ns):
                repos.append({'repo_id':r.id, 'repo_type':kind, 'private':r.private, 'revision':r.sha})
    # Do not dump whoami: token metadata and unrelated account details stay private.
    return {'authenticated':True, 'account':u['name'], 'namespaces':namespaces, 'is_pro':u.get('isPro'),
            'token_role':u.get('auth', {}).get('accessToken', {}).get('role'), 'repos':repos,
            'quota':'No account storage quota endpoint in pinned client. Confirm included free headroom in HF billing settings; repo sizes omit deleted/history storage.'}


def check_quota(receipt, namespace, new_bytes):
    q = json.loads(Path(receipt).read_text())
    checked = datetime.fromisoformat(q['checked_at'].replace('Z', '+00:00'))
    if checked.tzinfo is None: raise ValueError('Quota timestamp requires timezone')
    age = (datetime.now(timezone.utc) - checked).total_seconds()
    if not 0 <= age <= 86400: raise ValueError('Quota receipt must be from the past 24 hours, with timezone')
    if q['namespace'] != namespace or q.get('source') not in ['hf-billing-settings', 'authenticated-hf-api']:
        raise ValueError('Quota receipt namespace/source mismatch')
    if q.get('no_paid_overage') is not True or q['remaining_included_bytes'] < 2 * new_bytes:
        raise ValueError('Insufficient confirmed included storage; no paid overage authorized')


def upload(m, asset, source_root, repo_id, quota_receipt, cache, large=False, api=None):
    from huggingface_hub import HfApi, CommitOperationAdd
    from huggingface_hub.errors import RepositoryNotFoundError
    a, files = choose(m, asset, published=False)
    if a.get('read_only'): raise ValueError('Upstream asset is read-only; do not duplicate or mutate')
    if a.get('repo_id') and a['repo_id'] != repo_id: raise ValueError('Existing asset repo differs; do not create duplicate repos')
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo_id): raise ValueError('Explicit owner/repo required')
    api = api or HfApi(); identity = api.whoami(); namespace = repo_id.split('/')[0]
    permitted = [identity['name']] + [o['name'] for o in identity.get('orgs', []) if o.get('roleInOrg') in ['admin', 'write', 'contributor']]
    if namespace not in permitted: raise ValueError('Namespace write membership not established')
    sources = []
    for f in files:
        source = under(source_root, f['source_path']); verify_file(source, f)
        if source.is_symlink() or source.name.startswith('.env') or source.name in ['token', 'stored_tokens', 'credentials', 'id_rsa', 'id_ed25519']:
            raise ValueError('Credential/symlink source rejected')
        if source.stat().st_size < 2_000_000 and source.suffix in ['.txt','.md','.json','.yaml','.yml','.csv']:
            if re.search(rb'hf_[A-Za-z0-9]{20,}', source.read_bytes()): raise ValueError('Possible credential in upload source')
        sources.append((f, source))
    check_quota(quota_receipt, namespace, sum(f['bytes'] for f in files))
    try:
        info = api.repo_info(repo_id, repo_type=a['repo_type'], files_metadata=True)
        if not info.private: raise ValueError('Existing destination is public; refusing private asset publication')
    except RepositoryNotFoundError:
        # Existing matching repos are listed before creating. Never invent a suffixed duplicate.
        names = [x.id for x in (api.list_datasets(author=namespace) if a['repo_type']=='dataset' else api.list_models(author=namespace))]
        related = [x for x in names if 'financial' in x.lower() and x != repo_id]
        if related and a.get('reuse_reviewed_repos') != sorted(related):
            raise ValueError('Review existing financial repositories and record reuse_reviewed_repos before creating another')
        api.create_repo(repo_id, repo_type=a['repo_type'], private=True, exist_ok=False)
        info = api.repo_info(repo_id, repo_type=a['repo_type'], files_metadata=True)
    if large:
        stage = cache / 'upload-staging' / a['id']; stage.mkdir(parents=True, exist_ok=True)
        expected = {f['path'] for f in files}
        actual = {str(p.relative_to(stage)) for p in stage.rglob('*') if p.is_file() and '.cache' not in p.relative_to(stage).parts}
        if actual - expected: raise ValueError('Unexpected staged files; use a fresh project staging directory')
        for f, src in sources:
            dst = under(stage, f['path']); dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists(): verify_file(dst, f)
            else: shutil.copyfile(src, dst)
        # Official 0.36 task cache resumes hashing/preupload/commit; leave .cache intact on interruption.
        api.upload_large_folder(repo_id, stage, repo_type=a['repo_type'], private=True, num_workers=2, allow_patterns=sorted(expected))
        revision = api.repo_info(repo_id, repo_type=a['repo_type']).sha
    else:
        remote = {s.rfilename:s for s in (info.siblings or [])}; operations=[]
        for f, src in sources:
            r = remote.get(f['path']); same = False
            if r and r.lfs: same = r.lfs.sha256 == f['sha256']
            elif r and r.blob_id:
                h=hashlib.sha1(('blob %s\0' % f['bytes']).encode()); h.update(src.read_bytes()); same=h.hexdigest()==r.blob_id
            if r and not same and f['path']=='README.md': raise ValueError('Existing dataset card differs; preserve it and select a separate documented card path')
            if not same: operations.append(CommitOperationAdd(path_in_repo=f['path'], path_or_fileobj=str(src)))
        revision = info.sha
        for offset in range(0, len(operations), 50):
            c = api.create_commit(repo_id, repo_type=a['repo_type'], operations=operations[offset:offset+50], parent_commit=revision,
                                  commit_message='Versioned FinancialGraph asset ' + a['id'])
            revision=c.oid
    # Pin and independently read back every requested file, not merely accept an upload response.
    candidate=dict(a, repo_id=repo_id, revision=revision, status='published', private=True)
    verify_root = cache / 'upload-readback' / revision
    receipt = fetch(candidate, files, verify_root, cache / 'readback-cache', allow_local=False)
    a.update(candidate)
    a['verification']={'status':'downloaded-and-sha256-verified', 'checked_at':datetime.now(timezone.utc).isoformat()}
    return receipt


def stream(a, f, rows, columns, max_row_group_mb, allow_local):
    remote_guard(allow_local)
    from huggingface_hub import HfFileSystem
    fs = HfFileSystem(); prefix = 'datasets/' if a['repo_type']=='dataset' else ''
    uri=prefix + a['repo_id'] + '@' + a['revision'] + '/' + f['path']
    if f['path'].endswith('.csv'):
        with fs.open(uri, 'rt') as h: values=list(itertools.islice(csv.DictReader(h), rows))
    elif f['path'].endswith('.parquet'):
        import pyarrow.parquet as pq
        with fs.open(uri, 'rb', block_size=1024*1024) as h:
            p=pq.ParquetFile(h)
            rg=p.metadata.row_group(0)
            selected_size=sum(rg.column(i).total_uncompressed_size for i in range(rg.num_columns) if columns is None or rg.column(i).path_in_schema in columns)
            if selected_size > max_row_group_mb*1024**2:
                raise ValueError('First row group exceeds streaming budget; use fewer-column prepared shards')
            values=p.read_row_group(0, columns=columns).slice(0, rows).to_pylist()
    else: raise ValueError('Streaming supports CSV/Parquet only')
    return {'revision':a['revision'], 'integrity':'pinned range read; whole-file SHA256 NOT verified by streaming', 'rows':values}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', default=str(MANIFEST));p.add_argument('--cache-root',default=os.getenv('FG_CACHE_ROOT'))
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('validate');sub.add_parser('account')
    for name in ['fetch','verify','stream']:
        s=sub.add_parser(name);s.add_argument('--asset',required=True);s.add_argument('--file',action='append');s.add_argument('--data-root',default=os.getenv('FG_DATA_ROOT'));s.add_argument('--allow-local',action='store_true')
        if name=='stream':s.add_argument('--rows',type=int,default=5);s.add_argument('--columns',nargs='+');s.add_argument('--max-row-group-mb',type=int,default=128)
    u=sub.add_parser('upload');u.add_argument('--asset',required=True);u.add_argument('--source-root',required=True);u.add_argument('--repo-id',required=True);u.add_argument('--quota-receipt',required=True);u.add_argument('--large',action='store_true')
    args=p.parse_args();configure_tls();m=load_manifest(args.manifest)
    if args.command=='validate':result={'status':'valid','assets':[{k:a[k] for k in ['id','status','repo_type','revision']} for a in m['assets']]}
    elif args.command=='account':result=account_audit()
    else:
        cache=configure_cache(args.cache_root)
        if args.command=='upload':
            remote_guard(False)
            result=upload(m,args.asset,args.source_root,args.repo_id,args.quota_receipt,cache,args.large)
            path=Path(args.manifest);temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(m,indent=2)+'\n');os.replace(temp,path)
        else:
            a,files=choose(m,args.asset,args.file)
            if args.command=='stream':
                if len(files)!=1 or not 1<=args.rows<=1000:raise ValueError('Select exactly one file and 1..1000 rows')
                result=stream(a,files[0],args.rows,args.columns,args.max_row_group_mb,args.allow_local)
            else:
                if not args.data_root:raise ValueError('--data-root or FG_DATA_ROOT required')
                if args.command=='fetch':result=fetch(a,files,args.data_root,cache,args.allow_local)
                else:
                    for f in files:verify_file(under(Path(args.data_root)/a['id'],f['local_path']),f)
                    result={'status':'verified','asset':a['id'],'files':len(files),'revision':a['revision']}
    print(json.dumps(result,indent=2,default=str))

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,FileNotFoundError) as e:
        print('asset error: '+str(e),file=sys.stderr);sys.exit(2)
    except Exception as e:
        # Network/auth exceptions may carry request details; never print token-bearing objects.
        print('asset operation failed: '+type(e).__name__+'; inspect permissions/network securely',file=sys.stderr);sys.exit(1)
