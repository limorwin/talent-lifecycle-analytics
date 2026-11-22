SELECT
    stage_events.application_id,
    stage_events.stage,
    stage_events.entered_at
FROM stage_events
WHERE application_id = 1001
ORDER BY entered_at