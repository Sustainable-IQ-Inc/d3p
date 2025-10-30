 -f diLocal Development

Commands to create a migration:
supabase db diff -f BRANCH_NAME
supabase db reset
git checkout -b BRANCH_NAME
git add .
git commit -m “DESCRIPTION OF CHANGE"

**To create a seed file**
supabase db dump -f supabase/seed_temp.sql --data-only --local

go into the file and extract the table you want and add it into the seed.sql

Make sure that it is linked to the proper project first by using

supabase link --project-ref PROJECT_ID

To push the changes to the staging database, run this
supabase db push --linked

## Pushing to Production

After merging staging into main, you need to run migrations if they did not run successfully in GHA


op run --env-file=backend/.env -- python backend/main.py
