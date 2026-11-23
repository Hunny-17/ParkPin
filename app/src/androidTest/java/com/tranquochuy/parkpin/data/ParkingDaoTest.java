package com.tranquochuy.parkpin.data;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import androidx.room.Room;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.util.List;
import static org.junit.Assert.*;

/** Runs on emulator with connectedAndroidTest; CI assembleDebugAndroidTest only compiles it. */
@RunWith(AndroidJUnit4.class)
public class ParkingDaoTest {
    private ParkPinDatabase db;
    private ParkingDao dao;

    @Before public void setup() {
        Context context = ApplicationProvider.getApplicationContext();
        db = Room.inMemoryDatabaseBuilder(context, ParkPinDatabase.class)
                .allowMainThreadQueries().build(); // TEST-ONLY
        dao = db.parkingDao();
    }

    @After public void teardown() {
        if (db != null) db.close();
    }

    private static ParkingSpot spot(String name, long when) {
        return ParkingSpot.create(name, "B2", "A", "12", "Gần thang máy", when);
    }

    @Test public void savesOneActiveAndArchivesOlder() {
        long first = dao.saveActive(spot("First", 100));
        long second = dao.saveActive(spot("Second", 200));
        assertEquals(second, dao.getActive().id);
        assertFalse(dao.getById(first).active);
        assertEquals(1, dao.getHistory().size());
        assertEquals("First", dao.getHistory().get(0).placeName);
    }

    @Test public void readUpdateAndDelete() {
        long id = dao.saveActive(spot("Original", 100));
        assertEquals("Original", dao.getById(id).placeName);
        assertEquals(1, dao.updateDetails(id, "Updated", "B3", "C", "22", "New note", 200));
        assertEquals("Updated", dao.getById(id).placeName);
        assertEquals("B3", dao.getById(id).floor);
        assertEquals("New note", dao.getById(id).note);
        assertEquals(1, dao.deleteById(id));
        assertNull(dao.getActive());
        assertTrue(dao.getAll().isEmpty());
        assertEquals(0, dao.deleteById(id));
    }

    @Test public void reactivationIsAtomicAndIdempotent() {
        long first = dao.saveActive(spot("First", 100));
        long second = dao.saveActive(spot("Second", 200));
        assertTrue(dao.setActive(first, 300));
        assertEquals(first, dao.getActive().id);
        assertFalse(dao.getById(second).active);
        assertTrue(dao.setActive(first, 400));
        assertEquals(1, dao.getAll().stream().filter(x -> x.active).count());
        assertFalse(dao.setActive(99999L, 500));
        assertEquals(first, dao.getActive().id);
    }

    @Test public void emptyDatabaseAndHistoryOrder() {
        assertNull(dao.getActive());
        assertTrue(dao.getHistory().isEmpty());
        dao.saveActive(spot("Older", 100));
        dao.saveActive(spot("Recent", 300));
        dao.saveActive(spot("Middle", 200));
        List<ParkingSpot> history = dao.getHistory();
        assertEquals(2, history.size());
        assertEquals("Older", history.get(1).placeName);
        assertEquals("Recent", history.get(0).placeName);
    }

    @Test public void persistsAfterDatabaseCloseAndReopen() {
        Context context = ApplicationProvider.getApplicationContext();
        String dbName = "parkpin-instrumented-persistence.db";
        context.deleteDatabase(dbName);
        ParkPinDatabase disk = Room.databaseBuilder(context, ParkPinDatabase.class, dbName)
                .allowMainThreadQueries().build(); // TEST-ONLY
        try {
            long id = disk.parkingDao().saveActive(spot("Persisted", 100));
            disk.close();
            disk = Room.databaseBuilder(context, ParkPinDatabase.class, dbName)
                    .allowMainThreadQueries().build();
            assertEquals("Persisted", disk.parkingDao().getById(id).placeName);
            assertEquals(id, disk.parkingDao().getActive().id);
        } finally {
            disk.close();
            context.deleteDatabase(dbName);
        }
    }
    @Test public void gpsCoordinatesPersistAndManualUpdatePreservesThem() {
        ParkingSpot entry = spot("Has GPS", 100);
        entry.setGpsFix(new GpsFix(10.1234567, 106.9876543, 12f, 150));
        long id = dao.saveActive(entry);
        ParkingSpot fromDb = dao.getById(id);
        assertTrue(fromDb.hasCoordinates());
        assertEquals(10.1234567, fromDb.latitude, 0.0000001);
        assertEquals(106.9876543, fromDb.longitude, 0.0000001);
        assertEquals(12f, fromDb.accuracyMeters, 0.001f);
        dao.updateDetails(id, "Edited manually", "B1", "Z", "03", "Notes", 200);
        assertEquals(10.1234567, dao.getById(id).latitude, 0.0000001);
        dao.updateDetailsAndGps(id, "GPS updated", "B1", "Z", "03", "Notes",
                11, 107, 4f, 300, 301);
        assertEquals(11, dao.getById(id).latitude, 0.0000001);
        assertEquals(107, dao.getById(id).longitude, 0.0000001);
        assertEquals(300L, dao.getById(id).locationCapturedAt.longValue());
    }

    /** Upgrades an on-disk v1 database created from the G2 table schema, without deleting rows. */
    @Test public void migration1To2PreservesExistingParkingRecords() {
        Context context = ApplicationProvider.getApplicationContext();
        String name = "parkpin-g3-migration-test.db";
        context.deleteDatabase(name);
        SQLiteDatabase legacy = context.openOrCreateDatabase(name, Context.MODE_PRIVATE, null);
        try {
            legacy.execSQL("CREATE TABLE IF NOT EXISTS parking_spots (" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, " +
                    "placeName TEXT NOT NULL, floor TEXT NOT NULL, zone TEXT NOT NULL, " +
                    "columnLabel TEXT NOT NULL, note TEXT NOT NULL, active INTEGER NOT NULL, " +
                    "createdAt INTEGER NOT NULL, updatedAt INTEGER NOT NULL)");
            legacy.execSQL("CREATE INDEX IF NOT EXISTS index_parking_spots_active ON parking_spots(active)");
            legacy.execSQL("INSERT INTO parking_spots (placeName,floor,zone,columnLabel,note,active,createdAt,updatedAt) " +
                    "VALUES ('Legacy G2','B2','A','12','Do not lose',1,100,100)");
            legacy.setVersion(1);
        } finally {
            legacy.close();
        }
        ParkPinDatabase migrated = Room.databaseBuilder(context, ParkPinDatabase.class, name)
                .addMigrations(ParkPinDatabase.MIGRATION_1_2)
                .allowMainThreadQueries().build(); // TEST-ONLY
        try {
            ParkingSpot active = migrated.parkingDao().getActive();
            assertNotNull(active);
            assertEquals("Legacy G2", active.placeName);
            assertEquals("Do not lose", active.note);
            assertNull(active.latitude);
            assertNull(active.longitude);
            assertEquals(1, migrated.parkingDao().getAll().size());
        } finally {
            migrated.close();
            context.deleteDatabase(name);
        }
    }

}
