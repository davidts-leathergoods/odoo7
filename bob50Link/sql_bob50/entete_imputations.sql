select
j.code as TDBK,
right(per.name,4) as TFYEAR,
right(per.name,4) as TYEAR,
date_part('month',am.date) AS TMONTH,
right(am.name,6) as TDOCNO,
to_char(ai.date_invoice, 'DD/MM/YYYY') as TDOCDATE,
'C' as TTYPCIE,
partner.ref as TCOMPAN,
to_char(ai.date_due, 'DD/MM/YYYY') as TDUEDATE,
'' as TDISAMOUNT,
'' as TDISDATE,
CASE WHEN currency."name" not ilike 'EUR' THEN currency."name"  ELSE '' END as TCURRENCY,
CASE WHEN rate."rate" != 1 THEN to_char(round(rate.rate,2),'FM9999999999990D00') END as TCURRATE,
CASE WHEN currency."name" not ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00')  ELSE '0' END as TCURAMN,
CASE WHEN currency."name" ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00') ELSE to_char(round((ai.amount_untaxed/rate.rate),2),'FM9999999999990D00') END as TAMOUNT,
SUBSTR(am."narration",0,40) as TREMINT,
SUBSTR(am."narration",0,40) as TREMEXT,
'S' as TINTMODE
from account_move_line ml
left outer join account_journal j on ml.journal_id = j.id
left outer join account_period per on ml.period_id = per.id
left outer join account_account atax on atax.id = ml.tax_code_id
left outer join account_account ac on ml.account_id = ac.id
left outer join res_partner partner on ml.partner_id = partner.id
left outer join account_move am on am.id  = ml.move_id
left outer join "public"."account_tax_code" atc on atc."id" = ml."tax_code_id"
left outer join "public"."account_invoice" ai on ai."move_id" = am."id"
left outer join "public"."account_invoice_tax" tax on tax."invoice_id" = ai."id"
left outer join "public"."res_currency" currency on currency."id" = ai."currency_id"
left outer join "public"."res_currency_rate" rate on rate."currency_id" = currency."id"
left outer join "public"."account_fiscal_position" fiscal on fiscal."id" = ai."fiscal_position"
where
ac.code ilike '400000' and am.date >= '2015-01-01' and am.date <= '2015-01-31' and j.code = 'SAJ'
order by TDOCNO
