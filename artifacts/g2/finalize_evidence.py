"""Verify final real-device evidence, collect scoped logs, restore AVD settings."""
import hashlib
import json
import re
import adb_qa as q

cases=json.loads((q.OUT/'crud-results.json').read_text(encoding='utf-8'))
required={f'T{i:02d}' for i in range(1,11)}|{f'R{i:02d}' for i in range(1,7)}
assert required<=set(cases) and all(cases[k]['status']=='PASS' for k in required)
tests=json.loads((q.OUT/'database-tests.json').read_text(encoding='utf-8'))
assert {r['kind']:r['tests'] for r in tests}=={'jvm':1,'instrumentation':5}
assert all(r['failures']==r['errors']==r['skipped']==0 for r in tests)
assert json.loads((q.OUT/'database-final-empty.json').read_text())['count']==0

package=q.adb('shell','pm','list','packages','-U',q.PACKAGE)
uid=re.search(r'uid:(\d+)',package).group(1)
log=q.adb('logcat','-d','-v','threadtime','--uid='+uid)
(q.OUT/'logcat-app.log').write_text(log,encoding='utf-8')
markers=['FATAL EXCEPTION','AndroidRuntime','InflateException','Resources$NotFoundException']
hits=[line for line in log.splitlines() if any(marker in line for marker in markers)]
crashes=q.adb('logcat','-d','-b','crash','-v','threadtime')
report={'app_uid':int(uid),'app_log_lines':len(log.splitlines()),'crash_marker_lines':hits,
        'crash_buffer_package_references':crashes.count(q.PACKAGE),
        'scope':'Final installed app UID; unrelated system crashes excluded'}
(q.OUT/'crash-analysis.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not hits and report['crash_buffer_package_references']==0

apk=q.ROOT/'app/build/outputs/apk/debug/app-debug.apk'
installed_path=q.adb('shell','pm','path',q.PACKAGE).strip().split('package:')[1]
copy=q.ROOT/'.qa-tools/g2-final-installed.apk'
q.adb('pull',installed_path,str(copy))
expected=hashlib.sha256(apk.read_bytes()).hexdigest()
actual=hashlib.sha256(copy.read_bytes()).hexdigest()
assert expected==actual
test_apk=q.ROOT/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'
metadata={'build_apk_sha256':expected,'installed_apk_sha256':actual,'installed_matches_build':True,
          'android_test_apk_sha256':hashlib.sha256(test_apk.read_bytes()).hexdigest(),
          'build_tasks':'clean assembleDebug testDebugUnitTest assembleDebugAndroidTest',
          'crud_cases':10,'regression_cases':6}
(q.OUT/'apk-verification.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')

original=json.loads((q.OUT/'emulator-settings-before.json').read_text(encoding='utf-8'))
after={}
for pair,value in original.items():
    namespace,key=pair.split(':')
    q.adb('shell','settings','delete' if value=='null' else 'put',namespace,key,*([] if value=='null' else [value]))
    after[pair]=q.adb('shell','settings','get',namespace,key).strip()
assert after==original
(q.OUT/'emulator-settings-restored.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
print(json.dumps({'crud':'10/10 PASS','regression':'6/6 PASS','jvm':'1/1 PASS','instrumentation':'5/5 PASS',
                  'crash_analysis':report,'apk_verification':metadata,'avd_settings_restored':True},indent=2),flush=True)
