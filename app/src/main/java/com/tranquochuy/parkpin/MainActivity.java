package com.tranquochuy.parkpin;

import android.os.Bundle;
import android.view.View;
import androidx.activity.OnBackPressedCallback;
import androidx.annotation.IdRes;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.fragment.app.Fragment;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.tranquochuy.parkpin.ui.HomeFragment;
import com.tranquochuy.parkpin.ui.SaveParkingFragment;
import com.tranquochuy.parkpin.ui.HistoryFragment;

/** G1: navigation between static Fragments; GPS and persistence are deferred. */
public class MainActivity extends AppCompatActivity {
    private static final String KEY_SELECTED_TAB = "selected_tab";
    private BottomNavigationView bottomNav;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView())
                .setAppearanceLightStatusBars(true);
        WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView())
                .setAppearanceLightNavigationBars(true);
        setContentView(R.layout.activity_main);

        View root = findViewById(R.id.root_container);
        int l = root.getPaddingLeft(), t = root.getPaddingTop();
        int r = root.getPaddingRight(), b = root.getPaddingBottom();
        ViewCompat.setOnApplyWindowInsetsListener(root, (view, insets) -> {
            Insets safe = insets.getInsets(
                    WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.ime());
            view.setPadding(l + safe.left, t + safe.top, r + safe.right, b + safe.bottom);
            return insets;
        });
        ViewCompat.requestApplyInsets(root);

        bottomNav = findViewById(R.id.bottom_nav);
        bottomNav.setOnItemSelectedListener(item -> showTab(item.getItemId()));
        if (savedInstanceState == null) {
            getSupportFragmentManager().beginTransaction()
                    .replace(R.id.fragment_container, new HomeFragment()).commitNow();
        }
        int selected = savedInstanceState == null ? R.id.nav_home
                : savedInstanceState.getInt(KEY_SELECTED_TAB, R.id.nav_home);
        bottomNav.setSelectedItemId(selected);

        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override public void handleOnBackPressed() {
                if (bottomNav.getSelectedItemId() != R.id.nav_home) {
                    bottomNav.setSelectedItemId(R.id.nav_home);
                } else {
                    setEnabled(false);
                    getOnBackPressedDispatcher().onBackPressed();
                }
            }
        });
    }

    public void navigateTo(@IdRes int itemId) {
        bottomNav.setSelectedItemId(itemId);
    }

    private boolean showTab(@IdRes int id) {
        Fragment target;
        if (id == R.id.nav_home) target = new HomeFragment();
        else if (id == R.id.nav_save) target = new SaveParkingFragment();
        else if (id == R.id.nav_history) target = new HistoryFragment();
        else return false;

        Fragment current = getSupportFragmentManager().findFragmentById(R.id.fragment_container);
        if (current != null && current.getClass().equals(target.getClass())) return true;
        getSupportFragmentManager().beginTransaction().setReorderingAllowed(true)
                .replace(R.id.fragment_container, target).commit();
        return true;
    }

    @Override protected void onSaveInstanceState(Bundle outState) {
        outState.putInt(KEY_SELECTED_TAB, bottomNav.getSelectedItemId());
        super.onSaveInstanceState(outState);
    }
}
