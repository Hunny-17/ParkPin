"""Real precise permission, Room persistence and explicit recapture acceptance."""
import sys
import time
import g3_support as s
q=s.q
GPS=['latitude','longitude','accuracyMeters','locationCapturedAt']
def a(rows):return next(r for r in rows if r['placeName']=='QA-G3-A')
phase=sys.argv[1]
if phase=='1':
    q.tap('permission_location_accuracy_radio_fine')
    q.tap('permission_allow_foreground_only_button')
    s.inject('precise-HCMC',10.776889,106.700806,8)
    text=s.wait_gps('G3-05-precise-location')
    assert text.startswith('GPS:') and s.permissions('precise')=={'COARSE':True,'FINE':True}
    s.provider_trace('precise')
    s.record('gps-tests.json','T05','Precise permission returned actual FLP fix: '+text,['G3-05-precise-location.xml','permissions-precise.txt','provider-precise.txt'])
    q.fill('QA-G3-A','B4','D','44','GPS_HCMC');q.hide_keyboard();q.scroll();q.tap('btn_save_parking')
    t=q.capture('G3-06-save-with-gps');assert q.node(t,'home_spot_name').get('text')=='QA-G3-A'
    rows=q.database('gps-A-saved');entry=a(rows)
    assert len(rows)==2 and abs(entry['latitude']-10.776889)<.00001 and abs(entry['longitude']-106.700806)<.00001
    assert entry['accuracyMeters']>0 and entry['locationCapturedAt']>0 and sum(r['active'] for r in rows)==1
    s.record('gps-tests.json','P01','Saved A via real form; all four GPS fields persisted and match emulator HCMC fix',['database-gps-A-saved.json','G3-06-save-with-gps.xml'])
    old=q.adb('shell','pidof',q.PACKAGE).strip();q.adb('shell','am','force-stop',q.PACKAGE)
    assert not q.adb('shell','pidof',q.PACKAGE,check=False).strip()
    q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
    t=q.capture('G3-10-home-after-restart');assert q.node(t,'home_spot_name').get('text')=='QA-G3-A'
    assert q.adb('shell','pidof',q.PACKAGE).strip()!=old and q.database('gps-A-restarted')==rows
    s.record('gps-tests.json','P02','Actual force-stop/new process retained identical rows and GPS fields',['G3-10-home-after-restart.xml','database-gps-A-restarted.json'])
elif phase=='2':
    before=a(q.database('gps-A-before-manual-edit'))
    q.tap('nav_history');q.row_action('QA-G3-A','edit');q.capture('gps-edit-form')
    q.fill('QA-G3-A','B5','E','55','Manual_edit_preserves_GPS');q.hide_keyboard();q.scroll();q.tap('btn_save_parking')
    q.capture('gps-manual-edit-home',False);after=a(q.database('gps-A-after-manual-edit'))
    assert after['id']==before['id'] and after['note']=='Manual_edit_preserves_GPS'
    assert all(after[k]==before[k] for k in GPS)
    s.record('gps-tests.json','P03','Manual edit updated floor/zone/column/note and preserved all four existing GPS fields',['database-gps-A-before-manual-edit.json','database-gps-A-after-manual-edit.json'])
    q.tap('nav_history');q.row_action('QA-G3-A','edit');q.tap('btn_capture_gps')
    s.inject('recapture-Hanoi',21.028511,105.804817,8)
    text=s.wait_gps('gps-explicit-recapture');assert text.startswith('GPS:')
    q.scroll();q.tap('btn_save_parking');q.capture('gps-recaptured-home',False)
    after=a(q.database('gps-A-recaptured'))
    assert after['id']==before['id'] and abs(after['latitude']-21.028511)<.00001 and abs(after['longitude']-105.804817)<.00001
    assert after['locationCapturedAt']>before['locationCapturedAt']
    s.provider_trace('recaptured')
    s.record('gps-tests.json','P04','Explicit LẤY GPS recapture updated same A ID to real Hanoi fix and a newer capture timestamp',['gps-explicit-recapture.xml','database-gps-A-recaptured.json','provider-recaptured.txt'])
