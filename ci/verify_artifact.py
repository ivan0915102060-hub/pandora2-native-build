"""Read Java bytecode declarations and Android ELF symbols; never execute either."""
import argparse,hashlib,json,os,subprocess,zipfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--aar',required=True);p.add_argument('--lock',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    aar=Path(args.aar);out=Path(args.out);out.mkdir(exist_ok=False);lock=json.loads(Path(args.lock).read_text())
    rows=[]
    with zipfile.ZipFile(aar) as z:
        data=z.read('classes.jar');classes=out/'classes.jar';classes.write_bytes(data)
        with zipfile.ZipFile(classes) as jar:assert 'org/pandora/nativebridge/ProtectedAwgNative.class' in jar.namelist()
        javap=subprocess.check_output([str(Path(os.environ['JAVA_HOME'])/'bin/javap'),'-private','-s','-classpath',str(classes),'org.pandora.nativebridge.ProtectedAwgNative'],text=True)
        (out/'protected-api.txt').write_text(javap)
        for method in lock['javaMethods']:assert method in javap,('MISSING_JAVA_API',method)
        for descriptor in lock['jniDescriptors'].values():assert descriptor in javap,('MISSING_JNI_DESCRIPTOR',descriptor)
        rules=z.read('proguard.txt').decode('utf8')
        for required in lock['consumerRules']:assert required in rules,('MISSING_CONSUMER_RULE',required)
        (out/'packaged-consumer-rules.txt').write_text(rules)
        nm=Path(os.environ['ANDROID_HOME'])/'ndk/26.1.10909125/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-nm'
        for abi in ('arm64-v8a','armeabi-v7a','x86','x86_64'):
            binary=z.read('jni/'+abi+'/libwg-go.so');assert binary[:4]==b'\x7fELF'
            dest=out/(abi+'.so');dest.write_bytes(binary)
            symbols=subprocess.check_output([str(nm),'-D','--defined-only',str(dest)],text=True)
            (out/(abi+'-symbols.txt')).write_text(symbols)
            names={line.split()[-1] for line in symbols.splitlines() if line.split()}
            for name in lock['jniExports']:assert name in names,('MISSING_JNI_EXPORT',abi,name)
            rows.append({'abi':abi,'sha256':hashlib.sha256(binary).hexdigest(),'bytes':len(binary)})
    (out/'static-review.json').write_text(json.dumps({'staticApiAndJniExports':'PASS','aarSha256':hashlib.sha256(aar.read_bytes()).hexdigest(),'abis':rows,'jniExecution':'NOT_RUN','phone':'NOT_RUN'},indent=2)+'\n')
if __name__=='__main__':main()
