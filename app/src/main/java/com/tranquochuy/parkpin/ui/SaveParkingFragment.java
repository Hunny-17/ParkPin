package com.tranquochuy.parkpin.ui;

import android.Manifest;
import android.content.pm.PackageManager;
import android.location.Location;
import android.os.Bundle;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.activity.result.PickVisualMediaRequest;
import androidx.lifecycle.ViewModelProvider;
import com.tranquochuy.parkpin.photos.PhotoDraftViewModel;
import com.tranquochuy.parkpin.photos.PhotoViews;
import androidx.core.content.ContextCompat;
import com.google.android.gms.location.CurrentLocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.Priority;
import com.google.android.gms.tasks.CancellationTokenSource;
import com.tranquochuy.parkpin.data.GpsFix;
import java.util.Locale;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.textfield.TextInputLayout;
import com.tranquochuy.parkpin.MainActivity;
import com.tranquochuy.parkpin.R;
import com.tranquochuy.parkpin.data.ParkingRepository;
import com.tranquochuy.parkpin.data.ParkingSpot;

/** G3: manual-first parking form with optional, explicitly requested GPS capture. */
public class SaveParkingFragment extends Fragment {
    private static final String ARG_EDIT_ID = "edit_id";
    private static final String FIX_LAT = "fix_lat";
    private static final String FIX_LNG = "fix_lng";
    private static final String FIX_ACC = "fix_acc";
    private static final String FIX_TIME = "fix_time";
    private static final String FIX_NEW = "fix_new";
    private long editId = -1L;
    @Nullable private GpsFix currentFix;
    private boolean newGpsFix;
    @Nullable private CancellationTokenSource pendingRequest;
    private PhotoDraftViewModel photoDraft;
    private boolean loadingRecord;
    private final ActivityResultLauncher<PickVisualMediaRequest> photoPicker =
            registerForActivityResult(new ActivityResultContracts.PickVisualMedia(), uri -> {
                if(uri!=null) {
                    if(photoDraft==null)photoDraft=new ViewModelProvider(this).get(PhotoDraftViewModel.class);
                    photoDraft.select(uri);
                }
            });

    private final ActivityResultLauncher<String[]> permissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), result -> {
                if (!isAdded() || getView() == null) return;
                if (hasLocationPermission()) requestCurrentLocation(getView());
                else ((TextView) requireView().findViewById(R.id.gps_status)).setText(
                        "Không được cấp quyền vị trí. Bạn vẫn có thể lưu thủ công.");
            });

    public SaveParkingFragment() { super(R.layout.screen_save_parking); }

    public static SaveParkingFragment forEdit(long id) {
        SaveParkingFragment fragment = new SaveParkingFragment();
        Bundle args = new Bundle();
        args.putLong(ARG_EDIT_ID, id);
        fragment.setArguments(args);
        return fragment;
    }

    @Override public void onViewCreated(@NonNull View view, @Nullable Bundle state) {
        super.onViewCreated(view, state);
        editId = getArguments() == null ? -1L : getArguments().getLong(ARG_EDIT_ID, -1L);
        TextInputEditText name = view.findViewById(R.id.input_place_name);
        TextInputEditText floor = view.findViewById(R.id.input_floor);
        TextInputEditText zone = view.findViewById(R.id.input_zone);
        TextInputEditText column = view.findViewById(R.id.input_column);
        TextInputEditText note = view.findViewById(R.id.input_note);
        TextInputLayout nameLayout = view.findViewById(R.id.layout_place_name);
        MaterialButton save = view.findViewById(R.id.btn_save_parking);
        TextView status = view.findViewById(R.id.save_status);
        ParkingRepository repository = ParkingRepository.get(requireContext());
        photoDraft=new ViewModelProvider(this).get(PhotoDraftViewModel.class);
        loadingRecord=editId>0&&!photoDraft.initialized();
        if(editId<=0)photoDraft.initialize(null);
        view.findViewById(R.id.btn_pick_photo).setOnClickListener(v -> {
            try {photoPicker.launch(new PickVisualMediaRequest.Builder()
                    .setMediaType(ActivityResultContracts.PickVisualMedia.ImageOnly.INSTANCE).build());}
            catch(RuntimeException e){Toast.makeText(requireContext(),"Không mở được trình chọn ảnh. Bạn vẫn có thể lưu thủ công.",Toast.LENGTH_LONG).show();}
        });
        view.findViewById(R.id.btn_remove_photo).setOnClickListener(v -> photoDraft.remove());
        photoDraft.state().observe(getViewLifecycleOwner(),draft->{
            if(draft.saved){
                photoDraft.consumeSaved();
                Toast.makeText(requireContext(),editId>0?"Đã cập nhật vị trí":"Đã lưu vị trí đỗ xe",Toast.LENGTH_SHORT).show();
                ((MainActivity)requireActivity()).navigateTo(R.id.nav_home);return;
            }
            PhotoViews.bind(view.findViewById(R.id.photo_preview),view.findViewById(R.id.photo_status),draft.path,"Ảnh chỗ đỗ xe đã chọn");
            TextView photoError=view.findViewById(R.id.photo_error);
            photoError.setVisibility(draft.busy||draft.error!=null?View.VISIBLE:View.GONE);
            photoError.setText(draft.busy?"Đang chuẩn bị ảnh...":draft.error);
            MaterialButton pick=view.findViewById(R.id.btn_pick_photo);
            pick.setText(draft.path==null?"CHỌN ẢNH":"ĐỔI ẢNH");
            pick.setEnabled(!draft.busy&&!draft.saving&&!loadingRecord);
            view.findViewById(R.id.btn_remove_photo).setVisibility(draft.path==null?View.GONE:View.VISIBLE);
            view.findViewById(R.id.btn_remove_photo).setEnabled(!draft.busy&&!draft.saving&&!loadingRecord);
            save.setEnabled(!draft.busy&&!draft.saving&&!loadingRecord);
        });
        MaterialButton gpsButton = view.findViewById(R.id.btn_capture_gps);
        gpsButton.setOnClickListener(v -> {
            if (hasLocationPermission()) requestCurrentLocation(view);
            else permissionLauncher.launch(new String[] {
                    Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION
            });
        });

        if (state != null && state.containsKey(FIX_LAT)) {
            try {
                currentFix = new GpsFix(state.getDouble(FIX_LAT), state.getDouble(FIX_LNG),
                        state.containsKey(FIX_ACC) ? state.getFloat(FIX_ACC) : null,
                        state.getLong(FIX_TIME));
                newGpsFix = state.getBoolean(FIX_NEW, false);
                updateGpsLabel(view);
            } catch (IllegalArgumentException ignored) {
                currentFix = null;
                newGpsFix = false;
            }
        }

        name.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}
            @Override public void afterTextChanged(Editable text) {
                if (!text.toString().trim().isEmpty()) nameLayout.setError(null);
            }
        });

        if (editId > 0) {
            save.setText("CẬP NHẬT VỊ TRÍ");
            if (loadingRecord) {
                save.setEnabled(false);
                status.setText("Đang tải dữ liệu đã lưu...");
                repository.getById(editId, new ParkingRepository.Callback<ParkingSpot>() {
                    @Override public void onResult(ParkingSpot item) {
                        if (!isAdded() || getView() != view) return;
                        if (item == null) {
                            status.setText("Vị trí không còn tồn tại.");
                            return;
                        }
                        name.setText(item.placeName);
                        floor.setText(item.floor);
                        zone.setText(item.zone);
                        column.setText(item.columnLabel);
                        note.setText(item.note);
                        loadingRecord=false;
                        photoDraft.initialize(item.photoPath);
                        if (item.hasCoordinates() && !newGpsFix) {
                            currentFix = new GpsFix(item.latitude, item.longitude,
                                    item.accuracyMeters,
                                    item.locationCapturedAt == null ? 0 : item.locationCapturedAt);
                            updateGpsLabel(view);
                        }
                        status.setText("Đang sửa vị trí đã lưu trên thiết bị");
                        save.setEnabled(!photoDraft.current().busy&&!photoDraft.current().saving);
                    }
                    @Override public void onError(@NonNull Exception error) {
                        if (getView() == view) status.setText("Không tải được vị trí: " + error.getMessage());
                    }
                });
            }
        }

        save.setOnClickListener(v -> {
            String placeName = value(name);
            if (placeName.isEmpty()) {
                nameLayout.setError("Vui lòng nhập tên bãi đỗ");
                name.requestFocus();
                return;
            }
            nameLayout.setError(null);
            if(photoDraft.current().busy||photoDraft.current().saving||loadingRecord)return;
            photoDraft.beginSave();
            save.setEnabled(false);
            status.setText("Đang lưu trên thiết bị...");
            ParkingRepository.Callback<Boolean> updateCallback = new ParkingRepository.Callback<Boolean>() {
                @Override public void onResult(Boolean updated) {
                    if (!Boolean.TRUE.equals(updated)) {
                        photoDraft.finishSave();
                        if(getView()!=view)return;
                        status.setText("Vị trí không còn tồn tại.");
                        save.setEnabled(true);
                        return;
                    }
                    photoDraft.markSaved();
                }
                @Override public void onError(@NonNull Exception error) {
                    photoDraft.finishSave();
                    if (getView() != view) return;
                    status.setText("Lưu thất bại: " + error.getMessage());
                    save.setEnabled(true);
                }
            };
            if (editId > 0) {
                repository.updateDetails(editId, placeName, value(floor), value(zone),
                        value(column), value(note), newGpsFix ? currentFix : null,
                        photoDraft.current().changed,photoDraft.current().path,updateCallback);
            } else {
                repository.saveActive(placeName, value(floor), value(zone),
                        value(column), value(note), currentFix,photoDraft.current().path,new ParkingRepository.Callback<Long>() {
                    @Override public void onResult(Long id) {
                        photoDraft.markSaved();
                    }
                    @Override public void onError(@NonNull Exception error) {
                        photoDraft.finishSave();
                        if (getView() != view) return;
                        status.setText("Lưu thất bại: " + error.getMessage());
                        save.setEnabled(true);
                    }
                });
            }
        });
    }

    private boolean hasLocationPermission() {
        return ContextCompat.checkSelfPermission(requireContext(), Manifest.permission.ACCESS_FINE_LOCATION)
                    == PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(requireContext(), Manifest.permission.ACCESS_COARSE_LOCATION)
                    == PackageManager.PERMISSION_GRANTED;
    }

    private void requestCurrentLocation(View view) {
        TextView gpsStatus = view.findViewById(R.id.gps_status);
        MaterialButton gpsButton = view.findViewById(R.id.btn_capture_gps);
        boolean fine = ContextCompat.checkSelfPermission(requireContext(),
                Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
        gpsStatus.setText("Đang lấy vị trí thiết bị... Có thể tiếp tục nhập thủ công.");
        gpsButton.setEnabled(false);
        if (pendingRequest != null) pendingRequest.cancel();
        CancellationTokenSource source = new CancellationTokenSource();
        pendingRequest = source;
        try {
            CurrentLocationRequest request = new CurrentLocationRequest.Builder()
                    .setPriority(fine ? Priority.PRIORITY_HIGH_ACCURACY : Priority.PRIORITY_BALANCED_POWER_ACCURACY)
                    .setMaxUpdateAgeMillis(5_000L)
                    .setDurationMillis(15_000L)
                    .build();
            LocationServices.getFusedLocationProviderClient(requireContext())
                    .getCurrentLocation(request, source.getToken())
                    .addOnSuccessListener(location -> {
                        if (!isAdded() || getView() != view || pendingRequest != source) return;
                        pendingRequest = null;
                        gpsButton.setEnabled(true);
                        if (location == null || !GpsFix.validCoordinates(location.getLatitude(), location.getLongitude())) {
                            gpsStatus.setText("Chưa lấy được GPS. Bạn vẫn có thể lưu vị trí thủ công.");
                            return;
                        }
                        Float accuracy = location.hasAccuracy() ? location.getAccuracy() : null;
                        currentFix = new GpsFix(location.getLatitude(), location.getLongitude(),
                                accuracy, location.getTime() > 0 ? location.getTime() : System.currentTimeMillis());
                        newGpsFix = true;
                        updateGpsLabel(view);
                    })
                    .addOnFailureListener(error -> {
                        if (!isAdded() || getView() != view || pendingRequest != source) return;
                        pendingRequest = null;
                        gpsButton.setEnabled(true);
                        gpsStatus.setText("Không thể lấy GPS. Hãy kiểm tra định vị hoặc lưu thủ công.");
                    });
        } catch (RuntimeException error) {
            pendingRequest = null;
            gpsButton.setEnabled(true);
            gpsStatus.setText("Không thể truy cập định vị. Vẫn có thể lưu thủ công.");
        }
    }

    private void updateGpsLabel(View view) {
        TextView status = view.findViewById(R.id.gps_status);
        if (currentFix == null) {
            status.setText("Chưa lấy GPS · Có thể lưu vị trí thủ công");
        } else {
            String approx = ContextCompat.checkSelfPermission(requireContext(),
                    Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                    ? "GPS" : "Vị trí gần đúng";
            status.setText(String.format(Locale.US, "%s: %.6f, %.6f%s",
                    approx, currentFix.latitude, currentFix.longitude,
                    currentFix.accuracyMeters == null ? "" :
                            String.format(Locale.US, " (±%.0f m)", currentFix.accuracyMeters)));
        }
    }

    @Override public void onSaveInstanceState(@NonNull Bundle state) {
        if (currentFix != null) {
            state.putDouble(FIX_LAT, currentFix.latitude);
            state.putDouble(FIX_LNG, currentFix.longitude);
            if (currentFix.accuracyMeters != null) state.putFloat(FIX_ACC, currentFix.accuracyMeters);
            state.putLong(FIX_TIME, currentFix.capturedAt);
            state.putBoolean(FIX_NEW, newGpsFix);
        }
        super.onSaveInstanceState(state);
    }

    @Override public void onDestroyView() {
        if (pendingRequest != null) {
            pendingRequest.cancel();
            pendingRequest = null;
        }
        super.onDestroyView();
    }

    private static String value(TextInputEditText field) {
        return field.getText() == null ? "" : field.getText().toString().trim();
    }
}
