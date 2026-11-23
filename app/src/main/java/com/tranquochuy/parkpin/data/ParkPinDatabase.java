package com.tranquochuy.parkpin.data;

import android.content.Context;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

/** Version 1: offline-only local storage; migrations must be supplied for future schema changes. */
@Database(entities = {ParkingSpot.class}, version = 1, exportSchema = false)
public abstract class ParkPinDatabase extends RoomDatabase {
    private static volatile ParkPinDatabase instance;

    public abstract ParkingDao parkingDao();

    public static ParkPinDatabase get(Context context) {
        if (instance == null) {
            synchronized (ParkPinDatabase.class) {
                if (instance == null) {
                    instance = Room.databaseBuilder(context.getApplicationContext(),
                            ParkPinDatabase.class, "parkpin.db").build();
                }
            }
        }
        return instance;
    }
}
