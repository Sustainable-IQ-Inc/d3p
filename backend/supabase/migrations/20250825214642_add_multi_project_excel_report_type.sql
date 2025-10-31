-- Add multi-project Excel report type
INSERT INTO "public"."enum_report_types" ("id", "created_at", "name", "order", "identifier_name", "file_type", "ddx_report_type_name") VALUES
	(9, NOW(), 'Multi-Project Excel', NULL, 'multi_project_xlsx', '.xlsx', 'Other')
ON CONFLICT (id) DO UPDATE SET
	created_at = EXCLUDED.created_at,
	name = EXCLUDED.name,
	"order" = EXCLUDED."order",
	identifier_name = EXCLUDED.identifier_name,
	file_type = EXCLUDED.file_type,
	ddx_report_type_name = EXCLUDED.ddx_report_type_name;
