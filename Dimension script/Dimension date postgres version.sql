DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE,
    full_date_uk CHAR(10),
    full_date_usa CHAR(10),
    day_of_month VARCHAR(2),
    day_suffix VARCHAR(4),
    day_name VARCHAR(9),
    day_of_week_usa VARCHAR(9),
    day_of_week_uk VARCHAR(9),
    day_of_week_in_month INTEGER,
    day_of_week_in_year INTEGER,
    day_of_quarter INTEGER,
    day_of_year VARCHAR(3),
    week_of_month INTEGER,
    week_of_quarter INTEGER,
    week_of_year VARCHAR(2),
    month VARCHAR(2),
    month_name VARCHAR(9),
    month_of_quarter VARCHAR(2),
    quarter CHAR(1),
    quarter_name VARCHAR(9),
    year CHAR(4),
    year_name CHAR(7),
    month_year CHAR(10),
    mmyyyy CHAR(6),
    first_day_of_month DATE,
    last_day_of_month DATE,
    first_day_of_quarter DATE,
    last_day_of_quarter DATE,
    first_day_of_year DATE,
    last_day_of_year DATE,
    is_weekday BOOLEAN,
    holiday_uk VARCHAR(50),
    is_holiday_uk BOOLEAN,
    holiday_usa VARCHAR(50),
    is_holiday_usa BOOLEAN
);


INSERT INTO dim_date (
    date_key, date, full_date_uk, full_date_usa, day_of_month, day_suffix,
    day_name, day_of_week_usa, day_of_week_uk, day_of_week_in_month,
    day_of_week_in_year, day_of_quarter, day_of_year, week_of_month,
    week_of_quarter, week_of_year, month, month_name, month_of_quarter,
    quarter, quarter_name, year, year_name, month_year, mmyyyy,
    first_day_of_month, last_day_of_month, first_day_of_quarter,
    last_day_of_quarter, first_day_of_year, last_day_of_year, is_weekday,
    holiday_uk, is_holiday_uk, holiday_usa, is_holiday_usa
)
SELECT *
FROM (
    SELECT
        TO_CHAR(d, 'YYYYMMDD')::INTEGER AS date_key,
        d AS date,
        TO_CHAR(d, 'DD/MM/YYYY') AS full_date_uk,
        TO_CHAR(d, 'MM/DD/YYYY') AS full_date_usa,
        TO_CHAR(d, 'DD') AS day_of_month,
        CASE
            WHEN EXTRACT(DAY FROM d) IN (11,12,13) THEN TO_CHAR(d, 'DD') || 'th'
            WHEN RIGHT(TO_CHAR(d, 'DD'), 1) = '1' THEN TO_CHAR(d, 'DD') || 'st'
            WHEN RIGHT(TO_CHAR(d, 'DD'), 1) = '2' THEN TO_CHAR(d, 'DD') || 'nd'
            WHEN RIGHT(TO_CHAR(d, 'DD'), 1) = '3' THEN TO_CHAR(d, 'DD') || 'rd'
            ELSE TO_CHAR(d, 'DD') || 'th'
        END AS day_suffix,
        TO_CHAR(d, 'FMDay') AS day_name,
        TO_CHAR(d, 'FMDay') AS day_of_week_usa,
        CASE TO_CHAR(d, 'D')
            WHEN '1' THEN 'Sunday'
            WHEN '2' THEN 'Monday'
            WHEN '3' THEN 'Tuesday'
            WHEN '4' THEN 'Wednesday'
            WHEN '5' THEN 'Thursday'
            WHEN '6' THEN 'Friday'
            WHEN '7' THEN 'Saturday'
        END AS day_of_week_uk,
        ROW_NUMBER() OVER (PARTITION BY TO_CHAR(d, 'YYYY-MM'), TO_CHAR(d, 'D') ORDER BY d) AS day_of_week_in_month,
        ROW_NUMBER() OVER (PARTITION BY TO_CHAR(d, 'YYYY'), TO_CHAR(d, 'D') ORDER BY d) AS day_of_week_in_year,
        ROW_NUMBER() OVER (PARTITION BY TO_CHAR(d, 'YYYY') || TO_CHAR(d, 'Q'), TO_CHAR(d, 'D') ORDER BY d) AS day_of_quarter,
        TO_CHAR(d, 'DDD') AS day_of_year,
        (EXTRACT(WEEK FROM d) - EXTRACT(WEEK FROM DATE_TRUNC('month', d)) + 1)::INTEGER AS week_of_month,
        (EXTRACT(WEEK FROM d) - EXTRACT(WEEK FROM DATE_TRUNC('quarter', d)) + 1)::INTEGER AS week_of_quarter,
        TO_CHAR(d, 'WW') AS week_of_year,
        TO_CHAR(d, 'MM') AS month,
        TO_CHAR(d, 'FMMonth') AS month_name,
        CASE
            WHEN TO_CHAR(d, 'MM') IN ('01','04','07','10') THEN '1'
            WHEN TO_CHAR(d, 'MM') IN ('02','05','08','11') THEN '2'
            WHEN TO_CHAR(d, 'MM') IN ('03','06','09','12') THEN '3'
        END AS month_of_quarter,
        TO_CHAR(d, 'Q') AS quarter,
        CASE TO_CHAR(d, 'Q')
            WHEN '1' THEN 'First'
            WHEN '2' THEN 'Second'
            WHEN '3' THEN 'Third'
            WHEN '4' THEN 'Fourth'
        END AS quarter_name,
        TO_CHAR(d, 'YYYY') AS year,
        'CY ' || TO_CHAR(d, 'YYYY') AS year_name,
        TO_CHAR(d, 'Mon') || '-' || TO_CHAR(d, 'YYYY') AS month_year,
        TO_CHAR(d, 'MMYYYY') AS mmyyyy,
        DATE_TRUNC('month', d)::DATE AS first_day_of_month,
        (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::DATE AS last_day_of_month,
        DATE_TRUNC('quarter', d)::DATE AS first_day_of_quarter,
        (DATE_TRUNC('quarter', d) + INTERVAL '3 month - 1 day')::DATE AS last_day_of_quarter,
        DATE_TRUNC('year', d)::DATE AS first_day_of_year,
        (DATE_TRUNC('year', d) + INTERVAL '1 year - 1 day')::DATE AS last_day_of_year,
        (EXTRACT(ISODOW FROM d) < 6)::BOOLEAN AS is_weekday,
        NULL AS holiday_uk,
        FALSE AS is_holiday_uk,
        NULL AS holiday_usa,
        FALSE AS is_holiday_usa
    FROM generate_series('2000-01-01'::DATE, '2021-12-31'::DATE, INTERVAL '1 day') AS d
) AS sub;
