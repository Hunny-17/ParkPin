# G4 — Photo Picker và ảnh điểm đỗ

User instruction: merge PR #3, verify main CI, then implement Photo Picker and
parking photo persistence. Execution continues in the current dedicated checkout
on `codex/g4-photo-picker`, based on merged G3 main.

Main merge SHA: `44aac930382d87bec3f8bd6c08aa83bdc25fc2f2`.
Main push CI: [45159706681 — SUCCESS](https://github.com/Hunny-17/ParkPin/actions/runs/45159706681).

## Scope and implementation choices

- One optional image per parking spot, selected through AndroidX PickVisualMedia
  (ImageOnly); AndroidX falls back to the system document picker on older devices.
- Keep the existing Vietnamese Java/XML UI and all GPS/manual CRUD behavior.
- Replace the photo placeholder with preview, Chọn/Đổi ảnh and Bỏ ảnh. Selection
  and removal are drafts until Save; cancel/Back never changes a saved photo.
- Display the saved image on Home and History; missing/corrupt image has readable
  fallback and never prevents editing or saving manually.
- Import a sampled, oriented JPEG (long edge <=1600 pixels) into private files,
  off the main thread. Room v3 adds nullable photoPath; no storage/media/camera
  permissions, no backend, no camera capture or uploads.
- Preserve draft state during rotation/picker return using SavedStateHandle and
  ViewModel. Save disabled while importing to avoid storing half-written files.
- Delete replaced/removed files only after successful DB mutation. Delete a
  record's own photo after confirmed deletion. Unsaved draft files are cleaned
  when the form is discarded; stale abandoned drafts are pruned after 24 hours,
  while referenced files are always retained.

## Approaches considered

Persistable content URI avoids copying but depends on the provider/source file
remaining available. A private local copy costs bounded storage and keeps the
saved parking image available after restart/source deletion. The private-copy
approach is the implementation choice for this request, not an extra user promise.

## Acceptance

Actual system picker select/cancel/replace/remove; save/restart; manual edit keeps
photo and GPS; rotate with draft; graceful missing/corrupt source; real Room v2→v3
upgrade retaining existing records/GPS; file cleanup after replace/delete; no new
broad permissions; build/JVM/connected tests and G1–G3 regression.

API references: [Photo Picker](https://developer.android.com/training/data-storage/shared/photo-picker),
[ImageDecoder](https://developer.android.com/reference/android/graphics/ImageDecoder),
[AndroidX EXIF 1.4.2](https://developer.android.com/jetpack/androidx/releases/exifinterface).
