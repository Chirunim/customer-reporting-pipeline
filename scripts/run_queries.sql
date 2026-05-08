-- ============================================================
-- Query 1: First Bill SLA Breakdown by Bill Band
-- Customer count and percentage share of billed customers
-- ============================================================
SELECT
    bill_band,
    COUNT(*)                                                        AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)             AS pct_of_billed
FROM customers
WHERE bill_band IS NOT NULL
GROUP BY bill_band
ORDER BY bill_band;


-- ============================================================
-- Query 2: Weekly SLA Trend by Week Cohort and Bill Band
-- Percentage breakdown within each weekly cohort
-- ============================================================
SELECT
    week_cohort,
    bill_band,
    COUNT(*)                                                                          AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY week_cohort), 2)       AS pct_within_cohort
FROM customers
WHERE bill_band IS NOT NULL
GROUP BY week_cohort, bill_band
ORDER BY week_cohort, bill_band;


-- ============================================================
-- Query 3: Onboarding Health Scorecard
-- % fully onboarded by region and tariff type
-- ============================================================
SELECT
    region,
    tariff_type,
    COUNT(*)                                                    AS total_customers,
    SUM(fully_onboarded)                                        AS fully_onboarded_count,
    ROUND(SUM(fully_onboarded) * 100.0 / COUNT(*), 2)          AS pct_fully_onboarded
FROM customers
GROUP BY region, tariff_type
ORDER BY region, tariff_type;


-- ============================================================
-- Query 4: Individual Health Check Completion Rates
-- Completion rate for each onboarding flag separately
-- ============================================================
SELECT 'psr_flag'       AS health_check, SUM(psr_flag)       AS completed, COUNT(*) AS total, ROUND(SUM(psr_flag)       * 100.0 / COUNT(*), 2) AS completion_pct FROM customers
UNION ALL
SELECT 'direct_debit'   AS health_check, SUM(direct_debit)   AS completed, COUNT(*) AS total, ROUND(SUM(direct_debit)   * 100.0 / COUNT(*), 2) AS completion_pct FROM customers
UNION ALL
SELECT 'smart_meter'    AS health_check, SUM(smart_meter)    AS completed, COUNT(*) AS total, ROUND(SUM(smart_meter)    * 100.0 / COUNT(*), 2) AS completion_pct FROM customers
UNION ALL
SELECT 'app_registered' AS health_check, SUM(app_registered) AS completed, COUNT(*) AS total, ROUND(SUM(app_registered) * 100.0 / COUNT(*), 2) AS completion_pct FROM customers
ORDER BY completion_pct DESC;
