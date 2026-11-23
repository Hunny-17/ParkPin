package com.tranquochuy.parkpin.photos;

import android.app.Application;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import androidx.annotation.Nullable;
import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.SavedStateHandle;
import com.tranquochuy.parkpin.data.ParkingRepository;
import java.util.Objects;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Photo draft survives rotation; Room changes only when the user saves. */
public final class PhotoDraftViewModel extends AndroidViewModel {
    public static final class State {
        @Nullable public final String path,error;
        public final boolean changed,busy,saving,saved;
        State(String p,String e,boolean c,boolean b,boolean s,boolean done){
            path=p;error=e;changed=c;busy=b;saving=s;saved=done;
        }
    }
    private final SavedStateHandle savedState;
    private final MutableLiveData<State> state=new MutableLiveData<>();
    private final ExecutorService io=Executors.newSingleThreadExecutor();
    private final Handler main=new Handler(Looper.getMainLooper());
    private String path,original,error;
    private boolean changed,busy,saving,saved,closed,initialized;

    public PhotoDraftViewModel(Application app,SavedStateHandle handle){
        super(app);savedState=handle;
        path=handle.get("photo_path");original=handle.get("photo_original");
        changed=Boolean.TRUE.equals(handle.get("photo_changed"));
        initialized=Boolean.TRUE.equals(handle.get("photo_initialized"));
        publish();
    }
    public LiveData<State> state(){return state;}
    public State current(){return state.getValue();}
    public boolean initialized(){return initialized;}
    public void initialize(@Nullable String existing){
        if(initialized)return;
        initialized=true;path=original=existing;publish();
    }
    public void select(Uri uri){
        if(busy||saving||closed)return;
        busy=true;error=null;publish();
        io.execute(()->{
            String result=null,message=null;
            try {result=PhotoStorage.importPhoto(getApplication(),uri);}
            catch(Exception e){message="Không thể đọc ảnh. Hãy chọn ảnh khác (tối đa 20 MB).";}
            String imported=result,failed=message;
            main.post(()->{
                busy=false;
                if(closed){discard(imported);return;}
                if(imported!=null){discardDraft();path=imported;changed=true;initialized=true;}
                error=failed;publish();
            });
        });
    }
    public void remove(){
        if(busy||saving)return;
        discardDraft();path=null;changed=true;initialized=true;error=null;publish();
    }
    public void beginSave(){saving=true;error=null;publish();}
    public void finishSave(){saving=false;publish();}
    public void markSaved(){
        saving=false;original=path;changed=false;saved=true;publish();
    }
    public void consumeSaved(){saved=false;publish();}
    private void publish(){
        savedState.set("photo_path",path);savedState.set("photo_original",original);
        savedState.set("photo_changed",changed);savedState.set("photo_initialized",initialized);
        state.setValue(new State(path,error,changed,busy,saving,saved));
    }
    private void discardDraft(){if(changed&&!Objects.equals(path,original))discard(path);}
    private void discard(String candidate){ParkingRepository.get(getApplication()).discardPhoto(candidate);}
    @Override protected void onCleared(){closed=true;discardDraft();io.shutdown();}
}
