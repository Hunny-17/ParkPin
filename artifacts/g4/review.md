# Independent G4 review

Reviewer: fresh read-only agent, baseline main
`44aac930382d87bec3f8bd6c08aa83bdc25fc2f2`. Reviewed spec and full implementation
for photo ownership, async save/import/rotation, SavedStateHandle, migration/GPS,
API24 guards, permissions and memory safety.

## Material finding and fix

P2: initial History implementation decoded and retained a thumbnail for every
row in the existing non-recycling list. Hundreds of photos could exhaust memory.

Fix: keep original History layout; bind photos only when their ImageView
intersects the visible viewport. Clear offscreen/destroyed drawables; cancel
queued requests; recycle late decoded results. Fixed-height image slots preserve
scroll geometry. Home/Save images remain sampled and decoded asynchronously.

RED: `clearingOffscreenPhotoReleasesBitmapAndRejectsLateDecode` ran before the
release API existed and failed (1 test / 1 failure). Final test includes a real
JPEG positive control, release assertion and cancelled-result assertion.

Follow-up review: no remaining material findings in the fix. Reviewer explicitly
requested actual scroll-away/return QA, covered by P09 and its screenshots.

No additional material findings in file ownership, save/rotation lifecycle,
Room/GPS preservation, API24 guards or permission changes. Reviewer made no edits
and did not operate the emulator.
