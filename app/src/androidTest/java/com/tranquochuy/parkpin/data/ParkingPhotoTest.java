package com.tranquochuy.parkpin.data;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import androidx.room.Room;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.InvocationTargetException;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class ParkingPhotoTest {
    private final Context context = ApplicationProvider.getApplicationContext();

    @Test public void clearingOffscreenPhotoReleasesBitmapAndRejectsLateDecode() throws Exception {
        java.lang.reflect.Method clear;
        try {clear=Class.forName("com.tranquochuy.parkpin.photos.PhotoViews").getMethod("clear",android.widget.ImageView.class);}
        catch(ReflectiveOperationException e){throw new AssertionError("Offscreen photo cancellation/release is missing",e);}
        File dir=new File(context.getFilesDir(),"parking_photos");dir.mkdirs();
        File valid=new File(dir,"00000000-0000-0000-0000-000000000001.jpg");
        Bitmap fixture=Bitmap.createBitmap(640,480,Bitmap.Config.ARGB_8888);
        try(FileOutputStream out=new FileOutputStream(valid)){fixture.compress(Bitmap.CompressFormat.JPEG,90,out);}
        fixture.recycle();
        android.widget.ImageView[] image=new android.widget.ImageView[1];
        android.widget.TextView[] label=new android.widget.TextView[1];
        androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().runOnMainSync(()->{
            image[0]=new android.widget.ImageView(context);label[0]=new android.widget.TextView(context);
            image[0].setImageBitmap(Bitmap.createBitmap(8,8,Bitmap.Config.ARGB_8888));
            try {clear.invoke(null,image[0]);}catch(Exception e){throw new AssertionError(e);}
            assertNull(image[0].getDrawable());
            com.tranquochuy.parkpin.photos.PhotoViews.bind(image[0],label[0],"00000000-0000-0000-0000-000000000001.jpg","QA photo");
        });
        Thread.sleep(600);
        androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().runOnMainSync(()->{
            assertNotNull("Positive control must decode a real JPEG",image[0].getDrawable());
            try {clear.invoke(null,image[0]);}catch(Exception e){throw new AssertionError(e);}
            assertNull(image[0].getDrawable());
            com.tranquochuy.parkpin.photos.PhotoViews.bind(image[0],label[0],"00000000-0000-0000-0000-000000000001.jpg","QA photo");
            try {clear.invoke(null,image[0]);}catch(Exception e){throw new AssertionError(e);}
        });
        Thread.sleep(400);
        androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().runOnMainSync(()->assertNull(image[0].getDrawable()));
        valid.delete();
    }

    // Reflection lets the RED tests execute against the unmodified G3 binary.
    private Object storage(String name, Class<?>[] types, Object... args) throws Exception {
        Class<?> cls;
        try { cls = Class.forName("com.tranquochuy.parkpin.photos.PhotoStorage"); }
        catch (ClassNotFoundException e) { throw new AssertionError("G4 PhotoStorage is missing", e); }
        try { return cls.getMethod(name, types).invoke(null, args); }
        catch (InvocationTargetException e) {
            if (e.getCause() instanceof Exception) throw (Exception)e.getCause();
            throw e;
        }
    }

    @Test public void importedPhotoIsBoundedAndSurvivesSourceDeletion() throws Exception {
        File source = new File(context.getCacheDir(), "g4-source.png");
        Bitmap original = Bitmap.createBitmap(3200, 1600, Bitmap.Config.ARGB_8888);
        original.eraseColor(0xff087f69);
        try (FileOutputStream out = new FileOutputStream(source)) { original.compress(Bitmap.CompressFormat.PNG, 100, out); }
        original.recycle();
        String path = (String)storage("importPhoto", new Class[]{Context.class, Uri.class}, context, Uri.fromFile(source));
        assertTrue(source.delete());
        File saved = new File(context.getFilesDir(), "parking_photos/" + path);
        assertTrue(saved.isFile());
        Bitmap image = BitmapFactory.decodeFile(saved.getPath());
        assertNotNull(image);assertTrue(Math.max(image.getWidth(),image.getHeight())<=1600);
        assertEquals(2.0, (double)image.getWidth()/image.getHeight(), .01);
        image.recycle();
        assertEquals(true,storage("delete",new Class[]{Context.class,String.class},context,path));
        assertFalse(saved.exists());
    }

    @Test public void corruptSourceFailsWithoutLeavingOwnedFiles() throws Exception {
        File source = new File(context.getCacheDir(), "g4-bad.txt");
        try(FileOutputStream out = new FileOutputStream(source)){out.write(new byte[]{1,2,3});}
        File dir = new File(context.getFilesDir(), "parking_photos");
        int before=dir.list()==null?0:dir.list().length;
        try {
            storage("importPhoto",new Class[]{Context.class,Uri.class},context,Uri.fromFile(source));
            fail("Corrupt image must be rejected");
        } catch (java.io.IOException expected) { }
        assertEquals(before,dir.list()==null?0:dir.list().length);
        source.delete();
    }

    @Test public void oversizedSourceIsRejectedAndTemporaryFilesAreCleaned() throws Exception {
        File source=new File(context.getCacheDir(),"g4-oversized.bin");
        try(java.io.RandomAccessFile out=new java.io.RandomAccessFile(source,"rw")){out.setLength(20L*1024*1024+1);}
        File dir=new File(context.getFilesDir(),"parking_photos");
        int before=dir.list()==null?0:dir.list().length;
        try {storage("importPhoto",new Class[]{Context.class,Uri.class},context,Uri.fromFile(source));fail("Oversized source accepted");}
        catch(java.io.IOException expected){assertTrue(expected.getMessage().contains("20 MB"));}
        finally {source.delete();}
        assertEquals(before,dir.list()==null?0:dir.list().length);
    }

    @Test public void jpegExifOrientationIsAppliedBeforeSaving() throws Exception {
        File source=new File(context.getCacheDir(),"g4-rotated.jpg");
        Bitmap fixture=Bitmap.createBitmap(320,160,Bitmap.Config.ARGB_8888);
        try(FileOutputStream out=new FileOutputStream(source)){fixture.compress(Bitmap.CompressFormat.JPEG,90,out);}
        fixture.recycle();
        androidx.exifinterface.media.ExifInterface exif=new androidx.exifinterface.media.ExifInterface(source.getPath());
        exif.setAttribute(androidx.exifinterface.media.ExifInterface.TAG_ORIENTATION,"6");exif.saveAttributes();
        String path=(String)storage("importPhoto",new Class[]{Context.class,Uri.class},context,Uri.fromFile(source));
        Bitmap saved=BitmapFactory.decodeFile(new File(context.getFilesDir(),"parking_photos/"+path).getPath());
        assertEquals(160,saved.getWidth());assertEquals(320,saved.getHeight());saved.recycle();
        storage("delete",new Class[]{Context.class,String.class},context,path);source.delete();
    }

    @Test public void pruningOldDraftsNeverDeletesReferencedPhotos() throws Exception {
        File dir=new File(context.getFilesDir(),"parking_photos");dir.mkdirs();
        String keep="00000000-0000-0000-0000-000000000002.jpg";
        String stale="00000000-0000-0000-0000-000000000003.jpg";
        File committed=new File(dir,keep),draft=new File(dir,stale);
        try(FileOutputStream out=new FileOutputStream(committed)){out.write(1);}
        try(FileOutputStream out=new FileOutputStream(draft)){out.write(1);}
        committed.setLastModified(1000);draft.setLastModified(1000);
        storage("prune",new Class[]{Context.class,java.util.Set.class,long.class},context,java.util.Collections.singleton(keep),2000L);
        assertTrue(committed.exists());assertFalse(draft.exists());committed.delete();
    }

    @Test public void photoDeletionCannotEscapePrivatePhotoDirectory() throws Exception {
        File outside = new File(context.getFilesDir(), "g4-outside.jpg");
        try(FileOutputStream out=new FileOutputStream(outside)){out.write(7);}
        assertEquals(false,storage("delete",new Class[]{Context.class,String.class},context,"../g4-outside.jpg"));
        assertEquals(false,storage("delete",new Class[]{Context.class,String.class},context,outside.getAbsolutePath()));
        assertTrue(outside.exists());outside.delete();
    }

    @Test public void roomPhotoPersistsAndManualGpsUpdatesPreserveIt() throws Exception {
        String name="g4-photo-persistence-test.db";context.deleteDatabase(name);
        ParkPinDatabase db=Room.databaseBuilder(context,ParkPinDatabase.class,name).allowMainThreadQueries().build();
        try {
            ParkingSpot spot=ParkingSpot.create("Photo A","B2","A","12","Note",100);
            java.lang.reflect.Field field;
            try {field=ParkingSpot.class.getField("photoPath");}
            catch(NoSuchFieldException e){throw new AssertionError("Room photoPath column is missing",e);}
            field.set(spot,"00000000-0000-0000-0000-000000000001.jpg");
            spot.setGpsFix(new GpsFix(10,106,5f,90));
            long id=db.parkingDao().saveActive(spot);
            db.parkingDao().updateDetails(id,"Manual edit","B3","B","22","Edited",200);
            db.parkingDao().updateDetailsAndGps(id,"GPS edit","B3","B","22","Edited",21,105,4f,250,300);
            db.close();db=Room.databaseBuilder(context,ParkPinDatabase.class,name).allowMainThreadQueries().build();
            ParkingSpot saved=db.parkingDao().getById(id);
            assertEquals(field.get(spot),field.get(saved));assertEquals(21,saved.latitude,.00001);
            assertEquals(100,saved.createdAt);assertTrue(saved.active);
        } finally {db.close();context.deleteDatabase(name);}
    }

    @Test public void migration2To3RetainsGpsAndAddsNullablePhoto() {
        String name="g4-upgrade-test.db";context.deleteDatabase(name);
        SQLiteDatabase old=context.openOrCreateDatabase(name,Context.MODE_PRIVATE,null);
        old.execSQL("CREATE TABLE parking_spots (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,placeName TEXT NOT NULL,floor TEXT NOT NULL,zone TEXT NOT NULL,columnLabel TEXT NOT NULL,note TEXT NOT NULL,active INTEGER NOT NULL,createdAt INTEGER NOT NULL,updatedAt INTEGER NOT NULL,latitude REAL,longitude REAL,accuracyMeters REAL,locationCapturedAt INTEGER)");
        old.execSQL("CREATE INDEX index_parking_spots_active ON parking_spots(active)");
        old.execSQL("INSERT INTO parking_spots VALUES(42,'G3 preserved','B2','A','12','Keep',1,100,200,10.7,106.7,5,90)");
        old.setVersion(2);old.close();
        // Resolve migration reflectively so the RED test reaches the real old DB.
        try {
            androidx.room.migration.Migration migration;
            try {migration=(androidx.room.migration.Migration)ParkPinDatabase.class.getField("MIGRATION_2_3").get(null);}
            catch(ReflectiveOperationException e){throw new AssertionError("Non-destructive migration 2->3 is missing",e);}
            ParkPinDatabase db=Room.databaseBuilder(context,ParkPinDatabase.class,name).addMigrations(migration).allowMainThreadQueries().build();
            try {
                ParkingSpot saved=db.parkingDao().getActive();
                assertEquals(42,saved.id);assertEquals("G3 preserved",saved.placeName);assertEquals("Keep",saved.note);
                assertEquals(10.7,saved.latitude,.000001);assertEquals(106.7,saved.longitude,.000001);
                assertEquals(100,saved.createdAt);assertEquals(200,saved.updatedAt);
                assertNull(ParkingSpot.class.getField("photoPath").get(saved));
                assertEquals(3,db.getOpenHelper().getReadableDatabase().getVersion());
            } finally {db.close();}
        } catch(ReflectiveOperationException e){throw new AssertionError(e);}
        finally {context.deleteDatabase(name);}
    }
}
