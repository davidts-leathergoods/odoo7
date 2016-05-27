select
j.code as TDBK,
right(per.name,4) as TFYEAR,
right(per.name,4) as TYEAR,
date_part('month',am.date) AS TMONTH,
right(am.name,6) as TDOCNO,
'' as TDOCLINE, -- id de la ligne
'S' as TTYPELINE,
--to_char(am.date, 'DD/MM/YYYY') as TDOCDATE,
'A' as TACTTYPE,
CASE WHEN fiscal."id" = '1' THEN '700000' --vente
     WHEN fiscal."id" = '2' THEN '700002' --VENTE EXTRACOMMUNAUTAIRE
     WHEN fiscal."id" = '3' THEN '700001' --VENTE IC
  END as TACCOUNT,
CASE WHEN currency."name" not ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00')  ELSE '0' END as TCURAMN,
CASE WHEN currency."name" ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00') ELSE to_char(round((ai.amount_untaxed/rate.rate),2),'FM9999999999990D00') END as TAMOUNT,
CASE WHEN currency."name" not ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00')  ELSE '0' END as TCBVAT,
CASE WHEN currency."name" ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00') ELSE to_char(round((ai.amount_untaxed/rate.rate),2),'FM9999999999990D00') END as TBASVAT, -- montant htva en euros, champs obligatoire
CASE WHEN currency."name" not ilike 'EUR' THEN to_char(ai.amount_tax,'FM9999999999990D00') ELSE '0,00' END as TVCTOTAMN, -- montant de la tva en devise
CASE WHEN currency."name" ilike 'EUR' THEN to_char(ai.amount_tax,'FM9999999999990D00') ELSE '0,00' END as TVATTOTAMN, -- montant de la tva en euros
CASE WHEN currency."name" not ilike 'EUR' THEN to_char(ai.amount_tax,'FM9999999999990D00') ELSE '0,00' END as TCURVATMN, -- montant de la tva en devise
CASE WHEN currency."name" ilike 'EUR' THEN to_char(ai.amount_tax,'FM9999999999990D00') ELSE '0,00' END as TVATAMN, -- montant de la tva en euros
CASE WHEN currency."name" ilike 'EUR' THEN to_char(ai.amount_untaxed,'FM9999999999990D00') ELSE to_char(round((ai.amount_untaxed/rate.rate),2),'FM9999999999990D00') END as TBASLSTAMN,
CASE WHEN fiscal."id" = '1' THEN 'NSS  21'
     WHEN fiscal."id" = '2' THEN 'ISEXP0'
     WHEN fiscal."id" = '3' THEN 'ESTRF0'
  END as TVSTORED,
CASE WHEN ml.debit = 0 THEN 'C' ELSE 'D' END as TDC,
SUBSTR(am."narration",0,40) as TREM
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
ac.code ilike '400000' and am.date >= '2015-01-01'
order by TDOCNO
