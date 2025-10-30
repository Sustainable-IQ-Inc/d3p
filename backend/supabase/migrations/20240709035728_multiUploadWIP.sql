DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   information_schema.columns 
        WHERE  table_schema = 'public'
        AND    table_name   = 'upload_batches'
        AND    column_name  = 'company_id'
    )
    THEN
        ALTER TABLE public.upload_batches ADD COLUMN company_id uuid;
    END IF;
END
$$;