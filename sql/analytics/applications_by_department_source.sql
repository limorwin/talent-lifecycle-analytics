SELECT
    jobs.department,
    applications.source,
    COUNT(*) AS application_count
FROM applications
INNER JOIN jobs
    ON jobs.job_id = applications.job_id
WHERE jobs.department IN ({department_placeholders})
  AND applications.source IN ({source_placeholders})
  AND date(applications.applied_at) BETWEEN ? AND ?
  AND (
      {all_stages}
      OR EXISTS (
          SELECT 1
          FROM stage_events AS se
          WHERE se.application_id = applications.application_id
            AND se.stage IN ({stage_placeholders})
      )
  )
GROUP BY jobs.department, applications.source
ORDER BY application_count DESC;
