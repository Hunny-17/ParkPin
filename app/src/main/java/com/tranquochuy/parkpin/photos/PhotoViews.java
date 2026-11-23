package com.tranquochuy.parkpin.photos;

import android.content.Context;
import android.graphics.Bitmap;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.Nullable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.Objects;

/** Bounded decoding off the UI thread; request tokens reject stale callbacks. */
public final class PhotoViews {
    private PhotoViews(){}
    private static final ExecutorService IO=Executors.newFixedThreadPool(2);
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final class Request {
        final String path;
        volatile boolean cancelled;
        Request(String path){this.path=path;}
    }
    public static void bind(ImageView image,TextView status,@Nullable String path,String description){
        bind(image,status,path,description,1000);
    }
    public static void bind(ImageView image,TextView status,@Nullable String path,String description,int edge){
        if(image.getTag() instanceof Request&&Objects.equals(((Request)image.getTag()).path,path))return;
        Request token=new Request(path);
        clear(image);image.setTag(token);
        image.setVisibility(path==null?View.GONE:View.VISIBLE);
        image.setContentDescription(description);
        if(path==null){status.setText("Chưa có ảnh");status.setVisibility(View.VISIBLE);return;}
        status.setText("Đang tải ảnh...");status.setVisibility(View.VISIBLE);
        Context app=image.getContext().getApplicationContext();
        IO.execute(()->{
            if(token.cancelled)return;
            Bitmap bitmap=PhotoStorage.read(app,path,edge);
            MAIN.post(()->{
                if(token.cancelled||image.getTag()!=token){if(bitmap!=null)bitmap.recycle();return;}
                if(bitmap==null){status.setText("Không tải được ảnh. Bạn có thể chọn lại khi chỉnh sửa.");}
                else {image.setImageBitmap(bitmap);image.setVisibility(View.VISIBLE);status.setVisibility(View.GONE);}
            });
        });
    }
    /** Keep layout geometry stable while releasing offscreen bitmaps and work. */
    public static void clear(ImageView image){
        if(image.getTag() instanceof Request)((Request)image.getTag()).cancelled=true;
        image.setTag(null);image.setImageDrawable(null);
    }
}
