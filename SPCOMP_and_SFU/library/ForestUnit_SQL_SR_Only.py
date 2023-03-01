# Only SR folks should touch this!

SR_GLSL_SFU = {

# this SQL is owned by Glen Watt - talk to him if you have issues with it.
# fields required: POLYTYPE, Ecosite_GeoRangeAndNumber, (STKG or OSTKG) and (OSC or SC)


#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated

    1:  ['PR',     """ ("Pr">=70 and "Pw"<30) And <user_defined_sfu_field_name> Is Null """, ""],
    2:  ['PWUS4',  """ ("Pw"+"Pr">=50 and "Pw">"Pr" and (("Pw"+"Pr")*"OSTKG" >=30) and ("_Or"+"OB"+"Ow") < 20) And <user_defined_sfu_field_name> Is Null """, ""],
    3:  ['PWOR',   """ (("Pw"+"Pr"+"_Or"+"OB"+"Ow">=50) and "Pw">=("_Or"+"OB"+"Ow") and ("Pw"+"Pr"+"_Or"+"OB"+"Ow")*"OSTKG" >=30 and ("_Or"+"OB"+"Ow")>=20) And <user_defined_sfu_field_name> Is Null """, ""],
    4:  ['PWUSC',  """ (("Pw"+"Pr">=30 AND ("Pw"+"Pr")*"OSTKG" >=30 )  OR  ( ("Pw">="He" AND "Pw">="Sw") AND "Pw">("Ce" + "Cw") AND "Pw">="_Or" AND "Pw"+"Pr" >=30 AND ("Pw"+"Pr"+"Sw"+"He"+"_Or"+"Pj"+"Ce"+"Cw")*"OSTKG" >=30 AND ("Pw"+"Pr"+"Pj"+"Sw"+"Sb"+"Sr"+"Sx"+"He"+"Bf"+"Ce"+"Cw"+"La")>=80 )) And <user_defined_sfu_field_name> Is Null """, ""],
    5:  ['PWUSH',  """ (("Pw">="Pr" AND "Pw"+"Pr">=30 AND ("Pw"+"Pr")*"OSTKG" >=30 )  OR  ( "Pw">="Pr" AND "Pw">="He" AND "Pw">="Sw" AND "Pw">("Ce" + "Cw") AND "Pw">="_Or" AND ("Pw"+"Pr") >=30 AND ("Pw"+"Pr"+"Sw"+"He"+"_Or"+"Pj"+"Ce"+"Cw")*"OSTKG" >=30 AND ("Pw"+"Pr"+"Pj"+"Sw"+"Sr"+"Sx"+"Sb"+"He"+"Bf"+"Ce"+"Cw"+"La")<80 )) And <user_defined_sfu_field_name> Is Null """, ""],
    6:  ['PWST',   """ (("PW"+"PR">=30) AND ("PW"+"PR">="HE") AND ("PW"+"PR">="SW") AND ("PW"+"PR">="SB"+"SR"+"SX") AND ("PW"+"PR">=("CE"+"CW")) AND ("PW"+"PR">="_OR")) And <user_defined_sfu_field_name> Is Null """, ""],
    7:  ['PJ1',    """ (("PJ">=70) AND ("MH"+"AB"+"AW"+"BD"+"BE"+"CH"+"EW"+"IW"+"_OR"+"_BY"+"OW"+"Ob"+"PO"+"Pt"+"Pb"+"Pl"+"BW"+"MR"+"MS"+"AX"+"CB"+"EX"+"HI"+"BN"<=20)) And <user_defined_sfu_field_name> Is Null """, ""],
    8:  ['PJ2',    """ (((("PJ"+"SB"+"SR"+"SX"+"PR">=70) OR (("PJ">=50) AND ("PJ"+"SB"+"SR"+"SX"+"BF"+"SW"+"HE"+"PW"+"PR"+"CE"+"CW"+"LA">=70) AND ("BF"+"SW"+"HE"+"PW"+"CE"+"CW"+"LA"<=20))) AND ("PJ">="SB"+"SR"+"SX"))) And <user_defined_sfu_field_name> Is Null """, ""],
    9:  ['HE',     """ ("He">=40) And <user_defined_sfu_field_name> Is Null """, ""],
    10: ['CE',     """ (("CE"+"CW">=40) AND (("CE"+"CW")>="SB"+"SR"+"SX"+"LA"+"BF") AND ("OW"+"Ob"+"EW"+"IW"+"CH"+"MH"+"AB"+"AW"+"BD"+"BE"+"_OR"+"_BY"+"PO"+"Pb"+"Pt"+"Pl"+"BW"+"MR"+"MS"+"EX"+"CB"+"AX"+"HI"+"BN"<30)) And <user_defined_sfu_field_name> Is Null """, """ AND "Ecosite_GeoRangeAndNumber" In ('G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136') """],
    11: ['SB',     """ (("SB"+"SR"+"SX">=80) AND ("MH"+"AW"+"BD"+"BE"+"CH"+"IW"+"_OR"+"OW"+"Ob"+"_BY"+"PR"+"BN"+"HI"+"CB"=0) AND ("PW"+"PJ"<=10)) And <user_defined_sfu_field_name> Is Null """, """ and "Ecosite_GeoRangeAndNumber" In ('G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136') """],
    12: ['LC',     """ (("SB"+"SX"+"SR"+"CE"+"CW"+"LA">=80) AND ("MH"+"AW"+"BD"+"BE"+"CH"+"IW"+"_OR"+"OW"+"Ob"+"_BY"+"PR"+"CB"+"HI"+"BN"=0) AND ("PW"+"PJ"<=10))  And <user_defined_sfu_field_name> Is Null """, """AND "Ecosite_GeoRangeAndNumber" In ('G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136') """],
    13: ['SP1',    """ (("SB"+"SW"+"SR"+"SX"+"BF"+"CE"+"CW"+"LA"+"PW"+"PJ"+"PR"+"HE">=70) AND (("BF"+"CE"+"CW"+"PW"+"LA"+"SW"+"HE"<=20) OR ("PJ">=30))) And <user_defined_sfu_field_name> Is Null """, ""],
    14: ['SF',     """ (("SW"+"SR"+"SB"+"SX"+"PW"+"PR"+"PJ"+"BF"+"CE"+"CW"+"LA"+"HE">=70)) And <user_defined_sfu_field_name> Is Null """, ""],
    15: ['BY',     """ ("_By">=40) And <user_defined_sfu_field_name> Is Null """, ""],
    16: ['OAK',    """ (("_OR">="MH"+"BE") AND ("_OR">=30) AND ("_OR"+"MH"+"AW"+"AB"+"BE"+"BD"+"_BY"+"PW"+"PR"+"SW"+"HE"+"AX">=40)) And <user_defined_sfu_field_name> Is Null """, ""],
    17: ['HDSL2',  """ ((("BD"+"AW"+"CH"+"_OR"+"OW"+"Ob"+"CB">=30) OR (("BE"+"_OR"+"OW"+"Ob">=30) OR ("BE">=20)))) And <user_defined_sfu_field_name> Is Null """, ""],
    18: ['HDSL1',  """ (("MH"+"AW"+"BD"+"BE"+"CH"+"EW"+"IW"+"_OR"+"_BY"+"OW"+"Ob"+"HE"+"EX"+"CB">=50) AND ("PO"+"Pt"+"Pb"+"Pl"+"BW"+"BF"<=30) AND ("OSC" <= 2)) And <user_defined_sfu_field_name> Is Null """, ""],
    19: ['LWMW',   """ (("CE"+"CW"+"AB"+"LA"+"SB"+"AX"+"SR"+"SX">=30) AND (("AB"+"AX">=20) OR ("AB"+"AX"+"MR"+"MS"+"_BY">=30))) And <user_defined_sfu_field_name> Is Null """, """AND "Ecosite_GeoRangeAndNumber" In ('G071', 'G120', 'G130', 'G131', 'G132', 'G133', 'B071', 'B120', 'B130', 'B131', 'B132', 'B133') """],
    20: ['HDUS',   """ (("MH"+"AW"+"BD"+"BE"+"CH"+"EW"+"IW"+"_OR"+"_BY"+"OW"+"Ob"+"HE"+"CB"+"HI"+"EX"+"BN">=50)) And <user_defined_sfu_field_name> Is Null """, ""],
    21: ['PO',     """ (("PO"+"Pt"+"Pb"+"Pl">=50) AND ("MH"+"AB"+"AW"+"BD"+"BE"+"CH"+"EW"+"IW"+"_OR"+"_BY"+"OW"+"Ob"+"PO"+"Pb"+"Pt"+"Pl"+"BW"+"MR"+"MS"+"AX"+"BN"+"CB"+"EX"+"HI">=70)) And <user_defined_sfu_field_name> Is Null """, ""],
    22: ['BW',     """ (("PO"+"Pt"+"Pb"+"Pl"+"BW">=50) AND ("MH"+"AB"+"AW"+"BD"+"BE"+"CH"+"EW"+"IW"+"_OR"+"_BY"+"OW"+"Ob"+"PO"+"Pt"+"Pb"+"Pl"+"BW"+"MR"+"MS"+"AX"+"BN"+"CB"+"EX"+"HI">=70))  And <user_defined_sfu_field_name> Is Null """, ""],
    23: ['MWUS',   """ ((("SW"+"PW"+"PR"+"CE"+"CW"+"MH"+"_BY"+"AW"+"CH"+"BD"+"_OR"+"OW"+"Ob"+"IW"+"BE"+"HE"+"CB"+"HI"+"BN")*"OSTKG">=30)) And <user_defined_sfu_field_name> Is Null """, ""],
    24: ['MWD',    """ ("PJ"+"PW"+"PR">=20) And <user_defined_sfu_field_name> Is Null """, ""],
    25: ['MWR',    """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """, ""]
}

