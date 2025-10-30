-- Add unique constraint on visualization_name column
ALTER TABLE "public"."data_viz_chart_options" 
ADD CONSTRAINT "data_viz_chart_options_visualization_name_key" 
UNIQUE ("visualization_name");

--
-- Data for Name: data_viz_chart_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."data_viz_chart_options" ("visualization_name", "x_axis_field", "y_axis_field") VALUES
	('Total Energy vs Building Area', 'use_type_total_area', 'total_energy'),
	('Building Size vs Energy Intensity', 'use_type_total_area', 'total_energy'),
	('HVAC Fans vs Building Area', 'Fans_Electricity', 'use_type_total_area')
ON CONFLICT (visualization_name) DO UPDATE SET
	x_axis_field = EXCLUDED.x_axis_field,
	y_axis_field = EXCLUDED.y_axis_field;

