"""Reject dataset/checkpoint/cache payloads in the current Git index (history is unchanged)."""
import subprocess
from pathlib import Path
ALLOWED_CSV={'paper/workflow/results.csv'}
BAD_PREFIX=('evidence/','data/','datasets/','models/','checkpoints/','outputs/','cache/','.cache/','.venv/','venv/')
BAD_SUFFIX={'.parquet','.arrow','.feather','.h5','.hdf5','.npy','.npz','.pt','.pth','.ckpt','.safetensors','.pkl','.joblib','.tar','.gz','.zip','.bin'}
def main():
    bad=[]
    for s in subprocess.check_output(['git','ls-files','-z']).decode().split('\0'):
        if not s:continue
        p=Path(s)
        if s.startswith(BAD_PREFIX) or p.suffix in BAD_SUFFIX or (p.suffix=='.csv' and s not in ALLOWED_CSV) or p.name.startswith('.env') or p.name in ['token','stored_tokens','credentials','id_rsa','id_ed25519']:
            bad.append(s)
        elif p.is_file() and p.stat().st_size>1_000_000:bad.append(s+' (>1MB; review as asset)')
    if bad:raise SystemExit('Disallowed tracked assets:\n'+'\n'.join(bad))
    print('PASS: code/config/docs/lightweight summaries only in current Git index; history not rewritten')
if __name__=='__main__':main()
