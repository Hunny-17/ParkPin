"""UI-only regression on the explicitly selected disposable release QA AVD."""
import importlib.util
import json
import sys
import time
from pathlib import Path
import adb_qa as q

spec=importlib.util.spec_from_file_location('picker',q.ROOT/'scripts/api24_photo_e2e.py')
picker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(picker)
picker.adb=lambda *a,**kw:q.adb(*a,**{k:v for k,v in kw.items() if k!='timeout'})
picker.OUT=q.OUT/'regression-picker'
picker.OUT.mkdir(exist_ok=True)
A='QA_API24_REG_A'
B='QA_API24_REG_B'
EDIT='QA_API24_REG_B_EDIT'
checks={}

def check(name, condition):
    assert condition,name
    checks[name]='PASS'
    (q.OUT/'regression-result.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print('PASS',name,flush=True)

def top():
    q.hide_keyboard()
    q.scroll(False,4)

def save(double=False):
    q.hide_keyboard()
    r=q.ensure('btn_save_parking')
    if double:
        l,t,r_,b=q.bounds(q.node(r,'btn_save_parking'))
        x,y=(l+r_)//2,(t+b)//2
        q.adb('shell',f'input tap {x} {y}; input tap {x} {y}')
    else:q.tap('btn_save_parking',r)
    time.sleep(.8)

def photo():
    fixture=q.ROOT/'.qa-tools/release-qa'/picker.MEDIA
    picker.make_png(fixture)
    q.adb('push',str(fixture),'/sdcard/Download/'+picker.MEDIA)
    q.adb('shell','am','broadcast','-a','android.intent.action.MEDIA_SCANNER_SCAN_FILE','-d','file:///sdcard/Download/'+picker.MEDIA)
    picker.select_document()

def main():
    check('Starts with no QA records',q.database('reg-start')==[])
    q.tap('nav_history');q.capture('reg-history-empty')
    q.tap('nav_home');q.capture('reg-home-empty')
    q.tap('nav_save');q.selected(q.dump(),'save')
    q.tap('btn_save_parking',q.ensure('btn_save_parking'));time.sleep(.4)
    top();q.capture('reg-name-required')
    check('Blank name blocked',q.database('reg-invalid')==[])
    q.text_field('input_place_name',A)
    q.hide_keyboard()
    q.adb('shell','settings','put','secure','show_ime_with_hard_keyboard','1')
    q.tap('input_note',q.ensure('input_note'))
    q.adb('shell','input','text','Keyboard_QA')
    q.ensure('btn_save_parking')
    q.capture('reg-keyboard-save')
    check('Save reachable with IME shown','mInputShown=true' in q.adb('shell','dumpsys','input_method'))
    q.tap('btn_save_parking');time.sleep(.8)
    q.hide_keyboard()
    a=q.database('reg-a')
    check('Manual save without GPS permission',len(a)==1 and a[0]['placeName']==A and a[0]['latitude'] is None)
    q.tap('nav_save');q.text_field('input_place_name',B);q.hide_keyboard()
    photo();q.capture('reg-photo-draft')
    q.adb('shell','settings','put','system','accelerometer_rotation','0')
    q.adb('shell','settings','put','system','user_rotation','1');time.sleep(1)
    q.capture('reg-landscape')
    q.adb('shell','settings','put','system','user_rotation','0');time.sleep(1)
    q.ensure('photo_preview');q.capture('reg-portrait-restored')
    check('Photo draft survives rotation',bool(q.nodes(q.dump(),'photo_preview')))
    save(double=True)
    b=q.database('reg-b')
    check('Rapid save creates one B; B solely active',len(b)==2 and sum(r['active'] for r in b)==1 and next(r for r in b if r['active'])['placeName']==B)
    old=next(r for r in b if r['placeName']==B)['photoPath']
    q.tap('nav_history');q.row_action(B,'edit');photo();top()
    q.text_field('input_place_name',EDIT);save()
    replaced=q.database('reg-replaced')
    new=next(r for r in replaced if r['placeName']==EDIT)['photoPath']
    check('Replace image and edit persist; old file removed',new and new!=old and old not in picker.owned_files())
    q.tap('nav_history');q.row_action(EDIT,'edit')
    q.tap('btn_remove_photo',q.ensure('btn_remove_photo'));q.capture('reg-photo-removed-draft');save()
    removed=q.database('reg-removed')
    check('Remove image persists and cleans file',next(r for r in removed if r['placeName']==EDIT)['photoPath'] is None and new not in picker.owned_files())
    q.tap('nav_history');q.row_action(A,'activate');time.sleep(.5)
    active=q.database('reg-reactivated')
    check('Reactivation is exclusive',sum(r['active'] for r in active)==1 and next(r for r in active if r['active'])['placeName']==A)
    for label in [EDIT,A]:
        q.tap('nav_home');q.tap('nav_history');q.row_action(label,'delete')
        q.tap('button1');time.sleep(.5)
    check('Delete through UI returns empty Room',q.database('reg-end')==[])
    q.tap('nav_save');q.adb('shell','input','keyevent','4');q.selected(q.dump(),'home')
    q.capture('reg-back-home')
    check('Three tabs and Back operational',True)
    q.adb('shell','rm','-f','/sdcard/Download/'+picker.MEDIA)

if __name__=='__main__':
    try:main()
    except Exception:
        q.capture('reg-failure')
        raise
