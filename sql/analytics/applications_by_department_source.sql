SELECT
    jobs.department,
    applications.source,
    COUNT(*) AS application_count
FROM applications
INNER JOIN jobs
    ON jobs.job_id = applications.job_id
GROUP BY jobs.department, applications.source
ORDER BY application_count DESC;
