#!/usr/bin/env python3
"""API24 release smoke: system document selection -> own JPEG -> Room -> restart."""
import io, json, os, re, sqlite3, struct, subprocess, sys, tarfile, tempfile, time
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

PKG="com.tranquochuy.parkpin"
LABEL="QA_API24_RELEASE"
MEDIA="parkpin-api24-release.png"
OUT=Path(os.environ.get("PARKPIN_QA_OUT", "api24-e2e-evidence"))
OUT.mkdir(parents=True, exist_ok=True)

def adb(*args, check=True, binary=False, timeout=40):
    cmd=[os.environ.get("ADB", "adb")]
    if os.environ.get("ANDROID_SERIAL"):
        cmd += ["-s", os.environ["ANDROID_SERIAL"]]
    cmd += list(args)
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(f"{' '.join(cmd)} -> {p.returncode}\n{p.stderr.decode(errors='replace')}\n{p.stdout.decode(errors='replace')}")
    return p.stdout if binary else p.stdout.decode(errors="replace").strip()

def snap(name):
    (OUT/f"{name}.png").write_bytes(adb("exec-out","screencap","-p",binary=True))
    (OUT/f"{name}.xml").write_text(ET.tostring(ui(),encoding="unicode"),encoding="utf-8")
    print("Captured",name,flush=True)

def ui():
    # Retry only this read-only observation: Nougat's UiAutomation connection
    # can time out after many dumps. Never repeat a save/delete/selection action.
    for attempt in range(2):
        try:
            # A failed dump must not silently reuse a previous hierarchy.
            adb("shell","rm","-f","/sdcard/api24-window.xml")
            adb("shell","uiautomator","dump","/sdcard/api24-window.xml",timeout=30)
            return ET.fromstring(adb("exec-out","cat","/sdcard/api24-window.xml"))
        except (subprocess.TimeoutExpired,RuntimeError,ET.ParseError):
            if attempt: raise
            print("Retrying read-only UI hierarchy capture",flush=True)
            time.sleep(.5)

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
        assert not any("ParkPin has stopped" in (n.get("text") or "") for n in nodes), "ParkPin crash dialog"
        # API24 system image can show an unrelated Messenger crash dialog.
        # Clear only that specific popup, never ignore a ParkPin crash.
        if any("Messenger has stopped" in (n.get("text") or "") for n in nodes):
            snap("unrelated-messenger-crash")
            close=next((n for n in nodes if "Close app" in (n.get("text") or "")),None)
            if close:
                x,y=center(close)
                adb("shell","input","tap",str(x),str(y))
                time.sleep(.5)
                continue
        for word in tokens:
            for node in nodes:
                if (word == node.get("text") or word == node.get("content-desc")
                        or node.get("resource-id", "").endswith("/" + word)):
                    return node
        if scroll and scans%2==0: scroll_form()
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

def scroll_form(down=False):
    root=ui()
    pane=next(n for n in root.iter("node") if n.get("resource-id", "").endswith("/fragment_container"))
    l,t,r,b=map(int,re.findall(r"\d+",pane.get("bounds")))
    a,z=(t+70,b-70) if down else (b-70,t+70)
    adb("shell","input","swipe",str((l+r)//2),str(a),str((l+r)//2),str(z),"350")

def document_touch(node):
    """Nougat input tap has TOOL_TYPE_UNKNOWN; DocumentsUI requires finger/stylus.

    Use the emulator's hardware touchscreen, never inject an ActivityResult URI.
    Bounds still come from the exact, currently observed UI Automator node.
    """
    x,y=center(node)
    for state in ("1","0"):
        result=adb("emu","event","mouse",str(x),str(y),"0",state)
        assert "OK" in result and "KO:" not in result, result
        time.sleep(.1)
    time.sleep(.6)

def select_document():
    click("btn_pick_photo",timeout=20,scroll=True)
    find("Show roots",timeout=25)
    activities=adb("shell","dumpsys","activity","activities")
    (OUT/"picker-activities.txt").write_text(activities,encoding="utf-8")
    assert "act=android.intent.action.OPEN_DOCUMENT typ=image/*" in activities
    assert re.search(r"resultTo=ActivityRecord\{[^\n]*"+re.escape(PKG)+r"/\.MainActivity", activities)
    snap("01-document-picker")
    click("Show roots")
    click("Downloads")
    time.sleep(1)
    snap("01a-downloads-root")
    # API24 Downloads provider lists DownloadManager entries, not files pushed
    # by adb. Open the same real Download directory through internal storage.
    if not any(n.get("text")==MEDIA for n in ui().iter("node")):
        root=ui()
        if any(n.get("text")=="Open from" for n in root.iter("node")):
            click("Recent")  # Close the automatically opened empty-root drawer.
        click("More options")
        root=ui()
        if any(n.get("text")=="Show internal storage" for n in root.iter("node")):
            click("Show internal storage")
        else:
            adb("shell","input","keyevent","4")
        click("Show roots")
        model=adb("shell","getprop","ro.product.model").strip()
        click([model,"Internal storage"])
        document_touch(find("Download"))
    find(MEDIA)
    snap("01b-download-folder")
    document_touch(find(MEDIA))
    time.sleep(1)
    root=ui()
    if any(n.get("package")=="com.android.documentsui" for n in root.iter("node")):
        # Tapping a selection hotspot can require the explicit OPEN action.
        snap("01c-document-confirmation")
        click(["OPEN","Open"])
    find("btn_remove_photo",timeout=25,scroll=True)
    find("photo_preview",scroll=True)
    snap("02-picked-image-preview")
    activities=adb("shell","dumpsys","activity","activities")
    (OUT/"preview-activities.txt").write_text(activities,encoding="utf-8")
    assert re.search(r"mResumedActivity: ActivityRecord\{[^\n]*"+re.escape(PKG)+r"/\.MainActivity",activities)

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

def get_db_copy(stage):
    # One settled, read-only tar capture includes DB + WAL. A fresh host folder
    # per snapshot prevents stale WAL/SHM from contaminating another snapshot.
    payload=adb("exec-out","run-as",PKG,"tar","-cf","-","databases",binary=True)
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
            for member in archive.getmembers():
                name=Path(member.name).name
                if member.isfile() and name in ("parkpin.db","parkpin.db-wal"):
                    (Path(tmp)/name).write_bytes(archive.extractfile(member).read())
        c=sqlite3.connect(Path(tmp)/"parkpin.db")
        try:
            assert c.execute("PRAGMA quick_check").fetchone()==("ok",)
            rows=c.execute("SELECT id,placeName,photoPath,active FROM parking_spots ORDER BY id").fetchall()
        finally:
            c.close()
    (OUT/f"room-{stage}.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
    return rows

def main():
    serial=adb("get-serialno").strip()
    assert serial.startswith("emulator-"), "This runner is restricted to disposable QA emulators"
    api=adb("shell","getprop","ro.build.version.sdk").strip()
    assert api=="24",f"Wrong SDK: {api}"
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/MEDIA
        make_png(path)
        adb("push",str(path),"/sdcard/Download/"+MEDIA)
    adb("shell","am","broadcast","-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE",
        "-d","file:///sdcard/Download/"+MEDIA,check=False)
    time.sleep(1)
    # Close the standalone DocumentsUI smoke activity from the preceding CI step.
    # The real picker must start from ParkPin and return its result to ParkPin.
    adb("shell","am","force-stop","com.android.documentsui",check=False)
    adb("shell","am","force-stop",PKG)
    adb("shell","am","start","-W","-n",PKG+"/.MainActivity")
    before=get_db_copy("before")
    assert not before, "Nonempty Room database: preserve it; use a fresh dedicated QA emulator"
    click("Lưu xe",timeout=25)
    select_document()
    # Inputs are above Photo Picker. Restore scroll before editing the name.
    for _ in range(4):
        scroll_form(down=True)
    click("input_place_name",timeout=12)
    adb("shell","input","text",LABEL)
    if "mInputShown=true" in adb("shell","dumpsys","input_method"):
        adb("shell","input","keyevent","4")
    click("btn_save_parking",timeout=16,scroll=True)
    find(LABEL,timeout=25,scroll=True)
    find("home_photo",scroll=True)
    snap("03-home-after-save")
    rows=get_db_copy("saved")
    added=[r for r in rows if r[1]==LABEL]
    assert len(added)==1 and len(rows)==len(before)+1,f"Expected exactly one new QA row: {rows!r}"
    id_,name,photo,active=added[0]
    assert re.fullmatch(r"[0-9a-f-]{36}\.jpg",photo or ""),f"Unexpected photo: {photo!r}"
    assert photo in owned_files(),f"Owned JPEG missing: {photo}"
    jpeg=adb("exec-out","run-as",PKG,"cat","files/parking_photos/"+photo,binary=True)
    assert jpeg.startswith(b"\xff\xd8") and jpeg.endswith(b"\xff\xd9"),"Invalid JPEG envelope"
    (OUT/"private-photo.jpg").write_bytes(jpeg)
    adb("shell","am","force-stop",PKG)
    adb("shell","am","start","-W","-n",PKG+"/.MainActivity")
    find(LABEL,timeout=25,scroll=True)
    find("home_photo",scroll=True)
    snap("04-home-after-restart")
    after=get_db_copy("restarted")
    assert after==rows,f"Room persistence failed: {rows!r} -> {after!r}"
    assert photo in owned_files(),"Private JPEG lost after restart"
    assert adb("exec-out","run-as",PKG,"cat","files/parking_photos/"+photo,binary=True)==jpeg
    click("Lịch sử")
    find(LABEL,scroll=True)
    find("item_photo",scroll=True)
    snap("05-history-photo")
    click("item_delete",scroll=True)
    snap("06-delete-confirmation")
    click("button1")
    time.sleep(1)
    deleted=get_db_copy("deleted")
    assert not any(r[0]==id_ for r in deleted) and len(deleted)==len(before)
    assert photo not in owned_files(),"Deleted row left its private JPEG"
    snap("07-after-delete")
    click("Trang chủ")
    snap("08-home-after-delete")
    (OUT/"logcat.txt").write_text(adb("logcat","-d","-v","threadtime"),encoding="utf-8")
    (OUT/"result.json").write_text(json.dumps({
        "api":24,"status":"PASS","recordId":id_,"photoPath":photo,
        "records":after,"privateJpeg":True,"deletedViaUi":True,"fileCleaned":True,
        "intent":"ACTION_OPEN_DOCUMENT image/*; resultTo ParkPin MainActivity",
        "callbackEvidence":"Only real system selection: preview + new private JPEG + Room; no URI injection",
        "screenshots":len(list(OUT.glob("*.png")))},ensure_ascii=False,indent=2))
    print("API24 PHOTO E2E PASS",after,flush=True)
    adb("shell","rm","-f","/sdcard/Download/"+MEDIA,check=False)

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("API24 PHOTO E2E FAIL:",repr(e),file=sys.stderr,flush=True)
        try: snap("failure")
        except Exception: pass
        raise
