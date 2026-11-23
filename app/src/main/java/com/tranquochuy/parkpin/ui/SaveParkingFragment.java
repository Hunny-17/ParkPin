package com.tranquochuy.parkpin.ui;

import android.os.Bundle;
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

/** G2: manual local parking form. GPS and photo capture remain deferred. */
public class SaveParkingFragment extends Fragment {
    private static final String ARG_EDIT_ID = "edit_id";
    private long editId = -1L;

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

        if (editId > 0) {
            save.setText("CẬP NHẬT VỊ TRÍ");
            if (state == null) {
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
                        status.setText("Đang sửa vị trí đã lưu trên thiết bị");
                        save.setEnabled(true);
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
            save.setEnabled(false);
            status.setText("Đang lưu trên thiết bị...");
            ParkingRepository.Callback<Boolean> updateCallback = new ParkingRepository.Callback<Boolean>() {
                @Override public void onResult(Boolean updated) {
                    if (!isAdded() || getView() != view) return;
                    if (!Boolean.TRUE.equals(updated)) {
                        status.setText("Vị trí không còn tồn tại.");
                        save.setEnabled(true);
                        return;
                    }
                    Toast.makeText(requireContext(), "Đã cập nhật vị trí", Toast.LENGTH_SHORT).show();
                    ((MainActivity) requireActivity()).navigateTo(R.id.nav_home);
                }
                @Override public void onError(@NonNull Exception error) {
                    if (getView() != view) return;
                    status.setText("Lưu thất bại: " + error.getMessage());
                    save.setEnabled(true);
                }
            };
            if (editId > 0) {
                repository.updateDetails(editId, placeName, value(floor), value(zone),
                        value(column), value(note), updateCallback);
            } else {
                repository.saveActive(placeName, value(floor), value(zone),
                        value(column), value(note), new ParkingRepository.Callback<Long>() {
                    @Override public void onResult(Long id) {
                        if (!isAdded() || getView() != view) return;
                        Toast.makeText(requireContext(), "Đã lưu vị trí đỗ xe", Toast.LENGTH_SHORT).show();
                        ((MainActivity) requireActivity()).navigateTo(R.id.nav_home);
                    }
                    @Override public void onError(@NonNull Exception error) {
                        if (getView() != view) return;
                        status.setText("Lưu thất bại: " + error.getMessage());
                        save.setEnabled(true);
                    }
                });
            }
        });
    }

    private static String value(TextInputEditText field) {
        return field.getText() == null ? "" : field.getText().toString().trim();
    }
}
