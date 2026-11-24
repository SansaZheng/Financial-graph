import pathlib,json,hashlib,tarfile,io,time
root=pathlib.Path('/Users/zyy/.local/share/financial-graph/maintenance');m=json.loads((root/'mac-data-manifest.json').read_text());files=[pathlib.Path(x['source']) for x in m['failed']]
records=[];pending=files.copy();dest=root/'recovered-71-20261124.tar.gz'
with tarfile.open(dest,'w:gz') as tar:
 for attempt in range(12):
  for p in list(pending):
   if p.stat().st_flags & 0x40000000:continue
   b=p.read_bytes();st=p.stat();rel=str(p.relative_to('/Users/zyy/Documents/ChatGPT/FinancialAD'));h=hashlib.sha256(b).hexdigest()
   info=tarfile.TarInfo(rel);info.size=len(b);tar.addfile(info,io.BytesIO(b));records.append({'source':str(p),'archive_path':rel,'bytes':len(b),'sha256':h,'allocated_bytes':st.st_blocks*512});pending.remove(p)
  report={'date':'2026-11-24','expected':71,'recovered':len(records),'files':records,'pending':[str(p) for p in pending],'deleted':False}
  (root/'recovery-progress.json').write_text(json.dumps(report,indent=2));print('poll',attempt+1,'recovered',len(records),'pending',len(pending),flush=True)
  if not pending:break
  time.sleep(10)
 b=json.dumps(report,indent=2).encode();info=tarfile.TarInfo('manifest.json');info.size=len(b);tar.addfile(info,io.BytesIO(b))
report['archive_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();report['archive_bytes']=dest.stat().st_size;(root/'recovery-progress.json').write_text(json.dumps(report,indent=2))
