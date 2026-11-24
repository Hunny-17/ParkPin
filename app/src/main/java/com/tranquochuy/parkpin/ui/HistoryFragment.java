package com.tranquochuy.parkpin.ui;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ImageView;
import android.graphics.Rect;
import android.view.ViewTreeObserver;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import com.google.android.material.button.MaterialButton;
import com.tranquochuy.parkpin.MainActivity;
import com.tranquochuy.parkpin.R;
import com.tranquochuy.parkpin.data.ParkingRepository;
import com.tranquochuy.parkpin.data.ParkingSpot;
import com.tranquochuy.parkpin.navigation.MapsNavigation;
import com.tranquochuy.parkpin.photos.PhotoViews;
import java.text.DateFormat;
import java.util.Date;
import java.util.List;
import java.util.ArrayList;

/** G2: Room-backed list, edit, restore and delete with confirmation. */
public class HistoryFragment extends Fragment {
    private static final class PhotoSlot {
        final ImageView image;final TextView status;final String path,description;
        PhotoSlot(ImageView i,TextView s,String p,String d){image=i;status=s;path=p;description=d;}
    }
    private final List<PhotoSlot> photos=new ArrayList<>();
    private final ViewTreeObserver.OnScrollChangedListener photoScroll=this::updateVisiblePhotos;
    private final ViewTreeObserver.OnGlobalLayoutListener photoLayout=this::updateVisiblePhotos;
    public HistoryFragment() { super(R.layout.screen_history); }

    @Override public void onViewCreated(@NonNull View view, @Nullable Bundle state) {
        super.onViewCreated(view, state);
        view.getViewTreeObserver().addOnScrollChangedListener(photoScroll);
        view.getViewTreeObserver().addOnGlobalLayoutListener(photoLayout);
        load(view);
    }

    private void load(View root) {
        ParkingRepository repository = ParkingRepository.get(requireContext());
        repository.getAll(new ParkingRepository.Callback<List<ParkingSpot>>() {
            @Override public void onResult(List<ParkingSpot> items) {
                if (!isAdded() || getView() != root) return;
                LinearLayout list = root.findViewById(R.id.history_list);
                TextView count = root.findViewById(R.id.history_count);
                TextView empty = root.findViewById(R.id.history_empty);
                clearPhotos();list.removeAllViews();
                count.setText(items.size() + " VỊ TRÍ ĐÃ LƯU");
                empty.setVisibility(items.isEmpty() ? View.VISIBLE : View.GONE);
                for (ParkingSpot item : items) addItem(root, list, item);
                root.post(HistoryFragment.this::updateVisiblePhotos);
            }
            @Override public void onError(@NonNull Exception error) {
                if (getView() != root) return;
                ((TextView) root.findViewById(R.id.history_count)).setText("KHÔNG TẢI ĐƯỢC LỊCH SỬ");
                ((TextView) root.findViewById(R.id.history_empty)).setText(error.getMessage());
                root.findViewById(R.id.history_empty).setVisibility(View.VISIBLE);
            }
        });
    }

    private void addItem(View root, LinearLayout list, ParkingSpot spot) {
        View row = LayoutInflater.from(requireContext()).inflate(R.layout.item_parking_spot, list, false);
        ((TextView) row.findViewById(R.id.item_name)).setText(spot.placeName);
        ((TextView) row.findViewById(R.id.item_status)).setText(spot.active ? "ĐANG ĐỖ" : "ĐÃ LƯU");
        ((TextView) row.findViewById(R.id.item_details)).setText(
                "Tầng " + dash(spot.floor) + " · Khu " + dash(spot.zone) + " · Cột " + dash(spot.columnLabel));
        TextView note = row.findViewById(R.id.item_note);
        note.setText(spot.note);
        note.setVisibility(spot.note.isEmpty() ? View.GONE : View.VISIBLE);
        if(spot.photoPath!=null){
            ImageView image=row.findViewById(R.id.item_photo);
            image.setVisibility(View.VISIBLE);
            photos.add(new PhotoSlot(image,row.findViewById(R.id.item_photo_status),
                    spot.photoPath,"Ảnh chỗ đỗ xe tại "+spot.placeName));
        }
        ((TextView) row.findViewById(R.id.item_time)).setText(
                DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT)
                        .format(new Date(spot.createdAt)));
        row.<MaterialButton>findViewById(R.id.item_edit).setOnClickListener(
                v -> ((MainActivity) requireActivity()).editParking(spot.id));
        MaterialButton map = row.findViewById(R.id.item_map);
        map.setVisibility(spot.hasCoordinates() ? View.VISIBLE : View.GONE);
        map.setOnClickListener(v -> {
            if (spot.hasCoordinates() &&
                    !MapsNavigation.open(requireContext(), spot.latitude, spot.longitude)) {
                Toast.makeText(requireContext().getApplicationContext(),
                        "Không có ứng dụng bản đồ để mở vị trí này.", Toast.LENGTH_LONG).show();
            }
        });
        MaterialButton activate = row.findViewById(R.id.item_activate);
        activate.setVisibility(spot.active ? View.GONE : View.VISIBLE);
        activate.setOnClickListener(v -> ParkingRepository.get(requireContext())
                .activate(spot.id, new ParkingRepository.Callback<Boolean>() {
                    @Override public void onResult(Boolean ok) {
                        if (!isAdded() || getView() != root) return;
                        if (Boolean.TRUE.equals(ok)) load(root);
                        else Toast.makeText(requireContext().getApplicationContext(), "Vị trí đã bị xóa", Toast.LENGTH_SHORT).show();
                    }
                    @Override public void onError(@NonNull Exception error) { showError(root, error); }
                }));
        row.<MaterialButton>findViewById(R.id.item_delete).setOnClickListener(v ->
                new AlertDialog.Builder(requireContext())
                    .setTitle("Xóa vị trí đỗ xe?")
                    .setMessage("Thông tin này sẽ bị xóa khỏi thiết bị và không thể hoàn tác.")
                    .setNegativeButton("Hủy", null)
                    .setPositiveButton("Xóa", (dialog, which) ->
                        ParkingRepository.get(requireContext()).delete(spot.id,
                            new ParkingRepository.Callback<Boolean>() {
                                @Override public void onResult(Boolean ok) {
                                    if (!isAdded() || getView() != root) return;
                                    if (Boolean.TRUE.equals(ok)) load(root);
                                    else Toast.makeText(requireContext().getApplicationContext(), "Vị trí không còn tồn tại", Toast.LENGTH_SHORT).show();
                                }
                                @Override public void onError(@NonNull Exception error) { showError(root, error); }
                            }))
                    .show());
        list.addView(row);
    }

    private void showError(View root, Exception error) {
        if (isAdded() && getView() == root) {
            Toast.makeText(requireContext().getApplicationContext(), "Lỗi dữ liệu: " + error.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void updateVisiblePhotos(){
        if(getView()==null)return;
        Rect visible=new Rect();
        for(PhotoSlot slot:photos){
            if(slot.image.getGlobalVisibleRect(visible)&&!visible.isEmpty())
                PhotoViews.bind(slot.image,slot.status,slot.path,slot.description,320);
            else PhotoViews.clear(slot.image);
        }
    }
    private void clearPhotos(){for(PhotoSlot slot:photos)PhotoViews.clear(slot.image);photos.clear();}
    @Override public void onDestroyView(){
        View root=getView();
        if(root!=null&&root.getViewTreeObserver().isAlive()){
            root.getViewTreeObserver().removeOnScrollChangedListener(photoScroll);
            root.getViewTreeObserver().removeOnGlobalLayoutListener(photoLayout);
        }
        clearPhotos();super.onDestroyView();
    }

    private static String dash(String value) {
        return value == null || value.isEmpty() ? "—" : value;
    }
}
