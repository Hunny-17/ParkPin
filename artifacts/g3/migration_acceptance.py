"""Real G2 APK -> G3 APK upgrade on isolated AVD; UI seeds, read-only DB evidence."""
import hashlib
import json
import adb_qa as q

g2=q.ROOT/'.qa-tools/g2-final-installed.apk'
g3=q.ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert hashlib.sha256(g2.read_bytes()).hexdigest()=='c8ac8cef897412a95c236eb8111ffa6ccb9f5637228d483e7bbf54296c3f23a5'
q.adb('install','-r',str(g2))
q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
q.capture('migration-v1-initial',False)
assert not q.database('migration-v1-initial'), 'Refuse to overwrite existing records'
for name,floor,zone,column,note in [('QA-G3-MIG-A','B2','A','12','Migration_A'),('QA-G3-MIG-B','B3','C','22','Migration_B')]:
    q.tap('nav_save');q.fill(name,floor,zone,column,note);q.hide_keyboard();q.scroll();q.tap('btn_save_parking');q.hide_keyboard()
    t=q.capture('migration-v1-'+name,False);q.selected(t,'home');assert q.node(t,'home_spot_name').get('text')==name
before=q.database('migration-v1-before-upgrade')
metadata=json.loads((q.OUT/'database-migration-v1-before-upgrade.json').read_text())
assert len(before)==2 and metadata['user_version']==1
assert all('latitude' not in r for r in before)
q.adb('shell','am','force-stop',q.PACKAGE)
q.adb('install','-r',str(g3))  # no uninstall, clear, fixture SQL or destructive reset
q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
t=q.capture('G3-01-home-no-gps');q.selected(t,'home')
assert q.node(t,'home_spot_name').get('text')=='QA-G3-MIG-B'
assert not any(n.get('package','').endswith('.permissioncontroller') for n in t.iter('node'))
after=q.database('migration-v2-after-upgrade')
meta=json.loads((q.OUT/'database-migration-v2-after-upgrade.json').read_text())
assert meta['user_version']==2 and len(after)==len(before)
for old,new in zip(before,after):
    assert all(new[key]==value for key,value in old.items()), 'Legacy G2 field changed'
    assert all(new[key] is None for key in ['latitude','longitude','accuracyMeters','locationCapturedAt'])
assert all(c['notnull']==0 for c in meta['columns'] if c['name'] in ['latitude','longitude','accuracyMeters','locationCapturedAt'])
report={'status':'PASS','method':'Actual G2 APK seeded through UI; adb install -r G3 without clearing data',
        'g2_merged_app_tree':'4fd2251eaf624eb6893aaf5e6b4336068e670275','g2_apk_sha256':hashlib.sha256(g2.read_bytes()).hexdigest(),
        'g3_apk_sha256':hashlib.sha256(g3.read_bytes()).hexdigest(),'v1_rows':before,'v2_rows':after,
        'all_legacy_fields_identical':True,'new_gps_columns_nullable_and_null':True,'active_flag_and_history_preserved':True}
(q.OUT/'migration-tests.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
gps={'T01':{'status':'PASS','detail':'First G3 launch after real upgrade: no automatic permission dialog; request remains user initiated','evidence':'G3-01-home-no-gps.xml'}}
(q.OUT/'gps-tests.json').write_text(json.dumps(gps,indent=2),encoding='utf-8')
print('REAL APK MIGRATION PASS: all 9 legacy columns, IDs, two records, active flags and timestamps preserved; four new GPS columns NULL.',flush=True)
q.tap('nav_history')
for name in ['QA-G3-MIG-B','QA-G3-MIG-A']:
    q.row_action(name,'delete');q.tap('button1');q.time.sleep(.4)
assert not q.database('after-migration-qa-cleanup')
q.tap('nav_home')
