WITH stage_history AS (
    SELECT
        application_id,
        stage,
        entered_at,
        LAG(entered_at) OVER (
            PARTITION BY application_id
            ORDER BY entered_at
        ) AS previous_date
    FROM stage_events
),
stage_durations AS (
    SELECT
        application_id,
        stage,
        entered_at,
        previous_date,
        julianday(entered_at) - julianday(previous_date)
            AS days_since_previous_stage
    FROM stage_history
)
SELECT
    stage,
    ROUND(AVG(days_since_previous_stage), 2) AS avg_days
FROM stage_durations
GROUP BY stage
ORDER BY avg_days;