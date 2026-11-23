# ParkPin G2 — Room + local CRUD integration (QA pending)

Base: G1 merge commit `315aaf17681af2c3edca216c91b6e5a0b72c2f80`.
PR: https://github.com/Hunny-17/ParkPin/pull/2 (Draft)

## Implemented source (code review and runtime QA separate)
- Room 2.8.5 entity + DAO + database + async repository, persisted locally offline.
- One active parking entry at a time (Room transaction); older entries appear in History.
- Save Parking: manual inputs, required place name, save/update feedback, edit existing record.
- Home: displays active record or real empty state. Static map remains labeled illustrative.
- History: Room-backed records, edit, activate an older record, delete with confirmation, empty state.
- No seeded demo records, no login/Firebase, GPS, embedded Maps or camera.
- Android instrumentation DAO test source: active switching, CRUD, ordering, empty DB, persistence after close/reopen.
- Existing G1 navigation / keyboard insets retained.

## Pending verification (do not mark G2 PASS)
- Confirm PR #2 CI `assemble-debug` on final HEAD. CI build alone does not run instrumented tests.
- Android Studio / ADB: install APK on existing `Medium_Phone` emulator with API 37; run tests via:
  `gradlew.bat :app:connectedDebugAndroidTest`
- Manual UI QA on installed APK: empty state; invalid name blocked; create A and B; one active;
  history contains A and B; edit B; activate A; delete B; restart app retains A;
  delete A shows empty state; Back/rotation/keyboard regression. Save actual screenshots and logs.
- Verify Android test APK compiles; review any SDK/API warnings, error states and G1 regression.
- Update test table and screenshot evidence; keep Draft until CI + emulator + visual QA PASS.

## Acceptance policy
No `allowMainThreadQueries` in production; tests may use it with an in-memory/test DB.
No destructive migration; schema changes require explicit migration in a later release.
No untested PASS claims; no merge without QA.
