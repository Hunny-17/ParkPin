import json
import math
import time
import adb_qa as q

def record(file,key,detail,evidence=None,status='PASS'):
    path=q.OUT/file
    result=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    result[key]={'status':status,'detail':detail,'evidence':evidence or []}
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{key} {status}: {detail}',flush=True)

def permissions(label):
    raw=q.adb('shell','dumpsys','package',q.PACKAGE)
    lines=[l.strip() for l in raw.splitlines() if 'android.permission.ACCESS_' in l and 'LOCATION: granted=' in l]
    (q.OUT/f'permissions-{label}.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return {kind:any(f'ACCESS_{kind}_LOCATION: granted=true' in l for l in lines) for kind in ['COARSE','FINE']}

def inject(label,lat,lon,repeats=4):
    path=q.OUT/'provider-injections.json';events=json.loads(path.read_text()) if path.exists() else []
    for _ in range(repeats):
        response=q.adb('emu','geo','fix',str(lon),str(lat))
        assert 'OK' in response
        events.append({'label':label,'latitude':lat,'longitude':lon,'host_epoch_ms':int(time.time()*1000),'source':'Android Emulator geo fix command','response':response.strip()})
        time.sleep(.4)
    path.write_text(json.dumps(events,indent=2),encoding='utf-8')

def wait_gps(name,timeout=23):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        t=q.dump();text=q.node(t,'gps_status').get('text','')
        if not text.startswith('Đang lấy vị trí'):
            t=q.capture(name);return q.node(t,'gps_status').get('text','')
        time.sleep(.5)
    q.capture(name)
    raise AssertionError('Location request did not settle')

def provider_trace(label):
    raw=q.adb('shell','dumpsys','location')
    # Only controlled QA fixes and ParkPin requests are exported.
    selected=[l for l in raw.splitlines() if 'Location[' in l or q.PACKAGE in l or 'last location=' in l]
    (q.OUT/f'provider-{label}.txt').write_text('\n'.join(selected)+'\n',encoding='utf-8')

def toast(target,name):
    t=q.dump();q.tap(target,t)
    (q.OUT/'screenshots'/f'{name}.png').write_bytes(q.adb('exec-out','screencap','-p',binary=True))
    raw=q.adb('shell','dumpsys','activity','activities')
    focus='\n'.join(l for l in raw.splitlines() if 'topResumedActivity' in l)
    (q.OUT/f'{name}-foreground.txt').write_text(focus+'\n',encoding='utf-8')
    assert q.PACKAGE+'/.MainActivity' in focus

def close_maps():
    for _ in range(7):
        t=q.dump()
        if q.nodes(t,'nav_home') and q.nodes(t,'nav_save'):return t
        q.adb('shell','input','keyevent','4');time.sleep(.6)
    raise AssertionError('Back did not return from external map to ParkPin')
