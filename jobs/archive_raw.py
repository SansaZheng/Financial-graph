"""Stream pinned source into verified GitHub release parts; no model training."""
import hashlib,json,os,subprocess,urllib.request
from pathlib import Path
REV='0c6f25f287918b1421c2572d2c9e2b75bd8959a9'
SHA='59bc5acc7d278680c9090c53b10de6d6add796ebf19586be3873f19e3e789d7b'
SIZE=10927267185
BASE=f'https://huggingface.co/datasets/CryptoSpartan/stocks_bars_1m/resolve/{REV}'
TAG='raw-stocks-bars-1m-59bc5acc'
REPO=os.environ['GITHUB_REPOSITORY']

def gh(*args):return subprocess.check_output(['gh',*args],text=True)
def main():
    if REPO!='SansaZheng/Financial-graph':raise RuntimeError('Archive only to primary authorized repository')
    path=Path(os.environ.get('RUNNER_TEMP','.'))/'financialgraph-raw';path.mkdir(exist_ok=True)
    releases=json.loads(gh('api',f'repos/{REPO}/releases?per_page=100'))
    r=next((x for x in releases if x['tag_name']==TAG),None)
    if r is None:
        gh('release','create',TAG,'--repo',REPO,'--draft','--target',os.environ['GITHUB_SHA'],'--title','Pinned raw minute-bar data (SHA256 verified)','--notes','Source CryptoSpartan/stocks_bars_1m on Hugging Face, MIT metadata. Binary parts concatenate in part-number order. Verify manifest SHA256 before use. This is a data archive, not an experimental result.')
        releases=json.loads(gh('api',f'repos/{REPO}/releases?per_page=100'))
        r=next(x for x in releases if x['tag_name']==TAG)
    if not r['draft']:raise RuntimeError('Published archive already exists; preserve it')
    existing={x['name']:x for x in r['assets']};overall=hashlib.sha256();parts=[]
    chunk=1024**3
    for i,start in enumerate(range(0,SIZE,chunk)):
        end=min(start+chunk,SIZE)-1;name=f'stocks_bars_1m.parquet.part{i:03d}';p=path/name
        req=urllib.request.Request(BASE+'/stocks_bars_1m.parquet',headers={'Range':f'bytes={start}-{end}'})
        h=hashlib.sha256();written=0
        with urllib.request.urlopen(req,timeout=120) as response,p.open('wb') as f:
            if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end}/{SIZE}':raise RuntimeError('Range response mismatch')
            while True:
                b=response.read(8*1024**2)
                if not b:break
                written+=len(b)
                if written>end-start+1:raise RuntimeError('Oversized range')
                f.write(b);h.update(b);overall.update(b)
        if written!=end-start+1:raise RuntimeError('Truncated range')
        digest=h.hexdigest()
        if name in existing:
            a=existing[name]
            if a.get('digest')!='sha256:'+digest or a['size']!=written:raise RuntimeError('Existing asset differs; do not overwrite')
        else:
            gh('release','upload',TAG,str(p),'--repo',REPO)
            assets=json.loads(gh('api',f"repos/{REPO}/releases/{r['id']}/assets?per_page=100"));a=next(x for x in assets if x['name']==name)
            if a.get('digest')!='sha256:'+digest or a['size']!=written:raise RuntimeError('Remote digest verification failed')
        parts.append({'name':name,'bytes':written,'sha256':digest,'asset_id':a['id'],'url':a['browser_download_url']})
        p.unlink();print(f'{i+1}/11 verified parts',flush=True)
    if overall.hexdigest()!=SHA:raise RuntimeError('Whole source hash mismatch; keep draft')
    manifest={'source':BASE+'/stocks_bars_1m.parquet','source_revision':REV,'source_license_metadata':'MIT','sha256':SHA,'bytes':SIZE,'parts':parts,'verified_remote_asset_digests':True}
    m=path/'manifest.json';m.write_text(json.dumps(manifest,indent=2))
    card=path/'SOURCE_README.md'
    with urllib.request.urlopen(BASE+'/README.md',timeout=30) as f:card.write_bytes(f.read())
    gh('release','upload',TAG,str(m),str(card),'--repo',REPO,'--clobber')
    gh('release','edit',TAG,'--repo',REPO,'--draft=false')
    print(f'https://github.com/{REPO}/releases/tag/{TAG}',flush=True)
if __name__=='__main__':main()
