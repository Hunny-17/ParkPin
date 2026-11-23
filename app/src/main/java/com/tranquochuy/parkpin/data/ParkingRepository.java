package com.tranquochuy.parkpin.data;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Async gateway: never access Room on the main thread. No network/back-end dependencies. */
public final class ParkingRepository {
    public interface Callback<T> {
        void onResult(@Nullable T value);
        default void onError(@NonNull Exception error) {}
    }

    private static volatile ParkingRepository instance;
    private final ParkingDao dao;
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private final Handler main = new Handler(Looper.getMainLooper());

    private ParkingRepository(Context context) {
        dao = ParkPinDatabase.get(context).parkingDao();
    }

    public static ParkingRepository get(Context context) {
        if (instance == null) {
            synchronized (ParkingRepository.class) {
                if (instance == null) instance = new ParkingRepository(context.getApplicationContext());
            }
        }
        return instance;
    }

    private <T> void run(Task<T> task, Callback<T> callback) {
        io.execute(() -> {
            try {
                T result = task.execute();
                if (callback != null) main.post(() -> callback.onResult(result));
            } catch (Exception error) {
                if (callback != null) main.post(() -> callback.onError(error));
            }
        });
    }

    private interface Task<T> { T execute(); }

    public void saveActive(String name, String floor, String zone, String columnLabel,
                           String note, Callback<Long> callback) {
        saveActive(name, floor, zone, columnLabel, note, null, callback);
    }

    public void saveActive(String name, String floor, String zone, String columnLabel,
                           String note, @Nullable GpsFix fix, Callback<Long> callback) {
        if (name == null || name.trim().isEmpty()) {
            if (callback != null) main.post(() ->
                callback.onError(new IllegalArgumentException("Tên bãi đỗ không được trống")));
            return;
        }
        run(() -> {
            ParkingSpot item = ParkingSpot.create(name, safe(floor), safe(zone),
                    safe(columnLabel), safe(note), System.currentTimeMillis());
            item.setGpsFix(fix);
            return dao.saveActive(item);
        }, callback);
    }

    public void getActive(Callback<ParkingSpot> callback) {
        run(dao::getActive, callback);
    }

    public void getById(long id, Callback<ParkingSpot> callback) {
        run(() -> dao.getById(id), callback);
    }

    public void getAll(Callback<List<ParkingSpot>> callback) {
        run(dao::getAll, callback);
    }

    public void getHistory(Callback<List<ParkingSpot>> callback) {
        run(dao::getHistory, callback);
    }

    public void updateDetails(long id, String name, String floor, String zone,
                              String columnLabel, String note, Callback<Boolean> callback) {
        updateDetails(id, name, floor, zone, columnLabel, note, null, callback);
    }

    public void updateDetails(long id, String name, String floor, String zone,
                              String columnLabel, String note, @Nullable GpsFix fix,
                              Callback<Boolean> callback) {
        if (name == null || name.trim().isEmpty()) {
            if (callback != null) main.post(() ->
                callback.onError(new IllegalArgumentException("Tên bãi đỗ không được trống")));
            return;
        }
        run(() -> {
            long now = System.currentTimeMillis();
            return (fix == null
                ? dao.updateDetails(id, name.trim(), safe(floor), safe(zone),
                        safe(columnLabel), safe(note), now)
                : dao.updateDetailsAndGps(id, name.trim(), safe(floor), safe(zone),
                        safe(columnLabel), safe(note), fix.latitude, fix.longitude,
                        fix.accuracyMeters, fix.capturedAt, now)) == 1;
        }, callback);
    }

    public void activate(long id, Callback<Boolean> callback) {
        run(() -> dao.setActive(id, System.currentTimeMillis()), callback);
    }

    public void delete(long id, Callback<Boolean> callback) {
        run(() -> dao.deleteById(id) == 1, callback);
    }

    private static String safe(String value) {
        return value == null ? "" : value.trim();
    }
}
