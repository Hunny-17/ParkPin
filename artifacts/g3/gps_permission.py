"""Real runtime denial/manual save and approximate permission flow."""
import g3_support as s
q=s.q
t=q.capture('permission-dialog-check',False)
q.node(t,'permission_message');q.node(t,'permission_deny_button')
s.record('gps-tests.json','T02','User LẤY GPS action opened actual coarse/fine Android runtime permission dialog',['G3-02-gps-permission.xml'])
q.tap('permission_deny_button',t);t=q.capture('G3-03-permission-denied')
assert 'Không được cấp quyền' in q.node(t,'gps_status').get('text')
assert s.permissions('denied')=={'COARSE':False,'FINE':False}
q.fill('QA-G3-B','B2','B','08','Manual_after_denial');q.hide_keyboard();q.scroll()
t=q.dump();l,top,r,b=q.bounds(q.node(t,'btn_save_parking'));x=(l+r)//2;y=(top+b)//2
q.adb('shell',f'for n in 1 2 3 4 5; do input tap {x} {y}; done')
q.hide_keyboard();t=q.capture('manual-after-denial-home',False)
assert q.node(t,'home_spot_name').get('text')=='QA-G3-B'
rows=q.database('manual-after-denial');assert len(rows)==1 and rows[0]['latitude'] is None and rows[0]['longitude'] is None
s.record('gps-tests.json','T03','Denied both location permissions; real manual Save succeeded with NULL coordinates',['G3-03-permission-denied.xml','database-manual-after-denial.json'])
s.record('gps-tests.json','P05','Manual-only position B saved and displayed correctly without GPS',['database-manual-after-denial.json'])
s.record('regression-results.json','rapid_save','Five real consecutive Save taps produced one B row',['database-manual-after-denial.json'])
q.scroll();s.toast('card_find_car','maps-no-gps-toast')
s.record('maps-tests.json','M02','Saved active B has no GPS; friendly toast captured and ParkPin stayed foreground',['maps-no-gps-toast.png','maps-no-gps-toast-foreground.txt'])
q.tap('nav_save');q.tap('btn_capture_gps');t=q.capture('approximate-permission-dialog',False)
q.tap('permission_location_accuracy_radio_coarse',t)
q.tap('permission_allow_foreground_only_button')
s.inject('approximate',10.776889,106.700806)
text=s.wait_gps('G3-04-approximate-location')
assert s.permissions('approximate')=={'COARSE':True,'FINE':False}
assert text.startswith('Vị trí gần đúng:'), 'Coarse-only provider did not return a usable fix: '+text
s.provider_trace('approximate')
s.record('gps-tests.json','T04','Approximate-only runtime grant accepted; actual Fused Location Provider returned a coarse fix: '+text,['G3-04-approximate-location.xml','permissions-approximate.txt','provider-approximate.txt'])
