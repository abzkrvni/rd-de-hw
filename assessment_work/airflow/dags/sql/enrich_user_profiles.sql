-- dags/sql/merge_user_profiles.sql

DROP TABLE IF EXISTS tmp_user_profiles_enriched;

CREATE TEMP TABLE tmp_user_profiles_enriched AS
SELECT
    c.client_id,
    COALESCE(NULLIF(TRIM(c.first_name), ''), SPLIT_PART(TRIM(up.full_name), ' ', 1)) AS first_name,
    COALESCE(NULLIF(TRIM(c.last_name), ''), SPLIT_PART(TRIM(up.full_name), ' ', 2)) AS last_name,
    LOWER(TRIM(c.email)) AS email,
    COALESCE(NULLIF(TRIM(c.state), ''), TRIM(up.state)) AS state,
    c.registration_date,
    up.birth_date,
    up.phone_number
FROM silver.customers c
LEFT JOIN silver.user_profiles up
    ON LOWER(TRIM(c.email)) = LOWER(TRIM(up.email));

MERGE INTO gold.user_profiles_enriched
USING tmp_user_profiles_enriched
ON gold.user_profiles_enriched.client_id = tmp_user_profiles_enriched.client_id
WHEN MATCHED THEN UPDATE SET
    first_name = tmp_user_profiles_enriched.first_name,
    last_name = tmp_user_profiles_enriched.last_name,
    email = tmp_user_profiles_enriched.email,
    state = tmp_user_profiles_enriched.state,
    registration_date = tmp_user_profiles_enriched.registration_date,
    birth_date = tmp_user_profiles_enriched.birth_date,
    phone_number = tmp_user_profiles_enriched.phone_number
WHEN NOT MATCHED THEN
INSERT (client_id, first_name, last_name, email, state, registration_date, birth_date, phone_number)
VALUES (tmp_user_profiles_enriched.client_id,
        tmp_user_profiles_enriched.first_name,
        tmp_user_profiles_enriched.last_name,
        tmp_user_profiles_enriched.email,
        tmp_user_profiles_enriched.state,
        tmp_user_profiles_enriched.registration_date,
        tmp_user_profiles_enriched.birth_date,
        tmp_user_profiles_enriched.phone_number);
