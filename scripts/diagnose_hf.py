"""Bounded public-metadata diagnostics; no tokens, headers, signed URLs or file bodies logged."""
import argparse,json,os,hashlib
from pathlib import Path
from assets import configure_tls,load_manifest,digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--cached-root',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    bundle=configure_tls()
    import huggingface_hub
    from huggingface_hub import hf_hub_download,HfApi,HfFileSystem,get_hf_file_metadata,hf_hub_url
    asset=next(x for x in load_manifest()['assets'] if x['id']=='upstream-card');expected=asset['files'][0]
    def desc(path):return {'bytes':path.stat().st_size,'sha256':digest(path),'first16_hex':path.read_bytes()[:16].hex()}
    report={'client_version':huggingface_hub.__version__,'trusted_ca_path':bundle,'expected':expected,'old_cache':[]}
    for f in Path(a.cached_root).rglob('README.md'):
        if f.is_file():report['old_cache'].append(desc(f))
    try:
        info=HfApi().dataset_info(asset['repo_id'],revision=asset['revision'],files_metadata=True)
        meta=get_hf_file_metadata(hf_hub_url(asset['repo_id'],'README.md',repo_type='dataset',revision=asset['revision']))
        report['head_metadata']={'size':meta.size,'etag':meta.etag}
        report['api']={'sha':info.sha,'file':[{ 'path':s.rfilename,'size':s.size,'blob_id':s.blob_id } for s in info.siblings if s.rfilename=='README.md']}
        path=Path(hf_hub_download(asset['repo_id'],'README.md',repo_type='dataset',revision=asset['revision'],cache_dir=out/'fresh-cache',force_download=True))
        report['fresh']=desc(path);report['fresh_match']=report['fresh']['bytes']==expected['bytes'] and report['fresh']['sha256']==expected['sha256']
        uri='datasets/'+asset['repo_id']+'@'+asset['revision']+'/README.md'
        with HfFileSystem().open(uri,'rb',block_size=1024) as h:body=h.read()
        report['filesystem_read']={'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'matches':len(body)==expected['bytes'] and hashlib.sha256(body).hexdigest()==expected['sha256']}
    except Exception as e:report['error_type']=type(e).__name__;report['fresh_match']=False
    (out/'hf-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
