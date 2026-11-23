"""Device-observed external Intent handoff, fallback and History acceptance."""
import json
import sys
import time
import g3_support as s
q=s.q
MAPS='com.google.android.apps.maps'
FIXTURE='com.tranquochuy.parkpin.qa.geo'
def activity(label,uri,package):
    raw=q.adb('shell','dumpsys','activity','activities')
    events=q.adb('logcat','-d','-v','brief','-s','ActivityTaskManager:I')
    lines=[l.strip() for l in raw.splitlines() if ('topResumedActivity' in l or 'Intent {' in l and ('google.navigation:' in l or 'geo:' in l))]
    lines += [l.strip() for l in events.splitlines() if uri in l and ('START ' in l or 'Intent' in l)][-5:]
    (q.OUT/f'{label}-activity.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    assert any('topResumedActivity' in l and package in l for l in lines),lines
    assert any(uri in l for l in lines),'Actual Android Intent missing expected destination '+uri
    return lines
rows=q.database('maps-source-'+sys.argv[1]);a=next(r for r in rows if r['placeName']=='QA-G3-A')
destination=f"{a['latitude']:.7f},{a['longitude']:.7f}"
nav='google.navigation:q='+destination
geo='geo:0,0?q='+destination
phase=sys.argv[1]
if phase=='1':
    q.adb('shell','am','force-stop',MAPS)  # New task keeps full initial Intent in dumpsys; logcat redacts URI query on API 37.
    q.adb('shell','am','start','-n',q.PACKAGE+'/.MainActivity')
    q.tap('nav_home');q.scroll();q.tap('card_find_car');time.sleep(3)
    t=q.dump()
    if q.nodes(t,'Welcome to Google Maps navigation'):
        q.capture('maps-first-navigation-welcome');q.tap('OK',t);time.sleep(2)
    t=q.dump()
    if q.nodes(t,'How navigation data makes Maps better'):
        q.capture('maps-first-navigation-data-info');q.tap('Dismiss',t);time.sleep(3)
    q.capture('G3-08-maps-navigation')
    activity('maps-home-navigation',nav,MAPS)
    s.record('maps-tests.json','M03','Home Find Car opened installed real Google Maps activity',['G3-08-maps-navigation.xml','maps-home-navigation-activity.txt'])
    s.record('maps-tests.json','M04','Actual Android Intent destination '+destination+' equals Room A coordinates formatted to 7 decimals',['database-maps-source-1.json','maps-home-navigation-activity.txt'])
    t=s.close_maps();q.capture('maps-back-to-parkpin',False);q.selected(t,'home')
    s.record('maps-tests.json','M05','Android Back from real Maps returned to ParkPin Home normally',['maps-back-to-parkpin.xml'])
elif phase=='2':
    q.adb('shell','pm','disable-user','--user','0',MAPS)
    try:
        q.adb('install','-r',str(q.ROOT/'.qa-tools/g3-geo-handler/geo-handler-qa.apk'))
        handlers=q.adb('shell','cmd','package','query-activities','--brief','-a','android.intent.action.VIEW','-d',geo)
        (q.OUT/'maps-fallback-handlers.txt').write_text(handlers,encoding='utf-8')
        assert FIXTURE in handlers and MAPS not in handlers
        q.tap('nav_home');q.scroll();q.tap('card_find_car')
        t=q.capture('maps-generic-fallback');assert any(geo in n.get('text','') for n in t.iter('node'))
        activity('maps-generic-fallback',geo,FIXTURE)
        s.record('maps-tests.json','M06','Maps disabled only on isolated QA AVD; generic geo Intent reached separate QA-only receiver with exact Room destination. Fixture validates OS delivery, not third-party rendering.',['maps-generic-fallback.xml','maps-generic-fallback-activity.txt','maps-fallback-handlers.txt'])
        s.close_maps()
        q.adb('shell','pm','disable-user','--user','0',FIXTURE)
        handlers=q.adb('shell','cmd','package','query-activities','--brief','-a','android.intent.action.VIEW','-d',geo)
        (q.OUT/'maps-no-handlers.txt').write_text(handlers,encoding='utf-8')
        assert FIXTURE not in handlers and MAPS not in handlers
        q.tap('nav_home');q.scroll();s.toast('card_find_car','maps-no-handler-toast')
        assert q.database('maps-no-handler-unchanged')==rows
        s.record('maps-tests.json','M07','No geo or Maps handler: friendly toast captured, ParkPin foreground, Room unchanged',['maps-no-handler-toast.png','maps-no-handler-toast-foreground.txt','maps-no-handlers.txt'])
    finally:
        q.adb('shell','pm','default-state','--user','0',MAPS)
        q.adb('uninstall',FIXTURE,check=False)
elif phase=='3':
    q.tap('nav_history');q.row_action('QA-G3-B','activate');t=q.capture('G3-07-history-with-gps')
    after=q.database('gps-B-reactivated')
    assert len(after)==2 and sum(r['active'] for r in after)==1
    assert next(r for r in after if r['placeName']=='QA-G3-B')['active']==1
    assert next(r for r in after if r['placeName']=='QA-G3-A')['active']==0
    s.record('gps-tests.json','P06','Reactivated manual B from GPS A; exactly one active row, both retained',['database-gps-B-reactivated.json'])
    b=q.row(t,'QA-G3-B');assert not q.nodes(b,'item_map')
    s.record('maps-tests.json','M09','History manual B has no directions action; GPS A has directions',['G3-07-history-with-gps.xml'])
    q.adb('shell','am','force-stop',MAPS)
    q.row_action('QA-G3-A','map');time.sleep(2);q.capture('maps-history-navigation')
    activity('maps-history-navigation',nav,MAPS);s.close_maps()
    s.record('maps-tests.json','M08','Inactive GPS A History directions opened actual Maps with A Room destination',['maps-history-navigation.xml','maps-history-navigation-activity.txt'])
    q.row_action('QA-G3-A','delete');q.capture('gps-delete-dialog');q.tap('button1')
    t=q.capture('gps-deleted-history',False);assert not q.nodes(t,'QA-G3-A')
    after=q.database('gps-A-deleted');assert len(after)==1 and after[0]['placeName']=='QA-G3-B'
    s.record('gps-tests.json','P07','Confirmed UI deletion removed GPS A only; manual B retained',['gps-delete-dialog.xml','database-gps-A-deleted.json'])
    q.row_action('QA-G3-B','delete');q.tap('button1');q.tap('nav_home');q.scroll()
    s.toast('card_find_car','maps-empty-toast');assert not q.database('gps-final-empty')
    s.record('maps-tests.json','M01','Empty Home Find Car showed friendly toast and stayed in ParkPin; zero rows',['maps-empty-toast.png','maps-empty-toast-foreground.txt','database-gps-final-empty.json'])
