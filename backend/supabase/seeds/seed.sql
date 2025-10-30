SET session_replication_role = replica;


--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1 (Ubuntu 15.1-1.pgdg20.04+1)
-- Dumped by pg_dump version 15.5 (Ubuntu 15.5-1.pgdg20.04+1)

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





--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."companies" ("created_at", "company_name", "company_domain", "id") VALUES
	('2024-01-30 04:14:48.564647+00', 'Test Corp A', NULL, '92e00f3a-023d-4af9-a538-8d9bd5ca1f74'),
	('2024-02-25 04:40:26.728617+00', 'Test Corp B', NULL, '3a7a4ae7-ca08-4032-880f-7077984451e2');

--
-- Data for Name: enum_upload_statuses; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

--INSERT INTO "public"."projects" ("created_at", "project_name", "climate_zone_id", "conditioned_area_sf", "project_construction_category_id", "project_use_type_id", "company_id", "id") VALUES
	


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."users" ("id", "created_at", "user_first", "user_last", "user_email", "company_id") VALUES
	(3, '2024-02-18 06:06:36.177983+00', NULL, NULL, 'standard_user@email.com', '92e00f3a-023d-4af9-a538-8d9bd5ca1f74');


--
-- Data for Name: uploads; Type: TABLE DATA; Schema: public; Owner: postgres
--

--INSERT INTO "public"."uploads" ("id", "created_at", "area", "climate_zone_id", "climate_zone_str", "user_id", "area_units", "project_phase_id", "design_baseline_type", "report_type_id", "upload_status_id", "energy_code_id", "project_construction_category_id", "project_id", "project_use_type_id", "company_id", "id_uuid", "other_energy_code", "year") VALUES
	


--
-- Data for Name: eeu_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

--INSERT INTO "public"."eeu_data" ("id", "report_type", "use_type_total_area", "area_units", "energy_units", "Heating_Electricity", "Heating_NaturalGas", "Heating_DistrictHeating", "Heating_Other", "Cooling_Electricity", "Cooling_DistrictHeating", "Cooling_Other", "DHW_Electricity", "DHW_NaturalGas", "DHW_DistrictHeating", "DHW_Other", "Interior Lighting_Electricity", "Exterior Lighting_Electricity", "Plug Loads_Electricity", "Fans_Electricity", "Pumps_Electricity", "Pumps_NaturalGas", "Process Refrigeration_Electricity", "ExteriorUsage_Electricity", "ExteriorUsage_NaturalGas", "OtherEndUse_Electricity", "OtherEndUse_NaturalGas", "OtherEndUse_Other", "Heat Rejection_Electricity", "Humidification_Electricity", "HeatRecovery_Electricity", "HeatRecovery_Other", "SolarDHW_On-SiteRenewables", "SolarPV_On-SiteRenewables", "Wind_On-SiteRenewables", "Other_On-SiteRenewables", "total_Electricity", "total_NaturalGas", "total_DistrictHeating", "total_Other", "total_On-SiteRenewables", "total_energy", "project_name", "weather_string", "weather_station", "climate_zone", "file_url", "upload_id", "baseline_design", "created_at", "updated_at", "upload_warnings", "upload_errors", "file_type") VALUES
	


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."profiles" ("id", "first_name", "last_name", "email", "company_id", "confirmed_at", "last_sign_in_at", "role") VALUES
	('4109fef0-df8c-4398-8a99-1603997d8b3d', NULL, NULL, 'superadmin@email.com', '92e00f3a-023d-4af9-a538-8d9bd5ca1f74', NULL, NULL, 'superadmin'),
	('1e129b3f-e3cb-4158-8e34-d8fc3c0d68cd', NULL, NULL, 'standard_user@email.com', '92e00f3a-023d-4af9-a538-8d9bd5ca1f74', NULL, NULL, NULL);


-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."users" ("instance_id", "id", "aud", "role", "email", "encrypted_password", "email_confirmed_at", "invited_at", "confirmation_token", "confirmation_sent_at", "recovery_token", "recovery_sent_at", "email_change_token_new", "email_change", "email_change_sent_at", "last_sign_in_at", "raw_app_meta_data", "raw_user_meta_data", "is_super_admin", "created_at", "updated_at", "phone", "phone_confirmed_at", "phone_change", "phone_change_token", "phone_change_sent_at", "email_change_token_current", "email_change_confirm_status", "banned_until", "reauthentication_token", "reauthentication_sent_at", "is_sso_user", "deleted_at", "is_anonymous") VALUES
	('00000000-0000-0000-0000-000000000000', '1e129b3f-e3cb-4158-8e34-d8fc3c0d68cd', 'authenticated', 'authenticated', 'standard_user@email.com', '', NULL, '2024-03-27 04:05:16.702965+00', '5674200164967aaead024155245ae4d1ff609d6eb1c691ef3505cae8', '2024-03-27 04:05:16.702965+00', '', NULL, '', '', NULL, NULL, '{"provider": "email", "providers": ["email"]}', '{"company_id": "92e00f3a-023d-4af9-a538-8d9bd5ca1f74"}', NULL, '2024-03-27 04:05:16.685829+00', '2024-03-27 04:05:17.131373+00', NULL, NULL, '', '', NULL, '', 0, NULL, '', NULL, false, NULL, false),
	('00000000-0000-0000-0000-000000000000', '31432d66-d3b7-4d65-baaf-044684da0686', 'authenticated', 'authenticated', 'superuser@admin.com', '', '2024-03-07 18:27:22.528293+00', '2024-03-06 06:10:07.183428+00', '', '2024-03-06 06:10:07.183428+00', 'pkce_6f4ec853423384ba99f49de5e4a7ccf6998b1218b9850c8e1ae282f9', '2024-03-27 20:34:40.540119+00', '', '', NULL, '2024-03-27 12:52:30.605632+00', '{"provider": "email", "providers": ["email"]}', '{"role": "superadmin", "company_id": "92e00f3a-023d-4af9-a538-8d9bd5ca1f74"}', NULL, '2024-03-06 06:10:07.17638+00', '2024-03-27 20:34:41.11057+00', NULL, NULL, '', '', NULL, '', 0, NULL, '', NULL, false, NULL, false);

--
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

--INSERT INTO "auth"."sessions" ("id", "user_id", "created_at", "updated_at", "factor_id", "aal", "not_after", "refreshed_at", "user_agent", "ip", "tag") VALUES

--
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

--INSERT INTO "auth"."mfa_amr_claims" ("session_id", "created_at", "updated_at", "authentication_method", "id") VALUES


--
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

--INSERT INTO "auth"."refresh_tokens" ("instance_id", "id", "token", "user_id", "revoked", "created_at", "updated_at", "parent", "session_id") VALUES
	

--
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: key; Type: TABLE DATA; Schema: pgsodium; Owner: supabase_admin
--



--
-- Data for Name: secrets; Type: TABLE DATA; Schema: vault; Owner: supabase_admin
--



--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: supabase_auth_admin
--

-- You only need this line if you are restoring or seeding data into the "auth.refresh_tokens" table
-- and want to ensure that the sequence for the "id" column continues from the correct value (388 in this case).
-- If you are not restoring data or do not care about the next "id" value, you can safely remove this line.
SELECT pg_catalog.setval('"auth"."refresh_tokens_id_seq"', 388, true);


--
-- Name: key_key_id_seq; Type: SEQUENCE SET; Schema: pgsodium; Owner: supabase_admin
--



--
-- Name: eeu_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."eeu_data_id_seq"', 2478, true);


--
-- Name: enum_climate_zones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_climate_zones_id_seq"', 18, true);


--
-- Name: enum_energy_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_energy_codes_id_seq"', 31, true);


--
-- Name: enum_project_construction_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_project_construction_categories_id_seq"', 3, true);


--
-- Name: enum_project_phases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_project_phases_id_seq"', 7, true);


--
-- Name: enum_project_use_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_project_use_types_id_seq"', 25, true);


--
-- Name: enum_report_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_report_types_id_seq"', 8, true);


--
-- Name: enum_upload_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."enum_upload_statuses_id_seq"', 1, false);


--
-- Name: uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."uploads_id_seq"', 1561, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."users_id_seq"', 3, true);


--
-- PostgreSQL database dump complete
--

RESET ALL;
