package com.tranquochuy.parkpin.qa.geo;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

/** QA-only geo Intent consumer; renders the received URI, never creates coordinates. */
public final class GeoReceiverActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        TextView result = new TextView(this);
        result.setTextSize(20);
        result.setPadding(32, 64, 32, 32);
        result.setText("ParkPin QA geo receiver\n\n" + getIntent().getDataString());
        setContentView(result);
    }
}
