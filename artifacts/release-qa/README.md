# Final release QA evidence

See [the acceptance report](../../docs/RELEASE_QA.md) for decisions and limitations.

- `baseline/`, CI screenshots and `local-baseline-*`: reproduction of the original DocumentsUI automation failure.
- `e2e/`: first corrected picker run exposed a real API24 ParkPin Toast crash; retained as FAIL evidence.
- `toast-red-instrumentation.txt`: actual new regression test RED (1 failure). `toast-red-test.log` is an unsuccessful Gradle installer attempt and is never counted as a test PASS.
- `junit-fixed-api24.xml`: actual full GREEN 19/19, zero failure/error/skip. JVM JUnit files total 4/4.
- `e2e-fixed/`: first complete successful picker → preview → Room/private JPEG → restart → History → UI deletion run after the production fix.
- `e2e-final/`: repeated acceptance completed deletion, then UIAutomator hierarchy read timed out. It is not counted as a completed runner PASS.
- `e2e-verified/`: final guarded runner, including resumed Activity assertion and read-only UIAutomator retry. Its result and log state the observed verdict.
- `regression.py`, `regression-result.json`, `regression-run.log`, `database-reg-*.json`, `screenshots/reg-*`: actual 11/11 UI regression checks on the dedicated API24 AVD.
- `logcat-post-fix.txt`, `crash-post-fix.txt`, `post-fix-summary.json`: capture window starts after the fixed full suite and before UI acceptance. Pre-fix logs retain the reproduced crash separately.
- All Room reads use captured DB+WAL in fresh host directories. No SQL updates were sent to ParkPin. Synthetic QA rows were created/changed/deleted only through UI.
- The debug APK is not published or committed. `apk-debug-sha256.json` identifies the local binary tested. `reviewed-source-hashes.json` identifies final changed source files.
- Final CI runs are attached to the aggregate commit on GitHub; exact SHA/run links are verified after push and supplied in the final delivery. Live main CI badges are in the report.

**Physical device: BLOCKED — NO DEVICE. Release: HOLD.**
