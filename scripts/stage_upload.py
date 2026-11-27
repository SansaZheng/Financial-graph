#!/usr/bin/env python3
"""Materialize only allowlisted upload sources on remote storage; no whole-directory copies."""
import argparse,subprocess,re,tempfile,os
from pathlib import Path
from assets import load_manifest,choose,under,verify_file,remote_guard

def main():
    p=argparse.ArgumentParser();p.add_argument('--asset',required=True);p.add_argument('--source-root',required=True);p.add_argument('--legacy-commit',required=True);p.add_argument('--manifest',default=str(Path(__file__).resolve().parents[1]/'assets/manifest.json'));a=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',a.legacy_commit):raise ValueError('Legacy commit must be a full immutable SHA')
    remote_guard(False);repo=Path(__file__).resolve().parents[1];root=Path(a.source_root).resolve()
    if root.is_relative_to(repo):raise ValueError('Staging must be outside code checkout')
    m=load_manifest(a.manifest);asset,files=choose(m,a.asset,published=False)
    if asset.get('read_only'):raise ValueError('Do not stage duplicated upstream data')
    for f in files:
        dest=under(root,f['source_path'])
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            # git show retrieves just this manifest entry, from current code or recorded legacy commit.
            present=subprocess.run(['git','cat-file','-e','HEAD:'+f['source_path']],cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
            ref='HEAD' if present else a.legacy_commit
            fd,tmpname=tempfile.mkstemp(prefix='.stage-',dir=dest.parent)
            try:
                with os.fdopen(fd,'wb') as h:r=subprocess.run(['git','show',ref+':'+f['source_path']],cwd=repo,stdout=h)
                if r.returncode:raise RuntimeError('Source object unavailable; fetch the documented legacy commit first')
                verify_file(Path(tmpname),f);os.replace(tmpname,dest)
            finally:
                if Path(tmpname).exists():Path(tmpname).unlink()
        verify_file(dest,f)
    print(f'{len(files)} allowlisted source files staged and hash-verified')
if __name__=='__main__':main()
