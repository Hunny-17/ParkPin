package com.tranquochuy.parkpin.ui;

import android.os.Bundle;
import android.view.View;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.tranquochuy.parkpin.MainActivity;
import com.tranquochuy.parkpin.R;

/** G1: Home UI with navigation-only actions. */
public class HomeFragment extends Fragment {
    public HomeFragment() { super(R.layout.screen_home); }

    @Override public void onViewCreated(@NonNull View view, @Nullable Bundle state) {
        super.onViewCreated(view, state);
        MaterialButton save = view.findViewById(R.id.btn_save_parking_mock);
        save.setOnClickListener(v -> ((MainActivity) requireActivity()).navigateTo(R.id.nav_save));
        MaterialCardView history = view.findViewById(R.id.card_open_history);
        history.setOnClickListener(v -> ((MainActivity) requireActivity()).navigateTo(R.id.nav_history));
        MaterialCardView findCar = view.findViewById(R.id.card_find_car);
        findCar.setOnClickListener(v -> Toast.makeText(requireContext(),
                "Chỉ đường sẽ có ở G3 (GPS + Maps).", Toast.LENGTH_SHORT).show());
    }
}
