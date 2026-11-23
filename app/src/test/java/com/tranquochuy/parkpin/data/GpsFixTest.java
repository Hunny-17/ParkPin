package com.tranquochuy.parkpin.data;

import com.tranquochuy.parkpin.navigation.MapsNavigation;
import org.junit.Test;
import static org.junit.Assert.*;

public class GpsFixTest {
    @Test public void acceptsValidCoordinatesIncludingZero() {
        assertTrue(GpsFix.validCoordinates(0, 0));
        assertTrue(GpsFix.validCoordinates(-90, 180));
        assertFalse(GpsFix.validCoordinates(91, 0));
        assertFalse(GpsFix.validCoordinates(0, -181));
        assertFalse(GpsFix.validCoordinates(Double.NaN, 0));
        assertFalse(GpsFix.validCoordinates(Double.POSITIVE_INFINITY, 0));
    }

    @Test public void assignsOptionalFixWithoutChangingManualData() {
        ParkingSpot spot = ParkingSpot.create("Parking", "B2", "A", "12", "note", 100);
        assertFalse(spot.hasCoordinates());
        spot.setGpsFix(null);
        assertFalse(spot.hasCoordinates());
        spot.setGpsFix(new GpsFix(10.1234567, 106.9876543, 8f, 123));
        assertTrue(spot.hasCoordinates());
        assertEquals(10.1234567, spot.latitude, 0.0000001);
        assertEquals(106.9876543, spot.longitude, 0.0000001);
        assertEquals("Parking", spot.placeName);
    }

    @Test public void navigationUriUsesLocaleIndependentDecimalPoint() {
        assertEquals("google.navigation:q=10.1234567,106.9876543",
                MapsNavigation.navigationUriText(10.1234567, 106.9876543));
        assertEquals("geo:0,0?q=-1.0000000,0.0000000",
                MapsNavigation.fallbackUriText(-1, 0));
    }
}
