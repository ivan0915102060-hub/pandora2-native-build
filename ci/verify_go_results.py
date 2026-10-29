"""Check actual Linux go-test JSON, rejecting skipped/missing tests."""
import json,sys
from pathlib import Path

lock=json.loads(Path(sys.argv[1]).read_text());events=[json.loads(line) for line in Path(sys.argv[2]).read_text().splitlines() if line.startswith('{')]
assert events and not any(e.get('Action') in ('skip','fail') for e in events),'SKIPPED_OR_FAILED_NOT_PASS'
expected={(row['package'],name) for row in lock['linuxTests'] for name in row['tests']}
passed={(e['Package'],e['Test']) for e in events if e.get('Action')=='pass' and 'Test' in e}
assert passed==expected,('MISSING_OR_EXTRA_TESTS',sorted(expected-passed),sorted(passed-expected))
print(json.dumps({'linuxNewTests':'PASS','count':len(passed),'androidJniRuntime':'NOT_RUN'}))
