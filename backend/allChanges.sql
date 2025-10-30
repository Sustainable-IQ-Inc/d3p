
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

CREATE OR REPLACE FUNCTION "public"."custom_access_token_hook"("event" "jsonb") RETURNS "jsonb"
    LANGUAGE "plpgsql"
    AS $$
  declare
    claims jsonb;
    company_id uuid; -- Assuming company_id is of type UUID
  begin
    -- Fetch the company_id for the user from the profiles table
    select company_id into company_id from profiles where user_id = event->>'user_id'::uuid;

    -- Proceed only if a company_id was found
    if company_id is not null then
      claims := event->'claims';

      -- Check if 'app_metadata' exists in claims
      if jsonb_typeof(claims->'app_metadata') is null then
        -- If 'app_metadata' does not exist, create an empty object
        claims := jsonb_set(claims, '{app_metadata}', '{}');
      end if;

      -- Insert the company_id into the claims
      -- Assuming you want to add the company_id under app_metadata
      claims := jsonb_set(claims, '{app_metadata,company_id}', to_jsonb(company_id::text));

      -- Update the 'claims' object in the original event
      event := jsonb_set(event, '{claims}', claims);
    end if;

    -- Return the modified or original event
    return event;
  end;
$$;

ALTER FUNCTION "public"."custom_access_token_hook"("event" "jsonb") OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."handle_new_user"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
begin
  insert into public.profiles (id, email, company_id)
  values (new.id, new.email, (new.raw_user_meta_data->>'company_id')::uuid);
  return new;
end;
$$;

ALTER FUNCTION "public"."handle_new_user"() OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."handle_user_update"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    UPDATE public.profiles
    SET email = NEW.email, -- Update fields as necessary
        updated_at = CURRENT_TIMESTAMP, -- Assume you've added an updated_at column
        confirmed_at = NEW.confirmed_at
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$;

ALTER FUNCTION "public"."handle_user_update"() OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."update_user_profile"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  -- Update the corresponding profile in the public.profiles table
  UPDATE public.profiles
  SET email = NEW.email, 
      confirmed_at = NEW.confirmed_at, 
      last_logged_in_at = NEW.last_sign_in_at
  WHERE id = NEW.id;

  RETURN NEW;
END;
$$;

ALTER FUNCTION "public"."update_user_profile"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE IF NOT EXISTS "public"."companies" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "company_name" "text",
    "company_domain" "text",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);

ALTER TABLE "public"."companies" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."eeu_data" (
    "id" integer NOT NULL,
    "report_type" "text",
    "use_type_total_area" "text",
    "area_units" "text",
    "energy_units" "text",
    "Heating_Electricity" "text",
    "Heating_NaturalGas" "text",
    "Heating_DistrictHeating" "text",
    "Heating_Other" "text",
    "Cooling_Electricity" "text",
    "Cooling_DistrictHeating" "text",
    "Cooling_Other" "text",
    "DHW_Electricity" "text",
    "DHW_NaturalGas" "text",
    "DHW_DistrictHeating" "text",
    "DHW_Other" "text",
    "Interior Lighting_Electricity" "text",
    "Exterior Lighting_Electricity" "text",
    "Plug Loads_Electricity" "text",
    "Fans_Electricity" "text",
    "Pumps_Electricity" "text",
    "Pumps_NaturalGas" "text",
    "Process Refrigeration_Electricity" "text",
    "ExteriorUsage_Electricity" "text",
    "ExteriorUsage_NaturalGas" "text",
    "OtherEndUse_Electricity" "text",
    "OtherEndUse_NaturalGas" "text",
    "OtherEndUse_Other" "text",
    "Heat Rejection_Electricity" "text",
    "Humidification_Electricity" "text",
    "HeatRecovery_Electricity" "text",
    "HeatRecovery_Other" "text",
    "SolarDHW_On-SiteRenewables" "text",
    "SolarPV_On-SiteRenewables" "text",
    "Wind_On-SiteRenewables" "text",
    "Other_On-SiteRenewables" "text",
    "total_Electricity" "text",
    "total_NaturalGas" "text",
    "total_DistrictHeating" "text",
    "total_Other" "text",
    "total_On-SiteRenewables" "text",
    "total_energy" "text",
    "project_name" "text",
    "weather_string" "text",
    "weather_station" "text",
    "climate_zone" "text",
    "file_url" "text",
    "upload_id" bigint,
    "baseline_design" "text",
    "created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "upload_warnings" "text",
    "upload_errors" "text"
);

ALTER TABLE "public"."eeu_data" OWNER TO "postgres";

ALTER TABLE "public"."eeu_data" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."eeu_data_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_climate_zones" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint,
    "description" "text"
);

ALTER TABLE "public"."enum_climate_zones" OWNER TO "postgres";

ALTER TABLE "public"."enum_climate_zones" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_climate_zones_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_energy_codes" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint
);

ALTER TABLE "public"."enum_energy_codes" OWNER TO "postgres";

ALTER TABLE "public"."enum_energy_codes" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_energy_codes_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_project_construction_categories" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint
);

ALTER TABLE "public"."enum_project_construction_categories" OWNER TO "postgres";

ALTER TABLE "public"."enum_project_construction_categories" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_project_construction_categories_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_project_phases" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint
);

ALTER TABLE "public"."enum_project_phases" OWNER TO "postgres";

ALTER TABLE "public"."enum_project_phases" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_project_phases_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_project_use_types" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint
);

ALTER TABLE "public"."enum_project_use_types" OWNER TO "postgres";

ALTER TABLE "public"."enum_project_use_types" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_project_use_types_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_report_types" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint
);

ALTER TABLE "public"."enum_report_types" OWNER TO "postgres";

ALTER TABLE "public"."enum_report_types" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_report_types_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."enum_upload_statuses" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text",
    "order" smallint
);

ALTER TABLE "public"."enum_upload_statuses" OWNER TO "postgres";

ALTER TABLE "public"."enum_upload_statuses" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."enum_upload_statuses_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."projects" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "project_name" "text",
    "climate_zone_id" integer,
    "conditioned_area_sf" real,
    "project_construction_category_id" bigint,
    "project_use_type_id" bigint,
    "company_id" "uuid",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);

ALTER TABLE "public"."projects" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."uploads" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "area" real,
    "climate_zone_id" bigint,
    "climate_zone_str" "text",
    "user_id" bigint,
    "area_units" "text",
    "project_phase_id" bigint,
    "design_baseline_type" "text",
    "report_type_id" bigint,
    "upload_status_id" integer,
    "energy_code_id" integer,
    "project_construction_category_id" integer,
    "project_id" "uuid",
    "project_use_type_id" integer,
    "company_id" "uuid",
    "id_uuid" "uuid",
    "other_energy_code" "text",
    "year" smallint
);

ALTER TABLE "public"."uploads" OWNER TO "postgres";

CREATE OR REPLACE VIEW "public"."latest_project_uploads5" AS
 SELECT "p"."project_name",
    "ert"."name" AS "report_type",
    "eec"."name" AS "energy_code",
    "p"."company_id",
    "p"."id"
   FROM ((("public"."projects" "p"
     JOIN "public"."uploads" "u" ON (("p"."id" = "u"."project_id")))
     JOIN "public"."enum_energy_codes" "eec" ON (("u"."energy_code_id" = "eec"."id")))
     JOIN "public"."enum_report_types" "ert" ON (("u"."report_type_id" = "ert"."id")))
  WHERE ("u"."created_at" = ( SELECT "max"("u2"."created_at") AS "max"
           FROM "public"."uploads" "u2"
          WHERE ("u2"."project_id" = "p"."id")));

ALTER TABLE "public"."latest_project_uploads5" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "id" "uuid" NOT NULL,
    "first_name" "text",
    "last_name" "text",
    "email" "text",
    "company_id" "uuid",
    "confirmed_at" timestamp with time zone,
    "last_sign_in_at" timestamp with time zone,
    "role" "text"
);

ALTER TABLE "public"."profiles" OWNER TO "postgres";

CREATE OR REPLACE VIEW "public"."project_energy_summary4" AS
 WITH "ranked_uploads" AS (
         SELECT "p"."id" AS "project_id",
            "p"."project_name",
            "ud"."report_type",
            (("cz"."name" || ' - '::"text") || "cz"."description") AS "climate_zone",
            "ud"."total_energy",
            "ut"."name" AS "project_use_type",
            "ud"."baseline_design",
                CASE
                    WHEN ("u"."year" IS NOT NULL) THEN (("u"."year" || ' - '::"text") || "pp"."name")
                    ELSE "pp"."name"
                END AS "project_phase",
            "ud"."use_type_total_area" AS "conditioned_area",
            "row_number"() OVER (PARTITION BY "p"."id", "ud"."baseline_design" ORDER BY "u"."created_at" DESC) AS "rn",
            "p"."company_id",
                CASE
                    WHEN ((("regexp_replace"("ud"."SolarDHW_On-SiteRenewables", '\D'::"text", ''::"text", 'g'::"text") <> ''::"text") AND (("regexp_replace"("ud"."SolarDHW_On-SiteRenewables", '\D'::"text", ''::"text", 'g'::"text"))::numeric > (0)::numeric)) OR (("regexp_replace"("ud"."SolarPV_On-SiteRenewables", '\D'::"text", ''::"text", 'g'::"text") <> ''::"text") AND (("regexp_replace"("ud"."SolarPV_On-SiteRenewables", '\D'::"text", ''::"text", 'g'::"text"))::numeric > (0)::numeric)) OR (("regexp_replace"("ud"."Other_On-SiteRenewables", '\D'::"text", ''::"text", 'g'::"text") <> ''::"text") AND (("regexp_replace"("ud"."Other_On-SiteRenewables", '\D'::"text", ''::"text", 'g'::"text"))::numeric > (0)::numeric))) THEN 'Yes'::"text"
                    ELSE 'No'::"text"
                END AS "renewables"
           FROM ((((("public"."projects" "p"
             JOIN "public"."uploads" "u" ON (("p"."id" = "u"."project_id")))
             JOIN "public"."eeu_data" "ud" ON (("u"."id" = "ud"."upload_id")))
             LEFT JOIN "public"."enum_project_phases" "pp" ON (("u"."project_phase_id" = "pp"."id")))
             LEFT JOIN "public"."enum_project_use_types" "ut" ON (("u"."project_use_type_id" = "ut"."id")))
             LEFT JOIN "public"."enum_climate_zones" "cz" ON (("ud"."climate_zone" = "cz"."name")))
        ), "baseline" AS (
         SELECT "ranked_uploads"."project_id",
            "ranked_uploads"."project_name",
            "ranked_uploads"."report_type",
            "ranked_uploads"."climate_zone",
            "ranked_uploads"."project_phase",
            "ranked_uploads"."total_energy",
                CASE
                    WHEN (("ranked_uploads"."conditioned_area")::numeric > (0)::numeric) THEN ((("ranked_uploads"."total_energy")::numeric / ("ranked_uploads"."conditioned_area")::numeric) * (1000)::numeric)
                    ELSE NULL::numeric
                END AS "total_energy_per_unit_area_baseline",
            "ranked_uploads"."baseline_design",
            "ranked_uploads"."conditioned_area",
            "ranked_uploads"."rn",
            "ranked_uploads"."company_id",
            "ranked_uploads"."project_use_type",
            "ranked_uploads"."renewables"
           FROM "ranked_uploads"
          WHERE (("ranked_uploads"."baseline_design" = 'baseline'::"text") AND ("ranked_uploads"."rn" = 1))
        ), "design" AS (
         SELECT "ranked_uploads"."project_id",
            "ranked_uploads"."project_name",
            "ranked_uploads"."report_type",
            "ranked_uploads"."climate_zone",
            "ranked_uploads"."project_phase",
            "ranked_uploads"."total_energy",
                CASE
                    WHEN (("ranked_uploads"."conditioned_area")::numeric > (0)::numeric) THEN ((("ranked_uploads"."total_energy")::numeric / ("ranked_uploads"."conditioned_area")::numeric) * (1000)::numeric)
                    ELSE NULL::numeric
                END AS "total_energy_per_unit_area_design",
            "ranked_uploads"."baseline_design",
            "ranked_uploads"."conditioned_area",
            "ranked_uploads"."rn",
            "ranked_uploads"."company_id",
            "ranked_uploads"."project_use_type",
            "ranked_uploads"."renewables"
           FROM "ranked_uploads"
          WHERE (("ranked_uploads"."baseline_design" = 'design'::"text") AND ("ranked_uploads"."rn" = 1))
        )
 SELECT COALESCE("b"."project_id", "d"."project_id") AS "project_id",
    COALESCE("b"."project_name", "d"."project_name") AS "project_name",
    COALESCE("b"."report_type", "d"."report_type") AS "report_type",
    COALESCE("b"."climate_zone", "d"."climate_zone") AS "climate_zone",
    "b"."total_energy_per_unit_area_baseline",
    "d"."total_energy_per_unit_area_design",
    COALESCE("b"."conditioned_area", "d"."conditioned_area") AS "conditioned_area",
    COALESCE("b"."company_id", "d"."company_id") AS "company_id",
    COALESCE("b"."project_phase", "d"."project_phase") AS "project_phase",
    COALESCE("b"."project_use_type", "d"."project_use_type") AS "project_use_type",
    "b"."total_energy" AS "total_energy_baseline",
    "d"."total_energy" AS "total_energy_design",
    COALESCE("b"."renewables", "d"."renewables") AS "renewables"
   FROM ("baseline" "b"
     FULL JOIN "design" "d" ON (("b"."project_id" = "d"."project_id")));

ALTER TABLE "public"."project_energy_summary4" OWNER TO "postgres";

CREATE OR REPLACE VIEW "public"."project_latest_upload_by_type5" WITH ("security_invoker"='true') AS
 WITH "ranked_uploads" AS (
         SELECT "p"."id" AS "project_id",
            "p"."project_name" AS "proj_name",
            "u"."created_at" AS "upload_created_at",
            "ud_1"."id",
            "ud_1"."report_type",
            "ud_1"."use_type_total_area",
            "ud_1"."area_units",
            "ud_1"."energy_units",
            "ud_1"."Heating_Electricity",
            "ud_1"."Heating_NaturalGas",
            "ud_1"."Heating_DistrictHeating",
            "ud_1"."Heating_Other",
            "ud_1"."Cooling_Electricity",
            "ud_1"."Cooling_DistrictHeating",
            "ud_1"."Cooling_Other",
            "ud_1"."DHW_Electricity",
            "ud_1"."DHW_NaturalGas",
            "ud_1"."DHW_DistrictHeating",
            "ud_1"."DHW_Other",
            "ud_1"."Interior Lighting_Electricity",
            "ud_1"."Exterior Lighting_Electricity",
            "ud_1"."Plug Loads_Electricity",
            "ud_1"."Fans_Electricity",
            "ud_1"."Pumps_Electricity",
            "ud_1"."Pumps_NaturalGas",
            "ud_1"."Process Refrigeration_Electricity",
            "ud_1"."ExteriorUsage_Electricity",
            "ud_1"."ExteriorUsage_NaturalGas",
            "ud_1"."OtherEndUse_Electricity",
            "ud_1"."OtherEndUse_NaturalGas",
            "ud_1"."OtherEndUse_Other",
            "ud_1"."Heat Rejection_Electricity",
            "ud_1"."Humidification_Electricity",
            "ud_1"."HeatRecovery_Electricity",
            "ud_1"."HeatRecovery_Other",
            "ud_1"."SolarDHW_On-SiteRenewables",
            "ud_1"."SolarPV_On-SiteRenewables",
            "ud_1"."Wind_On-SiteRenewables",
            "ud_1"."Other_On-SiteRenewables",
            "ud_1"."total_Electricity",
            "ud_1"."total_NaturalGas",
            "ud_1"."total_DistrictHeating",
            "ud_1"."total_Other",
            "ud_1"."total_On-SiteRenewables",
            "ud_1"."total_energy",
            "ud_1"."project_name",
            "ud_1"."weather_string",
            "ud_1"."weather_station",
            "ud_1"."climate_zone",
            "ud_1"."file_url",
            "ud_1"."upload_id",
            "ud_1"."baseline_design",
            "row_number"() OVER (PARTITION BY "p"."id", "ud_1"."baseline_design" ORDER BY "u"."created_at" DESC) AS "rn",
            "p"."company_id",
            "pcc"."name" AS "project_construction_category",
            "put"."name" AS "project_use_type",
            "pp"."name" AS "project_phase"
           FROM (((((("public"."projects" "p"
             JOIN "public"."uploads" "u" ON (("p"."id" = "u"."project_id")))
             JOIN "public"."eeu_data" "ud_1" ON (("u"."id" = "ud_1"."upload_id")))
             LEFT JOIN "public"."enum_climate_zones" "cz" ON (("u"."climate_zone_id" = "cz"."id")))
             LEFT JOIN "public"."enum_project_construction_categories" "pcc" ON (("u"."project_construction_category_id" = "pcc"."id")))
             LEFT JOIN "public"."enum_project_use_types" "put" ON (("u"."project_use_type_id" = "put"."id")))
             LEFT JOIN "public"."enum_project_phases" "pp" ON (("u"."project_phase_id" = "pp"."id")))
        )
 SELECT "ranked_uploads"."project_id",
    "ranked_uploads"."proj_name",
    "ranked_uploads"."upload_created_at",
    "ranked_uploads"."id",
    "ranked_uploads"."report_type",
    "ranked_uploads"."use_type_total_area",
    "ranked_uploads"."area_units",
    "ranked_uploads"."energy_units",
    "ranked_uploads"."Heating_Electricity",
    "ranked_uploads"."Heating_NaturalGas",
    "ranked_uploads"."Heating_DistrictHeating",
    "ranked_uploads"."Heating_Other",
    "ranked_uploads"."Cooling_Electricity",
    "ranked_uploads"."Cooling_DistrictHeating",
    "ranked_uploads"."Cooling_Other",
    "ranked_uploads"."DHW_Electricity",
    "ranked_uploads"."DHW_NaturalGas",
    "ranked_uploads"."DHW_DistrictHeating",
    "ranked_uploads"."DHW_Other",
    "ranked_uploads"."Interior Lighting_Electricity",
    "ranked_uploads"."Exterior Lighting_Electricity",
    "ranked_uploads"."Plug Loads_Electricity",
    "ranked_uploads"."Fans_Electricity",
    "ranked_uploads"."Pumps_Electricity",
    "ranked_uploads"."Pumps_NaturalGas",
    "ranked_uploads"."Process Refrigeration_Electricity",
    "ranked_uploads"."ExteriorUsage_Electricity",
    "ranked_uploads"."ExteriorUsage_NaturalGas",
    "ranked_uploads"."OtherEndUse_Electricity",
    "ranked_uploads"."OtherEndUse_NaturalGas",
    "ranked_uploads"."OtherEndUse_Other",
    "ranked_uploads"."Heat Rejection_Electricity",
    "ranked_uploads"."Humidification_Electricity",
    "ranked_uploads"."HeatRecovery_Electricity",
    "ranked_uploads"."HeatRecovery_Other",
    "ranked_uploads"."SolarDHW_On-SiteRenewables",
    "ranked_uploads"."SolarPV_On-SiteRenewables",
    "ranked_uploads"."Wind_On-SiteRenewables",
    "ranked_uploads"."Other_On-SiteRenewables",
    "ranked_uploads"."total_Electricity",
    "ranked_uploads"."total_NaturalGas",
    "ranked_uploads"."total_DistrictHeating",
    "ranked_uploads"."total_Other",
    "ranked_uploads"."total_On-SiteRenewables",
    "ranked_uploads"."total_energy",
    "ranked_uploads"."project_name",
    "ranked_uploads"."weather_string",
    "ranked_uploads"."weather_station",
    "ranked_uploads"."climate_zone",
    "ranked_uploads"."file_url",
    "ranked_uploads"."upload_id",
    "ranked_uploads"."baseline_design",
    "ranked_uploads"."rn",
    "ranked_uploads"."company_id",
    "ranked_uploads"."project_construction_category",
    "ranked_uploads"."project_use_type",
    "ranked_uploads"."project_phase"
   FROM ("ranked_uploads"
     JOIN "public"."eeu_data" "ud" ON (("ranked_uploads"."id" = "ud"."id")))
  WHERE ("ranked_uploads"."rn" = 1);

ALTER TABLE "public"."project_latest_upload_by_type5" OWNER TO "postgres";

ALTER TABLE "public"."uploads" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."uploads_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_first" "text",
    "user_last" "text",
    "user_email" "text",
    "company_id" "uuid"
);

ALTER TABLE "public"."users" OWNER TO "postgres";

ALTER TABLE "public"."users" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."users_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE ONLY "public"."enum_climate_zones"
    ADD CONSTRAINT "climate_zones_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."companies"
    ADD CONSTRAINT "companies_id_uuid_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."companies"
    ADD CONSTRAINT "companies_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."eeu_data"
    ADD CONSTRAINT "eeu_data_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."eeu_data"
    ADD CONSTRAINT "eeu_data_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."enum_energy_codes"
    ADD CONSTRAINT "energy_codes_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."enum_project_construction_categories"
    ADD CONSTRAINT "project_construction_categories_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."enum_project_construction_categories"
    ADD CONSTRAINT "project_construction_categories_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."enum_project_phases"
    ADD CONSTRAINT "project_phases_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."enum_project_use_types"
    ADD CONSTRAINT "project_use_types_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."projects"
    ADD CONSTRAINT "projects_pkey1" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."enum_report_types"
    ADD CONSTRAINT "report_types_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."enum_upload_statuses"
    ADD CONSTRAINT "upload_statuses_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "uploads_id_uuid_key" UNIQUE ("id_uuid");

ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY ("id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."projects"
    ADD CONSTRAINT "projects_climate_zone_id_fkey" FOREIGN KEY ("climate_zone_id") REFERENCES "public"."enum_climate_zones"("id");

ALTER TABLE ONLY "public"."projects"
    ADD CONSTRAINT "projects_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id");

ALTER TABLE ONLY "public"."projects"
    ADD CONSTRAINT "projects_project_construction_category_id_fkey" FOREIGN KEY ("project_construction_category_id") REFERENCES "public"."enum_project_construction_categories"("id");

ALTER TABLE ONLY "public"."projects"
    ADD CONSTRAINT "projects_project_use_type_id_fkey" FOREIGN KEY ("project_use_type_id") REFERENCES "public"."enum_project_use_types"("id");

ALTER TABLE ONLY "public"."eeu_data"
    ADD CONSTRAINT "public_eeu_data_upload_id_fkey" FOREIGN KEY ("upload_id") REFERENCES "public"."uploads"("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "public_profiles_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "public_uploads_climate_zone_id_fkey" FOREIGN KEY ("climate_zone_id") REFERENCES "public"."enum_climate_zones"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "public_uploads_energy_code_id_fkey" FOREIGN KEY ("energy_code_id") REFERENCES "public"."enum_energy_codes"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "public_uploads_project_construction_category_id_fkey" FOREIGN KEY ("project_construction_category_id") REFERENCES "public"."enum_project_construction_categories"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "public_uploads_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "public"."projects"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "public_uploads_project_phase_id_fkey" FOREIGN KEY ("project_phase_id") REFERENCES "public"."enum_project_phases"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "public_uploads_project_use_type_id_fkey" FOREIGN KEY ("project_use_type_id") REFERENCES "public"."enum_project_use_types"("id") ON DELETE SET NULL;

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "uploads_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "public"."companies"("id");

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "uploads_report_type_id_fkey" FOREIGN KEY ("report_type_id") REFERENCES "public"."enum_report_types"("id");

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "uploads_upload_status_id_fkey" FOREIGN KEY ("upload_status_id") REFERENCES "public"."enum_upload_statuses"("id");

ALTER TABLE ONLY "public"."uploads"
    ADD CONSTRAINT "uploads_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE RESTRICT;

CREATE POLICY "Allow authenticated users to update data." ON "public"."profiles" FOR UPDATE USING ((("auth"."uid"())::"text" = CURRENT_USER));

CREATE POLICY "Enable insert for authenticated users only" ON "public"."companies" TO "authenticated" WITH CHECK (true);

CREATE POLICY "Enable insert for authenticated users only" ON "public"."projects" FOR INSERT TO "authenticated" WITH CHECK (true);

CREATE POLICY "Enable insert for authenticated users only" ON "public"."uploads" FOR INSERT TO "authenticated" WITH CHECK (true);

CREATE POLICY "Enable insert for users based on user_id" ON "public"."uploads" FOR INSERT WITH CHECK (true);

CREATE POLICY "Public profiles are viewable by everyone." ON "public"."profiles" FOR SELECT USING (true);

CREATE POLICY "Users can insert their own profile." ON "public"."profiles" FOR INSERT WITH CHECK (("auth"."uid"() = "id"));

CREATE POLICY "auth req for all" ON "public"."enum_energy_codes" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

CREATE POLICY "auth req for all" ON "public"."enum_project_use_types" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

CREATE POLICY "auth req for all" ON "public"."enum_report_types" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

CREATE POLICY "auth req for all" ON "public"."enum_upload_statuses" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

ALTER TABLE "public"."companies" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."eeu_data" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_climate_zones" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_energy_codes" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_project_construction_categories" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_project_phases" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_project_use_types" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_report_types" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."enum_upload_statuses" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."projects" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "req for all" ON "public"."enum_project_construction_categories" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

CREATE POLICY "req for all" ON "public"."enum_project_phases" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

CREATE POLICY "select auth only" ON "public"."profiles" USING (("auth"."uid"() IS NOT NULL)) WITH CHECK (("auth"."uid"() IS NOT NULL));

CREATE POLICY "select authenticated only" ON "public"."enum_climate_zones" FOR SELECT USING (("auth"."uid"() IS NOT NULL));

CREATE POLICY "select_for_authenticated_users" ON "public"."eeu_data" FOR SELECT USING (("auth"."uid"() IS NOT NULL));

CREATE POLICY "select_only_authenticated" ON "public"."companies" FOR SELECT USING (("auth"."uid"() IS NOT NULL));

CREATE POLICY "select_only_authenticated" ON "public"."projects" FOR SELECT USING (("auth"."uid"() IS NOT NULL));

ALTER TABLE "public"."uploads" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;

ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";

REVOKE USAGE ON SCHEMA "public" FROM PUBLIC;
GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON FUNCTION "public"."custom_access_token_hook"("event" "jsonb") TO "service_role";
GRANT ALL ON FUNCTION "public"."custom_access_token_hook"("event" "jsonb") TO "supabase_auth_admin";

GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_new_user"() TO "service_role";

GRANT ALL ON FUNCTION "public"."handle_user_update"() TO "anon";
GRANT ALL ON FUNCTION "public"."handle_user_update"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."handle_user_update"() TO "service_role";

GRANT ALL ON FUNCTION "public"."update_user_profile"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_user_profile"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_user_profile"() TO "service_role";

GRANT ALL ON TABLE "public"."companies" TO "anon";
GRANT ALL ON TABLE "public"."companies" TO "authenticated";
GRANT ALL ON TABLE "public"."companies" TO "service_role";

GRANT ALL ON TABLE "public"."eeu_data" TO "anon";
GRANT ALL ON TABLE "public"."eeu_data" TO "authenticated";
GRANT ALL ON TABLE "public"."eeu_data" TO "service_role";

GRANT ALL ON SEQUENCE "public"."eeu_data_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."eeu_data_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."eeu_data_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_climate_zones" TO "anon";
GRANT ALL ON TABLE "public"."enum_climate_zones" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_climate_zones" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_climate_zones_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_climate_zones_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_climate_zones_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_energy_codes" TO "anon";
GRANT ALL ON TABLE "public"."enum_energy_codes" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_energy_codes" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_energy_codes_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_energy_codes_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_energy_codes_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_project_construction_categories" TO "anon";
GRANT ALL ON TABLE "public"."enum_project_construction_categories" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_project_construction_categories" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_project_construction_categories_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_project_construction_categories_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_project_construction_categories_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_project_phases" TO "anon";
GRANT ALL ON TABLE "public"."enum_project_phases" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_project_phases" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_project_phases_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_project_phases_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_project_phases_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_project_use_types" TO "anon";
GRANT ALL ON TABLE "public"."enum_project_use_types" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_project_use_types" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_project_use_types_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_project_use_types_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_project_use_types_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_report_types" TO "anon";
GRANT ALL ON TABLE "public"."enum_report_types" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_report_types" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_report_types_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_report_types_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_report_types_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."enum_upload_statuses" TO "anon";
GRANT ALL ON TABLE "public"."enum_upload_statuses" TO "authenticated";
GRANT ALL ON TABLE "public"."enum_upload_statuses" TO "service_role";

GRANT ALL ON SEQUENCE "public"."enum_upload_statuses_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."enum_upload_statuses_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."enum_upload_statuses_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."projects" TO "anon";
GRANT ALL ON TABLE "public"."projects" TO "authenticated";
GRANT ALL ON TABLE "public"."projects" TO "service_role";

GRANT ALL ON TABLE "public"."uploads" TO "anon";
GRANT ALL ON TABLE "public"."uploads" TO "authenticated";
GRANT ALL ON TABLE "public"."uploads" TO "service_role";

GRANT ALL ON TABLE "public"."latest_project_uploads5" TO "anon";
GRANT ALL ON TABLE "public"."latest_project_uploads5" TO "authenticated";
GRANT ALL ON TABLE "public"."latest_project_uploads5" TO "service_role";

GRANT ALL ON TABLE "public"."profiles" TO "service_role";
GRANT ALL ON TABLE "public"."profiles" TO "supabase_auth_admin";

GRANT ALL ON TABLE "public"."project_energy_summary4" TO "anon";
GRANT ALL ON TABLE "public"."project_energy_summary4" TO "authenticated";
GRANT ALL ON TABLE "public"."project_energy_summary4" TO "service_role";

GRANT ALL ON TABLE "public"."project_latest_upload_by_type5" TO "anon";
GRANT ALL ON TABLE "public"."project_latest_upload_by_type5" TO "authenticated";
GRANT ALL ON TABLE "public"."project_latest_upload_by_type5" TO "service_role";

GRANT ALL ON SEQUENCE "public"."uploads_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."uploads_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."uploads_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."users" TO "anon";
GRANT ALL ON TABLE "public"."users" TO "authenticated";
GRANT ALL ON TABLE "public"."users" TO "service_role";

GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";

RESET ALL;
