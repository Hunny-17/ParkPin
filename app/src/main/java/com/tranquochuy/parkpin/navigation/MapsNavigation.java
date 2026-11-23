package com.tranquochuy.parkpin.navigation;

import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import androidx.annotation.NonNull;
import com.tranquochuy.parkpin.data.GpsFix;
import java.util.Locale;

/** Opens external Maps only for a saved valid coordinate; never embeds an API-key map. */
public final class MapsNavigation {
    private MapsNavigation() {}

    public static String navigationUriText(double lat, double lng) {
        if (!GpsFix.validCoordinates(lat, lng)) throw new IllegalArgumentException("Invalid GPS coordinates");
        return String.format(Locale.US, "google.navigation:q=%.7f,%.7f", lat, lng);
    }

    public static String fallbackUriText(double lat, double lng) {
        if (!GpsFix.validCoordinates(lat, lng)) throw new IllegalArgumentException("Invalid GPS coordinates");
        return String.format(Locale.US, "geo:0,0?q=%.7f,%.7f", lat, lng);
    }

    /** Returns false when neither Google Maps nor a generic geo handler is installed. */
    public static boolean open(@NonNull Context context, double lat, double lng) {
        if (!GpsFix.validCoordinates(lat, lng)) return false;
        Intent google = new Intent(Intent.ACTION_VIEW, Uri.parse(navigationUriText(lat, lng)));
        google.setPackage("com.google.android.apps.maps");
        try {
            context.startActivity(google);
            return true;
        } catch (ActivityNotFoundException | SecurityException ignored) {
            // Allow any other installed geo map app to handle the saved coordinate.
        }
        Intent generic = new Intent(Intent.ACTION_VIEW, Uri.parse(fallbackUriText(lat, lng)));
        try {
            context.startActivity(generic);
            return true;
        } catch (ActivityNotFoundException | SecurityException ignored) {
            return false;
        }
    }
}
