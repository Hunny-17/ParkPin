"""Actual system picker and durable photo UI acceptance; QA-created records only."""
import hashlib,json,sys,time
import qa_support as s
q=s.q
A='QA-G4-LEGACY-A';B='QA-G4-LEGACY-B'
GPS=['latitude','longitude','accuracyMeters','locationCapturedAt']
def entry(rows):return next(r for r in rows if r['placeName']==A)
def pick(index=0):
    t=q.dump();photos=[n for n in t.iter('node') if n.get('content-desc','').startswith('Photo taken on')]
    assert len(photos)>index,'Actual system picker has no requested QA photo'
    q.tap_node(photos[index]);time.sleep(.4)
    t=q.dump()
    if q.nodes(t,'Done'):q.tap('Done',t)
    time.sleep(1)
def owned(path):return q.adb('exec-out','run-as',q.PACKAGE,'cat','files/parking_photos/'+path,binary=True)
def photo_files():return q.adb('shell','run-as',q.PACKAGE,'ls','files/parking_photos',check=False).splitlines()
def save(name):
    q.hide_keyboard();q.scroll(times=2);q.tap('btn_save_parking');return q.capture(name,False)
def maps_and_cleanup(after):
    uri=f"google.navigation:q={after['latitude']:.7f},{after['longitude']:.7f}"
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        t=q.dump()
        if q.nodes(t,'permission_allow_foreground_only_button'):
            q.tap('permission_allow_foreground_only_button',t);continue
        if q.nodes(t,'No thanks'):q.tap('No thanks',t);continue
        raw=q.adb('shell','dumpsys','activity','activities')
        lines=[l.strip() for l in raw.splitlines() if 'topResumedActivity' in l or uri in l]
        if any('topResumedActivity' in l and 'com.google.android.apps.maps' in l for l in lines):break
        time.sleep(.5)
    else:raise AssertionError('Maps did not finish actual cold-start/permission flow')
    q.capture('G4-17-maps-regression');(q.OUT/'maps-activity.txt').write_text('\n'.join(lines)+'\n')
    assert any(uri in l for l in lines)
    s.close_maps()
    s.record('photo-results.json','P14','G3 regression: active parking with photo launched real Maps using exact Room destination; Back returned to ParkPin',['maps-activity.txt','G4-17-maps-regression.xml'])
    q.tap('nav_history');q.row_action(B,'activate');q.tap('nav_home');q.scroll();s.toast('card_find_car','G4-no-gps-toast')
    s.record('photo-results.json','P15','Manual-only B activation preserved single-active invariant; Find Car stayed in ParkPin with no-GPS toast',['G4-no-gps-toast.png'])
    q.tap('nav_history')
    for name in [A,B]:q.row_action(name,'delete');q.tap('button1');time.sleep(.4)
    q.tap('nav_home');q.capture('G4-18-final-empty');assert not q.database('photo-qa-final-empty')
    assert not photo_files(),photo_files()
    s.record('photo-results.json','P16','Deleted only UI-created QA A/B/C; Room and owned photo directory both empty; no data clearing',['database-photo-qa-final-empty.json','G4-18-final-empty.xml'])
phase=sys.argv[1]
if phase=='1':
    before=q.database('before-photo')
    pick(0);t=q.capture('G4-04-selected-preview');q.node(t,'photo_preview');assert q.node(t,'btn_pick_photo').get('text')=='ĐỔI ẢNH'
    files=photo_files();assert any(x.endswith('.jpg') for x in files)
    assert q.database('selected-draft-unchanged')==before
    original={k:q.adb('shell','settings','get',*k.split(':')).strip() for k in ['system:accelerometer_rotation','system:user_rotation','secure:show_ime_with_hard_keyboard']}
    (q.OUT/'settings-before.json').write_text(json.dumps(original,indent=2))
    q.adb('shell','settings','put','system','accelerometer_rotation','0');q.adb('shell','settings','put','system','user_rotation','1');time.sleep(.5)
    q.scroll(times=2);q.capture('G4-05-draft-landscape')
    q.adb('shell','settings','put','system','user_rotation','0');time.sleep(.5);q.scroll(times=2)
    t=q.capture('draft-portrait',False);q.node(t,'photo_preview');assert photo_files()==files
    s.record('photo-results.json','P02','Selected photo preview survived portrait/landscape with identical owned draft file; Room unchanged until Save',['G4-04-selected-preview.xml','G4-05-draft-landscape.xml','database-selected-draft-unchanged.json'])
    save('photo-save-home');after=q.database('photo-A-saved');a=entry(after)
    assert a['photoPath'] and all(a[k]==entry(before)[k] for k in GPS)
    payload=owned(a['photoPath']);assert payload.startswith(b'\xff\xd8')
    (q.OUT/'photo-A-owned.jpg').write_bytes(payload)
    q.tap('nav_history');q.row_action(A,'activate');q.tap('nav_home');q.scroll()
    t=q.capture('G4-06-home-photo');q.node(t,'home_photo')
    rows=q.database('photo-A-active');old=q.adb('shell','pidof',q.PACKAGE).strip()
    q.adb('shell','am','force-stop',q.PACKAGE);q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
    q.scroll();t=q.capture('G4-08-home-after-restart');q.node(t,'home_photo');assert q.database('photo-after-restart')==rows
    assert old!=q.adb('shell','pidof',q.PACKAGE).strip()
    s.record('photo-results.json','P03','Saved private JPEG and Room photoPath; GPS retained; force-stop/new process retained identical rows and photo',['database-photo-A-saved.json','database-photo-after-restart.json','G4-08-home-after-restart.xml'])
    q.adb('shell','rm','/sdcard/Pictures/ParkPinG4QA/g4-A.png')
    q.adb('shell','am','broadcast','-a','android.intent.action.MEDIA_SCANNER_SCAN_FILE','-d','file:///sdcard/Pictures/ParkPinG4QA/g4-A.png')
    q.adb('shell','am','force-stop',q.PACKAGE);q.adb('shell','am','start','-n',q.PACKAGE+'/.MainActivity');q.scroll()
    t=q.capture('photo-survives-source-deletion');q.node(t,'home_photo');assert hashlib.sha256(owned(a['photoPath'])).digest()==hashlib.sha256(payload).digest()
    s.record('photo-results.json','P04','Deleted only source QA fixture A from shared media; private saved JPEG and Home photo remained after restart',['photo-survives-source-deletion.xml'])
    q.tap('nav_history');q.capture('G4-07-history-photo');q.row_action(A,'edit')
    q.adb('shell','settings','put','secure','show_ime_with_hard_keyboard','1')
    q.fill(A,'B4','C','44','Manual_edit_with_photo');q.scroll(times=2);t=q.capture('G4-09-keyboard')
    ime=q.adb('shell','dumpsys','input_method');assert 'mInputShown=true' in ime
    _,top,_,bottom=q.bounds(q.node(t,'btn_save_parking'));_,ft,_,fb=q.bounds(q.node(t,'fragment_container'));assert ft<=top<bottom<=fb
    q.tap('btn_save_parking',t);q.hide_keyboard();q.capture('manual-edit-photo-home',False)
    final=entry(q.database('photo-manual-edit'));assert final['photoPath']==a['photoPath'] and all(final[k]==a[k] for k in GPS)
    s.record('photo-results.json','P05','Manual edit kept photo/GPS; update succeeded with software keyboard visible and button entirely above navigation',['G4-09-keyboard.xml','database-photo-manual-edit.json'])
elif phase=='2':
    before=q.database('before-replace');a=entry(before);old=a['photoPath']
    q.tap('nav_history');q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_pick_photo');pick(0)
    q.capture('replacement-draft',False);assert q.database('replace-draft-room')==before
    assert len(photo_files())==2
    q.adb('shell','input','keyevent','4');time.sleep(.7)
    assert photo_files()==[old] and q.database('discarded-replacement')==before
    s.record('photo-results.json','P06','Back after choosing a replacement discarded only the new draft; original photo and Room row unchanged',['database-discarded-replacement.json'])
    q.tap('nav_history');q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_pick_photo');pick(0)
    save('replacement-home');after=q.database('photo-replaced');new=entry(after)['photoPath']
    assert new and new!=old and old not in photo_files() and new in photo_files()
    assert all(entry(after)[k]==a[k] for k in GPS)
    q.scroll();t=q.capture('G4-10-replaced-photo');q.node(t,'home_photo')
    s.record('photo-results.json','P07','Explicit replacement saved a new owned JPEG and deleted old unreferenced file after DB success; GPS preserved',['database-photo-replaced.json','G4-10-replaced-photo.xml'])
    q.tap('nav_history');q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_remove_photo')
    assert entry(q.database('remove-draft-room'))['photoPath']==new
    q.adb('shell','input','keyevent','4');time.sleep(.5)
    assert new in photo_files() and entry(q.database('remove-draft-cancelled'))['photoPath']==new
    s.record('photo-results.json','P08','Removing a photo then leaving without Save kept the committed photo and file',['database-remove-draft-cancelled.json'])
    q.tap('nav_save');q.fill('QA-G4-PHOTO-C','B6','F','66','Photo_only_no_GPS');q.hide_keyboard();q.scroll(times=2);q.tap('btn_pick_photo');pick(0)
    save('new-photo-C-home');rows=q.database('new-photo-C');c=next(r for r in rows if r['placeName']=='QA-G4-PHOTO-C')
    assert c['photoPath'] and c['latitude'] is None and sum(r['active'] for r in rows)==1
    q.tap('nav_history');q.capture('G4-13-history-top');q.scroll(times=3);t=q.capture('G4-14-history-scrolled')
    q.node(q.row(t,A),'item_photo');q.scroll(False,3);t=q.capture('history-return-top');q.node(q.row(t,'QA-G4-PHOTO-C'),'item_photo')
    s.record('photo-results.json','P09','Photo-only new C saved without GPS; History images loaded at top/bottom and again when scrolling back after viewport cleanup',['database-new-photo-C.json','G4-13-history-top.xml','G4-14-history-scrolled.xml','history-return-top.xml'])
    q.row_action('QA-G4-PHOTO-C','delete');q.capture('G4-15-delete-photo-dialog');q.tap('button1');q.capture('deleted-C-history',False)
    rows=q.database('photo-C-deleted');assert len(rows)==2 and c['photoPath'] not in photo_files() and new in photo_files()
    s.record('photo-results.json','P10','Confirmed deletion removed photo record C and only its owned file; A photo retained',['G4-15-delete-photo-dialog.xml','database-photo-C-deleted.json'])
    q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_remove_photo');save('removed-photo-home')
    rows=q.database('photo-removed');assert entry(rows)['photoPath'] is None and new not in photo_files()
    q.scroll();q.capture('G4-11-photo-removed')
    s.record('photo-results.json','P11','Explicit remove plus Save cleared nullable photoPath and removed owned file; parking/GPS retained',['database-photo-removed.json','G4-11-photo-removed.xml'])
    q.tap('nav_history');q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_pick_photo');pick(0);save('missing-source-setup')
    q.tap('nav_history');q.row_action(A,'activate');q.tap('nav_home')
    path=entry(q.database('before-missing-file'))['photoPath']
    q.adb('shell','run-as',q.PACKAGE,'rm','files/parking_photos/'+path)
    q.adb('shell','am','force-stop',q.PACKAGE);q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity');q.scroll()
    t=q.capture('G4-12-image-unavailable');assert 'Không tải được ảnh' in q.node(t,'home_photo_status').get('text','')
    q.tap('nav_history');q.row_action(A,'edit');q.text_field('input_note','Missing_file_manual_save');save('missing-file-manual-home')
    rows=q.database('missing-file-manual-saved');assert entry(rows)['photoPath']==path and entry(rows)['note']=='Missing_file_manual_save'
    s.record('photo-results.json','P12','Simulated missing owned QA photo: friendly error, no crash; manual update still succeeded without silently clearing path/GPS',['G4-12-image-unavailable.xml','database-missing-file-manual-saved.json'])
    q.tap('nav_history');q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_remove_photo');save('missing-file-cleared')
elif phase=='3':
    before=entry(q.database('before-gps-recapture'))
    q.tap('nav_history');q.row_action(A,'edit');q.scroll(times=2);q.tap('btn_pick_photo')
    q.adb('shell','settings','put','system','user_rotation','1');time.sleep(.5)
    q.capture('picker-landscape',False);pick(0)
    q.adb('shell','settings','put','system','user_rotation','0');time.sleep(.5)
    q.scroll(False,3);q.tap('btn_capture_gps');s.inject('G4-recapture-with-photo',10.776889,106.700806,8)
    status=s.wait_gps('G4-16-photo-and-gps');assert status.startswith('GPS:')
    save('recapture-photo-home');after=entry(q.database('gps-recaptured-with-photo'))
    assert after['photoPath'] and abs(after['latitude']-10.776889)<.00001 and after['locationCapturedAt']>before['locationCapturedAt']
    s.record('photo-results.json','P13','Rotated while system picker was open; selected photo returned to correct edit; explicit GPS recapture saved photo and new provider fix to same ID',['picker-landscape.xml','G4-16-photo-and-gps.xml','database-gps-recaptured-with-photo.json'])
    q.adb('shell','am','force-stop','com.google.android.apps.maps');q.scroll();q.tap('card_find_car');time.sleep(2)
    maps_and_cleanup(after)
elif phase=='4':maps_and_cleanup(entry(q.database('maps-resume-source')))
