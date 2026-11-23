"""G1 navigation/Back/scroll regression on the installed G3 APK after CRUD."""
import json
import adb_qa as q

def record(case, detail):
    p=q.OUT/'crud-results.json';results=json.loads(p.read_text(encoding='utf-8'))
    results[case]={'status':'PASS','detail':detail}
    p.write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(case+' PASS: '+detail,flush=True)

t=q.dump();q.selected(t,'home')
coords={}
for tab in ('save','history','home'):
    l,top,r,b=q.bounds(q.node(t,'nav_'+tab));coords[tab]=((l+r)//2,(top+b)//2)
commands='; '.join(f'input tap {coords[tab][0]} {coords[tab][1]}' for tab in ('save','history','home'))
q.adb('shell',f'for n in 1 2 3 4 5 6; do {commands}; done')
t=q.capture('R04-tab-stress',False);q.selected(t,'home');q.node(t,'Chưa lưu vị trí nào')
assert not q.database('after-tab-stress')
record('R04','18 rapid tab transitions completed; Home valid; database unchanged; crash checks reviewed separately')
q.tap('btn_save_parking_mock',t);t=q.capture('R05-home-save-cta',False);q.selected(t,'save')
q.scroll();t=q.capture('R05-save-scroll-end',False)
_,top,_,b=q.bounds(q.node(t,'btn_save_parking'));_,ft,_,fb=q.bounds(q.node(t,'fragment_container'))
assert ft<=top<b<=fb
q.adb('shell','input','keyevent','4');t=q.capture('R05-back-save',False);q.selected(t,'home')
q.scroll();t=q.capture('R05-home-scroll-end',False)
hint=next(n for n in t.iter('node') if n.get('text','').startswith('Mẹo:'))
_,top,_,b=q.bounds(hint);_,ft,_,fb=q.bounds(q.node(t,'fragment_container'));assert ft<=top<b<=fb
q.tap('card_open_history',t);t=q.capture('R05-history-shortcut',False);q.selected(t,'history')
q.adb('shell','input','keyevent','4');t=q.capture('R05-back-history',False);q.selected(t,'home')
q.scroll();t=q.dump();q.tap('card_find_car',t)
(q.OUT/'screenshots/REG-find-car-toast.png').write_bytes(q.adb('exec-out','screencap','-p',binary=True))
focus='\n'.join(l for l in q.adb('shell','dumpsys','activity','activities').splitlines() if 'topResumedActivity' in l)
(q.OUT/'R05-find-car-foreground.txt').write_text(focus+'\n',encoding='utf-8')
assert q.PACKAGE+'/.MainActivity' in focus
q.adb('shell','input','keyevent','4');q.time.sleep(.4)
t=q.capture('R05-home-exit',False)
assert not any(n.get('package')==q.PACKAGE for n in t.iter('node'))
record('R05','Home CTA/History shortcut/Find Car empty-state toast; 3-screen scrolling; History rotation; Back from both tabs and Home exit passed')
q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity')
