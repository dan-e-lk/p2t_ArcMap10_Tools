 SELECT f.ogc_fid,
    'cosen'::text AS unit,
    2020 AS pyear,
    "left"(f.pri_eco::text, 4) AS ecopri,
    "substring"(f.pri_eco::text, 2, 3)::integer AS econum,
    code.ecogrp(f.pri_eco::text) AS ecogrp,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN 'Under'::text
            ELSE 'Over'::text
        END AS story,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN f.uspcomp
            ELSE f.ospcomp
        END AS sspcomp,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN f.uyrorg
            ELSE f.oyrorg
        END AS syrorg,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN f.uleadspc
            ELSE f.oleadspc
        END AS sleadspc,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN f.uage
            ELSE f.oage
        END AS sage,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN f.uht
            ELSE f.oht
        END AS sht,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN f.usc
            ELSE f.osc
        END AS ssc,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN 2020 - f.uyrorg
            ELSE 2020 - f.oyrorg
        END AS sage_pyear,
        CASE
            WHEN (f.vert::text = ANY (ARRAY['TU'::text, 'MU'::text])) AND f.uage > 20 AND (2020 - f.yrsource) <= 20 THEN si_hi.calc_single_ht(f.uleadspc::bpchar, f.uage::numeric, f.uht::numeric, f.yrsource::numeric, 2020::numeric)
            WHEN (f.vert::text = ANY (ARRAY['TU'::text, 'MU'::text])) AND f.uage > 20 AND (2020 - f.yrsource) > 20 THEN si_hi.calc_single_ht(f.uleadspc::bpchar, f.uage::numeric, f.uht::numeric, f.yrsource::numeric, f.yrsource::numeric + 20::numeric)
            WHEN (f.vert::text = ANY (ARRAY['TO'::text, 'MO'::text, 'SI'::text, 'SV'::text, 'CX'::text])) AND f.oage > 20 AND (2020 - f.yrsource) <= 20 THEN si_hi.calc_single_ht(f.oleadspc::bpchar, f.oage::numeric, f.oht::numeric, f.yrsource::numeric, 2020::numeric)
            WHEN (f.vert::text = ANY (ARRAY['TO'::text, 'MO'::text, 'SI'::text, 'SV'::text, 'CX'::text])) AND f.oage > 20 AND (2020 - f.yrsource) > 20 THEN si_hi.calc_single_ht(f.oleadspc::bpchar, f.oage::numeric, f.oht::numeric, f.yrsource::numeric, f.yrsource::numeric + 20::numeric)
            WHEN (f.vert::text = ANY (ARRAY['TU'::text, 'MU'::text])) AND f.uage <= 20 THEN f.uht::real
            WHEN (f.vert::text = ANY (ARRAY['TO'::text, 'MO'::text, 'SI'::text, 'SV'::text, 'CX'::text])) AND f.oage <= 20 THEN f.oht::real
            ELSE 999::real
        END AS sht_pyear,
        CASE
            WHEN f.vert::text = 'TU'::text OR f.vert::text = 'MU'::text THEN round(si_hi.calc_single_si(f.uleadspc::text::bpchar, f.uage::numeric, f.uht::numeric)::numeric, 2)
            ELSE round(si_hi.calc_single_si(f.oleadspc::text::bpchar, f.oage::numeric, f.oht::numeric)::numeric, 2)
        END AS ssindex
   FROM ze_cosen.bmi_a f
  WHERE f.polytype::text = 'FOR'::text;