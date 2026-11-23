# G3 QA observations — 23/11/2026

No production-code defect has been identified by the acceptance flows so far.

1. Initial Approximate request returned no fix. Device provider dumps showed
   network disabled and no cached GPS/fused fix. A real Google Maps first-run
   permission/Location Accuracy flow enabled the QA AVD's location services.
   Retest with ParkPin coarse granted/fine denied returned an actual coarse fix
   (approximately 2 km accuracy). The original no-fix screenshot/XML and failed
   runner assertion are retained; this was an emulator prerequisite, not replaced
   by hardcoded ParkPin coordinates.
2. Android displayed its own "No location access" warning after turning off
   location. The runner was corrected to dismiss that system warning before
   looking for ParkPin controls. T06 then completed with the friendly no-fix
   message; manual-only B and GPS A were unchanged.
3. API 37 logcat redacts the query from URI strings. Maps also reuses its previous
   activity via `onNewIntent`. Creating a fresh Maps task before tapping ParkPin
   allows `dumpsys activity activities` to expose the actual initial Intent with
   the full destination. No application code was changed to obtain this evidence.
4. Both Maps and ParkPin have a control named `bottom_nav`. The runner initially
   mistook Maps for ParkPin. Back verification was corrected to require ParkPin's
   `nav_home` and `nav_save`; actual Back then returned to Home successfully.
5. The AVD could reach 8.8.8.8 but could not resolve www.google.com. Restarting
   only its workspace copy with `-dns-server 8.8.8.8` fixed name resolution and
   Maps tiles loaded. User data was retained. Maps displayed the correct Hanoi
   destination and map, but its external driving-route service reported that it
   could not find a route. Acceptance verifies the Maps Intent and destination;
   it does not claim successful turn-by-turn travel or a calculated driving route.

Earlier failed runner attempts remain in the raw execution logs. Final case JSON
records contain the assertions from their successful real-device retests.
