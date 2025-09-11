DROP TABLE IF EXISTS dim_time;

CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,
    hour24 INTEGER,
    hour24_short_string VARCHAR(2),
    hour24_min_string VARCHAR(5),
    hour24_full_string VARCHAR(8),
    hour12 INTEGER,
    hour12_short_string VARCHAR(2),
    hour12_min_string VARCHAR(5),
    hour12_full_string VARCHAR(8),
    am_pm_code INTEGER,
    am_pm_string VARCHAR(2) NOT NULL,
    minute INTEGER,
    minute_code INTEGER,
    minute_short_string VARCHAR(2),
    minute_full_string24 VARCHAR(8),
    minute_full_string12 VARCHAR(8),
    half_hour INTEGER,
    half_hour_code INTEGER,
    half_hour_short_string VARCHAR(2),
    half_hour_full_string24 VARCHAR(8),
    half_hour_full_string12 VARCHAR(8),
    second INTEGER,
    second_short_string VARCHAR(2),
    full_time_string24 VARCHAR(8),
    full_time_string12 VARCHAR(8),
    full_time TIME
);


INSERT INTO dim_time (
    time_key, hour24, hour24_short_string, hour24_min_string, hour24_full_string,
    hour12, hour12_short_string, hour12_min_string, hour12_full_string,
    am_pm_code, am_pm_string, minute, minute_code, minute_short_string,
    minute_full_string24, minute_full_string12, half_hour, half_hour_code,
    half_hour_short_string, half_hour_full_string24, half_hour_full_string12,
    second, second_short_string, full_time_string24, full_time_string12, full_time
)
SELECT
    (EXTRACT(HOUR FROM t) * 10000 + EXTRACT(MINUTE FROM t) * 100 + EXTRACT(SECOND FROM t))::INTEGER,
    EXTRACT(HOUR FROM t)::INTEGER,
    TO_CHAR(t, 'HH24'),
    TO_CHAR(t, 'HH24') || ':00',
    TO_CHAR(t, 'HH24') || ':00:00',
    (EXTRACT(HOUR FROM t)::INTEGER % 12),
    TO_CHAR(t, 'HH12'),
    TO_CHAR(t, 'HH12') || ':00',
    TO_CHAR(t, 'HH12') || ':00:00',
    CASE WHEN EXTRACT(HOUR FROM t) < 12 THEN 0 ELSE 1 END,
    TO_CHAR(t, 'AM'),
    EXTRACT(MINUTE FROM t)::INTEGER,
    (EXTRACT(HOUR FROM t)::INTEGER * 100 + EXTRACT(MINUTE FROM t)::INTEGER),
    TO_CHAR(t, 'MI'),
    TO_CHAR(t, 'HH24:MI') || ':00',
    TO_CHAR(t, 'HH12:MI') || ':00',
    (EXTRACT(MINUTE FROM t)::INTEGER / 30),
    (EXTRACT(HOUR FROM t)::INTEGER * 100 + ((EXTRACT(MINUTE FROM t)::INTEGER / 30) * 30)),
    LPAD(((EXTRACT(MINUTE FROM t)::INTEGER / 30) * 30)::TEXT, 2, '0'),
    TO_CHAR(t, 'HH24') || ':' || LPAD(((EXTRACT(MINUTE FROM t)::INTEGER / 30) * 30)::TEXT, 2, '0') || ':00',
    TO_CHAR(t, 'HH12') || ':' || LPAD(((EXTRACT(MINUTE FROM t)::INTEGER / 30) * 30)::TEXT, 2, '0') || ':00',
    EXTRACT(SECOND FROM t)::INTEGER,
    TO_CHAR(t, 'SS'),
    TO_CHAR(t, 'HH24:MI:SS'),
    TO_CHAR(t, 'HH12:MI:SS'),
    CAST(t AS TIME)
FROM generate_series(
    TIMESTAMP '2000-01-01 00:00:00',
    TIMESTAMP '2000-01-01 23:59:59',
    INTERVAL '1 second'
) AS t;
