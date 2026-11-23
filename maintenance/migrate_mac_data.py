import pathlib,json,hashlib,tarfile,io,signal,datetime
root=pathlib.Path('/Users/zyy/Documents/ChatGPT/FinancialAD');out=pathlib.Path('/Users/zyy/.local/share/financial-graph/maintenance')
files=[]
for p in (root/'results').iterdir():
 if p.name=='expanded' or p.name.startswith('public') or p.name=='cluster_gae_inventory.json':
  files.extend([f for f in p.rglob('*') if f.is_file()] if p.is_dir() else [p])
for p in (root/'financial-graph-research/evidence').rglob('*'):
 if p.is_file():files.append(p)
files+=list((pathlib.Path('/Users/zyy/.local/share/financial-graph/evidence')).rglob('*'))
files=[f for f in files if f.is_file()]
records=[];failed=[]
def timeout(*a):raise TimeoutError('iCloud read timeout')
signal.signal(signal.SIGALRM,timeout)
with tarfile.open(out/'mac-data-20261124.tar.gz','w:gz') as tar:
 for n,p in enumerate(files):
  try:
   if p.stat().st_flags & 0x40000000: raise IOError('iCloud dataless placeholder; earlier hydration attempts timed out; preserve source')
   signal.alarm(15);b=p.read_bytes();signal.alarm(0)
   rel=str(p.relative_to(root)) if p.is_relative_to(root) else 'recovery/'+str(p.relative_to('/Users/zyy/.local/share/financial-graph'))
   st=p.stat();h=hashlib.sha256(b).hexdigest();info=tarfile.TarInfo(rel);info.size=len(b);tar.addfile(info,io.BytesIO(b));records.append({'source':str(p),'archive_path':rel,'bytes':len(b),'allocated_bytes':st.st_blocks*512,'sha256':h})
   print(n+1,len(files),'archived',rel,flush=True)
  except Exception as e:
   signal.alarm(0);failed.append({'source':str(p),'error':str(e)});print('FAILED',str(p),str(e),flush=True)
 manifest={'created':'2026-11-24 Asia/Singapore','files':records,'failed':failed,'deletion_status':'not started'}
 b=json.dumps(manifest,indent=2).encode();info=tarfile.TarInfo('manifest.json');info.size=len(b);tar.addfile(info,io.BytesIO(b))
(out/'mac-data-manifest.json').write_text(json.dumps(manifest,indent=2))
print('COMPLETE',len(records),'failed',len(failed),flush=True)
