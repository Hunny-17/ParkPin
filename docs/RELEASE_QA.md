# ParkPin — Final Release QA (23/11/2026)

**Status: NOT RELEASED.** This file describes gates, not an authorization to publish.

## Baseline
- G1–G4 merged into `main`; G4 Merge commit: `f622762eac27eca4655cd9421fa6294a91c5997c`.
- User-accepted G4 evidence: [G4_ACCEPTANCE.md](G4_ACCEPTANCE.md), PR #4 and CI on main.
- Production code is unchanged by the release QA checks; tests and workflow only.

## Required gates
| Gate | Current state | Proof |
|---|---|---|
| Main build | PASS on G4 merge; recheck final HEAD | https://github.com/Hunny-17/ParkPin/actions |
| API 37.2 G4: UI/photo/GPS/Maps and migration | PASS (prior local QA; 16/16 + 10/10 + 6/6) | [G4 acceptance](G4_ACCEPTANCE.md) |
| API 24: Room, EXIF, private JPEG, startup | PASS (18/18 instrumented on baseline) | https://github.com/Hunny-17/ParkPin/actions/runs/45207616072 |
| API 24: real DocumentsUI photo selection → preview → Room/owned JPEG → app restart | PENDING dedicated workflow | `.github/workflows/android-api24-compat.yml`, `scripts/api24_photo_e2e.py` |
| API 24 visual QA: no other app's crash dialog / no blocked fields | PENDING review of new screenshots | Workflow artifact `api24-compatibility-evidence` |
| Physical Android device: APK installation, manual CRUD/photo picker/GPS/Maps/keyboard/rotation | BLOCKED — device not connected to GitHub Actions | Local ADB evidence required |
| Release APK package/hash/signing/distribution | NOT STARTED | Create only after release gates complete |

## API 24 end-to-end workflow checks
1. Disposable Google APIs Android 7.0 emulator, exact `ro.build.version.sdk=24`.
2. Full `connectedDebugAndroidTest` suite, must have zero failures/skips.
3. Reinstall debug APK after suite; verify MainActivity and DocumentsUI launch.
4. Generate an artificial PNG labeled by distinct QA filename and push only to the disposable emulator's Downloads.
5. Navigate ParkPin UI to Save, invoke app's actual AndroidX photo contract; choose the file through system DocumentsUI.
6. Verify preview/Remove control is available, save a uniquely named parking entry using UI.
7. Read back the Row `photoPath` with read-only SQL from a copied Room database; check owned JPEG exists.
8. Force-stop and reopen app; verify same record/owned JPEG, and capture screenshots.
9. Upload screenshots, window dumps, records and JUnit logs even on failure.

No test may set the Room `photoPath` directly to simulate the picker; no prefilled data or invented success.
The API 24 test runs solely on an ephemeral CI emulator. No user data is cleared.

## Device QA still required
Use a dedicated test phone (Android API 24 or higher, preferably one near the minimum version).
Do not wipe or uninstall a live copy containing user parking records.
Install the chosen APK using `adb install -r`, run Save with camera/photo library choice,
preview/reselect/remove, close/reopen, edit/delete, GPS denial and grant, Maps handoff,
keyboard rotation and battery/network offline scenarios. Capture screenshots + Logcat,
APK SHA256, manufacturer, model, API version, and verdicts.

**Release decision:** `RELEASE HOLD` until API 24 e2e and physical-device QA have verifiable PASS evidence.
Compile/CI success and `minSdk 24` alone do not constitute release acceptance.
