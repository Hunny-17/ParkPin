package com.tranquochuy.parkpin.data;

import androidx.annotation.NonNull;
import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

/** One saved parking place. GPS/photo fields are intentionally deferred. */
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
