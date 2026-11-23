"""Location-off, enabled-but-no-fix and pending-rotation acceptance on QA AVD."""
import time
import g3_support as s
q=s.q
before=q.database('gps-before-unavailable')
q.tap('nav_history');q.row_action('QA-G3-B','edit')
q.adb('shell','cmd','location','set-location-enabled','false')
try:
    t=q.dump()
    if q.nodes(t,'No location access'):q.tap('Close',t)
    q.tap('btn_capture_gps')
    text=s.wait_gps('G3-09-location-unavailable')
    assert 'GPS:' not in text and ('Chưa lấy được GPS' in text or 'Không thể lấy GPS' in text)
    assert q.database('gps-location-off')==before
    s.record('gps-tests.json','T06','Master location disabled: request settled with friendly manual-save message; Room unchanged and app alive',['G3-09-location-unavailable.xml','database-gps-location-off.json'])
finally:q.adb('shell','cmd','location','set-location-enabled','true')
# Replace GPS provider with an enabled test provider that emits no location. No
# coordinates are supplied; this deliberately tests a provider that cannot fix.
q.adb('shell','appops','set','com.android.shell','android:mock_location','allow')
q.adb('shell','cmd','location','providers','add-test-provider','gps','--requiresSatellite')
try:
    q.adb('shell','cmd','location','providers','set-test-provider-enabled','gps','true')
    time.sleep(6)
    q.tap('btn_capture_gps')
    text=s.wait_gps('gps-enabled-no-fix')
    assert 'GPS:' not in text and ('Chưa lấy được GPS' in text or 'Không thể lấy GPS' in text),text
    q.text_field('input_note','No_fix_manual_update');q.hide_keyboard();q.scroll();q.tap('btn_save_parking')
    q.capture('gps-no-fix-manual-save',False)
    after=q.database('gps-no-fix-manual-saved');b=next(r for r in after if r['placeName']=='QA-G3-B')
    assert b['note']=='No_fix_manual_update' and all(b[k] is None for k in ['latitude','longitude','accuracyMeters','locationCapturedAt'])
    assert next(r for r in after if r['placeName']=='QA-G3-A')==next(r for r in before if r['placeName']=='QA-G3-A')
    s.record('gps-tests.json','T07','Enabled GPS test provider emitted no fixes: friendly timeout, manual UI update succeeded, all B GPS columns remain NULL and A unchanged',['gps-enabled-no-fix.xml','database-gps-no-fix-manual-saved.json'])
    q.tap('nav_history');q.row_action('QA-G3-B','edit')
    q.adb('shell','settings','put','system','accelerometer_rotation','0')
    q.adb('shell','settings','put','system','user_rotation','0')
    t=q.dump();x,y,r,b=q.bounds(q.node(t,'btn_capture_gps'))
    q.adb('shell','input','tap',str((x+r)//2),str((y+b)//2))
    # Capture the pending state before the 15s request times out.
    t=q.capture('gps-rotation-pending',False)
    assert q.node(t,'gps_status').get('text').startswith('Đang lấy vị trí')
    q.adb('shell','settings','put','system','user_rotation','1');time.sleep(.5)
    t=q.capture('gps-rotation-landscape');q.selected(t,'save')
    q.adb('shell','settings','put','system','user_rotation','0');time.sleep(.5)
    t=q.capture('gps-rotation-restored',False);q.selected(t,'save')
    assert q.node(t,'input_place_name').get('text')=='QA-G3-B'
    q.scroll();q.tap('btn_save_parking');q.capture('gps-rotation-saved',False)
    final=q.database('gps-after-pending-rotation')
    assert len(final)==2 and next(r for r in final if r['placeName']=='QA-G3-A')==next(r for r in after if r['placeName']=='QA-G3-A')
    b=next(r for r in final if r['placeName']=='QA-G3-B')
    assert all(b[k] is None for k in ['latitude','longitude','accuracyMeters','locationCapturedAt'])
    s.record('gps-tests.json','P08','Rotated portrait/landscape during actual pending request; same B edit saved with NULL GPS, A unchanged and no crash',['gps-rotation-pending.xml','gps-rotation-landscape.xml','database-gps-after-pending-rotation.json'])
finally:
    q.adb('shell','cmd','location','providers','remove-test-provider','gps')
    q.adb('shell','appops','set','com.android.shell','android:mock_location','default')
    q.adb('shell','settings','put','system','user_rotation','0')
