UPDATE #example
SET
    pick_completed_time_utc = CASE WHEN pick_completed_time_utc < pick_active_time_utc THEN NULL ELSE pick_completed_time_utc END;
