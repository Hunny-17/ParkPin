# ParkPin G3 — GPS + Google Maps Intent (QA pending)

**Base:** merged G2 on main at `87bafe7293afa455cde3fe2ed686f54bf79102ea`.
**Feature:** `feat/g3-gps-maps-intent`; PR #3 Draft.
**Scope:** Java + XML, no authentication, backend, embedded map, API key or camera.

## Source delivered — not yet accepted
- Optional `ACCESS_COARSE_LOCATION` and `ACCESS_FINE_LOCATION` permissions, requested ONLY on “LẤY GPS”.
- Fused Location Provider from Google Play services location 21.4.0, current one-shot fix; timeout/null/denial does not prevent manual parking.
- Approximate/precise location display; recorded latitude/longitude, optional accuracy and capture time.
- Room schema v1→v2 migration adds four nullable columns without deleting original records or dropping the active index.
- New records may save captured GPS; edits preserve existing GPS unless a new fix is explicitly requested.
- Home “Tìm xe” and GPS-equipped History rows use external Google Maps navigation Intent; generic `geo:` fallback; missing map app handled without crashes.
- Static homepage illustration remains clearly labeled illustrative; no embedded or simulated live map.
- Existing G2 CRUD/History/Delete/Back/IME flows preserved in implementation.
- JVM GPS/URI tests and Android DAO GPS/migration test cases added to test source.

## Required G3 acceptance (not run here)
| ID | Case | Expected |
|---|---|---|
| G3-T01 | Fresh install or upgrade, no GPS action | No location permission prompt; manual save works |
| G3-T02 | Deny both location permissions | Manual CRUD works; user-friendly status |
| G3-T03 | Approximate-only permission | Coarse fix supported, accuracy honestly labeled |
| G3-T04 | Precise permission and fresh emulator fix | Lat/lng saved to the same parking entry |
| G3-T05 | GPS disabled, unavailable or null | No crash or false coordinates; manual save remains available |
| G3-T06 | GPS captured → save → force-stop/restart | Same lat/lng persisted in Room |
| G3-T07 | Edit G2 spot without GPS capture | Manual update does not overwrite coordinates |
| G3-T08 | Explicit GPS recapture during edit | Existing row ID retained and GPS updated |
| G3-T09 | Migrate real v1 database with existing rows | Original rows/active/history preserved; new columns null |
| G3-T10 | Find Car with valid GPS | External Maps receives saved exact destination |
| G3-T11 | Find Car with missing GPS | Helpful message; no invented location |
| G3-T12 | Maps unavailable | Fallback `geo:` handler or graceful user-visible error |
| G3-R01 | G2 CRUD regression | 10/10 G2 cases still pass |
| G3-R02 | G1 navigation/rotation/keyboard | No regression |
| G3-R03 | Security/privacy | Location permission requested on action only; never auto-uploads |

## Technical gates
- CI on final G3 HEAD: debug build, androidTest APK build and JVM tests.
- On Medium_Phone API 37: `gradlew.bat :app:connectedDebugAndroidTest` (7 DAO tests expected).
- Confirm v1→v2 migration on a copy/test DB; never wipe existing user data to make migration pass.
- ADB/UI Automator screenshots for Save GPS (before/after), Home GPS/no-GPS,
  History, permission dialogs, coarse/fine, Maps handoff and failures.
- Capture exact GPS values from emulator and compare Room, intent destination and UI.
- Zero app crashes. List any limitations and unresolved defects.
- Only after real-device QA and CI SUCCESS can PR #3 be Ready for Review.

## Warnings
- Outdoor GPS alone is insufficient for indoor basements; retain floor, zone, column and notes.
- On some emulator/device configurations location may be absent despite permission.
- Do not claim Maps verified by reading a URI string only; inspect actual external activity
  handoff with emulator tools and verify the destination.
- `allowMainThreadQueries` remains test-only; no destructive migrations.
- **G3 status: CODE ADDED · NOT YET QA ACCEPTED · DRAFT · DO NOT MERGE.**
