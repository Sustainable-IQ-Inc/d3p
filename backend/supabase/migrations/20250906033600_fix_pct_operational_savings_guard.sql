create or replace view "public"."project_energy_summary" as  WITH ranked_uploads AS (
         SELECT p.id AS project_id,
            p.project_name,
            ud.report_type,
            ((cz.name || ' - '::text) || cz.description) AS climate_zone,
            ud.total_energy,
            ut.name AS project_use_type,
            ud.baseline_design,
            u.year,
            pp.name AS project_phase_only,
                CASE
                    WHEN (u.year IS NOT NULL) THEN ((u.year || ' - '::text) || pp.name)
                    ELSE pp.name
                END AS project_phase,
            (ud.use_type_total_area)::numeric AS conditioned_area,
            row_number() OVER (PARTITION BY p.id, ud.baseline_design ORDER BY u.created_at DESC) AS rn,
            p.company_id,
                CASE
                    WHEN (((regexp_replace(ud."SolarDHW_On-SiteRenewables", '\\D'::text, ''::text, 'g'::text) <> ''::text) AND ((regexp_replace(ud."SolarDHW_On-SiteRenewables", '\\D'::text, ''::text, 'g'::text))::numeric > (0)::numeric)) OR ((regexp_replace(ud."SolarPV_On-SiteRenewables", '\\D'::text, ''::text, 'g'::text) <> ''::text) AND ((regexp_replace(ud."SolarPV_On-SiteRenewables", '\\D'::text, ''::text, 'g'::text))::numeric > (0)::numeric)) OR ((regexp_replace(ud."Other_On-SiteRenewables", '\\D'::text, ''::text, 'g'::text) <> ''::text) AND ((regexp_replace(ud."Other_On-SiteRenewables", '\\D'::text, ''::text, 'g'::text))::numeric > (0)::numeric))) THEN 'Yes'::text
                    ELSE 'No'::text
                END AS renewables,
            cc.name AS project_construction_category_name,
            u.project_construction_category_id,
            u.energy_code_id,
            u.project_phase_id,
            u.project_use_type_id,
            rt.name AS report_type_name,
            ec.name AS energy_code_name,
            GREATEST(COALESCE(u.updated_at, '1900-01-01 00:00:00+00'::timestamp with time zone), COALESCE(ud.updated_at, '1900-01-01 00:00:00+00'::timestamp with time zone), COALESCE(p.updated_at, '1900-01-01 00:00:00+00'::timestamp with time zone)) AS most_recent_updated_at,
                CASE
                    WHEN (ud.energy_units = 'gj'::text) THEN ((ud."total_Electricity")::numeric * 0.947817)
                    ELSE (ud."total_Electricity")::numeric
                END AS building_total_electricity,
                CASE
                    WHEN (ud.energy_units = 'gj'::text) THEN ((ud.total_energy)::numeric * 0.947817)
                    ELSE (ud.total_energy)::numeric
                END AS building_total_energy,
                CASE
                    WHEN (ud.energy_units = 'gj'::text) THEN ((((ud."total_NaturalGas")::numeric + (ud."total_DistrictHeating")::numeric) + (ud."total_Other")::numeric) * 0.947817)
                    ELSE (((ud."total_NaturalGas")::numeric + (ud."total_DistrictHeating")::numeric) + (ud."total_Other")::numeric)
                END AS building_total_fossil_fuels,
                CASE
                    WHEN (ud.energy_units = 'gj'::text) THEN ((ud."total_On-SiteRenewables")::numeric * 0.947817)
                    ELSE (ud."total_On-SiteRenewables")::numeric
                END AS building_onsite_renewables,
                CASE
                    WHEN (ud.energy_units = 'gj'::text) THEN (((ud."total_Electricity")::numeric - (ud."total_On-SiteRenewables")::numeric) * 0.947817)
                    ELSE ((ud."total_Electricity")::numeric - (ud."total_On-SiteRenewables")::numeric)
                END AS building_net_electricity,
                CASE
                    WHEN (ud.energy_units = 'gj'::text) THEN ((((ud."total_Electricity")::numeric - (ud."total_On-SiteRenewables")::numeric) + (((ud."total_DistrictHeating")::numeric + (ud."total_NaturalGas")::numeric) + (ud."total_Other")::numeric)) * 0.947817)
                    ELSE (((ud."total_Electricity")::numeric - (ud."total_On-SiteRenewables")::numeric) + (((ud."total_DistrictHeating")::numeric + (ud."total_NaturalGas")::numeric) + (ud."total_Other")::numeric))
                END AS net_operational_energy_total,
            u.use_type_subtype_id,
            utst.name AS use_type_subtype_name,
            ud.energy_units,
            u.custom_project_id,
            u.ddx_override_use_type_total_area_sf,
            ud.zip_code,
            ud.city,
            ud.state
           FROM (((((((((projects p
             JOIN uploads u ON ((p.id = u.project_id)))
             JOIN eeu_data ud ON ((u.id = ud.upload_id)))
             LEFT JOIN enum_project_phases pp ON ((u.project_phase_id = pp.id)))
             LEFT JOIN enum_project_use_types ut ON ((u.project_use_type_id = ut.id)))
             LEFT JOIN enum_climate_zones cz ON ((ud.climate_zone = cz.name)))
             LEFT JOIN enum_project_construction_categories cc ON ((u.project_construction_category_id = cc.id)))
             LEFT JOIN enum_energy_codes ec ON ((u.energy_code_id = ec.id)))
             LEFT JOIN enum_report_types rt ON ((ud.report_type = rt.identifier_name)))
             LEFT JOIN enum_use_type_subtypes utst ON ((u.use_type_subtype_id = utst.id)))
        ), baseline AS (
         SELECT ranked_uploads.project_id,
            ranked_uploads.project_name,
            ranked_uploads.report_type,
            ranked_uploads.climate_zone,
            ranked_uploads.year,
            ranked_uploads.project_phase,
            ranked_uploads.project_phase_only,
            ranked_uploads.total_energy,
            ranked_uploads.building_total_energy,
                CASE
                    WHEN (ranked_uploads.conditioned_area > (0)::numeric) THEN ((ranked_uploads.building_total_energy / ranked_uploads.conditioned_area) * (1000)::numeric)
                    ELSE NULL::numeric
                END AS total_energy_per_unit_area_baseline,
            ranked_uploads.baseline_design,
            ranked_uploads.conditioned_area,
            ranked_uploads.rn,
            ranked_uploads.company_id,
            ranked_uploads.project_use_type,
            ranked_uploads.renewables,
            ranked_uploads.project_construction_category_id,
            ranked_uploads.energy_code_id,
            ranked_uploads.project_phase_id,
            ranked_uploads.project_use_type_id,
            ranked_uploads.project_construction_category_name,
            ranked_uploads.report_type_name,
            ranked_uploads.energy_code_name,
            ranked_uploads.most_recent_updated_at,
            ranked_uploads.building_total_electricity,
            ranked_uploads.building_total_fossil_fuels,
            ranked_uploads.building_onsite_renewables,
            ranked_uploads.building_net_electricity,
            ranked_uploads.net_operational_energy_total,
            ranked_uploads.use_type_subtype_id,
            ranked_uploads.use_type_subtype_name,
            ranked_uploads.custom_project_id,
            ranked_uploads.ddx_override_use_type_total_area_sf,
            ranked_uploads.zip_code,
            ranked_uploads.city,
            ranked_uploads.state
           FROM ranked_uploads
          WHERE ((ranked_uploads.baseline_design = 'baseline'::text) AND (ranked_uploads.rn = 1))
        ), design AS (
         SELECT ranked_uploads.project_id,
            ranked_uploads.project_name,
            ranked_uploads.report_type,
            ranked_uploads.climate_zone,
            ranked_uploads.year,
            ranked_uploads.project_phase,
            ranked_uploads.project_phase_only,
            ranked_uploads.total_energy,
            ranked_uploads.building_total_energy,
                CASE
                    WHEN (ranked_uploads.conditioned_area > (0)::numeric) THEN ((ranked_uploads.building_total_energy / ranked_uploads.conditioned_area) * (1000)::numeric)
                    ELSE NULL::numeric
                END AS total_energy_per_unit_area_design,
            ranked_uploads.baseline_design,
            ranked_uploads.conditioned_area,
            ranked_uploads.rn,
            ranked_uploads.company_id,
            ranked_uploads.project_use_type,
            ranked_uploads.renewables,
            ranked_uploads.project_construction_category_id,
            ranked_uploads.energy_code_id,
            ranked_uploads.project_phase_id,
            ranked_uploads.project_use_type_id,
            ranked_uploads.project_construction_category_name,
            ranked_uploads.report_type_name,
            ranked_uploads.energy_code_name,
            ranked_uploads.most_recent_updated_at,
            ranked_uploads.building_total_electricity,
            ranked_uploads.building_total_fossil_fuels,
            ranked_uploads.building_onsite_renewables,
            ranked_uploads.building_net_electricity,
            ranked_uploads.net_operational_energy_total,
            ranked_uploads.use_type_subtype_id,
            ranked_uploads.use_type_subtype_name,
            ranked_uploads.custom_project_id,
            ranked_uploads.ddx_override_use_type_total_area_sf,
            ranked_uploads.zip_code,
            ranked_uploads.city,
            ranked_uploads.state
           FROM ranked_uploads
          WHERE ((ranked_uploads.baseline_design = 'design'::text) AND (ranked_uploads.rn = 1))
        )
 SELECT COALESCE(b.project_id, d.project_id) AS project_id,
    COALESCE(b.project_name, d.project_name) AS project_name,
    COALESCE(b.report_type, d.report_type) AS report_type,
    COALESCE(b.climate_zone, d.climate_zone) AS climate_zone,
    b.total_energy_per_unit_area_baseline,
    d.total_energy_per_unit_area_design,
    COALESCE(b.conditioned_area, d.conditioned_area) AS conditioned_area,
    COALESCE(b.company_id, d.company_id) AS company_id,
    COALESCE(b.year, d.year) AS year,
    COALESCE(b.project_phase, d.project_phase) AS project_phase,
    COALESCE(b.project_phase_only, d.project_phase_only) AS project_phase_only,
    COALESCE(b.project_use_type, d.project_use_type) AS project_use_type,
    b.building_total_energy AS total_energy_baseline,
    d.building_total_energy AS total_energy_design,
    COALESCE(b.renewables, d.renewables) AS renewables,
    COALESCE(b.project_construction_category_id, d.project_construction_category_id) AS project_construction_category_id,
    COALESCE(b.energy_code_id, d.energy_code_id) AS energy_code_id,
    COALESCE(b.project_phase_id, d.project_phase_id) AS project_phase_id,
    COALESCE(b.project_use_type_id, d.project_use_type_id) AS project_use_type_id,
    COALESCE(b.project_construction_category_name, d.project_construction_category_name) AS project_construction_category_name,
    COALESCE(b.report_type_name, d.report_type_name) AS report_type_name,
    COALESCE(b.energy_code_name, d.energy_code_name) AS energy_code_name,
    COALESCE(b.most_recent_updated_at, d.most_recent_updated_at) AS most_recent_updated_at,
    COALESCE(b.building_total_electricity, d.building_total_electricity) AS building_total_electricity,
    COALESCE(b.building_total_energy, d.building_total_energy) AS building_total_energy,
    COALESCE(b.building_total_fossil_fuels, d.building_total_fossil_fuels) AS building_total_fossil_fuels,
    COALESCE(b.building_onsite_renewables, d.building_onsite_renewables) AS building_onsite_renewables,
    COALESCE(b.building_net_electricity, d.building_net_electricity) AS building_net_electricity,
    COALESCE(b.net_operational_energy_total, d.net_operational_energy_total) AS net_operational_energy_total,
    CASE
      WHEN b.total_energy_per_unit_area_baseline IS NULL
           OR b.total_energy_per_unit_area_baseline = 0
           OR d.total_energy_per_unit_area_design IS NULL
      THEN NULL
      ELSE (1)::numeric - (d.total_energy_per_unit_area_design / b.total_energy_per_unit_area_baseline)
    END AS pct_operational_energy_savings,
    COALESCE(b.use_type_subtype_id, d.use_type_subtype_id) AS use_type_subtype_id,
    COALESCE(b.use_type_subtype_name, d.use_type_subtype_name) AS use_type_subtype_name,
    COALESCE(b.custom_project_id, d.custom_project_id) AS custom_project_id,
    COALESCE(b.ddx_override_use_type_total_area_sf, d.ddx_override_use_type_total_area_sf) AS ddx_override_use_type_total_area_sf,
    COALESCE(b.zip_code, d.zip_code) AS zip_code,
    COALESCE(b.city, d.city) AS city,
    COALESCE(b.state, d.state) AS state
   FROM (baseline b
     FULL JOIN design d ON ((b.project_id = d.project_id)));


