package com.tranquochuy.parkpin.data;

import android.content.Context;
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
}
