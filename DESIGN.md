# ParkPin design context

Established Vietnamese native Android Java/XML application. Preserve the G1–G3
accepted interface rather than restyling it for G4. Canonical runtime tokens are
`app/src/main/res/values/colors.xml` and styles.xml: navy #15263F, muted #61738A,
green #087F69, mint #DDF8EC, background #F6F8FC, surface #FFFFFF.

System sans typography, existing rounded cards and green actions, fixed Bottom
Navigation, independently scrollable fragment content and IME-aware insets.
Photo actions use existing outlined Material buttons; image previews add content,
not new decorative treatments. Minimum photo action target 48dp. Meaningful
Vietnamese content descriptions; busy/error/empty states remain readable.

Forms save back to Home, secondary-tab Back returns Home; confirmed record delete
is the existing irreversible action. Photo changes are not committed until Save.
Keep offline manual-first behavior and optional user-initiated GPS.
