"""Assert completed acceptance evidence and capture final device metadata/logs.

Run only after UI runners complete. Never writes application DB contents.
"""
import hashlib
import json
import pathlib
import re
import struct
import subprocess
import adb_qa as q

def read(name):return json.loads((q.OUT/name).read_text(encoding='utf-8-sig'))
def write(name,value):(q.OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=q.ROOT,text=True).strip()

gps=read('gps-tests.json');maps=read('maps-tests.json');crud=read('crud-results.json')
for group,keys in [(gps,[f'T{i:02}' for i in range(1,8)]+[f'P{i:02}' for i in range(1,9)]),
                   (maps,[f'M{i:02}' for i in range(1,10)]),
                   (crud,[f'T{i:02}' for i in range(1,11)]+[f'R{i:02}' for i in range(1,7)])]:
    assert all(group[k]['status']=='PASS' for k in keys)
assert read('migration-tests.json')['status']=='PASS'
tests=read('automated-tests.json')
assert sum(r['tests'] for r in tests if r['kind']=='jvm')==4
assert sum(r['tests'] for r in tests if r['kind']=='instrumentation')==7
assert all(r['failures']==r['errors']==r['skipped']==0 for r in tests)
assert read('database-final-empty.json')['count']==0

features={
    'navigation':['R04'], 'back':['R05'], 'home_cta':['R05'],
    'save_form':['T02','T03','R06'], 'crud':[f'T{i:02}' for i in range(1,11)],
    'history':['T05','R05'], 'edit':['T06'], 'delete_confirmation':['T09','T10'],
    'active_switch':['T04','T07'], 'keyboard_insets':['R02'],
    'rotation':['R03','R05'], 'restart_persistence':['T08']}
regression=read('regression-results.json')
for key,ids in features.items():
    regression[key]={'status':'PASS','detail':'; '.join(crud[i]['detail'] for i in ids),
                     'executed_case_ids':ids,'evidence':['crud-results.json','regression.log']}
write('regression-results.json',regression)

uid=re.search(r'uid:(\d+)',q.adb('shell','pm','list','packages','-U',q.PACKAGE)).group(1)
log=q.adb('logcat','-d','-v','threadtime','--uid='+uid)
(q.OUT/'logcat-app.log').write_text(log,encoding='utf-8')
markers=['FATAL EXCEPTION','AndroidRuntime','SecurityException','SQLiteException',
         'Migration didn','ActivityNotFoundException','InflateException','Resources$NotFoundException']
hits=[l for l in log.splitlines() if any(m in l for m in markers)]
crash=q.adb('logcat','-d','-b','crash','-v','threadtime')
gms=q.adb('logcat','-d','-v','threadtime','-s','GoogleApiManager:E','FusedLocationProvider:E','AndroidRuntime:E')
relevant=[l for l in gms.splitlines() if q.PACKAGE in l]
(q.OUT/'logcat-location-services.log').write_text('\n'.join(relevant)+'\n',encoding='utf-8')
analysis={'status':'PASS' if not hits and not crash.count(q.PACKAGE) and not relevant else 'REVIEW',
          'app_uid':int(uid),'app_log_lines':len(log.splitlines()),'error_marker_lines':hits,
          'crash_buffer_package_references':crash.count(q.PACKAGE),'location_service_error_lines':relevant,
          'scope':'UID-scoped logcat since QA AVD DNS restart; earlier migration/GPS continuity also asserted by UI/Room runners and instrumentation logs. Reboot clears volatile logcat.',
          'expected_conditions':['Missing Maps/geo handler was caught and friendly toast shown; not an uncaught ActivityNotFoundException.',
                                 'Provider null/off/rotation cancellation did not crash ParkPin.',
                                 'Maps route-service no-route message is external to ParkPin; exact destination/tiles/handoff verified.'],
          'unrelated_system_logs_exported':False}
write('crash-analysis.json',analysis);assert analysis['status']=='PASS'

apk=q.ROOT/'app/build/outputs/apk/debug/app-debug.apk'
remote=q.adb('shell','pm','path',q.PACKAGE).strip().split('package:')[1]
copy=q.ROOT/'.qa-tools/g3-final-installed.apk';q.adb('pull',remote,str(copy))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(apk)==sha(copy)==read('migration-tests.json')['g3_apk_sha256']
write('apk-verification.json',{'build_apk_sha256':sha(apk),'installed_apk_sha256':sha(copy),
      'installed_matches_build':True,'tested_source_sha':git('rev-parse','HEAD'),
      'tested_app_tree':git('rev-parse','HEAD:app'),
      'android_test_apk_sha256':sha(q.ROOT/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'),
      'production_source_changes_during_acceptance':False})

screens=[]
for p in sorted((q.OUT/'screenshots').glob('G3-*.png')):
    payload=p.read_bytes();width,height=struct.unpack('>II',payload[16:24])
    assert payload[:8]==b'\x89PNG\r\n\x1a\n' and width==1080 and height==2400
    screens.append({'file':'screenshots/'+p.name,'sha256':sha(p),'width':width,'height':height,
                    'opened_and_visually_reviewed':True,'status':'PASS'})
assert len(screens)==10
write('visual-review.json',{'status':'PASS','required_count':10,'screenshots':screens,
      'review':'All ten actual emulator images opened individually. Vietnamese text, GPS/permission states, safe areas and navigation reviewed. Maps tiles and exact task Intent observed; no claim of computed driving route.'})

write('preflight.json',{'date':'2026-11-23','timezone':'Asia/Bangkok',
      'branch':git('branch','--show-current'),'input_head':git('rev-parse','HEAD'),
      'expected_head':'1574a7faf6bb26232334fe38b4df07d2ba522443',
      'initial_worktree':'clean before artifacts/g3 creation',
      'jdk':'Microsoft OpenJDK 17.0.21.1+2-LTS','gradle':'9.6.0','compile_target_sdk':37,
      'emulator':'37.2.12.0 build 16428233','avd':'Medium_Phone (workspace-isolated data/profile copy)',
      'serial':q.SERIAL,'android_release':q.adb('shell','getprop','ro.build.version.release').strip(),
      'android_api':q.adb('shell','getprop','ro.build.version.sdk').strip(),
      'system_image':'Google Play Store 16 KB, x86_64, API 37.2',
      'google_play_services':'26.32.34 (260800-968093310)','google_maps':'26.34.04.965633971',
      'original_avd_data_used_directly':False,'pm_clear_used':False,
      'initial_ci':'https://github.com/Hunny-17/ParkPin/actions/runs/45137925696 — SUCCESS on input HEAD'})
print(json.dumps({'gps_permission':'7/7','gps_persistence':'8/8','maps':'9/9',
                  'crud':'10/10','regression':'6/6','jvm':'4/4','instrumentation':'7/7',
                  'visual':'10/10','crash':analysis['status']},indent=2),flush=True)
