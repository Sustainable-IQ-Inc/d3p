-- Add reporting_year field to uploads table
alter table "public"."uploads" add column "reporting_year" smallint;

-- Set default value to match existing year values for existing records
update "public"."uploads" set "reporting_year" = "year" where "year" is not null;

