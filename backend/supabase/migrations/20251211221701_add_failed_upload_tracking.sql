-- Add fields to uploads table for failed upload tracking
ALTER TABLE "public"."uploads" 
ADD COLUMN IF NOT EXISTS "file_url" text,
ADD COLUMN IF NOT EXISTS "file_name" text,
ADD COLUMN IF NOT EXISTS "processing_error" text,
ADD COLUMN IF NOT EXISTS "notified_admin" boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS "notified_user_complete" boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS "baseline_status" text,
ADD COLUMN IF NOT EXISTS "design_status" text;

-- Populate enum_upload_statuses with status values
INSERT INTO "public"."enum_upload_statuses" ("name", "order") 
VALUES 
  ('pending', 1),
  ('processing', 2),
  ('failed', 3),
  ('completed', 4)
ON CONFLICT DO NOTHING;


