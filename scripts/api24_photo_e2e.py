#!/usr/bin/env python3
"""API24 release smoke: system document selection -> own JPEG -> Room -> restart."""
import json, re, sqlite3, struct, subprocess, sys, tempfile, time
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

PKG="com.tranquochuy.parkpin"
LABEL="QA_API24_RELEASE"
MEDIA="parkpin-api24-release.png"
OUT=Path("api24-e2e-evidence")
OUT.mkdir(exist_ok=True)

def adb(*args, check=True, binary=False, timeout=40):
    cmd=["adb",*args]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(f"{' '.join(cmd)} -> {p.returncode}\n{p.stderr.decode(errors='replace')}\n{p.stdout.decode(errors='replace')}")
    return p.stdout if binary else p.stdout.decode(errors="replace").strip()

def snap(name):
    (OUT/f"{name}.png").write_bytes(adb("exec-out","screencap","-p",binary=True))

def ui():
    adb("shell","uiautomator","dump","/sdcard/api24-window.xml",timeout=30)
    return ET.fromstring(adb("exec-out","cat","/sdcard/api24-window.xml"))

def center(node):
    n=[int(v) for v in re.findall(r"\d+",node.get("bounds",""))]
    if len(n)!=4: raise RuntimeError("Bad bounds: "+str(node.attrib))
    return (n[0]+n[2])//2,(n[1]+n[3])//2

def find(tokens, *, timeout=15, scroll=False):
    if isinstance(tokens,str): tokens=[tokens]
    start=time.monotonic()
    scans=0
    while time.monotonic()-start<timeout:
        root=ui()
        nodes=list(root.iter("node"))
        # API24 system image can show an unrelated Messenger crash dialog.
        # Clear only that specific popup, never ignore a ParkPin crash.
        if any("Messenger has stopped" in (n.get("text") or "") for n in nodes):
            close=next((n for n in nodes if "Close app" in (n.get("text") or "")),None)
            if close:
                x,y=center(close)
                adb("shell","input","tap",str(x),str(y))
                time.sleep(.5)
                continue
        for word in tokens:
            for node in nodes:
                hay=" ".join(node.get(k,"") for k in ("text","content-desc","resource-id"))
                if word.lower() in hay.lower():
                    return node
        if scroll and scans%2==0: adb("shell","input","swipe","165","510","165","235","350")
        time.sleep(.6)
        scans+=1
    snap("failed-lookup")
    (OUT/"failed-window.xml").write_text(ET.tostring(ui(),encoding="unicode"))
    raise AssertionError(f"UI element missing {tokens}")

def click(target, **kw):
    node=find(target,**kw)
    x,y=center(node)
    adb("shell","input","tap",str(x),str(y))
    time.sleep(.6)

def make_png(dst):
    w,h=120,72
    pixels=bytearray()
    for y in range(h):
        pixels.append(0)
        for x in range(w):
            pixels.extend((8,128,105) if x<w//2 else (25,47,69))
    def chunk(t,b):
        return struct.pack(">I",len(b))+t+b+struct.pack(">I",zlib.crc32(t+b)&0xffffffff)
    dst.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">2I5B",w,h,8,2,0,0,0))
                    +chunk(b"IDAT",zlib.compress(bytes(pixels)))+chunk(b"IEND",b""))

def owned_files():
    result=adb("shell","run-as",PKG,"ls","files/parking_photos",check=False)
    return [s for s in result.splitlines() if s.endswith(".jpg")]

def get_db_copy():
    folder=OUT/"room-copy"
    folder.mkdir(exist_ok=True)
    for suffix in ("","-wal","-shm"):
        name="parkpin.db"+suffix
        data=adb("exec-out","run-as",PKG,"cat","databases/"+name,check=False,binary=True)
        if data and not data.startswith(b"cat:"): (folder/name).write_bytes(data)
    db=folder/"parkpin.db"
    assert db.is_file(),"Room DB missing"
    c=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
    try: return c.execute("SELECT id,placeName,photoPath,active FROM parking_spots WHERE placeName=?",(LABEL,)).fetchall()
    finally: c.close()

def main():
    api=adb("shell","getprop","ro.build.version.sdk").strip()
    assert api=="24",f"Wrong SDK: {api}"
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/MEDIA
        make_png(path)
        adb("push",str(path),"/sdcard/Download/"+MEDIA)
    adb("shell","am","broadcast","-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE",
        "-d","file:///sdcard/Download/"+MEDIA,check=False)
    time.sleep(1)
    adb("shell","am","force-stop",PKG)
    adb("shell","am","start","-W","-n",PKG+"/.MainActivity")
    click("Lưu xe",timeout=25)
    click("btn_pick_photo",timeout=20,scroll=True)
    find(["Recent","Downloads","Documents"],timeout=25)
    snap("01-document-picker")
    try:
        click(MEDIA,timeout=5)
    except AssertionError:
        click(["Show roots","Navigate up","Open navigation drawer"],timeout=12)
        click("Downloads",timeout=12)
        click(MEDIA,timeout=20)
    find("btn_remove_photo",timeout=40,scroll=True)
    snap("02-picked-image-preview")
    click("input_place_name",timeout=12,scroll=True)
    adb("shell","input","text",LABEL)
    click("btn_save_parking",timeout=16,scroll=True)
    find(LABEL,timeout=25)
    snap("03-home-after-save")
    rows=get_db_copy()
    assert len(rows)==1,f"Room expected 1 row; found {rows!r}"
    id_,name,photo,active=rows[0]
    assert re.fullmatch(r"[0-9a-f-]{36}\.jpg",photo or ""),f"Unexpected photo: {photo!r}"
    assert photo in owned_files(),f"Owned JPEG missing: {photo}"
    adb("shell","am","force-stop",PKG)
    adb("shell","am","start","-W","-n",PKG+"/.MainActivity")
    find(LABEL,timeout=25)
    snap("04-home-after-restart")
    after=get_db_copy()
    assert after==rows,f"Room persistence failed: {rows!r} -> {after!r}"
    assert photo in owned_files(),"Private JPEG lost after restart"
    (OUT/"result.json").write_text(json.dumps({
        "api":24,"status":"PASS","recordId":id_,"photoPath":photo,
        "records":after,"privateJpeg":True,"screenshots":4},ensure_ascii=False,indent=2))
    print("API24 PHOTO E2E PASS",after,flush=True)
    adb("shell","rm","-f","/sdcard/Download/"+MEDIA,check=False)

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("API24 PHOTO E2E FAIL:",repr(e),file=sys.stderr,flush=True)
        try: snap("failure")
        except Exception: pass
        raise
