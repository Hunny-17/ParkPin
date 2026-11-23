package com.tranquochuy.parkpin.data;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.HashSet;
import java.util.Objects;
import com.tranquochuy.parkpin.photos.PhotoStorage;

/** Async gateway: never access Room on the main thread. No network/back-end dependencies. */
public final class ParkingRepository {
    public interface Callback<T> {
        void onResult(@Nullable T value);
        default void onError(@NonNull Exception error) {}
    }

    private static volatile ParkingRepository instance;
    private final ParkingDao dao;
    private final Context app;
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private final Handler main = new Handler(Looper.getMainLooper());

    private ParkingRepository(Context context) {
        app = context.getApplicationContext();
        dao = ParkPinDatabase.get(context).parkingDao();
        run(() -> {
            PhotoStorage.prune(app,new HashSet<>(dao.photoPaths()),
                    System.currentTimeMillis()-24L*60*60*1000);
            return null;
        },null);
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

    private interface Task<T> { T execute() throws Exception; }

    public void saveActive(String name, String floor, String zone, String columnLabel,
                           String note, Callback<Long> callback) {
        saveActive(name, floor, zone, columnLabel, note, null, callback);
    }

    public void saveActive(String name, String floor, String zone, String columnLabel,
                           String note, @Nullable GpsFix fix, Callback<Long> callback) {
        saveActive(name,floor,zone,columnLabel,note,fix,null,callback);
    }

    public void saveActive(String name, String floor, String zone, String columnLabel,
                           String note, @Nullable GpsFix fix, @Nullable String photoPath,
                           Callback<Long> callback) {
        if (name == null || name.trim().isEmpty()) {
            if (callback != null) main.post(() ->
                callback.onError(new IllegalArgumentException("Tên bãi đỗ không được trống")));
            return;
        }
        run(() -> {
            validatePhoto(photoPath);
            ParkingSpot item = ParkingSpot.create(name, safe(floor), safe(zone),
                    safe(columnLabel), safe(note), System.currentTimeMillis());
            item.setGpsFix(fix);
            item.photoPath=photoPath;
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
        updateDetails(id,name,floor,zone,columnLabel,note,fix,false,null,callback);
    }

    public void updateDetails(long id, String name, String floor, String zone,
                              String columnLabel, String note, @Nullable GpsFix fix,
                              boolean changePhoto,@Nullable String photoPath,
                              Callback<Boolean> callback) {
        if (name == null || name.trim().isEmpty()) {
            if (callback != null) main.post(() ->
                callback.onError(new IllegalArgumentException("Tên bãi đỗ không được trống")));
            return;
        }
        run(() -> {
            ParkingSpot old=dao.getById(id);
            if(old==null)return false;
            if(changePhoto)validatePhoto(photoPath);
            long now = System.currentTimeMillis();
            boolean updated=dao.updateWithPhoto(id,name.trim(),safe(floor),safe(zone),
                    safe(columnLabel),safe(note),fix,changePhoto,photoPath,now);
            if(updated&&changePhoto&&!Objects.equals(old.photoPath,photoPath))cleanupPhoto(old.photoPath);
            return updated;
        }, callback);
    }

    public void activate(long id, Callback<Boolean> callback) {
        run(() -> dao.setActive(id, System.currentTimeMillis()), callback);
    }

    public void delete(long id, Callback<Boolean> callback) {
        run(() -> {
            ParkingSpot old=dao.getById(id);
            boolean deleted=dao.deleteById(id)==1;
            if(deleted&&old!=null)cleanupPhoto(old.photoPath);
            return deleted;
        }, callback);
    }

    /** Also safe when a form is destroyed while its save callback is pending. */
    public void discardPhoto(@Nullable String path) {
        run(() -> {cleanupPhoto(path);return null;},null);
    }

    private void cleanupPhoto(@Nullable String path) {
        if(path!=null&&dao.photoReferences(path)==0)PhotoStorage.delete(app,path);
    }

    private void validatePhoto(@Nullable String path) throws java.io.IOException {
        if(path!=null&&(PhotoStorage.file(app,path)==null||!PhotoStorage.file(app,path).isFile()))
            throw new java.io.IOException("Ảnh đã chọn không còn khả dụng. Hãy chọn lại ảnh.");
    }

    private static String safe(String value) {
        return value == null ? "" : value.trim();
    }
}
