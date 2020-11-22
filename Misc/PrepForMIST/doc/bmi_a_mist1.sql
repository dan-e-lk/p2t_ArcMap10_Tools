 SELECT e.ogc_fid,
    e.ogc_fid AS polyid,
    e.polyid AS polyid_o,
    e.polytype,
        CASE
            WHEN btrim(e.source::text)::character varying::text = 'DIGITALP'::text THEN 'DIGITAL'::character varying
            WHEN btrim(e.source::text)::character varying::text = 'SUPINFO'::text THEN 'PLOTFIXD'::character varying
            ELSE btrim(e.source::text)::character varying
        END AS source,
    btrim(e.source::text)::character varying AS source_o,
    round(st_area(e.geom)::numeric, 2) AS area,
    e.owner,
    e.avail AS avail_o,
        CASE
            WHEN e.formod::text = 'PF'::text OR e.access1::text = 'GEO'::text OR e.access1::text = 'ISL'::text OR e.access1::text = 'NAT'::text OR e.access1::text = 'OTH'::text THEN 'U'::character varying
            WHEN e.owner::numeric = ANY (ARRAY[5::numeric, 7::numeric]) THEN 'U'::character varying
            ELSE 'A'::character varying
        END AS avail,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND (e.access1 IS NULL OR btrim(e.access1::text) = ''::text) THEN 'NON'::character varying
            ELSE e.access1
        END AS access1,
        CASE
            WHEN e.formod IS NULL THEN 'PF'::character varying
            ELSE e.formod
        END AS formod,
    e.access1 AS access1_o,
        CASE
            WHEN e.devstage::text = ANY (ARRAY['NAT'::text, 'ESTNAT'::text]) THEN 'FTGNAT'::character varying
            ELSE e.devstage
        END AS devstage,
    e.devstage AS devstage_o,
    e.deptype,
    e.mgmtcon1,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 'E'::text
            ELSE NULL::text
        END AS agestr,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 'CC'::text
            ELSE NULL::text
        END AS silvsys,
    c.sspcomp AS spcomp,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Ab'::text THEN 'AX'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Bd'::text THEN 'OH'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Cw'::text THEN 'Ce'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Ew'::text THEN 'OH'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Ob'::text THEN 'OH'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Pl'::text THEN 'PO'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Pt'::text THEN 'PO'::character varying
            WHEN e.polytype::text = 'FOR'::text AND c.sleadspc::text = 'Sn'::text THEN 'SX'::character varying
            ELSE c.sleadspc
        END AS wg,
    c.sleadspc AS wg1,
    c.sht_pyear AS ht,
    c.sht AS ht_o,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND e.stkg > 2.5::double precision THEN 1::double precision
            ELSE e.stkg
        END AS stkg,
    c.ssc::double precision AS sc,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN e.yrdep::double precision
            ELSE NULL::double precision
        END AS yrdep,
    e.yrsource::double precision AS yrupd,
    c.syrorg::double precision AS yrorg,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND c.sage::numeric > 250::numeric THEN 250::numeric
            ELSE c.sage::numeric
        END AS age,
    e.source AS ecosrc,
    c.ecopri AS ecosite1,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND (e.sec_eco IS NULL OR e.sec_eco::text = ' '::text) THEN 100::double precision
            WHEN e.polytype::text = 'FOR'::text THEN 90::double precision
            ELSE NULL::double precision
        END AS ecopct1,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND (e.sec_eco IS NULL OR e.sec_eco::text = ' '::text) THEN NULL::text
            ELSE "left"(e.sec_eco::text, 4)
        END AS ecosite2,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND (e.sec_eco::text <> ' '::text OR e.sec_eco IS NULL) THEN 10::double precision
            ELSE NULL::double precision
        END AS ecopct2,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ags_pole,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ags_sml,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ags_med,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ags_lge,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ugs_pole,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ugs_sml,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ugs_med,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ugs_lge,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS agsp,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ugsp,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ags,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS ugs,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN '0'::text
            ELSE NULL::text
        END AS ags_class,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN '0'::text
            ELSE NULL::text
        END AS ugs_class,
        CASE
            WHEN e.vert::text = 'TU'::text OR e.vert::text = 'MU'::text THEN e.ospcomp
            WHEN e.vert::text = 'TO'::text OR e.vert::text = 'MO'::text THEN e.uspcomp
            ELSE NULL::character varying
        END AS uspcomp,
        CASE
            WHEN e.vert::text = 'TU'::text OR e.vert::text = 'MU'::text THEN e.oyrorg::numeric
            WHEN e.vert::text = 'TO'::text OR e.vert::text = 'MO'::text THEN e.uyrorg::numeric
            ELSE NULL::integer::numeric
        END AS uyrorg,
        CASE
            WHEN e.vert::text = 'TU'::text OR e.vert::text = 'MU'::text OR e.vert::text = 'TO'::text OR e.vert::text = 'MO'::text THEN e.stkg
            ELSE NULL::double precision
        END AS ustkg,
        CASE
            WHEN e.vert::text = 'TU'::text OR e.vert::text = 'MU'::text THEN e.osc::numeric
            WHEN e.vert::text = 'TO'::text OR e.vert::text = 'MO'::text THEN e.usc::numeric
            ELSE NULL::integer::numeric
        END AS usc,
    '3E'::text AS submu,
    '3E'::text AS omz,
    c.unit,
    e.au,
    e.planfu AS sfu,
    e.planfu,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 0::double precision
            ELSE NULL::double precision
        END AS defer,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 'CLEARCUT'::text
            ELSE NULL::text
        END AS mgmtstg,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 'CONVENTN'::text
            ELSE NULL::text
        END AS nextstg,
    'Prsnt'::text AS si,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND (e.devstage::text = 'NEWSEED'::text OR e.devstage::text = 'NEWPLANT'::text OR e.devstage::text = 'FTGSEED'::text OR e.devstage::text = 'FTGPLANT'::text) THEN 'Basc'::text
            WHEN e.polytype::text = 'FOR'::text AND (e.deptype::text <> 'HARVEST'::text OR e.deptype IS NULL) THEN
            CASE
                WHEN e.devstage::text = ANY (ARRAY['DEPHARV'::character varying::text]) THEN 'MDepl'::text
                WHEN (e.devstage::text = ANY (ARRAY['NEWNAT'::character varying::text, 'LOWMGMT'::character varying::text])) OR e.mgmtcon1::text = 'UPFR'::text THEN 'Exten'::text
                ELSE 'Prsnt'::text
            END
            WHEN e.polytype::text = 'FOR'::text THEN 'Exten'::text
            ELSE NULL::text
        END AS si1,
        CASE
            WHEN e.polytype::text = 'FOR'::text AND e.devstage::text = 'DEPHARV'::text THEN 'mdepl'::text
            WHEN e.polytype::text = 'FOR'::text AND e.devstage::text ~~ 'LOW%'::text THEN 'bs'::text
            WHEN e.polytype::text = 'FOR'::text AND e.deptype::text ~~ 'HARV%'::text THEN 'man'::text
            WHEN e.polytype::text = 'FOR'::text AND (e.devstage::text ~~ 'NEWNAT%'::text OR e.devstage::text ~~ 'FTGNAT%'::text) AND (e.deptype::text ~~ '%BLOWDOWN%'::text OR e.deptype::text ~~ '%DISEASE%'::text OR e.deptype::text ~~ '%DROUGHT%'::text OR e.deptype::text ~~ '%FLOOD%'::text OR e.deptype::text ~~ '%ICE%'::text OR e.deptype::text ~~ '%INSECTS%'::text OR e.deptype::text ~~ '%SNOW%'::text) THEN 'pdam'::text
            WHEN e.polytype::text = 'FOR'::text AND (e.devstage::text ~~ 'NEWNAT%'::text OR e.devstage::text ~~ 'FTGNAT%'::text) THEN 'prsnt'::text
            WHEN e.polytype::text = 'FOR'::text AND (e.devstage::text ~~ '%PASS'::text OR e.devstage::text ~~ '%SEED'::text OR e.devstage::text ~~ '%PLANT'::text OR e.devstage::text ~~ '%CUT'::text OR e.devstage::text ~~ 'THIN%'::text OR e.devstage::text = 'SELECT'::text) THEN 'man'::text
            ELSE '--'::text
        END AS si2,
        CASE
            WHEN e.polytype::text = 'FOR'::text THEN 'ASSIGNED'::text
            ELSE NULL::text
        END AS sisrc
   FROM ze_cosen.bmi_a e
     JOIN ze_cosen.bmi_a_basecls c ON e.ogc_fid = c.ogc_fid
  WHERE e.polytype::text = 'FOR'::text AND (e.owner::numeric = ANY (ARRAY[1::numeric, 5::numeric, 7::numeric])) AND (e.devstage::text = ANY (ARRAY['ESTNAT'::character varying::text, 'FTGNAT'::character varying::text, 'DEPNAT'::character varying::text, 'NEWNAT'::character varying::text, 'NAT'::character varying::text, 'LOWNAT'::character varying::text])) AND (e.deptype IS NULL OR e.deptype::text <> 'HARVEST'::text OR e.deptype::text <> 'SALVAGE'::text) AND st_area(e.geom) IS NOT NULL;