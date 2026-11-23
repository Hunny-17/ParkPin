"""Run G1 interactions against a real emulator; inspect captured PNGs separately.

Requires Python 3, adb, installed ParkPin APK and a booted emulator.
ANDROID_HOME / ANDROID_SDK_ROOT and ANDROID_SERIAL can override defaults.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

OUT = pathlib.Path(__file__).resolve().parent
SDK = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
ADB = str(pathlib.Path(SDK) / 'platform-tools' / ('adb.exe' if os.name == 'nt' else 'adb')) if SDK else shutil.which('adb')
SERIAL = os.environ.get('ANDROID_SERIAL', 'emulator-5554')
PACKAGE = 'com.tranquochuy.parkpin'
RESULTS = {}

def adb(*args, binary=False):
    p = subprocess.run([ADB, '-s', SERIAL, *args], capture_output=True, timeout=60)
    if not binary:
        with (OUT / 'emulator.log').open('a', encoding='utf-8') as log:
            log.write(f'\n$ adb {" ".join(args)}\n{p.stdout.decode("utf-8", "replace")}\n{p.stderr.decode("utf-8", "replace")}\nexit={p.returncode}\n')
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8', 'replace'))
    return p.stdout if binary else p.stdout.decode('utf-8', 'replace')

def state(name):
    adb('shell', 'uiautomator', 'dump', '/sdcard/parkpin-g1-ui.xml')
    raw = adb('shell', 'cat', '/sdcard/parkpin-g1-ui.xml')
    (OUT / f'{name}.xml').write_text(raw, encoding='utf-8')
    (OUT / 'screenshots' / f'{name}.png').write_bytes(adb('exec-out', 'screencap', '-p', binary=True))
    return ET.fromstring(raw)

def node(tree, value):
    return next(n for n in tree.iter('node') if any(value in n.get(k, '') for k in ('resource-id', 'text', 'content-desc')))

def bounds(n):
    return list(map(int, re.findall(r'\d+', n.get('bounds'))))

def tap(tree, value):
    left, top, right, bottom = bounds(node(tree, value))
    adb('shell', 'input', 'tap', str((left + right) // 2), str((top + bottom) // 2))
    time.sleep(.5)

def selected(tree, tab):
    assert node(tree, '/nav_' + tab).get('selected') == 'true', f'{tab} is not selected'

def fragment(name, expected):
    raw = adb('shell', 'dumpsys', 'activity', PACKAGE)
    (OUT / f'{name}-fragments.txt').write_text(raw, encoding='utf-8')
    assert f'    {expected}' in raw, f'{expected} is not active'

def swipe(x, y1, y2):
    adb('shell', 'input', 'swipe', str(x), str(y1), str(x), str(y2), '600')
    time.sleep(.4)

def endpoint(tree, text):
    left, top, right, bottom = bounds(node(tree, text))
    fl, ft, fr, fb = bounds(node(tree, '/fragment_container'))
    assert fl <= left < right <= fr and ft <= top < bottom <= fb, f'Endpoint clipped: {text}'
    assert bottom <= bounds(node(tree, '/bottom_nav'))[1], 'Bottom Navigation overlaps content'

def record(case, evidence):
    RESULTS[case] = {'status': 'PASS', 'evidence': evidence}
    (OUT / 'test-results.json').write_text(json.dumps(RESULTS, indent=2), encoding='utf-8')
    print(f'{case} PASS: {evidence}', flush=True)

original = {}
try:
    for namespace, key in [('secure', 'show_ime_with_hard_keyboard'), ('system', 'accelerometer_rotation'), ('system', 'user_rotation')]:
        original[(namespace, key)] = adb('shell', 'settings', 'get', namespace, key).strip()
    adb('shell', 'settings', 'put', 'system', 'accelerometer_rotation', '0')
    adb('shell', 'settings', 'put', 'system', 'user_rotation', '0')
    adb('shell', 'settings', 'put', 'secure', 'show_ime_with_hard_keyboard', '1')
    adb('shell', 'am', 'force-stop', PACKAGE)
    adb('shell', 'am', 'start', '-W', '-n', PACKAGE + '/.MainActivity')
    t = state('G1-01-home'); selected(t, 'home'); node(t, 'ParkPin'); fragment('T01', 'HomeFragment')
    record('T01', 'G1-01-home.xml; T01-fragments.txt')
    for tab, name in [('save', 'G1-02-save'), ('history', 'G1-03-history'), ('home', 'T02-home')]:
        tap(t, '/nav_' + tab); t = state(name); selected(t, tab)
    record('T02', 'G1-02-save.xml; G1-03-history.xml; T02-home.xml')
    tap(t, '/btn_save_parking_mock'); t = state('T03-home-save-cta'); selected(t, 'save'); fragment('T03', 'SaveParkingFragment')
    record('T03', 'T03-home-save-cta.xml; T03-fragments.txt')
    tap(t, '/nav_home'); swipe(540, 1850, 450); t = state('T06-home-bottom')
    endpoint(t, 'Mẹo:')
    tap(t, '/card_open_history'); t = state('T04-history-shortcut'); selected(t, 'history'); fragment('T04', 'HistoryFragment')
    for title in ['3 ĐIỂM ĐỖ MẪU', 'Bãi xe trung tâm', 'Nhà xe khu B', 'Bãi xe siêu thị']: node(t, title)
    record('T04', 'T04-history-shortcut.xml; T04-fragments.txt')
    tap(t, '/nav_home'); swipe(540, 1850, 450); t = state('T05-before')
    left, top, right, bottom = bounds(node(t, '/card_find_car'))
    adb('shell', 'input', 'tap', str((left + right) // 2), str((top + bottom) // 2)); time.sleep(.2)
    (OUT / 'screenshots/T05-find-car-toast.png').write_bytes(adb('exec-out', 'screencap', '-p', binary=True))
    focus = '\n'.join(line for line in adb('shell', 'dumpsys', 'activity', 'activities').splitlines() if 'topResumedActivity' in line)
    (OUT / 'T05-foreground.txt').write_text(focus, encoding='utf-8')
    assert PACKAGE + '/.MainActivity' in focus
    t = state('T05-after'); selected(t, 'home')
    record('T05', 'T05-foreground.txt; T05-find-car-toast.png (visual inspection required)')
    tap(t, '/nav_save'); t = state('T07-save-normal'); swipe(540, 1850, 450); t = state('T06-save-bottom')
    endpoint(t, 'Bản UI: biểu mẫu chưa ghi dữ liệu')
    swipe(540, 450, 1850); t = state('T07-save-top'); tap(t, 'Bãi xe trung tâm')
    adb('shell', 'input', 'text', '%sQA-G1'); t = state('T07-keyboard-input')
    node(t, 'Bãi xe trung tâm QA-G1')
    ime = adb('shell', 'dumpsys', 'input_method'); (OUT/'T07-ime.txt').write_text(ime, encoding='utf-8')
    assert 'mInputShown=true' in ime and 'mIsInputViewShown=true' in ime
    for _ in range(2): swipe(540, 1150, 150)
    t = state('G1-04-keyboard'); endpoint(t, 'Bản UI: biểu mẫu chưa ghi dữ liệu')
    assert bounds(node(t, '/bottom_nav'))[3] - bounds(node(t, '/bottom_nav'))[1] <= 275
    record('T07', 'T07-keyboard-input.xml; T07-ime.txt; G1-04-keyboard.xml')
    adb('shell', 'input', 'keyevent', '4'); time.sleep(.4); t = state('T07-hidden')
    tap(t, '/nav_history'); t = state('G1-03-history')
    adb('shell', 'settings', 'put', 'system', 'user_rotation', '1'); time.sleep(1)
    t = state('G1-05-rotation'); selected(t, 'history'); fragment('T08', 'HistoryFragment')
    assert t.get('rotation') == '1'
    for _ in range(2): swipe(1200, 760, 150)
    t = state('T06-history-landscape-bottom'); endpoint(t, 'Các mục ở đây')
    record('T06', 'T06-home-bottom.xml; T06-save-bottom.xml; T06-history-landscape-bottom.xml')
    adb('shell', 'settings', 'put', 'system', 'user_rotation', '0'); time.sleep(1)
    t = state('T08-history-restored-portrait'); selected(t, 'history')
    record('T08', 'G1-05-rotation.xml; T08-fragments.txt; T08-history-restored-portrait.xml')
    adb('shell', 'input', 'keyevent', '4'); time.sleep(.4); t = state('T09-history-back-home'); selected(t, 'home')
    tap(t, '/nav_save'); t = state('T09-save')
    adb('shell', 'input', 'keyevent', '4'); time.sleep(.4); t = state('T09-save-back-home'); selected(t, 'home')
    adb('shell', 'input', 'keyevent', '4'); time.sleep(.7); t = state('T09-home-exit')
    assert not any(n.get('package') == PACKAGE for n in t.iter('node')), 'App did not exit'
    record('T09', 'T09-history-back-home.xml; T09-save-back-home.xml; T09-home-exit.xml')
    print('9/9 interaction and UI hierarchy checks passed; inspect screenshots before final acceptance.', flush=True)
finally:
    for (namespace, key), value in original.items():
        adb('shell', 'settings', 'delete' if value == 'null' else 'put', namespace, key, *([] if value == 'null' else [value]))
