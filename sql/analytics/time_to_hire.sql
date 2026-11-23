SELECT
    a.application_id,
    a.job_id,
    a.applied_at,
    se.entered_at AS hired_at,
    ROUND(
        julianday(se.entered_at) - julianday(a.applied_at),
        1
    ) AS time_to_hire_days
FROM applications AS a
JOIN stage_events AS se
    ON a.application_id = se.application_id
JOIN jobs AS j
    ON a.job_id = j.job_id
WHERE a.status = 'Hired'
  AND se.stage = 'Hired'
  AND j.department IN ({department_placeholders})
  AND a.source IN ({source_placeholders})
  AND date(a.applied_at) BETWEEN ? AND ?
ORDER BY time_to_hire_days DESC;