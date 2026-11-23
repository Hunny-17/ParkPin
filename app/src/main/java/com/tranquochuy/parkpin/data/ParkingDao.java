package com.tranquochuy.parkpin.data;

import androidx.annotation.Nullable;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Transaction;
import java.util.List;

/** All mutating operations are intended to run on the repository's background executor. */
@Dao
public abstract class ParkingDao {
    @Insert
    protected abstract long insert(ParkingSpot spot);

    @Query("UPDATE parking_spots SET active = 0 WHERE active = 1")
    protected abstract void deactivateAll();

    @Query("UPDATE parking_spots SET active = 1, updatedAt = :now WHERE id = :id")
    protected abstract int activateOne(long id, long now);

    @Transaction
    public long saveActive(ParkingSpot spot) {
        deactivateAll();
        spot.active = true;
        return insert(spot);
    }

    @Transaction
    public boolean setActive(long id, long now) {
        if (getById(id) == null) return false;
        deactivateAll();
        return activateOne(id, now) == 1;
    }

    @Nullable
    @Query("SELECT * FROM parking_spots WHERE active = 1 LIMIT 1")
    public abstract ParkingSpot getActive();

    @Nullable
    @Query("SELECT * FROM parking_spots WHERE id = :id LIMIT 1")
    public abstract ParkingSpot getById(long id);

    @Query("SELECT * FROM parking_spots ORDER BY createdAt DESC, id DESC")
    public abstract List<ParkingSpot> getAll();

    @Query("SELECT * FROM parking_spots WHERE active = 0 ORDER BY createdAt DESC, id DESC")
    public abstract List<ParkingSpot> getHistory();

    @Query("UPDATE parking_spots SET placeName = :name, floor = :floor, zone = :zone, " +
           "columnLabel = :columnLabel, note = :note, updatedAt = :now WHERE id = :id")
    public abstract int updateDetails(long id, String name, String floor, String zone,
                                      String columnLabel, String note, long now);

    /** Replaces GPS only when the user explicitly captured a fresh fix. */
    @Query("UPDATE parking_spots SET placeName=:name, floor=:floor, zone=:zone, " +
           "columnLabel=:columnLabel, note=:note, latitude=:latitude, longitude=:longitude, " +
           "accuracyMeters=:accuracy, locationCapturedAt=:capturedAt, updatedAt=:now WHERE id=:id")
    public abstract int updateDetailsAndGps(long id, String name, String floor, String zone,
            String columnLabel, String note, double latitude, double longitude,
            Float accuracy, long capturedAt, long now);

    @Query("DELETE FROM parking_spots WHERE id = :id")
    public abstract int deleteById(long id);

    @Query("UPDATE parking_spots SET photoPath=:path, updatedAt=:now WHERE id=:id")
    public abstract int updatePhoto(long id, @Nullable String path, long now);

    @Query("SELECT COUNT(*) FROM parking_spots WHERE photoPath=:path")
    public abstract int photoReferences(String path);

    @Query("SELECT photoPath FROM parking_spots WHERE photoPath IS NOT NULL")
    public abstract List<String> photoPaths();

    @Transaction
    public boolean updateWithPhoto(long id, String name, String floor, String zone,
            String column, String note, @Nullable GpsFix fix, boolean changePhoto,
            @Nullable String path, long now) {
        int changed = fix == null ? updateDetails(id,name,floor,zone,column,note,now)
                : updateDetailsAndGps(id,name,floor,zone,column,note,fix.latitude,
                        fix.longitude,fix.accuracyMeters,fix.capturedAt,now);
        if (changed == 1 && changePhoto) updatePhoto(id,path,now);
        return changed == 1;
    }
}
