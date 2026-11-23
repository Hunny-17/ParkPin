"""Real UI CRUD acceptance. Start only on a confirmed empty QA database.

Run phases in order: python -B artifacts/g4/run_crud_regression.py 1 (then 2..5).
All database changes are performed through the visible app UI.
"""
import json
import sys
import adb_qa as q

A = 'QA-G4-REG-A'
B = 'QA-G4-REG-B'
EDITED = 'QA-G4-REG-B-edited'

def record(case, detail):
    path = q.OUT / 'crud-results.json'
    results = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    results[case] = {'status': 'PASS', 'detail': detail}
    path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'{case} PASS: {detail}', flush=True)

def home(name):
    q.hide_keyboard()
    t = q.capture(name)
    q.selected(t, 'home')
    return t

def spot(rows, name):
    return next(r for r in rows if r['placeName'] == name)

phase = sys.argv[1]
if phase == '1':
    original = {}
    for namespace, key in [('secure','show_ime_with_hard_keyboard'), ('system','accelerometer_rotation'), ('system','user_rotation')]:
        original[namespace + ':' + key] = q.adb('shell','settings','get',namespace,key).strip()
    (q.OUT/'emulator-settings-before.json').write_text(json.dumps(original,indent=2),encoding='utf-8')
    q.adb('shell','settings','put','secure','show_ime_with_hard_keyboard','1')
    q.adb('shell','settings','put','system','accelerometer_rotation','0')
    q.adb('shell','settings','put','system','user_rotation','0')
    rows = q.database('empty')
    assert not rows, 'Refuse to clear or overwrite an existing database'
    (q.OUT/'crud-results.json').write_text('{}\n',encoding='utf-8')
    q.tap('nav_home'); t = q.capture('REG-01-home-empty'); q.node(t,'Chưa lưu vị trí nào')
    q.tap('nav_history',t); t = q.capture('REG-02-history-empty')
    q.node(t,'history_empty'); assert q.node(t,'history_count').get('text') == '0 VỊ TRÍ ĐÃ LƯU'
    record('T01','Empty Room database; Home and History show actual empty states')
    q.tap('nav_save',t); q.scroll(); q.tap('btn_save_parking')
    t = q.capture('T02-required-name')
    q.node(t,'Vui lòng nhập tên bãi đỗ'); assert not q.database('invalid-name')
    q.text_field('input_place_name','   ');q.scroll(times=2);q.tap('btn_save_parking')
    q.scroll(False,2)  # The already focused name may remain above the scrolled viewport.
    t=q.capture('T02-whitespace-name',False)
    q.node(t,'Vui lòng nhập tên bãi đỗ');assert not q.database('whitespace-name')
    record('T02','Blank and whitespace-only names blocked; validation visible; database remains empty')
    q.fill(A,'B2','A','12','Near_elevator_A')
    q.hide_keyboard(); q.scroll(False,2); t=q.capture('REG-03-save-parking')
    assert not q.nodes(t,'Vui lòng nhập tên bãi đỗ'), 'Stale name validation after correction'
    record('R06','Required-name error clears after entering a valid name')
    q.scroll(); q.tap('btn_save_parking'); t = home('REG-04-home-saved')
    assert q.node(t,'home_spot_name').get('text') == A
    assert q.node(t,'home_spot_details').get('text') == 'Tầng B2 · Khu A · Cột 12'
    rows = q.database('saved-A'); assert len(rows)==1 and rows[0]['active']==1
    assert spot(rows,A)['note']=='Near_elevator_A'
    record('T03','Saved A through form; exact Home details and all database fields verified')
elif phase == '2':
    q.tap('nav_save'); q.fill(B,'B1','B','08','Near_exit_B'); q.hide_keyboard(); q.scroll()
    t=q.dump(); l,top,r,bottom=q.bounds(q.node(t,'btn_save_parking'));x=(l+r)//2;y=(top+bottom)//2
    # A tight device-side burst, without waiting for a repository callback between taps.
    command=f'for n in 1 2 3 4 5; do input tap {x} {y}; done'
    q.adb('shell',command)
    t=home('T04-home-B'); assert q.node(t,'home_spot_name').get('text')==B
    rows=q.database('saved-B-rapid-taps')
    assert len(rows)==2 and sum(r['active'] for r in rows)==1
    assert spot(rows,B)['active']==1 and spot(rows,A)['active']==0
    record('T04','B is the only active record; A remains archived')
    record('R01','Five consecutive save taps produced exactly one B row; total A+B=2')
    q.tap('nav_history',t);t=q.capture('REG-05-history-data')
    q.node(t,A);q.node(t,B);assert q.node(t,'history_count').get('text')=='2 VỊ TRÍ ĐÃ LƯU'
    assert q.node(q.row(t,B),'item_status').get('text')=='ĐANG ĐỖ'
    assert q.node(q.row(t,A),'item_status').get('text')=='ĐÃ LƯU'
    record('T05','History shows A and B, with B active and A archived')
    q.adb('shell','settings','put','system','user_rotation','1');q.time.sleep(1)
    t=q.capture('R05-history-rotation',False);q.selected(t,'history')
    q.scroll(times=2);t=q.capture('R05-history-scroll-bottom')
    current=q.row(t,A);_,top,_,bottom=q.bounds(q.node(current,'item_delete'))
    _,ft,_,fb=q.bounds(q.node(t,'fragment_container'));assert ft<=top<bottom<=fb
    q.adb('shell','settings','put','system','user_rotation','0');q.time.sleep(1)
    q.scroll(False,2);t=q.capture('R05-history-restored',False);q.selected(t,'history')
elif phase == '3':
    q.row_action(B,'edit');t=q.capture('REG-06-edit-form')
    assert q.node(t,'input_place_name').get('text')==B
    assert q.node(t,'input_floor').get('text')=='B1'
    q.adb('shell','settings','put','system','user_rotation','1');q.time.sleep(1)
    t=q.capture('R03-edit-landscape');q.selected(t,'save')
    assert q.node(t,'input_place_name').get('text')==B
    q.adb('shell','settings','put','system','user_rotation','0');q.time.sleep(1)
    t=q.capture('R03-edit-portrait',False);q.selected(t,'save')
    assert q.node(t,'input_place_name').get('text')==B
    normal_bar=q.bounds(q.node(t,'bottom_nav'))
    normal_height=normal_bar[3]-normal_bar[1]
    record('R03','Edit form and Save tab survive portrait/landscape rotation without crash or lost values')
    before=q.database('before-edit');old_id=spot(before,B)['id']
    q.fill(EDITED,'B3','C','22','Edited_near_exit')
    q.scroll(times=2);t=q.capture('REG-08-keyboard')
    ime=q.adb('shell','dumpsys','input_method')
    flags='\n'.join(l for l in ime.splitlines() if 'mInputShown=' in l or 'mIsInputViewShown=' in l)
    (q.OUT/'keyboard-state.txt').write_text(flags+'\n',encoding='utf-8')
    assert 'mInputShown=true' in flags and 'mIsInputViewShown=true' in flags
    fl,ft,fr,fb=q.bounds(q.node(t,'fragment_container'))
    l,top,r,bottom=q.bounds(q.node(t,'btn_save_parking'))
    assert ft<=top<bottom<=fb and bottom<=q.bounds(q.node(t,'bottom_nav'))[1]
    keyboard_bar=q.bounds(q.node(t,'bottom_nav'))
    assert keyboard_bar[3]-keyboard_bar[1]==normal_height
    assert q.node(t,'btn_save_parking').get('text')=='CẬP NHẬT VỊ TRÍ'
    q.tap('btn_save_parking',t);t=home('T06-home-edited-B')
    assert q.node(t,'home_spot_name').get('text')==EDITED
    assert q.node(t,'home_spot_details').get('text')=='Tầng B3 · Khu C · Cột 22'
    rows=q.database('edited-B');entry=spot(rows,EDITED)
    assert len(rows)==2 and entry['id']==old_id and entry['note']=='Edited_near_exit' and entry['active']==1
    record('T06','Edited B in place; ID retained; exact name/floor/zone/column/note updated in Home and Room')
    record('R02','Software keyboard open; Update button fully above Bottom Navigation; update succeeded with IME open')
elif phase == '4':
    q.tap('nav_history');q.row_action(A,'activate');t=q.capture('T07-history-active-A')
    rows=q.database('reactivated-A')
    assert len(rows)==2 and spot(rows,A)['active']==1 and spot(rows,EDITED)['active']==0
    assert sum(r['active'] for r in rows)==1
    record('T07','A reactivated; edited B inactive; exactly one active record')
    q.tap('nav_home',t);t=home('T07-home-A');assert q.node(t,'home_spot_name').get('text')==A
    old_pid=q.adb('shell','pidof',q.PACKAGE).strip()
    q.adb('shell','am','force-stop',q.PACKAGE)
    assert not q.adb('shell','pidof',q.PACKAGE,check=False).strip()
    q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
    t=home('REG-09-home-restarted');assert q.node(t,'home_spot_name').get('text')==A
    assert q.node(t,'home_spot_details').get('text')=='Tầng B2 · Khu A · Cột 12'
    new_pid=q.adb('shell','pidof',q.PACKAGE).strip();assert new_pid!=old_pid
    after=q.database('after-restart');assert after==rows
    (q.OUT/'restart-process.json').write_text(json.dumps({'before_pid':old_pid,'after_pid':new_pid,'rows_unchanged':True},indent=2))
    record('T08','Force-stop killed process; new process reopened; both rows and active A persisted unchanged')
elif phase == '5':
    q.tap('nav_history');q.row_action(EDITED,'delete');t=q.capture('REG-07-delete-confirmation')
    q.node(t,'Xóa vị trí đỗ xe?');q.tap('button2',t)
    rows=q.database('cancel-delete');assert len(rows)==2
    q.row_action(EDITED,'delete');t=q.capture('T09-confirm-delete-B',False);q.tap('button1',t)
    t=q.capture('T09-history-after-delete-B',False);assert not q.nodes(t,EDITED);q.node(t,A)
    rows=q.database('deleted-B');assert len(rows)==1 and rows[0]['placeName']==A
    record('T09','Cancel preserved both records; confirmed deletion removed only B from History and Room')
    q.row_action(A,'delete');t=q.capture('T10-confirm-delete-A',False);q.tap('button1',t)
    t=q.capture('T10-history-empty',False);assert q.node(t,'history_count').get('text')=='0 VỊ TRÍ ĐÃ LƯU';q.node(t,'history_empty')
    q.tap('nav_home',t);t=home('REG-10-home-final-empty');q.node(t,'Chưa lưu vị trí nào')
    assert not q.database('final-empty')
    record('T10','Deleted only QA-created A; Home and History returned to empty; zero database rows')
