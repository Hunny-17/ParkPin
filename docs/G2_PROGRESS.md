# ParkPin G2 — Room + Local CRUD (work in progress)

Base: merged G1 on `main`, merge commit `315aaf17681af2c3edca216c91b6e5a0b72c2f80`.

## Delivered in initial G2 slice
- Java-only Room 2.8.5 entity, DAO, RoomDatabase and asynchronous repository.
- Persistence model: place name, floor, zone, column, note, timestamps, active flag.
- DAO create/current/history/list/read/update/delete and atomic active switching.
- Single-thread background executor; no database access on UI thread.
- No Firebase, login, GPS, Maps, camera, or seeded demo records.

## Still pending (do not claim G2 acceptance)
- Bind Save Parking XML to repository and implement input validation / form feedback.
- Replace hard-coded Home and History with actual saved data and empty states.
- Implement edit/delete UI confirmation and active-item switching UI.
- Room unit/instrumentation tests: create, update, delete, persistence after restart,
  1 active only, empty database, invalid input, ordered history.
- Emulator visual and interaction QA with screenshots (G1 regressions included).

CI build is an initial technical gate, **not** proof of CRUD runtime behavior.
No destructive migrations or allowMainThreadQueries.
