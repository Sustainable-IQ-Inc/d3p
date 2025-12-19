-- Add user_id (UUID) field to projects, eeu_data, and uploads tables
-- This stores the authenticated user's UUID from the auth system
-- Note: uploads already has a bigint user_id field that references the old users table,
-- so we're adding a UUID field for the auth user_id

-- Add user_id to projects table
alter table "public"."projects" add column if not exists "user_id" uuid;

-- Add user_id and company_id to eeu_data table
alter table "public"."eeu_data" add column if not exists "user_id" uuid;
alter table "public"."eeu_data" add column if not exists "company_id" uuid;

-- Add auth_user_id to uploads table (UUID from auth system)
-- Note: uploads already has user_id (bigint) for the old users table
-- We add auth_user_id as UUID to store the authenticated user
alter table "public"."uploads" add column if not exists "auth_user_id" uuid;

-- Add foreign key constraints
-- user_id in projects and eeu_data should reference auth.users (via profiles.id)
-- Note: We don't add a foreign key constraint because user_id references auth.users.id
-- which is in a different schema, and Supabase handles this relationship via profiles

-- Add foreign key for company_id in eeu_data
alter table "public"."eeu_data" 
    add constraint "eeu_data_company_id_fkey" 
    FOREIGN KEY ("company_id") 
    REFERENCES "public"."companies"("id") 
    ON DELETE SET NULL;

