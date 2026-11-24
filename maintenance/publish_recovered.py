"""Publish and redownload a complete recovery archive; never deletes sources."""
import pathlib,json,hashlib,urllib.request,subprocess,tarfile,io
root=pathlib.Path(__file__).resolve().parent
r=json.loads((root/'recovery-progress.json').read_text())
assert r['expected']==r['recovered']==71 and not r['pending'],'Recovery incomplete; refuse publishing as complete'
archive=root/'recovered-71-20261124.tar.gz';body=archive.read_bytes();assert hashlib.sha256(body).hexdigest()==r['archive_sha256']
for f in r['files']:assert hashlib.sha256(pathlib.Path(f['source']).read_bytes()).hexdigest()==f['sha256'],'Source changed'
cred=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,check=True)
c=dict(x.split('=',1) for x in cred.stdout.splitlines() if '=' in x)
headers={'Authorization':'Bearer '+c['password'],'Accept':'application/vnd.github+json','User-Agent':'FinancialGraph-migration'}
repo='SansaZheng/Financial-graph';api='https://api.github.com/repos/'+repo

def request(url,data=None,method=None,ctype='application/json'):
 h=dict(headers);h['Content-Type']=ctype
 with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=h,method=method),timeout=60) as response:return json.load(response)
tag='mac-recovered-71-20261124'
releases=request(api+'/releases?per_page=100');release=next((x for x in releases if x['tag_name']==tag),None)
if release is None:release=request(api+'/releases',json.dumps({'tag_name':tag,'target_commitish':'main','name':'Verified recovery of 71 GAE iCloud files','body':'Project-only data archive. Verify manifest hashes before restoration. No other project files included.','draft':True}).encode(),'POST')
assets={x['name']:x for x in release['assets']}
for name,b in [('recovered-71-20261124.tar.gz',body),('manifest.json',json.dumps(r,indent=2).encode())]:
 h=hashlib.sha256(b).hexdigest()
 if name in assets:
  a=assets[name];assert a.get('digest')=='sha256:'+h and a['size']==len(b),'Existing asset differs'
 else:
  url=release['upload_url'].split('{')[0]+'?name='+name;a=request(url,b,'POST','application/octet-stream');assert a.get('digest')=='sha256:'+h and a['size']==len(b)
 assets[name]=a
request(api+'/releases/'+str(release['id']),json.dumps({'draft':False}).encode(),'PATCH')
with urllib.request.urlopen(assets['recovered-71-20261124.tar.gz']['browser_download_url'],timeout=60) as response:download=response.read()
assert hashlib.sha256(download).hexdigest()==r['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(download),mode='r:gz') as tar:
 for f in r['files']:assert hashlib.sha256(tar.extractfile(f['archive_path']).read()).hexdigest()==f['sha256']
receipt={'verified':True,'count':71,'archive_sha256':r['archive_sha256'],'release_url':release['html_url'],'remote_redownload_verified':True,'every_member_verified':True,'deletion_performed':False}
(root/'recovered-remote-verification.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
