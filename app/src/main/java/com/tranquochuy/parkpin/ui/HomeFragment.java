package com.tranquochuy.parkpin.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.tranquochuy.parkpin.MainActivity;
import com.tranquochuy.parkpin.R;
import com.tranquochuy.parkpin.data.ParkingRepository;
import com.tranquochuy.parkpin.data.ParkingSpot;
import com.tranquochuy.parkpin.navigation.MapsNavigation;
import com.tranquochuy.parkpin.photos.PhotoViews;
import java.text.DateFormat;
import java.util.Date;

/** G2: latest real local parking spot, no seeded/demo record. */
public class HomeFragment extends Fragment {
    private long activeId = -1L;
    @Nullable private ParkingSpot activeSpot;

    public HomeFragment() { super(R.layout.screen_home); }

    @Override public void onViewCreated(@NonNull View view, @Nullable Bundle state) {
        super.onViewCreated(view, state);
        MaterialButton save = view.findViewById(R.id.btn_save_parking_mock);
        save.setOnClickListener(v -> ((MainActivity) requireActivity()).navigateTo(R.id.nav_save));
        MaterialCardView history = view.findViewById(R.id.card_open_history);
        history.setOnClickListener(v -> ((MainActivity) requireActivity()).navigateTo(R.id.nav_history));
        MaterialCardView current = view.findViewById(R.id.card_current_parking);
        current.setOnClickListener(v -> {
            MainActivity activity = (MainActivity) requireActivity();
            if (activeId > 0) activity.editParking(activeId);
            else activity.navigateTo(R.id.nav_save);
        });
        MaterialCardView findCar = view.findViewById(R.id.card_find_car);
        findCar.setOnClickListener(v -> {
            if (activeSpot == null) {
                Toast.makeText(requireContext(), "Chưa có vị trí đỗ xe để tìm.", Toast.LENGTH_SHORT).show();
            } else if (!activeSpot.hasCoordinates()) {
                Toast.makeText(requireContext(),
                        "Điểm đỗ chưa có GPS. Hãy chỉnh sửa vị trí và nhấn LẤY GPS.",
                        Toast.LENGTH_LONG).show();
            } else if (!MapsNavigation.open(requireContext(), activeSpot.latitude, activeSpot.longitude)) {
                Toast.makeText(requireContext(),
                        "Không tìm thấy ứng dụng bản đồ. Dữ liệu đỗ xe vẫn được giữ nguyên.",
                        Toast.LENGTH_LONG).show();
            }
        });
        refresh(view);
    }

    private void refresh(View view) {
        ParkingRepository.get(requireContext()).getActive(new ParkingRepository.Callback<ParkingSpot>() {
            @Override public void onResult(ParkingSpot spot) {
                if (!isAdded() || getView() != view) return;
                activeId = spot == null ? -1L : spot.id;
                activeSpot = spot;
                PhotoViews.bind(view.findViewById(R.id.home_photo),view.findViewById(R.id.home_photo_status),
                        spot==null?null:spot.photoPath,"Ảnh chỗ đỗ xe hiện tại");
                if(spot==null||spot.photoPath==null)view.findViewById(R.id.home_photo_status).setVisibility(View.GONE);
                TextView name = view.findViewById(R.id.home_spot_name);
                TextView details = view.findViewById(R.id.home_spot_details);
                TextView time = view.findViewById(R.id.home_spot_time);
                TextView gps = view.findViewById(R.id.home_spot_gps);
                if (spot == null) {
                    name.setText("Chưa lưu vị trí nào");
                    details.setText("Nhấn LƯU VỊ TRÍ ĐỖ XE để bắt đầu");
                    time.setText("Dữ liệu chỉ lưu trên thiết bị");
                    gps.setText("Chưa có GPS");
                } else {
                    name.setText(spot.placeName);
                    details.setText("Tầng " + dash(spot.floor) + " · Khu " + dash(spot.zone)
                            + " · Cột " + dash(spot.columnLabel));
                    time.setText(DateFormat.getDateTimeInstance(DateFormat.SHORT,
                            DateFormat.SHORT).format(new Date(spot.createdAt)));
                    gps.setText(spot.hasCoordinates() ? "Có GPS · Chạm Tìm xe để mở bản đồ" : "Chưa lưu GPS · Vẫn có thể chỉnh sửa thủ công");
                }
            }
            @Override public void onError(@NonNull Exception error) {
                if (getView() == view) {
                    ((TextView) view.findViewById(R.id.home_spot_name)).setText("Không tải được dữ liệu");
                    ((TextView) view.findViewById(R.id.home_spot_details)).setText(error.getMessage());
                }
            }
        });
    }

    private static String dash(String value) {
        return value == null || value.isEmpty() ? "—" : value;
    }
}
