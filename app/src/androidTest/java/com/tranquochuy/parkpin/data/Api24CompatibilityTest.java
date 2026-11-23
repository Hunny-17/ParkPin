package com.tranquochuy.parkpin.data;

import android.content.Context;
import android.content.Intent;
import android.os.Build;
import androidx.activity.result.PickVisualMediaRequest;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.test.core.app.ActivityScenario;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import com.tranquochuy.parkpin.MainActivity;
import com.tranquochuy.parkpin.R;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;
import static org.junit.Assume.assumeTrue;

/** API 24 compatibility checks; no automatic media read permissions or destructive operations. */
@RunWith(AndroidJUnit4.class)
public class Api24CompatibilityTest {
    @Test public void imagePickerContractResolvesOnApi24() {
        assumeTrue(Build.VERSION.SDK_INT == 24);
        Context context = ApplicationProvider.getApplicationContext();
        ActivityResultContracts.PickVisualMedia contract =
                new ActivityResultContracts.PickVisualMedia();
        PickVisualMediaRequest request = new PickVisualMediaRequest.Builder()
                .setMediaType(ActivityResultContracts.PickVisualMedia.ImageOnly.INSTANCE)
                .build();
        Intent intent = contract.createIntent(context, request);
        assertNotNull(intent);
        assertNotNull(intent.getAction());
        assertNotNull("No picker or document provider resolves the image selection intent",
                intent.resolveActivity(context.getPackageManager()));
        if (Intent.ACTION_OPEN_DOCUMENT.equals(intent.getAction())) {
            // AndroidX may omit CATEGORY_OPENABLE for ACTION_OPEN_DOCUMENT; the
            // supported fallback contract is the resolvable action + image MIME type.
            assertEquals("image/*", intent.getType());
        }
    }

    @Test public void mainActivityLaunchesOnApi24() {
        assumeTrue(Build.VERSION.SDK_INT == 24);
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity ->
                assertNotNull("Main Fragment container is missing",
                        activity.findViewById(R.id.fragment_container)));
        }
    }
}
