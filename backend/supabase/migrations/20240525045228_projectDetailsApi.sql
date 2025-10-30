create table "public"."eeu_fields" (
    "field_name" text,
    "energy_type" text,
    "display_name" text
);


alter table "public"."eeu_data" add column "file_type" character varying(255);

alter table "public"."enum_report_types" add column "file_type" text;

grant delete on table "public"."eeu_fields" to "anon";

grant insert on table "public"."eeu_fields" to "anon";

grant references on table "public"."eeu_fields" to "anon";

grant select on table "public"."eeu_fields" to "anon";

grant trigger on table "public"."eeu_fields" to "anon";

grant truncate on table "public"."eeu_fields" to "anon";

grant update on table "public"."eeu_fields" to "anon";

grant delete on table "public"."eeu_fields" to "authenticated";

grant insert on table "public"."eeu_fields" to "authenticated";

grant references on table "public"."eeu_fields" to "authenticated";

grant select on table "public"."eeu_fields" to "authenticated";

grant trigger on table "public"."eeu_fields" to "authenticated";

grant truncate on table "public"."eeu_fields" to "authenticated";

grant update on table "public"."eeu_fields" to "authenticated";

grant delete on table "public"."eeu_fields" to "service_role";

grant insert on table "public"."eeu_fields" to "service_role";

grant references on table "public"."eeu_fields" to "service_role";

grant select on table "public"."eeu_fields" to "service_role";

grant trigger on table "public"."eeu_fields" to "service_role";

grant truncate on table "public"."eeu_fields" to "service_role";

grant update on table "public"."eeu_fields" to "service_role";


