"""Verify final dependency/build with actual picker/save/restart/delete."""
import json,time
import qa_support as s
q=s.q
q.adb('shell','mkdir','-p','/sdcard/Pictures/ParkPinG4QA')
q.adb('push',str(q.OUT/'fixtures/g4-B.png'),'/sdcard/Pictures/ParkPinG4QA/g4-B.png')
q.adb('shell','am','broadcast','-a','android.intent.action.MEDIA_SCANNER_SCAN_FILE','-d','file:///sdcard/Pictures/ParkPinG4QA/g4-B.png')
q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity');time.sleep(1)
assert not q.database('final-smoke-before')
q.tap('nav_save');q.fill('QA-G4-FINAL-SMOKE','B2','S','17','Final_EXIF_build');q.hide_keyboard();q.scroll(times=2)
q.tap('btn_pick_photo');t=q.dump()
photos=[n for n in t.iter('node') if n.get('content-desc','').startswith('Photo taken on')]
assert len(photos)==1; q.tap_node(photos[0]);t=q.dump()
if q.nodes(t,'Done'):q.tap('Done',t)
time.sleep(.5);q.scroll(times=2);q.capture('final-smoke-preview');q.tap('btn_save_parking')
q.capture('final-smoke-home',False);rows=q.database('final-smoke-saved');assert len(rows)==1 and rows[0]['photoPath']
q.adb('shell','am','force-stop',q.PACKAGE);q.adb('shell','am','start','-W','-n',q.PACKAGE+'/.MainActivity');q.scroll()
t=q.capture('final-smoke-restarted');q.node(t,'home_photo');assert q.database('final-smoke-restarted')==rows
q.tap('nav_history');q.row_action('QA-G4-FINAL-SMOKE','delete');q.tap('button1');q.tap('nav_home')
assert not q.database('final-smoke-empty')
assert not q.adb('shell','run-as',q.PACKAGE,'ls','files/parking_photos').strip()
(q.OUT/'final-smoke-results.json').write_text(json.dumps({'status':'PASS','actual_system_picker':True,'save_restart_delete':True,'owned_files_cleaned':True,'stage':'Final AndroidX EXIF build'},indent=2))
print('Final system picker/save/restart/delete PASS',flush=True)
