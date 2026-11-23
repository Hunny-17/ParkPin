package com.tranquochuy.parkpin.data;

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.room.migration.Migration;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

/** Version 2: optional GPS columns; all existing G2 records are preserved. */
@Database(entities = {ParkingSpot.class}, version = 2, exportSchema = false)
public abstract class ParkPinDatabase extends RoomDatabase {
    public static final Migration MIGRATION_1_2 = new Migration(1, 2) {
        @Override public void migrate(@NonNull SupportSQLiteDatabase database) {
            database.execSQL("ALTER TABLE parking_spots ADD COLUMN latitude REAL");
            database.execSQL("ALTER TABLE parking_spots ADD COLUMN longitude REAL");
            database.execSQL("ALTER TABLE parking_spots ADD COLUMN accuracyMeters REAL");
            database.execSQL("ALTER TABLE parking_spots ADD COLUMN locationCapturedAt INTEGER");
        }
    };

    private static volatile ParkPinDatabase instance;

    public abstract ParkingDao parkingDao();

    public static ParkPinDatabase get(Context context) {
        if (instance == null) {
            synchronized (ParkPinDatabase.class) {
                if (instance == null) {
                    instance = Room.databaseBuilder(context.getApplicationContext(),
                            ParkPinDatabase.class, "parkpin.db")
                            .addMigrations(MIGRATION_1_2).build();
                }
            }
        }
        return instance;
    }
}
