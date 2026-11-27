import hashlib,json,sys,tempfile,unittest,io
from datetime import datetime,timezone,timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import assets

class AssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.src=self.root/'source.csv';self.src.write_text('x\n1\n')
        self.file={'path':'derived/source.csv','local_path':'derived/source.csv','source_path':'source.csv','bytes':self.src.stat().st_size,'sha256':assets.digest(self.src)}
        self.asset={'id':'sample','status':'published','repo_type':'dataset','repo_id':'owner/sample','revision':'a'*40,'private':True,'files':[self.file]}
        self.manifest={'schema_version':1,'assets':[self.asset]}
        self.quota=self.root/'quota.json';self.quota.write_text(json.dumps({'namespace':'owner','checked_at':datetime.now(timezone.utc).isoformat(),'source':'hf-billing-settings','no_paid_overage':True,'remaining_included_bytes':10000}))
    def tearDown(self):self.tmp.cleanup()
    def test_rejects_paths_and_symlink_escape(self):
        for path in ['../secret','/etc/passwd','.git/config','a/../../b','.','a\\b']:
            with self.assertRaises(ValueError):assets.relative(path)
        (self.root/'link').symlink_to('/tmp')
        with self.assertRaises(ValueError):assets.under(self.root,'link/outside')
    def test_requires_immutable_revision(self):
        self.asset['revision']='main';p=self.root/'manifest.json';p.write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):assets.load_manifest(p)
    def test_pending_asset_cannot_be_downloaded(self):
        self.asset['status']='pending-authentication-and-upload'
        with self.assertRaises(ValueError):assets.choose(self.manifest,'sample')
    def test_integrity_detects_same_size_corruption(self):
        self.src.write_text('x\n2\n')
        with self.assertRaises(ValueError):assets.verify_file(self.src,self.file)
    def test_selective_pinned_fetch_and_repeat(self):
        with patch('huggingface_hub.hf_hub_download',return_value=str(self.src)) as dl,patch('assets.platform.system',return_value='Linux'):
            r=assets.fetch(self.asset,[self.file],self.root/'data',self.root/'cache')
            self.assertEqual(dl.call_args.kwargs['revision'],'a'*40)
            self.assertEqual(dl.call_args.args,('owner/sample','derived/source.csv'))
            assets.fetch(self.asset,[self.file],self.root/'data',self.root/'cache')
            self.assertEqual(dl.call_count,1)
            self.assertEqual(r['status'],'verified')
    def test_mac_requires_explicit_override(self):
        with patch('assets.platform.system',return_value='Darwin'):
            with self.assertRaises(ValueError):assets.remote_guard(False)
            assets.remote_guard(True)
    def test_quota_stale_or_insufficient_fails(self):
        assets.check_quota(self.quota,'owner',10)
        with self.assertRaises(ValueError):assets.check_quota(self.quota,'owner',10000)
        q=json.loads(self.quota.read_text());q['checked_at']=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat();self.quota.write_text(json.dumps(q))
        with self.assertRaises(ValueError):assets.check_quota(self.quota,'owner',10)
    def api(self,private=True):
        api=Mock();api.whoami.return_value={'name':'owner','orgs':[]};api.repo_info.return_value=SimpleNamespace(private=private,sha='a'*40,siblings=[]);api.create_commit.return_value=SimpleNamespace(oid='b'*40);return api
    def test_public_destination_never_written(self):
        api=self.api(False)
        with self.assertRaises(ValueError):assets.upload(self.manifest,'sample',self.root,'owner/sample',self.quota,self.root/'cache',api=api)
        api.create_commit.assert_not_called();api.create_repo.assert_not_called()
    def test_readback_failure_does_not_advance_manifest(self):
        api=self.api()
        with patch('assets.fetch',side_effect=ValueError('corrupt')):
            with self.assertRaises(ValueError):assets.upload(self.manifest,'sample',self.root,'owner/sample',self.quota,self.root/'cache',api=api)
        self.assertEqual(self.asset['revision'],'a'*40)
        self.assertEqual(api.create_commit.call_args.kwargs['parent_commit'],'a'*40)
    def test_identical_remote_file_is_not_uploaded_again(self):
        api=self.api();api.repo_info.return_value.siblings=[SimpleNamespace(rfilename=self.file['path'],lfs=SimpleNamespace(sha256=self.file['sha256']),blob_id=None)]
        with patch('assets.fetch',return_value={'status':'verified'}):assets.upload(self.manifest,'sample',self.root,'owner/sample',self.quota,self.root/'cache',api=api)
        api.create_commit.assert_not_called();self.assertEqual(self.asset['verification']['status'],'downloaded-and-sha256-verified')
    def test_zero_byte_hub_download_uses_verified_official_range_read(self):
        empty=self.root/'empty';empty.write_bytes(b'');body=self.src.read_bytes()
        fs=Mock();fs.open.return_value=io.BytesIO(body)
        with patch('huggingface_hub.hf_hub_download',return_value=str(empty)),patch('huggingface_hub.HfFileSystem',return_value=fs),patch('assets.platform.system',return_value='Linux'):
            r=assets.fetch(self.asset,[self.file],self.root/'data',self.root/'cache')
        self.assertEqual(r['files'][0]['transport'],'hf-filesystem-verified-range-fallback')
        self.assertIn('@'+'a'*40,fs.open.call_args.args[0])
        self.assertEqual(empty.stat().st_size,0)  # damaged original cache is not overwritten
    def test_range_resume_requires_full_checksum(self):
        cache=self.root/'cache';folder=cache/'verified-ranges';folder.mkdir(parents=True)
        partial=folder/(self.file['sha256']+'.partial');partial.write_bytes(self.src.read_bytes()[:2])
        fs=Mock();fs.open.return_value=io.BytesIO(self.src.read_bytes())
        with patch('huggingface_hub.HfFileSystem',return_value=fs):out=assets.filesystem_download(self.asset,self.file,cache)
        self.assertEqual(out.read_bytes(),self.src.read_bytes());self.assertFalse(partial.exists())
    def test_unknown_selected_file_rejected(self):
        with self.assertRaises(ValueError):assets.choose(self.manifest,'sample',['other.csv'])

if __name__=='__main__':unittest.main()
