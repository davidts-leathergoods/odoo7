SELECT
     partner."ref" AS CID,
     'C' AS CCUSTYPE,
     'U' AS CSUPTYPE,
     partner."name" AS CNAME1,
     '' AS CNAME2,
     partner."street" AS CADDRESS1,
     partner."street2" AS CADDRESS2,
     partner."zip" AS CZIPCODE,
     partner."city" AS CLOCALITY,
     left(upper(partner."lang"),1) AS CLANGUAGE,
     currency."name" AS CCURRENCY,
     ir_translation."value" AS CVATREF,
     partner."vat" as CVATNO,
     CASE WHEN partner."vat" is null OR partner."vat" ilike 'NA' THEN 'N' ELSE '' END as CVATCAT,
     '' AS CVATCAT,
     partner."phone" as CTELNO,
     partner."fax" as CFAXNO,
     country."code" AS CCOUNTRY,
     ir_translation."value" AS CCOUHEAD
     --partner."supplier" as fournisseur,
     --partner."customer" as client

FROM
     "public"."res_country" country INNER JOIN "public"."res_partner" partner ON country."id" = partner."country_id"
     INNER JOIN "public"."ir_translation" ir_translation ON country."name" = ir_translation."src" AND ir_translation."lang" = 'fr_FR'
     INNER JOIN "public"."res_users" res_users ON partner."user_id" = res_users."id"
     INNER JOIN "public"."res_currency" currency ON country."currency_id" = currency."id"

WHERE

partner."active" = true
and partner."customer" = true
--and partner."supplier" = true
and partner."is_company" = true

ORDER BY
     partner."name" ASC