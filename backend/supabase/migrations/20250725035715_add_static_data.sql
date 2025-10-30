
--
-- Data for Name: ddx_energy_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."ddx_energy_codes" ("id", "created_at", "ddx_energy_code") VALUES
	(1, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-1999'),
	(2, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2001'),
	(3, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2004'),
	(4, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2007'),
	(5, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2010'),
	(6, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2013'),
	(7, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2016'),
	(8, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2019'),
	(9, '2025-06-08 04:43:59.439093+00', 'ASHRAE 189.1-2020'),
	(10, '2025-06-08 04:43:59.439093+00', 'California Title 24 2005 for high rise residential'),
	(11, '2025-06-08 04:43:59.439093+00', 'California Title 24 2005 for single family residential'),
	(12, '2025-06-08 04:43:59.439093+00', 'California Title 24 2008'),
	(13, '2025-06-08 04:43:59.439093+00', 'California Title 24 2010'),
	(14, '2025-06-08 04:43:59.439093+00', 'California Title 24 2013'),
	(15, '2025-06-08 04:43:59.439093+00', 'California Title 24 2016'),
	(16, '2025-06-08 04:43:59.439093+00', 'California Title 24 2019'),
	(17, '2025-06-08 04:43:59.439093+00', 'California Title 24 Non Residential 2008'),
	(18, '2025-06-08 04:43:59.439093+00', 'California Title 24 Residential 2005'),
	(19, '2025-06-08 04:43:59.439093+00', 'California Title 24 Residential 2008'),
	(20, '2025-06-08 04:43:59.439093+00', 'California Title 24 2022'),
	(21, '2025-06-08 04:43:59.439093+00', 'IECC 2003'),
	(22, '2025-06-08 04:43:59.439093+00', 'IECC 2006'),
	(23, '2025-06-08 04:43:59.439093+00', 'IECC 2009'),
	(24, '2025-06-08 04:43:59.439093+00', 'IECC 2012'),
	(25, '2025-06-08 04:43:59.439093+00', 'IECC 2015'),
	(26, '2025-06-08 04:43:59.439093+00', 'IECC 2018'),
	(27, '2025-06-08 04:43:59.439093+00', 'IECC 2021'),
	(28, '2025-06-08 04:43:59.439093+00', 'NECB 2011'),
	(29, '2025-06-08 04:43:59.439093+00', 'NECB 2015'),
	(30, '2025-06-08 04:43:59.439093+00', 'NECB 2017'),
	(31, '2025-06-08 04:43:59.439093+00', 'New York Stretch Code 2018'),
	(32, '2025-06-08 04:43:59.439093+00', 'Older than 1999'),
	(33, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Code'),
	(34, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Code 2010'),
	(35, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Code 2014'),
	(36, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Efficiency Specialty Code 2010'),
	(37, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Efficiency Specialty Code 2014'),
	(38, '2025-06-08 04:43:59.439093+00', 'Washington Energy Code'),
	(39, '2025-06-08 04:43:59.439093+00', 'Washington Energy Code 2012'),
	(40, '2025-06-08 04:43:59.439093+00', 'Washington Energy Code 2015'),
	(41, '2025-06-08 04:43:59.439093+00', 'ASHRAE 90.1-2022'),
	(42, '2025-06-08 04:43:59.439093+00', 'Massachusetts Stretch Code 2017'),
	(43, '2025-06-08 04:43:59.439093+00', 'Massachusetts Stretch Code 2020'),
	(44, '2025-06-08 04:43:59.439093+00', 'Massachusetts Stretch Code 2023'),
	(45, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Code Non Residential 2021'),
	(46, '2025-06-08 04:43:59.439093+00', 'Oregon Energy Code Residential 2021'),
	(47, '2025-06-08 04:43:59.439093+00', 'Washington Energy Code Non Residential 2021'),
	(48, '2025-06-08 04:43:59.439093+00', '2020 CoBECC 41.4'),
	(49, '2025-06-08 04:43:59.439093+00', '2021 Seattle Energy Code')
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	ddx_energy_code = EXCLUDED.ddx_energy_code;




--
-- Data for Name: ddx_phase_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."ddx_phase_types" ("id", "created_at", "ddx_phase_type") VALUES
	(1, '2025-06-06 04:18:35.123966+00', 'Concept'),
	(2, '2025-06-06 04:18:44.789646+00', 'Schematic Design'),
	(3, '2025-06-06 04:18:55.472291+00', 'Design Development'),
	(4, '2025-06-06 04:19:04.032303+00', 'Construction Documents'),
	(5, '2025-06-06 04:19:15.313737+00', 'Construction Administration')
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	ddx_phase_type = EXCLUDED.ddx_phase_type;


--
-- Data for Name: ddx_use_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."ddx_use_types" ("id", "created_at", "ddx_use_type", "baseline_eui") VALUES
	(1, '2025-06-06 03:57:06.222179+00', 'Bank/Financial Institution', 52.9),
	(2, '2025-06-06 03:57:06.222179+00', 'Courthouse', 101.2),
	(3, '2025-06-06 03:57:06.222179+00', 'Data Center', NULL),
	(4, '2025-06-06 03:57:06.222179+00', 'Education - College/University (campus-level)', 84.3),
	(5, '2025-06-06 03:57:06.222179+00', 'Education - General', 52.4),
	(6, '2025-06-06 03:57:06.222179+00', 'Education - K-12 School', 48.5),
	(7, '2025-06-06 03:57:06.222179+00', 'Food Sales - Convenience Store (w/ or w/out gas station)', 350.9),
	(8, '2025-06-06 03:57:06.222179+00', 'Food Sales - General', 231.4),
	(9, '2025-06-06 03:57:06.222179+00', 'Food Sales - Supermarket/Grocery', 196),
	(10, '2025-06-06 03:57:06.222179+00', 'Food Service - Fast Food', 402.7),
	(11, '2025-06-06 03:57:06.222179+00', 'Food Service - General', 325.6),
	(12, '2025-06-06 03:57:06.222179+00', 'Food Service - Restaurant/Cafeteria', 325.6),
	(13, '2025-06-06 03:57:06.222179+00', 'Health Care - Clinic', 64.5),
	(14, '2025-06-06 03:57:06.222179+00', 'Health Care - Hospital Inpatient', 234.3),
	(15, '2025-06-06 03:57:06.222179+00', 'Health Care - Medical Office', 97.7),
	(16, '2025-06-06 03:57:06.222179+00', 'Health Care - Nursing/Assisted Living', 99),
	(17, '2025-06-06 03:57:06.222179+00', 'Health Care - Outpatient - General', 62),
	(18, '2025-06-06 03:57:06.222179+00', 'Laboratory - recommend use of Labs21', 115.3),
	(19, '2025-06-06 03:57:06.222179+00', 'Lodging - Hotel/Motel', 63),
	(20, '2025-06-06 03:57:06.222179+00', 'Lodging - Residence Hall/Dormitory', 57.9),
	(21, '2025-06-06 03:57:06.222179+00', 'Mixed-Use', 40.1),
	(22, '2025-06-06 03:57:06.222179+00', 'Office - Large', 52.9),
	(23, '2025-06-06 03:57:06.222179+00', 'Office - Medium (< 100,000 sf)', 52.9),
	(24, '2025-06-06 03:57:06.222179+00', 'Office - Small ( < 10,000 sf)', 52.9),
	(25, '2025-06-06 03:57:06.222179+00', 'Other', 40.1),
	(26, '2025-06-06 03:57:06.222179+00', 'Parking', NULL),
	(27, '2025-06-06 03:57:06.222179+00', 'Public Assembly - Entertainment/Culture', 56.1),
	(28, '2025-06-06 03:57:06.222179+00', 'Public Assembly - General', 40.1),
	(29, '2025-06-06 03:57:06.222179+00', 'Public Assembly - Library', 71.6),
	(30, '2025-06-06 03:57:06.222179+00', 'Public Assembly - Recreation', 50.8),
	(31, '2025-06-06 03:57:06.222179+00', 'Public Assembly - Social/Meeting', 56.1),
	(32, '2025-06-06 03:57:06.222179+00', 'Public Safety - Fire/Police Station', 63.5),
	(33, '2025-06-06 03:57:06.222179+00', 'Public Safety - General', 40.1),
	(34, '2025-06-06 03:57:06.222179+00', 'Religious Worship', 30.5),
	(35, '2025-06-06 03:57:06.222179+00', 'Residential - Mid-Rise/High-Rise', 63.6),
	(36, '2025-06-06 03:57:06.222179+00', 'Residential - Mobile Homes', NULL),
	(37, '2025-06-06 03:57:06.222179+00', 'Residential - Multi-Family, 2-4 units', 59.6),
	(38, '2025-06-06 03:57:06.222179+00', 'Residential - Multi-Family, 5 or more units', 59.6),
	(39, '2025-06-06 03:57:06.222179+00', 'Residential - Single-Family Detached', NULL),
	(40, '2025-06-06 03:57:06.222179+00', 'Retail - Mall', 103.5),
	(41, '2025-06-06 03:57:06.222179+00', 'Retail - Non-mall, Vehicle Dealerships, misc.', 71.9),
	(42, '2025-06-06 03:57:06.222179+00', 'Retail Store', 51.4),
	(43, '2025-06-06 03:57:06.222179+00', 'Service (vehicle repair/service, postal service)', 47.9),
	(44, '2025-06-06 03:57:06.222179+00', 'Storage - Distribution/Shipping Center', 22.7),
	(45, '2025-06-06 03:57:06.222179+00', 'Storage - General', 20.2),
	(46, '2025-06-06 03:57:06.222179+00', 'Storage - Non-refrigerated warehouse', 22.7),
	(47, '2025-06-06 03:57:06.222179+00', 'Storage - Refrigerated warehouse', 84.1),
	(48, '2025-06-06 03:57:06.222179+00', 'Warehouse - Self-storage', 20.2)
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	ddx_use_type = EXCLUDED.ddx_use_type,
	baseline_eui = EXCLUDED.baseline_eui;
--
-- Data for Name: enum_climate_zones; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_climate_zones" ("id", "created_at", "name", "order", "description", "ddx_climate_zone") VALUES
	(3, '2024-03-22 03:11:04.013257+00', '1A', NULL, 'Very hot, humid', '1a very hot humid'),
	(4, '2024-03-22 03:11:04.013257+00', '1B', NULL, 'Very hot, dry', '1b very hot dry'),
	(5, '2024-03-22 03:11:04.013257+00', '2A', NULL, 'Hot, humid', '2a hot humid'),
	(6, '2024-03-22 03:11:04.013257+00', '2B', NULL, 'Hot, dry', '2b hot dry'),
	(7, '2024-03-22 03:11:04.013257+00', '3A', NULL, 'Warm, humid', '3a warm humid'),
	(8, '2024-03-22 03:11:04.013257+00', '3B', NULL, 'Warm, dry', '3b warm dry'),
	(9, '2024-03-22 03:11:04.013257+00', '3C', NULL, 'Warm, marine', '3c warm marine'),
	(10, '2024-03-22 03:11:04.013257+00', '4A', NULL, 'Mild, humid', '4a mixed humid'),
	(11, '2024-03-22 03:11:04.013257+00', '4B', NULL, 'Mild, dry', '4b mixed dry'),
	(12, '2024-03-22 03:11:04.013257+00', '4C', NULL, 'Mild, marine', '4c mixed marine'),
	(13, '2024-03-22 03:11:04.013257+00', '5A', NULL, 'Cool, humid', '5a cool humid'),
	(14, '2024-03-22 03:11:04.013257+00', '5B', NULL, 'Cool, dry', '5b cool dry'),
	(15, '2024-03-22 03:11:04.013257+00', '6A', NULL, 'Cold, humid', '6a cold humid'),
	(16, '2024-03-22 03:11:04.013257+00', '6B', NULL, 'Cold, dry', '6b cold dry'),
	(17, '2024-03-22 03:11:04.013257+00', '7', NULL, 'Very cold', '7 very cold'),
	(18, '2024-03-22 03:11:04.013257+00', '8', NULL, 'Sub-Arctic', '8 subarctic')
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order",
	description = EXCLUDED.description,
	ddx_climate_zone = EXCLUDED.ddx_climate_zone;



--
-- Data for Name: enum_energy_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_energy_codes" ("id", "created_at", "name", "order", "included_ddx", "ddx_energy_code_id") VALUES
	(6, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2010', NULL, true, 5),
	(37, '2025-02-26 04:17:36.536657+00', 'California Title 24 2016', NULL, true, 15),
	(38, '2025-02-26 04:17:43.594862+00', 'California Title 24 2019', NULL, true, 16),
	(39, '2025-02-26 04:17:51.051286+00', 'California Title 24 Non Residential 2008', NULL, true, 17),
	(40, '2025-02-26 04:17:58.156354+00', 'California Title 24 Residential 2005', NULL, true, 18),
	(28, '2024-02-27 04:34:57.58681+00', 'Massachusetts Stretch Code 2020', NULL, false, 43),
	(27, '2024-02-27 04:34:57.58681+00', 'Massachusetts Stretch Code 2017', NULL, false, 42),
	(25, '2024-02-27 04:34:57.58681+00', 'California Title 24 2016', NULL, true, 15),
	(29, '2024-02-27 04:34:57.58681+00', 'ASHRAE 189.1-2020', NULL, true, 9),
	(1, '2024-01-30 06:34:20.24263+00', 'Older than 1999', NULL, true, 32),
	(17, '2024-02-27 04:34:57.58681+00', 'NECB 2011', NULL, true, 28),
	(18, '2024-02-27 04:34:57.58681+00', 'NECB 2015', NULL, true, 29),
	(19, '2024-02-27 04:34:57.58681+00', 'NECB 2017', NULL, true, 30),
	(20, '2024-02-27 04:34:57.58681+00', 'Oregon 2021', NULL, false, NULL),
	(23, '2024-02-27 04:34:57.58681+00', 'Washington 2021', NULL, false, NULL),
	(24, '2024-02-27 04:34:57.58681+00', 'California Title 24 2019', NULL, true, 16),
	(7, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2013', NULL, true, 6),
	(8, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2016', NULL, true, 7),
	(9, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2019', NULL, true, 8),
	(10, '2024-02-27 04:34:57.58681+00', 'IECC 2003', NULL, true, 21),
	(11, '2024-02-27 04:34:57.58681+00', 'IECC 2006', NULL, true, 22),
	(13, '2024-02-27 04:34:57.58681+00', 'IECC 2012', NULL, true, 24),
	(12, '2024-02-27 04:34:57.58681+00', 'IECC 2009', NULL, true, 23),
	(14, '2024-02-27 04:34:57.58681+00', 'IECC 2015', NULL, true, 25),
	(15, '2024-02-27 04:34:57.58681+00', 'IECC 2018', NULL, true, 26),
	(16, '2024-02-27 04:34:57.58681+00', 'IECC 2021', NULL, true, 27),
	(26, '2024-02-27 04:34:57.58681+00', 'New York Stretch Code 2018', NULL, true, 31),
	(32, '2025-02-26 04:16:52.096843+00', 'California Title 24 2005 for high rise residential', NULL, true, 10),
	(33, '2025-02-26 04:17:03.995146+00', 'California Title 24 2005 for single family residential', NULL, true, 11),
	(34, '2025-02-26 04:17:12.724614+00', 'California Title 24 2008', NULL, true, 12),
	(35, '2025-02-26 04:17:20.979965+00', 'California Title 24 2010', NULL, true, 13),
	(36, '2025-02-26 04:17:30.236352+00', 'California Title 24 2013', NULL, true, 14),
	(44, '2025-02-26 04:18:35.407577+00', 'Oregon Energy Code', NULL, true, 33),
	(51, '2025-02-26 04:20:10.602328+00', 'Washington Energy Code 2015', NULL, true, 40),
	(49, '2025-02-26 04:19:56.284525+00', 'Washington Energy Code', NULL, true, 38),
	(50, '2025-02-26 04:20:03.094992+00', 'Washington Energy Code 2012', NULL, true, 39),
	(48, '2025-02-26 04:19:08.78752+00', 'Oregon Energy Efficiency Specialty Code 2014', NULL, true, 37),
	(47, '2025-02-26 04:18:59.996925+00', 'Oregon Energy Efficiency Specialty Code 2010', NULL, true, 36),
	(46, '2025-02-26 04:18:53.090663+00', 'Oregon Energy Code 2014', NULL, true, 35),
	(45, '2025-02-26 04:18:43.468735+00', 'Oregon Energy Code 2010', NULL, true, 34),
	(42, '2025-02-26 04:18:11.015494+00', 'California Title 24 2022', NULL, true, 20),
	(41, '2025-02-26 04:18:03.816167+00', 'California Title 24 Residential 2008', NULL, true, 19),
	(2, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-1999', NULL, true, 1),
	(3, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2001', NULL, true, 2),
	(4, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2004', NULL, true, 3),
	(5, '2024-02-27 04:34:57.58681+00', 'ASHRAE 90.1-2007', NULL, true, 4),
	(31, '2024-03-23 03:59:20.547342+00', 'Other', NULL, false, 32),
	(30, '2024-02-29 05:37:14.643785+00', 'Unknown', NULL, false, 32),
	(43, '2025-02-26 04:18:17.88067+00', 'Massachusetts Stretch Code', NULL, false, NULL)
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order",
	included_ddx = EXCLUDED.included_ddx,
	ddx_energy_code_id = EXCLUDED.ddx_energy_code_id;



--
-- Data for Name: enum_project_construction_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_project_construction_categories" ("id", "created_at", "name", "order") VALUES
	(1, '2024-01-30 06:34:01.923314+00', 'New', NULL),
	(2, '2024-01-30 06:34:08.259768+00', 'Existing', NULL)
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order";


--
-- Data for Name: enum_project_phases; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_project_phases" ("id", "created_at", "name", "order", "ddx_phase_type_id") VALUES
	(1, '2024-01-27 20:29:03.058582+00', 'Design', NULL, 3),
	(2, '2024-02-27 04:27:48.282894+00', 'Concept', NULL, 1),
	(3, '2024-02-27 04:27:48.282894+00', 'Construction Documents', NULL, 4),
	(4, '2024-02-27 04:27:48.282894+00', 'Design Development', NULL, 3),
	(5, '2024-02-27 04:27:48.282894+00', 'Final Design', NULL, 5),
	(6, '2024-02-27 04:27:48.282894+00', 'Schematic Design', NULL, 2),
	(7, '2024-02-29 05:34:15.918183+00', 'Unknown', NULL, 5)
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order",
	ddx_phase_type_id = EXCLUDED.ddx_phase_type_id;




--
-- Data for Name: enum_project_use_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_project_use_types" ("id", "created_at", "name", "order", "has_subtypes", "ddx_use_type_id") VALUES
	(2, '2024-02-27 04:24:56.704629+00', 'Airport', 1, false, NULL),
	(3, '2024-02-27 04:24:56.704629+00', 'Bank/Financial Institution', 2, false, 1),
	(4, '2024-02-27 04:24:56.704629+00', 'Courthouse', 3, false, 2),
	(5, '2024-02-27 04:24:56.704629+00', 'Data Center', 4, false, 3),
	(6, '2024-02-27 04:24:56.704629+00', 'Education - College/University (campus-level)', 5, false, 4),
	(7, '2024-02-27 04:24:56.704629+00', 'Education - K-12 School', 6, false, 6),
	(26, '2024-04-30 03:59:39.263644+00', 'Education - General', 7, false, 5),
	(27, '2024-04-30 03:59:58.913314+00', 'Food Sales - Convenience Store (w/ or w/out gas station)', 8, false, 7),
	(28, '2024-04-30 04:00:09.05905+00', 'Food Sales - Supermarket/Grocery', 9, false, 9),
	(30, '2024-04-30 04:00:39.480176+00', 'Food Service - Fast Food', 11, false, 10),
	(31, '2024-04-30 04:00:51.367564+00', 'Food Service - Restaurant/Cafeteria', 12, false, 12),
	(8, '2024-02-27 04:24:56.704629+00', 'Health Care - Hospital Inpatient', 14, false, 14),
	(9, '2024-02-27 04:24:56.704629+00', 'Health Care - Medical Office', 15, false, 15),
	(10, '2024-02-27 04:24:56.704629+00', 'Health Care - Nursing/Assisted Living', 16, false, 16),
	(11, '2024-02-27 04:24:56.704629+00', 'Health Care - Outpatient - General', 17, false, 17),
	(14, '2024-02-27 04:24:56.704629+00', 'Lodging - Hotel/Motel', 20, false, 19),
	(15, '2024-02-27 04:24:56.704629+00', 'Lodging - Residence Hall/Dormitory', 21, false, 20),
	(16, '2024-02-27 04:24:56.704629+00', 'Mixed-Use', 23, false, 21),
	(34, '2024-04-30 04:02:13.542401+00', 'Other', 25, false, 25),
	(18, '2024-02-27 04:24:56.704629+00', 'Public Assembly - Entertainment/Culture', 26, false, 27),
	(35, '2024-04-30 04:02:46.077638+00', 'Public Assembly - Social/Meeting', 27, false, 31),
	(22, '2024-02-27 04:24:56.704629+00', 'Public Safety - Fire/Police Station', 31, false, 32),
	(36, '2024-04-30 04:03:41.318347+00', 'Religious Worship', 33, false, 34),
	(24, '2024-02-27 04:24:56.704629+00', 'Residential - Mid-Rise/High-Rise', 34, false, 35),
	(37, '2024-04-30 04:04:11.218564+00', 'Residential - Mobile Homes', 35, false, 36),
	(39, '2024-04-30 04:04:37.619538+00', 'Residential - Multi-Family, 5 or more units', 37, false, 38),
	(50, '2024-04-30 04:08:03.487443+00', 'Residential - Single-Family Detached', 39, false, 39),
	(51, '2024-04-30 04:08:03.487443+00', 'Retail - Non-mall, Vehicle Dealerships, misc.', 40, false, 41),
	(53, '2024-04-30 04:08:03.487443+00', 'Retail Store', 42, false, 42),
	(54, '2024-04-30 04:08:03.487443+00', 'Storage - Distribution/Shipping Center', 44, false, 44),
	(55, '2024-04-30 04:08:03.487443+00', 'Storage - Non-refrigerated warehouse', 45, false, 46),
	(56, '2024-04-30 04:08:03.487443+00', 'Storage - Refrigerated warehouse', 46, false, 47),
	(58, '2024-04-30 04:08:03.487443+00', 'Warehouse - Self-storage', 48, false, 48),
	(25, '2024-02-27 04:24:56.704629+00', 'Service (vehicle repair/service, postal service)', 43, false, 43),
	(12, '2024-02-27 04:24:56.704629+00', 'Health Care - Clinic', 18, false, 13),
	(32, '2024-04-30 04:01:02.821847+00', 'Food Service - General', 13, false, 11),
	(20, '2024-02-27 04:24:56.704629+00', 'Public Assembly - Library', 29, false, 29),
	(19, '2024-02-27 04:24:56.704629+00', 'Public Assembly - General', 28, false, 28),
	(21, '2024-02-27 04:24:56.704629+00', 'Public Assembly - Recreation', 30, false, 30),
	(23, '2024-02-27 04:24:56.704629+00', 'Public Safety - General', 32, false, 33),
	(52, '2024-04-30 04:08:03.487443+00', 'Retail - Mall', 41, false, 40),
	(57, '2024-04-30 04:08:03.487443+00', 'Storage - General', 47, false, 45),
	(29, '2024-04-30 04:00:22.340006+00', 'Food Sales - General', 10, false, 8),
	(33, '2024-04-30 04:01:47.944565+00', 'Lodging - General', 22, false, 19),
	(38, '2024-04-30 04:04:26.690994+00', 'Residential - Multi-Family, 2 to 4 units', 36, false, 37),
	(13, '2024-02-27 04:24:56.704629+00', 'Laboratory', 19, true, 18),
	(17, '2024-02-27 04:24:56.704629+00', 'Office', 24, false, 23)
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order",
	has_subtypes = EXCLUDED.has_subtypes,
	ddx_use_type_id = EXCLUDED.ddx_use_type_id;



--
-- Data for Name: enum_use_type_subtypes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_use_type_subtypes" ("id", "created_at", "name", "use_type_id", "order") VALUES
	(1, '2024-06-01 20:39:09.991465+00', 'Computer Lab', 13, NULL),
	(2, '2024-06-01 20:39:28.834383+00', 'Pharmaceutical', 13, NULL)
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	use_type_id = EXCLUDED.use_type_id,
	"order" = EXCLUDED."order";




--
-- Data for Name: enum_report_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."enum_report_types" ("id", "created_at", "name", "order", "identifier_name", "file_type", "ddx_report_type_name") VALUES
	(7, '2024-02-01 02:56:48.790844+00', 'Other', NULL, 'other', NULL, 'EnergyPlus Other'),
	(8, '2024-02-28 04:26:56.049239+00', 'IESVE PRM', NULL, 'iesve_prm', '.pdf', 'IES - Virtual Environment'),
	(1, '2024-01-27 04:23:04.671682+00', 'IESVE', NULL, 'iesve', '.pdf', 'IES - Virtual Environment'),
	(3, '2024-02-01 02:56:08.740667+00', 'EQuest - SIM Report', NULL, 'sim', '.sim', 'DOE-2.2 eQuest'),
	(5, '2024-02-01 02:56:28.783792+00', 'EQuest - BEPS Report', NULL, 'equest_beps', '.pdf', 'DOE-2.2 eQuest'),
	(6, '2024-02-01 02:56:40.867302+00', 'EQuest - Standard Report', NULL, 'equest_standard', '.pdf', 'DOE-2.2 eQuest'),
	(4, '2024-02-01 02:56:17.268106+00', 'Generic .XLSX', NULL, 'generic_xlsx', '.xlsx', 'EnergyPlus Other'),
	(2, '2024-02-01 02:55:56.02628+00', 'EnergyPlus Report', NULL, 'eplus', '.html', 'EnergyPlus Other')
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order",
	identifier_name = EXCLUDED.identifier_name,
	file_type = EXCLUDED.file_type,
	ddx_report_type_name = EXCLUDED.ddx_report_type_name;




--
-- Data for Name: eeu_fields; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."eeu_fields" ("field_name", "fuel_category", "fuel_type", "id", "use_type") VALUES
	('Heating_Electricity', 'electricity', 'Electricity', 1, 'Heating'),
	('Heating_NaturalGas', 'fossil_fuels', 'Natural Gas', 2, 'Heating'),
	('Heating_DistrictHeating', 'district', 'District Heating', 3, 'Heating'),
	('Cooling_Electricity', 'electricity', 'Electricity', 5, 'Cooling'),
	('Cooling_DistrictHeating', 'district', 'District Heating', 6, 'Cooling'),
	('DHW_Electricity', 'electricity', 'Electricity', 8, 'DHW'),
	('DHW_NaturalGas', 'fossil_fuels', 'Natural Gas', 9, 'DHW'),
	('total_Electricity', 'electricity', 'Electricity', 32, 'Total'),
	('HeatRecovery_Electricity', 'electricity', 'Electricity', 26, 'Heat Recovery'),
	('Humidification_Electricity', 'electricity', 'Electricity', 25, 'Humidification'),
	('Heat Rejection_Electricity', 'electricity', 'Electricity', 24, 'Heat Rejection'),
	('total_NaturalGas', 'fossil_fuels', 'Natural Gas', 33, 'Total'),
	('total_DistrictHeating', 'district', 'District Heating', 34, 'Total'),
	('OtherEndUse_NaturalGas', 'fossil_fuels', 'Natural Gas', 22, 'Other End Use'),
	('OtherEndUse_Electricity', 'electricity', 'Electricity', 21, 'Other End Use'),
	('ExteriorUsage_NaturalGas', 'fossil_fuels', 'Natural Gas', 20, 'Exterior Usage'),
	('ExteriorUsage_Electricity', 'electricity', 'Electricity', 19, 'Exterior Usage'),
	('Process Refrigeration_Electricity', 'electricity', 'Electricity', 18, 'Process Refrigeration'),
	('Pumps_NaturalGas', 'fossil_fuels', 'Natural Gas', 17, 'Pumps'),
	('Pumps_Electricity', 'electricity', 'Electricity', 16, 'Pumps'),
	('Fans_Electricity', 'electricity', 'Electricity', 15, 'Fans'),
	('Plug Loads_Electricity', 'electricity', 'Electricity', 14, 'Plug Loads'),
	('Exterior Lighting_Electricity', 'electricity', 'Electricity', 13, 'Exterior Lighting'),
	('Interior Lighting_Electricity', 'electricity', 'Electricity', 12, 'Interior Lighting'),
	('DHW_DistrictHeating', 'district', 'District Heating', 10, 'DHW'),
	('Heating_Other', 'other', 'Other', 4, 'Heating'),
	('Cooling_Other', 'other', 'Other', 7, 'Cooling'),
	('total_Other', 'other', 'Other', 35, 'Total'),
	('OtherEndUse_Other', 'other', 'Other', 23, 'Other End Use'),
	('HeatRecovery_Other', 'other', 'Other', 27, 'Heat Recovery'),
	('DHW_Other', 'other', 'Other', 11, 'DHW'),
	('Other_On-SiteRenewables', 'onsite_renewables', 'On-Site Renewables', 31, 'Other On-Site Renewables'),
	('Wind_On-SiteRenewables', 'onsite_renewables', 'On-Site Renewables', 30, 'Wind On-Site Renewables'),
	('SolarPV_On-SiteRenewables', 'onsite_renewables', 'On-Site Renewables', 29, 'Solar PV On-Site Renewables'),
	('SolarDHW_On-SiteRenewables', 'onsite_renewables', 'On-Site Renewables', 28, 'Solar DHW On-Site Renewables'),
	('total_energy', NULL, 'Total Energy', 37, 'Total Energy'),
	('total_On-SiteRenewables', NULL, 'On-Site Renewables', 36, 'Total')
ON CONFLICT (id) DO UPDATE SET
	field_name = EXCLUDED.field_name,
	fuel_category = EXCLUDED.fuel_category,
	fuel_type = EXCLUDED.fuel_type,
	use_type = EXCLUDED.use_type;



--
-- Data for Name: column_metadata; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."column_metadata" ("id", "table_name", "column_name", "has_units", "unit_type", "conversion_needed") VALUES
	(1, 'column_metadata', 'id', false, NULL, false),
	(2, 'column_metadata', 'has_units', false, NULL, false),
	(3, 'column_metadata', 'conversion_needed', false, NULL, false),
	(4, 'latest_project_uploads5', 'company_id', false, NULL, false),
	(5, 'latest_project_uploads5', 'id', false, NULL, false),
	(6, 'project_energy_summary', 'project_id', false, NULL, false),
	(9, 'project_energy_summary', 'company_id', false, NULL, false),
	(10, 'project_latest_upload_by_type5', 'project_id', false, NULL, false),
	(11, 'project_latest_upload_by_type5', 'upload_created_at', false, NULL, false),
	(12, 'project_latest_upload_by_type5', 'id', false, NULL, false),
	(13, 'project_latest_upload_by_type5', 'upload_id', false, NULL, false),
	(14, 'project_latest_upload_by_type5', 'rn', false, NULL, false),
	(15, 'project_latest_upload_by_type5', 'company_id', false, NULL, false),
	(16, 'companies', 'created_at', false, NULL, false),
	(17, 'companies', 'id', false, NULL, false),
	(18, 'eeu_data', 'id', false, NULL, false),
	(19, 'eeu_data', 'upload_id', false, NULL, false),
	(20, 'eeu_data', 'created_at', false, NULL, false),
	(21, 'eeu_data', 'updated_at', false, NULL, false),
	(22, 'enum_climate_zones', 'id', false, NULL, false),
	(23, 'enum_climate_zones', 'created_at', false, NULL, false),
	(24, 'enum_climate_zones', 'order', false, NULL, false),
	(25, 'enum_energy_codes', 'id', false, NULL, false),
	(26, 'enum_energy_codes', 'created_at', false, NULL, false),
	(27, 'enum_energy_codes', 'order', false, NULL, false),
	(28, 'enum_project_construction_categories', 'id', false, NULL, false),
	(29, 'enum_project_construction_categories', 'created_at', false, NULL, false),
	(30, 'enum_project_construction_categories', 'order', false, NULL, false),
	(31, 'enum_project_phases', 'id', false, NULL, false),
	(32, 'enum_project_phases', 'created_at', false, NULL, false),
	(33, 'enum_project_phases', 'order', false, NULL, false),
	(34, 'enum_project_use_types', 'id', false, NULL, false),
	(35, 'enum_project_use_types', 'created_at', false, NULL, false),
	(36, 'enum_project_use_types', 'order', false, NULL, false),
	(37, 'enum_report_types', 'id', false, NULL, false),
	(38, 'enum_report_types', 'created_at', false, NULL, false),
	(39, 'enum_report_types', 'order', false, NULL, false),
	(40, 'enum_upload_statuses', 'id', false, NULL, false),
	(41, 'enum_upload_statuses', 'created_at', false, NULL, false),
	(42, 'enum_upload_statuses', 'order', false, NULL, false),
	(43, 'profiles', 'id', false, NULL, false),
	(44, 'profiles', 'company_id', false, NULL, false),
	(45, 'profiles', 'confirmed_at', false, NULL, false),
	(46, 'profiles', 'last_sign_in_at', false, NULL, false),
	(47, 'projects', 'created_at', false, NULL, false),
	(48, 'projects', 'climate_zone_id', false, NULL, false),
	(50, 'projects', 'project_construction_category_id', false, NULL, false),
	(51, 'projects', 'project_use_type_id', false, NULL, false),
	(52, 'projects', 'company_id', false, NULL, false),
	(53, 'projects', 'id', false, NULL, false),
	(54, 'uploads', 'id', false, NULL, false),
	(55, 'uploads', 'created_at', false, NULL, false),
	(56, 'uploads', 'area', false, NULL, false),
	(57, 'uploads', 'climate_zone_id', false, NULL, false),
	(58, 'uploads', 'user_id', false, NULL, false),
	(59, 'uploads', 'project_phase_id', false, NULL, false),
	(60, 'uploads', 'report_type_id', false, NULL, false),
	(61, 'uploads', 'upload_status_id', false, NULL, false),
	(62, 'uploads', 'energy_code_id', false, NULL, false),
	(63, 'uploads', 'project_construction_category_id', false, NULL, false),
	(64, 'uploads', 'project_id', false, NULL, false),
	(65, 'uploads', 'project_use_type_id', false, NULL, false),
	(66, 'uploads', 'company_id', false, NULL, false),
	(67, 'uploads', 'id_uuid', false, NULL, false),
	(68, 'uploads', 'year', false, NULL, false),
	(209, 'uploads', 'reporting_year', false, NULL, false),
	(69, 'users', 'id', false, NULL, false),
	(70, 'users', 'created_at', false, NULL, false),
	(71, 'users', 'company_id', false, NULL, false),
	(72, 'project_latest_upload_by_type5', 'weather_station', false, NULL, false),
	(73, 'project_latest_upload_by_type5', 'climate_zone', false, NULL, false),
	(74, 'project_latest_upload_by_type5', 'file_url', false, NULL, false),
	(75, 'enum_project_construction_categories', 'name', false, NULL, false),
	(76, 'project_latest_upload_by_type5', 'baseline_design', false, NULL, false),
	(77, 'uploads', 'other_energy_code', false, NULL, false),
	(78, 'users', 'user_first', false, NULL, false),
	(79, 'project_latest_upload_by_type5', 'project_construction_category', false, NULL, false),
	(80, 'project_latest_upload_by_type5', 'project_use_type', false, NULL, false),
	(81, 'project_latest_upload_by_type5', 'project_phase', false, NULL, false),
	(82, 'profiles', 'first_name', false, NULL, false),
	(83, 'companies', 'company_name', false, NULL, false),
	(84, 'companies', 'company_domain', false, NULL, false),
	(85, 'enum_project_phases', 'name', false, NULL, false),
	(86, 'profiles', 'last_name', false, NULL, false),
	(87, 'eeu_data', 'report_type', false, NULL, false),
	(90, 'eeu_data', 'energy_units', false, NULL, false),
	(137, 'eeu_data', 'upload_warnings', false, '', false),
	(138, 'eeu_data', 'upload_errors', false, '', false),
	(139, 'column_metadata', 'table_name', false, '', false),
	(140, 'column_metadata', 'column_name', false, '', false),
	(141, 'users', 'user_last', false, '', false),
	(142, 'column_metadata', 'original_unit', false, '', false),
	(143, 'uploads', 'area_units', false, '', false),
	(144, 'latest_project_uploads5', 'project_name', false, '', false),
	(145, 'latest_project_uploads5', 'report_type', false, '', false),
	(146, 'latest_project_uploads5', 'energy_code', false, '', false),
	(147, 'enum_climate_zones', 'name', false, '', false),
	(148, 'profiles', 'role', false, '', false),
	(149, 'enum_climate_zones', 'description', false, '', false),
	(150, 'project_energy_summary', 'project_name', false, '', false),
	(151, 'project_energy_summary', 'report_type', false, '', false),
	(152, 'project_energy_summary', 'climate_zone', false, '', false),
	(153, 'enum_report_types', 'name', false, '', false),
	(154, 'users', 'user_email', false, '', false),
	(156, 'enum_energy_codes', 'name', false, '', false),
	(157, 'project_energy_summary', 'project_phase', false, '', false),
	(158, 'project_energy_summary', 'project_use_type', false, '', false),
	(162, 'projects', 'project_name', false, '', false),
	(163, 'project_latest_upload_by_type5', 'proj_name', false, '', false),
	(164, 'uploads', 'design_baseline_type', false, '', false),
	(165, 'enum_upload_statuses', 'name', false, '', false),
	(166, 'project_latest_upload_by_type5', 'report_type', false, '', false),
	(94, 'eeu_data', 'Heating_Other', true, 'energy', true),
	(169, 'project_latest_upload_by_type5', 'energy_units', false, '', false),
	(207, 'project_latest_upload_by_type5', 'project_name', false, NULL, false),
	(208, 'project_latest_upload_by_type5', 'weather_string', false, NULL, false),
	(128, 'eeu_data', 'project_name', false, '', false),
	(129, 'eeu_data', 'weather_string', false, '', false),
	(130, 'eeu_data', 'weather_station', false, '', false),
	(131, 'eeu_data', 'climate_zone', false, '', false),
	(132, 'eeu_data', 'file_url', false, '', false),
	(133, 'profiles', 'email', false, '', false),
	(8, 'project_energy_summary', 'total_energy_per_unit_area_design', true, 'eui', true),
	(134, 'eeu_data', 'baseline_design', false, '', false),
	(135, 'uploads', 'climate_zone_str', false, '', false),
	(136, 'enum_project_use_types', 'name', false, '', false),
	(92, 'eeu_data', 'Heating_NaturalGas', true, 'energy', true),
	(93, 'eeu_data', 'Heating_DistrictHeating', true, 'energy', true),
	(89, 'eeu_data', 'area_units', true, NULL, true),
	(88, 'eeu_data', 'use_type_total_area', true, 'area', true),
	(49, 'projects', 'conditioned_area_sf', true, NULL, true),
	(155, 'project_energy_summary', 'conditioned_area', true, 'area', true),
	(97, 'eeu_data', 'Cooling_Other', true, 'energy', true),
	(91, 'eeu_data', 'Heating_Electricity', true, 'energy', true),
	(167, 'project_latest_upload_by_type5', 'use_type_total_area', true, 'area', true),
	(168, 'project_latest_upload_by_type5', 'area_units', true, 'area', true),
	(160, 'project_energy_summary', 'total_energy_design', true, 'energy', true),
	(98, 'eeu_data', 'DHW_Electricity', true, 'energy', true),
	(161, 'project_energy_summary', 'renewables', false, '', false),
	(159, 'project_energy_summary', 'total_energy_baseline', true, 'energy', true),
	(95, 'eeu_data', 'Cooling_Electricity', true, 'energy', true),
	(96, 'eeu_data', 'Cooling_DistrictHeating', true, 'energy', true),
	(99, 'eeu_data', 'DHW_NaturalGas', true, 'energy', true),
	(100, 'eeu_data', 'DHW_DistrictHeating', true, 'energy', true),
	(101, 'eeu_data', 'DHW_Other', true, 'energy', true),
	(102, 'eeu_data', 'Interior Lighting_Electricity', true, 'energy', true),
	(103, 'eeu_data', 'Exterior Lighting_Electricity', true, 'energy', true),
	(104, 'eeu_data', 'Plug Loads_Electricity', true, 'energy', true),
	(105, 'eeu_data', 'Fans_Electricity', true, 'energy', true),
	(106, 'eeu_data', 'Pumps_Electricity', true, 'energy', true),
	(107, 'eeu_data', 'Pumps_NaturalGas', true, 'energy', true),
	(108, 'eeu_data', 'Process Refrigeration_Electricity', true, 'energy', true),
	(109, 'eeu_data', 'ExteriorUsage_Electricity', true, 'energy', true),
	(110, 'eeu_data', 'ExteriorUsage_NaturalGas', true, 'energy', true),
	(111, 'eeu_data', 'OtherEndUse_Electricity', true, 'energy', true),
	(112, 'eeu_data', 'OtherEndUse_NaturalGas', true, 'energy', true),
	(113, 'eeu_data', 'OtherEndUse_Other', true, 'energy', true),
	(114, 'eeu_data', 'Heat Rejection_Electricity', true, 'energy', true),
	(115, 'eeu_data', 'Humidification_Electricity', true, 'energy', true),
	(116, 'eeu_data', 'HeatRecovery_Electricity', true, 'energy', true),
	(117, 'eeu_data', 'HeatRecovery_Other', true, 'energy', true),
	(118, 'eeu_data', 'SolarDHW_On-SiteRenewables', true, 'energy', true),
	(119, 'eeu_data', 'SolarPV_On-SiteRenewables', true, 'energy', true),
	(120, 'eeu_data', 'Wind_On-SiteRenewables', true, 'energy', true),
	(121, 'eeu_data', 'Other_On-SiteRenewables', true, 'energy', true),
	(122, 'eeu_data', 'total_Electricity', true, 'energy', true),
	(123, 'eeu_data', 'total_NaturalGas', true, 'energy', true),
	(124, 'eeu_data', 'total_DistrictHeating', true, 'energy', true),
	(125, 'eeu_data', 'total_Other', true, 'energy', true),
	(126, 'eeu_data', 'total_On-SiteRenewables', true, 'energy', true),
	(127, 'eeu_data', 'total_energy', true, 'energy', true),
	(170, 'project_latest_upload_by_type5', 'Heating_Electricity', true, 'energy', true),
	(171, 'project_latest_upload_by_type5', 'Heating_NaturalGas', true, 'energy', true),
	(172, 'project_latest_upload_by_type5', 'Heating_DistrictHeating', true, 'energy', true),
	(173, 'project_latest_upload_by_type5', 'Heating_Other', true, 'energy', true),
	(174, 'project_latest_upload_by_type5', 'Cooling_Electricity', true, 'energy', true),
	(175, 'project_latest_upload_by_type5', 'Cooling_DistrictHeating', true, 'energy', true),
	(176, 'project_latest_upload_by_type5', 'Cooling_Other', true, 'energy', true),
	(177, 'project_latest_upload_by_type5', 'DHW_Electricity', true, 'energy', true),
	(178, 'project_latest_upload_by_type5', 'DHW_NaturalGas', true, 'energy', true),
	(179, 'project_latest_upload_by_type5', 'DHW_DistrictHeating', true, 'energy', true),
	(180, 'project_latest_upload_by_type5', 'DHW_Other', true, 'energy', true),
	(181, 'project_latest_upload_by_type5', 'Interior Lighting_Electricity', true, 'energy', true),
	(182, 'project_latest_upload_by_type5', 'Exterior Lighting_Electricity', true, 'energy', true),
	(183, 'project_latest_upload_by_type5', 'Plug Loads_Electricity', true, 'energy', true),
	(184, 'project_latest_upload_by_type5', 'Fans_Electricity', true, 'energy', true),
	(185, 'project_latest_upload_by_type5', 'Pumps_Electricity', true, 'energy', true),
	(186, 'project_latest_upload_by_type5', 'Pumps_NaturalGas', true, 'energy', true),
	(187, 'project_latest_upload_by_type5', 'Process Refrigeration_Electricity', true, 'energy', true),
	(188, 'project_latest_upload_by_type5', 'ExteriorUsage_Electricity', true, 'energy', true),
	(189, 'project_latest_upload_by_type5', 'ExteriorUsage_NaturalGas', true, 'energy', true),
	(190, 'project_latest_upload_by_type5', 'OtherEndUse_Electricity', true, 'energy', true),
	(191, 'project_latest_upload_by_type5', 'OtherEndUse_NaturalGas', true, 'energy', true),
	(192, 'project_latest_upload_by_type5', 'OtherEndUse_Other', true, 'energy', true),
	(193, 'project_latest_upload_by_type5', 'Heat Rejection_Electricity', true, 'energy', true),
	(194, 'project_latest_upload_by_type5', 'Humidification_Electricity', true, 'energy', true),
	(195, 'project_latest_upload_by_type5', 'HeatRecovery_Electricity', true, 'energy', true),
	(196, 'project_latest_upload_by_type5', 'HeatRecovery_Other', true, 'energy', true),
	(197, 'project_latest_upload_by_type5', 'SolarDHW_On-SiteRenewables', true, 'energy', true),
	(198, 'project_latest_upload_by_type5', 'SolarPV_On-SiteRenewables', true, 'energy', true),
	(199, 'project_latest_upload_by_type5', 'Wind_On-SiteRenewables', true, 'energy', true),
	(200, 'project_latest_upload_by_type5', 'Other_On-SiteRenewables', true, 'energy', true),
	(201, 'project_latest_upload_by_type5', 'total_Electricity', true, 'energy', true),
	(202, 'project_latest_upload_by_type5', 'total_NaturalGas', true, 'energy', true),
	(203, 'project_latest_upload_by_type5', 'total_DistrictHeating', true, 'energy', true),
	(204, 'project_latest_upload_by_type5', 'total_Other', true, 'energy', true),
	(205, 'project_latest_upload_by_type5', 'total_On-SiteRenewables', true, 'energy', true),
	(206, 'project_latest_upload_by_type5', 'total_energy', true, 'energy', true),
	(7, 'project_energy_summary', 'total_energy_per_unit_area_baseline', true, 'eui', true)
ON CONFLICT (id) DO UPDATE SET
	table_name = EXCLUDED.table_name,
	column_name = EXCLUDED.column_name,
	has_units = EXCLUDED.has_units,
	unit_type = EXCLUDED.unit_type,
	conversion_needed = EXCLUDED.conversion_needed;

--