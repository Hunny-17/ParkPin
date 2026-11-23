# QA-only generic geo receiver

Used only for M06 because this AVD originally had Google Maps as its sole `geo:`
handler. The separate package `com.tranquochuy.parkpin.qa.geo` renders the URI it
actually receives from Android. It has no permissions, location provider, network,
storage or hardcoded destination. It does not change the ParkPin APK.

The fixture was compiled with JDK 17 `javac -source 8 -target 8`, Android platform
37 `android.jar`, and SDK Build Tools 36.0.0 (`aapt2 link`, `d8`, `zipalign`,
`apksigner`). Only its source is committed. The locally signed APK remained under
ignored `.qa-tools/g3-geo-handler/geo-handler-qa.apk`.

Tested APK SHA-256:
`d95b40f524ae9212615831629087282de37c58f18ab086ea5d96c5943149cc00`.

Maps was disabled only on copied QA AVD emulator-5556. With the fixture as the
only remaining handler, ParkPin's generic `geo:` Intent launched this activity
and delivered the exact Room destination. With both handlers disabled, ParkPin
showed its friendly error. The fixture was then uninstalled and Maps restored to
its original default enabled state.

This proves actual Android fallback delivery. It does not claim to test another
commercial map application's cartography or route calculation.
