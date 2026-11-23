# G4 Photo Picker Implementation Plan

> Execute inline with executing-plans and TDD; review the whole change before PR.

**Goal:** Choose, persist, replace and remove one local parking image.
**Architecture:** Private sampled JPEG files; Room v3 nullable photoPath;
SavedStateHandle draft import state; asynchronous shared image binding.
**Tech Stack:** Java 17/XML, AndroidX Activity/Fragment/Lifecycle, Room 2.8.5.
**Spec:** [G4_DESIGN.md](../../G4_DESIGN.md).

## Constraints and review focus

Keep API 24 minimum and existing UI/navigation/GPS. No broad media permission,
camera, backend or destructive migration. Handle source errors, rotation while
importing, abandoned edits, DB failures and stale async image callbacks safely.

### Task 1 — Persistence and storage
- [x] Add failing on-device tests: Room migration v2→v3/photo field, JPEG import,
  invalid source, path confinement, bounded decoding, preserving GPS/manual edits.
- [x] Run tests on the isolated QA emulator; record RED before implementation.
- [x] Add nullable ParkingSpot.photoPath, MIGRATION_2_3 and photo DAO operations.
- [x] Add PhotoStorage.importPhoto(Context, Uri), file deletion/confinement and
  pruning; integrate repository save/update/delete with photo ownership.
- [x] Verify storage and DAO tests GREEN, existing JVM tests still GREEN.

### Task 2 — Picker and rendering
- [x] Add PhotoDraftViewModel with saved draft path, changed/busy/error state;
  never delete committed images when a form is discarded.
- [x] Wire PickVisualMedia ImageOnly into Save, preview/replace/remove controls;
  old image/GPS persist on manual edit, picker cancel leaves draft unchanged.
- [x] Add shared asynchronous PhotoViews binding to Save/Home/History with stale
  request protection and missing-image feedback, using existing colors/styles.
- [x] Build and run actual picker/rotation/restart/source-deletion/error flows.

### Task 3 — Verification and handoff
- [x] Real G3 APK → G4 upgrade without clearing data; read-only Room comparison.
- [x] Clean build, JVM and connected tests; actual screenshots opened, logcat and
  G1–G3 regression. Independent whole-change review, fix any material findings.
- [ ] Record actual results and limitations; commit/push G4 branch, create PR,
  verify exact final HEAD CI. Do not merge G4 without a separate instruction.
