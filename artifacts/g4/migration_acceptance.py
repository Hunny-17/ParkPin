"""Actual merged G3 APK upgrade to G4; all records created through UI."""
import json
import qa_support as s
q=s.q
q.tap('nav_save');q.tap('btn_capture_gps')
t=q.capture('migration-g3-permission',False)
q.tap('permission_allow_foreground_only_button',t)
s.inject('g4-migration-G3-fix',21.028511,105.804817,8)
status=s.wait_gps('migration-g3-gps')
assert status.startswith('GPS:'),status
q.fill('QA-G4-LEGACY-A','B2','A','12','G3_GPS_preserved');q.hide_keyboard();q.scroll();q.tap('btn_save_parking')
q.capture('migration-g3-A-home',False)
q.tap('nav_save');q.fill('QA-G4-LEGACY-B','B3','B','22','G3_manual_preserved');q.hide_keyboard();q.scroll();q.tap('btn_save_parking')
q.capture('migration-g3-B-home',False)
before=q.database('migration-v2-before')
assert len(before)==2 and before[0]['latitude'] is not None and before[1]['latitude'] is None
q.adb('shell','am','force-stop',q.PACKAGE)
q.adb('install','-r',str(q.ROOT/'app/build/outputs/apk/debug/app-debug.apk'))
q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
q.capture('G4-01-migrated-home')
after=q.database('migration-v3-after')
assert len(after)==2
for old,new in zip(before,after):
    assert all(new[k]==v for k,v in old.items()) and new['photoPath'] is None
assert json.loads((q.OUT/'database-migration-v3-after.json').read_text())['user_version']==3
(q.OUT/'migration-results.json').write_text(json.dumps({'status':'PASS','method':'Actual G3 APK seeded via UI, install -r G4 without data clear','before':before,'after':after},indent=2))
print('Actual G3 -> G4 migration PASS',flush=True)
