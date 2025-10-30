create sequence "public"."column_metadata_id_seq";

create table "public"."column_metadata" (
    "id" integer not null default nextval('column_metadata_id_seq'::regclass),
    "table_name" character varying(255),
    "column_name" character varying(255),
    "has_units" boolean default false,
    "unit_type" character varying(50),
    "conversion_needed" boolean default false
);


alter sequence "public"."column_metadata_id_seq" owned by "public"."column_metadata"."id";

CREATE UNIQUE INDEX column_metadata_pkey ON public.column_metadata USING btree (id);

alter table "public"."column_metadata" add constraint "column_metadata_pkey" PRIMARY KEY using index "column_metadata_pkey";

grant delete on table "public"."column_metadata" to "anon";

grant insert on table "public"."column_metadata" to "anon";

grant references on table "public"."column_metadata" to "anon";

grant select on table "public"."column_metadata" to "anon";

grant trigger on table "public"."column_metadata" to "anon";

grant truncate on table "public"."column_metadata" to "anon";

grant update on table "public"."column_metadata" to "anon";

grant delete on table "public"."column_metadata" to "authenticated";

grant insert on table "public"."column_metadata" to "authenticated";

grant references on table "public"."column_metadata" to "authenticated";

grant select on table "public"."column_metadata" to "authenticated";

grant trigger on table "public"."column_metadata" to "authenticated";

grant truncate on table "public"."column_metadata" to "authenticated";

grant update on table "public"."column_metadata" to "authenticated";

grant delete on table "public"."column_metadata" to "service_role";

grant insert on table "public"."column_metadata" to "service_role";

grant references on table "public"."column_metadata" to "service_role";

grant select on table "public"."column_metadata" to "service_role";

grant trigger on table "public"."column_metadata" to "service_role";

grant truncate on table "public"."column_metadata" to "service_role";

grant update on table "public"."column_metadata" to "service_role";


