package com.tranquochuy.parkpin.data;

import org.junit.Test;
import static org.junit.Assert.*;

public class ParkingSpotTest {
    @Test public void createNormalizesManualInput() {
        ParkingSpot spot = ParkingSpot.create("  Trung tâm  ", " B2 ", " A ", " 12 ", "  Gần thang máy  ", 120);
        assertEquals("Trung tâm", spot.placeName);
        assertEquals("B2", spot.floor);
        assertEquals("A", spot.zone);
        assertEquals("12", spot.columnLabel);
        assertEquals("Gần thang máy", spot.note);
        assertTrue(spot.active);
        assertEquals(120, spot.createdAt);
        assertEquals(120, spot.updatedAt);
    }
}
