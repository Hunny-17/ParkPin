package com.tranquochuy.parkpin.photos;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageDecoder;
import android.graphics.Matrix;
import androidx.exifinterface.media.ExifInterface;
import android.net.Uri;
import android.os.Build;
import androidx.annotation.Nullable;
import androidx.annotation.WorkerThread;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Set;
import java.util.UUID;

/** Private sampled JPEGs; all I/O/decoding runs on a background executor. */
public final class PhotoStorage {
    private PhotoStorage() {}
    private static final int EDGE = 1600;
    private static final long MAX_SOURCE_BYTES = 20L * 1024 * 1024;
    private static File directory(Context context) { return new File(context.getFilesDir(), "parking_photos"); }

    @Nullable public static File file(Context context, @Nullable String path) {
        if (path == null || !path.matches("[0-9a-fA-F-]{36}\\.jpg")) return null;
        return new File(directory(context), path);
    }

    @WorkerThread public static String importPhoto(Context context, Uri uri) throws IOException {
        File dir=directory(context);
        if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("Không tạo được thư mục ảnh");
        String name=UUID.randomUUID()+".jpg";
        File source=File.createTempFile("source-", ".tmp", dir);
        File staged=new File(dir,name+".tmp");
        File target=new File(dir,name);
        Bitmap image=null;
        try {
            try(InputStream in=context.getContentResolver().openInputStream(uri);
                FileOutputStream out=new FileOutputStream(source)) {
                if(in==null) throw new IOException("Không đọc được ảnh");
                byte[] buffer=new byte[16384];long total=0;int n;
                while((n=in.read(buffer))!=-1){
                    total+=n;if(total>MAX_SOURCE_BYTES)throw new IOException("Ảnh vượt quá 20 MB");
                    out.write(buffer,0,n);
                }
            }
            image=decode(source,EDGE);
            if(image==null)throw new IOException("Ảnh không hợp lệ hoặc không được hỗ trợ");
            try(FileOutputStream out=new FileOutputStream(staged)){
                if(!image.compress(Bitmap.CompressFormat.JPEG,90,out))throw new IOException("Không ghi được ảnh");
            }
            if(!staged.renameTo(target))throw new IOException("Không hoàn tất lưu ảnh");
            return name;
        } catch(RuntimeException e){ throw new IOException("Không thể đọc ảnh đã chọn",e); }
        finally {
            if(image!=null)image.recycle();
            source.delete();staged.delete();
        }
    }

    @WorkerThread @Nullable public static Bitmap read(Context context, @Nullable String path, int edge) {
        File photo=file(context,path);
        if(photo==null||!photo.isFile())return null;
        try{return decode(photo,Math.min(EDGE,Math.max(1,edge)));}
        catch(IOException|RuntimeException e){return null;}
    }

    private static Bitmap decode(File source,int edge) throws IOException {
        if(Build.VERSION.SDK_INT>=28){
            return ImageDecoder.decodeBitmap(ImageDecoder.createSource(source),(decoder,info,s)->{
                int w=info.getSize().getWidth(),h=info.getSize().getHeight();
                if(w<=0||h<=0||w>50000||h>50000)throw new IllegalArgumentException("Invalid image dimensions");
                float scale=Math.min(1f,(float)edge/Math.max(w,h));
                decoder.setTargetSize(Math.max(1,Math.round(w*scale)),Math.max(1,Math.round(h*scale)));
                decoder.setAllocator(ImageDecoder.ALLOCATOR_SOFTWARE);
            });
        }
        BitmapFactory.Options bounds=new BitmapFactory.Options();bounds.inJustDecodeBounds=true;
        BitmapFactory.decodeFile(source.getPath(),bounds);
        if(bounds.outWidth<=0||bounds.outHeight<=0||bounds.outWidth>50000||bounds.outHeight>50000)throw new IOException("Invalid image");
        BitmapFactory.Options options=new BitmapFactory.Options();
        options.inSampleSize=1;
        while(Math.max(bounds.outWidth,bounds.outHeight)/options.inSampleSize>edge)options.inSampleSize*=2;
        Bitmap image=BitmapFactory.decodeFile(source.getPath(),options);
        if(image==null)throw new IOException("Invalid image");
        int orientation=ExifInterface.ORIENTATION_NORMAL;
        try {
            ExifInterface exif=new ExifInterface(source.getPath());
            orientation=exif.getAttributeInt(ExifInterface.TAG_ORIENTATION,ExifInterface.ORIENTATION_NORMAL);
        } catch(IOException ignored) { /* Older ExifInterface does not recognize every decodable image format. */ }
        Matrix matrix=new Matrix();
        switch(orientation){
            case ExifInterface.ORIENTATION_FLIP_HORIZONTAL: matrix.setScale(-1,1);break;
            case ExifInterface.ORIENTATION_ROTATE_180: matrix.setRotate(180);break;
            case ExifInterface.ORIENTATION_FLIP_VERTICAL: matrix.setScale(1,-1);break;
            case ExifInterface.ORIENTATION_TRANSPOSE: matrix.setRotate(90);matrix.postScale(-1,1);break;
            case ExifInterface.ORIENTATION_ROTATE_90: matrix.setRotate(90);break;
            case ExifInterface.ORIENTATION_TRANSVERSE: matrix.setRotate(270);matrix.postScale(-1,1);break;
            case ExifInterface.ORIENTATION_ROTATE_270: matrix.setRotate(270);break;
        }
        if(matrix.isIdentity())return image;
        Bitmap rotated=Bitmap.createBitmap(image,0,0,image.getWidth(),image.getHeight(),matrix,true);
        if(rotated!=image)image.recycle();return rotated;
    }

    @WorkerThread public static boolean delete(Context context,@Nullable String path){
        File photo=file(context,path);return photo!=null&&photo.delete();
    }

    /** Recent uncommitted drafts may be in use by a form or import. */
    @WorkerThread public static void prune(Context context,Set<String> referenced,long olderThan){
        File[] files=directory(context).listFiles();if(files==null)return;
        for(File f:files)if(f.isFile()&&f.lastModified()<olderThan&&!referenced.contains(f.getName())
                &&(file(context,f.getName())!=null||f.getName().endsWith(".tmp")))f.delete();
    }
}
