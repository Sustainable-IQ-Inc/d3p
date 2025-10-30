alter table "public"."data_viz_chart_options" add column "x_axis_label" text;

alter table "public"."data_viz_chart_options" add column "x_axis_units" text;

alter table "public"."data_viz_chart_options" add column "y_axis_label" text;

alter table "public"."data_viz_chart_options" add column "y_axis_units" text;


UPDATE "public"."data_viz_chart_options" 
SET 
    y_axis_label = 'Energy Intensity',
    x_axis_label = 'Building Area',
    y_axis_units = 'kBtu/SF',
    x_axis_units = 'SF'
WHERE visualization_name = 'Total Energy vs Building Area';

UPDATE "public"."data_viz_chart_options" 
SET 
    y_axis_label = 'Energy Intensity',
    x_axis_label = 'Building Area', 
    y_axis_units = 'kBtu/SF',
    x_axis_units = 'SF'
WHERE visualization_name = 'Building Size vs Energy Intensity';

UPDATE "public"."data_viz_chart_options" 
SET 
    y_axis_label = 'Building Area',
    x_axis_label = 'Fans Intensity',
    y_axis_units = 'SF',
    x_axis_units = 'kBtu/SF'
WHERE visualization_name = 'HVAC Fans vs Building Area';