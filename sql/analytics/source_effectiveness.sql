SELECT
    a.source,
    COUNT(*) AS total_applications,
    SUM(CASE WHEN a.status = 'Hired' THEN 1 ELSE 0 END) AS total_hires,
    ROUND(
        100.0 * SUM(CASE WHEN a.status = 'Hired' THEN 1 ELSE 0 END)
        / COUNT(*),
        1
    ) AS hire_rate
FROM applications AS a
JOIN jobs AS j
    ON a.job_id = j.job_id
WHERE j.department IN ({department_placeholders})
AND a.source IN ({source_placeholders})
AND date(a.applied_at) BETWEEN ? AND ?
GROUP BY a.source
ORDER BY hire_rate DESC;