package com.tranquochuy.parkpin.data;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

/** One saved parking place. GPS coordinates are optional; photos are deferred. */
@Entity(tableName = "parking_spots")
public class ParkingSpot {
    @PrimaryKey(autoGenerate = true)
    public long id;

    @NonNull
    public String placeName = "";

    @NonNull
    public String floor = "";

    @NonNull
    public String zone = "";

    @NonNull
    public String columnLabel = "";

    @NonNull
    public String note = "";

    @ColumnInfo(index = true)
    public boolean active;

    @Nullable public Double latitude;
    @Nullable public Double longitude;
    @Nullable public Float accuracyMeters;
    @Nullable public Long locationCapturedAt;

    public boolean hasCoordinates() {
        return latitude != null && longitude != null && GpsFix.validCoordinates(latitude, longitude);
    }

    public void setGpsFix(@Nullable GpsFix fix) {
        if (fix == null) return;
        latitude = fix.latitude;
        longitude = fix.longitude;
        accuracyMeters = fix.accuracyMeters;
        locationCapturedAt = fix.capturedAt;
    }

    public long createdAt;
    public long updatedAt;

    public ParkingSpot() {}

    public static ParkingSpot create(String placeName, String floor, String zone,
                                     String columnLabel, String note, long now) {
        ParkingSpot item = new ParkingSpot();
        item.placeName = placeName.trim();
        item.floor = floor.trim();
        item.zone = zone.trim();
        item.columnLabel = columnLabel.trim();
        item.note = note.trim();
        item.active = true;
        item.createdAt = now;
        item.updatedAt = now;
        return item;
    }
}
