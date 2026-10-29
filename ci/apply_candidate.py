"""CI-only exact public derivative patch application; never run locally here."""
import argparse,hashlib,json,subprocess
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',required=True);parser.add_argument('--payload',required=True);args=parser.parse_args()
    work=Path(args.work).resolve();payload=Path(args.payload).resolve()
    lock=json.loads((payload/'ci/source-lock.json').read_text())
    assert lock['sourceReview']=='READY_FOR_CI_REVIEW_NOT_RUNTIME_QUALIFIED'
    roots={'amneziawg-android':work/'source','amneziawg-go':work/'amneziawg-go'}
    for repo,commit in lock['commits'].items():assert git(roots[repo],'rev-parse','HEAD')==commit,'WRONG_TREE'
    for row in lock['baseline']:
        assert digest(roots[row['repo']]/row['path'])==row['sha256'],'BASELINE_CHANGED'
    # 00's audited compatibility correction has already been applied to Makefile,
    # which is NOT one of B's patched-source baseline entries.
    makefile=roots['amneziawg-android']/'tunnel/tools/libwg-go/Makefile'
    text=makefile.read_text();assert 'GO_VERSION := 1.26.10' in text and 'GO_VERSION := 1.24.2' not in text
    assert 'GO_HASH_linux-amd64 := ccfe7ae822d2c2f41f4fe7c956199967a4dac22d0ee0d2b2bfdb440aab3b20c5' in text
    for row in lock['patches']:
        patch=payload/row['file'];assert digest(patch)==row['sha256'],'PATCH_CHANGED'
        root=roots[row['repo']]
        subprocess.run(['git','-C',str(root),'apply','-p3','--check','--verbose',str(patch)],check=True)
        subprocess.run(['git','-C',str(root),'apply','-p3',str(patch)],check=True)
    for row in lock['candidate']:
        assert digest(roots[row['repo']]/row['path'])==row['sha256'],'PATCH_OUTPUT_CHANGED'
    mod=(roots['amneziawg-android']/'tunnel/tools/libwg-go/go.mod').read_text()
    replace='replace github.com/amnezia-vpn/amneziawg-go/v3 => ../../../../amneziawg-go'
    assert mod.count(replace)==1,'REPLACE_NOT_EXACT'
    assert (roots['amneziawg-android']/'tunnel/tools/libwg-go/../../../../amneziawg-go').resolve()==roots['amneziawg-go'].resolve()
    print('EXACT_BASELINE_PATCH_OUTPUT_AND_REPLACE=PASS')
if __name__=='__main__':main()
