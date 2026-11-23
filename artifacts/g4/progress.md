# G4 progress — plan: docs/superpowers/plans/2026-11-23-g4-photo-picker.md

- PR #3 merged: 44aac930382d87bec3f8bd6c08aa83bdc25fc2f2.
- Main CI 45159706681 completed SUCCESS; verified public Actions API exact SHA.
- Dedicated current checkout clean; G4 branch codex/g4-photo-picker.
- Shared interface: storage path -> Room nullable photoPath -> saved draft state
  -> shared photo binding. Retain old reference until DB success; never delete
  another record's referenced file.
- Task 1: in progress. No production code changed before RED tests.
- RED confirmed: 5 tests executed, 5 assertion failures for missing PhotoStorage/photoPath/MIGRATION_2_3; XML retained.

- Tasks 1/2: complete. Final JVM4, instrumentation16, photo UI16, migration APK and CRUD10/regression6 PASS.
- Review P2 History retention fixed RED->GREEN; second review clean. Lint platform EXIF warning fixed with AndroidX1.4.2, final tests rerun16/16.
- Task3 local: complete; original AVD7 hashes/lengths/timestamps unchanged. QA restored/stopped. Aggregate commit/push/PR/final CI remain remote gate.
