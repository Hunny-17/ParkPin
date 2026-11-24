"""Release API24 isolated-emulator QA helpers. No application data clearing or SQL mutations.

ANDROID_HOME / ANDROID_SERIAL select the SDK and device. Database evidence is
read from copies of the app's db/WAL while UI is idle; only UI performs CRUD.
"""
import io
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import tarfile
import time
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SDK = os.environ.get('ANDROID_HOME', r'C:\Users\ASUS\AppData\Local\Android\Sdk')
ADB = str(pathlib.Path(SDK) / 'platform-tools' / ('adb.exe' if os.name == 'nt' else 'adb'))
SERIAL = os.environ.get('ANDROID_SERIAL', 'emulator-5558')
PACKAGE = 'com.tranquochuy.parkpin'

def adb(*args, binary=False, check=True):
    p = subprocess.run([ADB, '-s', SERIAL, *args], capture_output=True, timeout=60)
    if not binary:
        output = p.stdout.decode('utf-8', 'replace').replace('\r', '')
        error = p.stderr.decode('utf-8', 'replace').replace('\r', '')
        logged = output
        if args[:2] == ('shell', 'cat') and 'parkpin-release-ui.xml' in args[-1]:
            logged = f'UI hierarchy read ({len(output)} characters); named captures saved separately.\n'
        elif args == ('shell', 'dumpsys', 'input_method'):
            logged = '\n'.join(line for line in output.splitlines()
                               if 'mInputShown=' in line or 'mIsInputViewShown=' in line)
        elif args == ('shell', 'dumpsys', 'activity', 'activities'):
            logged = '\n'.join(line for line in output.splitlines() if 'topResumedActivity' in line)
        elif args[:4] == ('logcat', '-d', '-b', 'crash'):
            logged = f'Crash buffer inspected: {output.count(PACKAGE)} ParkPin references; unrelated system text omitted.'
        with (OUT / 'emulator.log').open('a', encoding='utf-8', newline='\n') as log:
            log.write(f'\n$ adb {" ".join(args)}\n{logged.rstrip()}\n{error.rstrip()}\nexit={p.returncode}\n')
    if check and p.returncode:
        raise RuntimeError((p.stdout + p.stderr).decode('utf-8', 'replace'))
    return p.stdout if binary else output

def dump():
    adb('shell', 'uiautomator', 'dump', '/sdcard/parkpin-release-ui.xml')
    return ET.fromstring(adb('shell', 'cat', '/sdcard/parkpin-release-ui.xml'))

def capture(name, screenshot=True):
    tree = dump()
    ET.indent(tree)
    (OUT / f'{name}.xml').write_text(ET.tostring(tree, encoding='unicode') + '\n', encoding='utf-8')
    if screenshot:
        (OUT / 'screenshots' / f'{name}.png').write_bytes(adb('exec-out', 'screencap', '-p', binary=True))
    texts = [n.get('text') for n in tree.iter('node') if n.get('text')]
    selected = [n.get('resource-id') for n in tree.iter('node') if n.get('selected') == 'true' and '/nav_' in n.get('resource-id', '')]
    print(json.dumps({'screen': name, 'selected': selected, 'texts': texts}, ensure_ascii=False), flush=True)
    return tree

def nodes(tree, value):
    return [n for n in tree.iter('node') if n.get('resource-id', '').endswith('/' + value)
            or n.get('text') == value or n.get('content-desc') == value]

def node(tree, value):
    matches = nodes(tree, value)
    if not matches:
        raise AssertionError(f'Visible UI target absent: {value}')
    return matches[0]

def bounds(n):
    return tuple(map(int, re.findall(r'\d+', n.get('bounds'))))

def tap_node(n):
    l, t, r, b = bounds(n)
    assert r > l and b > t, 'Cannot tap empty bounds'
    adb('shell', 'input', 'tap', str((l+r)//2), str((t+b)//2))
    time.sleep(.35)

def tap(value, tree=None):
    tap_node(node(tree if tree is not None else dump(), value))

def selected(tree, tab):
    assert node(tree, 'nav_' + tab).get('selected') == 'true', f'{tab} not selected'

def scroll(up=True, times=1):
    for _ in range(times):
        tree = dump()
        l, t, r, b = bounds(node(tree, 'fragment_container'))
        x = (l+r)//2
        a, z = (b-80, t+80) if up else (t+80, b-80)
        adb('shell', 'input', 'swipe', str(x), str(a), str(x), str(z), '450')
        time.sleep(.25)

def ensure(value):
    for _ in range(5):
        tree = dump()
        if nodes(tree, value):
            return tree
        scroll()
    raise AssertionError(f'Cannot reveal {value}')

def text_field(field, value):
    tree = ensure(field)
    current = node(tree, field).get('text', '')
    tap(field, tree)
    adb('shell', 'input', 'keyevent', '123')
    if current:
        adb('shell', 'input', 'keyevent', *(['67'] * len(current)))
    adb('shell', 'input', 'text', value.replace(' ', '%s'))


def hide_keyboard():
    ime = adb('shell', 'dumpsys', 'input_method')
    if 'mInputShown=true' in ime:
        adb('shell', 'input', 'keyevent', '4')
        time.sleep(.3)

def fill(name, floor, zone, column, note):
    for key, value in [('input_place_name', name), ('input_floor', floor),
                       ('input_zone', zone), ('input_column', column), ('input_note', note)]:
        text_field(key, value)

def row(tree, name):
    candidates = [n for n in tree.iter('node') if nodes(n, name) and nodes(n, 'item_edit')]
    assert candidates, f'No visible history row: {name}'
    return min(candidates, key=lambda n: len(list(n.iter())))

def row_action(name, action):
    for _ in range(5):
        tree = dump()
        try:
            current = row(tree, name)
            target = node(current, 'item_' + action)
            tap_node(target)
            return
        except AssertionError:
            scroll()
    raise AssertionError(f'Cannot reach {action} for {name}')

def database(label):
    payload = adb('exec-out', 'run-as', PACKAGE, 'tar', '-cf', '-', 'databases', binary=True)
    dest = ROOT / '.qa-tools' / 'release-qa/db-snapshots' / label
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        for member in archive.getmembers():
            name = pathlib.PurePosixPath(member.name).name
            if member.isfile() and name in ('parkpin.db', 'parkpin.db-wal'):
                (dest / name).write_bytes(archive.extractfile(member).read())
    with sqlite3.connect(dest / 'parkpin.db') as db:
        assert db.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
        db.row_factory = sqlite3.Row
        rows = [dict(r) for r in db.execute('SELECT * FROM parking_spots ORDER BY id')]
        version = db.execute('PRAGMA user_version').fetchone()[0]
        columns = [dict(r) for r in db.execute('PRAGMA table_info(parking_spots)')]
    report = {'label': label, 'rows': rows, 'count': len(rows),
              'active_count': sum(r['active'] for r in rows),
              'user_version': version, 'columns': columns,
              'source': 'Read-only app db/WAL capture after UI settled; SQL only reads host copies'}
    (OUT / f'database-{label}.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)
    return rows

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'capture': capture(sys.argv[2])
    elif action == 'tap': tap(sys.argv[2]); capture(sys.argv[3])
    elif action == 'scroll': scroll(sys.argv[2] != 'down', int(sys.argv[3])); capture(sys.argv[4])
    elif action == 'db': database(sys.argv[2])
    elif action == 'shell': print(adb('shell', *sys.argv[2:]))
