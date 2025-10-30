alter type "public"."fuel_types" rename to "fuel_types__old_version_to_be_dropped";

create type "public"."fuel_types" as enum ('electricity', 'fossil_fuels', 'district', 'other', 'onsite_renewables');

alter table "public"."eeu_fields" alter column fuel_category type "public"."fuel_types" using fuel_category::text::"public"."fuel_types";

drop type "public"."fuel_types__old_version_to_be_dropped";


