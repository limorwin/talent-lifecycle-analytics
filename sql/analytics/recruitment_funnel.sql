WITH stage_counts AS (
    SELECT
        se.stage,
        COUNT(DISTINCT se.application_id) AS application_count
    FROM stage_events AS se
    JOIN applications AS a
        ON se.application_id = a.application_id
    JOIN jobs AS j
        ON a.job_id = j.job_id
    WHERE j.department IN ({department_placeholders})
    AND a.source IN ({source_placeholders})
    AND date(a.applied_at) BETWEEN ? AND ?
        GROUP BY se.stage
),
ordered_stages AS (
    SELECT
        stage,
        application_count,
        LAG(application_count) OVER (
            ORDER BY CASE stage
                WHEN 'Applied' THEN 1
                WHEN 'Screening' THEN 2
                WHEN 'Interview' THEN 3
                WHEN 'Offer' THEN 4
                WHEN 'Hired' THEN 5
            END
        ) AS previous_count
    FROM stage_counts
)
SELECT
    stage,
    application_count,
    ROUND(
        100.0 * application_count / NULLIF(previous_count, 0),
        1
    ) AS conversion_rate
FROM ordered_stages
ORDER BY CASE stage
    WHEN 'Applied' THEN 1
    WHEN 'Screening' THEN 2
    WHEN 'Interview' THEN 3
    WHEN 'Offer' THEN 4
    WHEN 'Hired' THEN 5
END;