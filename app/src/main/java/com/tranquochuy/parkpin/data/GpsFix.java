package com.tranquochuy.parkpin.data;

import androidx.annotation.Nullable;

/** Optional user-requested GPS fix. Manual parking records never require coordinates. */
public final class GpsFix {
    public final double latitude;
    public final double longitude;
    @Nullable public final Float accuracyMeters;
    public final long capturedAt;

    public GpsFix(double latitude, double longitude, @Nullable Float accuracyMeters, long capturedAt) {
        if (!validCoordinates(latitude, longitude)) throw new IllegalArgumentException("Tọa độ GPS không hợp lệ");
        if (accuracyMeters != null && (!Float.isFinite(accuracyMeters) || accuracyMeters < 0))
            throw new IllegalArgumentException("Độ chính xác GPS không hợp lệ");
        this.latitude = latitude;
        this.longitude = longitude;
        this.accuracyMeters = accuracyMeters;
        this.capturedAt = capturedAt;
    }

    public static boolean validCoordinates(double latitude, double longitude) {
        return Double.isFinite(latitude) && Double.isFinite(longitude)
                && latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
    }
}
