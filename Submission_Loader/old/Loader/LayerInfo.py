

AR_new = {
# Lyr acronym            name                 order       mandatory fields                                            Data Type   Tech Spec 

    "AGG":  ["01Forestry Aggregate Pits",         1,      ['PITID','REHABREQ','REHAB','PITCLOSE','TONNES'],           'point',    '4.3.18'],
    "EST":  ["06Establishment Assessment",        6,      ['ARDSTGRP','SILVSYS','AGEEST','YRDEP','DSTBFU','SGR',
                                                            'TARGETFU','TARGETYD','ESTIND','ESTFU','ESTYIELD',
                                                            'SPCOMP','HT','DENSITY','STKG'],                        'polygon',  '4.3.15'],

    "FTG":  ["05Free-To-Grow",                    5,      ['ARDSTGRP','YRDEP','DSTBFU','SGR','TARGETFU','FTG'],       'polygon',  '4.3.17'],

    "HRV":  ["13Harvest Disturbance",             13,     ['BLOCKID','HARVCAT','SILVSYS','HARVMTHD','MGMTSTG',
                                                            'ESTAREA','SGR','DSTBFU','TARGETFU','TARGETYD','TRIAL',
                                                            'LOGMTHD'],                                             'polygon',  '4.3.8'],

    "NDB":  ["07Natural Disturbance",             7,      ['NDEPCAT','VOLCON','VOLHWD','DSTBFU'],                     'polygon',  '4.3.7'],
    "PER":  ["11Performance Assessment",          11,     ['SILVSYS','PERFU','PERYIELD','SPCOMP','BHA','HT',
                                                            'DENSITY','STKG','AGS','UGS'],                          'polygon',  '4.3.16'],

    "PRT":  ["09Protection Treatment",            9,      ['TRTMTHD1','TRTCAT1'],                                     'polygon',  '4.3.14'],
    "RDS":  ["03Road Construction and Road Use",  3,      ['ROADID','ROADCLAS','CONSTRCT','DECOM','TRANS','ACCESS',
                                                            'MAINTAIN','MONITOR','CONTROL1','CONTROL2'],            'arc',      '4.3.9'],

    "RGN":  ["08Regeneration Treatment",          8,      ['TRTMTHD1','TRTCAT1','ESTAREA','SP1','SP2'],               'polygon',  '4.3.11'],
    "SCT":  ["04Slash and Chip Treatment",        4,      ['SLASHPIL','CHIPPIL','BURN','MECHANIC','REMOVAL'],         'arc',      '4.3.20'],
    "SGR":  ["14Silvicultural Ground Rule Update",14,     ['SGR','TARGETFU','TARGETYD','TRIAL'],                      'polygon',  '4.3.19'],
    "SIP":  ["10Site Preparation Treatment",      10,     ['TRTMTHD1','TRTCAT1'],                                     'polygon',  '4.3.12'],
    "TND":  ["12Tending Treatment",               12,     ['TRTMTHD1','TRTCAT1'],                                     'polygon',  '4.3.13'],
    "WTX":  ["02Water Crossings",                 2,      ['WATXID','WATXTYPE','CONSTRCT','MONITOR','REMOVE',
                                                            'REPLACE','REVIEW','ROADID','TRANS'],                   'point',    '4.3.10']
        }

# AR_old = {
# # Lyr acronym            name                           mandatory fields                                            Data Type   Tech Spec       Tech Spec URL

#     "AGG":  ["Forestry Aggregate Pits",                 ['PIT_ID','REHABREQ','REHAB','TONNES'],                     'point',    'A1.10',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=106'],
#     "FTG":  ["Free-To-Grow",                            ['ARDSTGRP','YRDEP','DSTBFU','SGR','TARGETFU','FTG'],       'polygon',  'A1.9',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=99'],
#     "HRV":  ["Harvest Disturbance",                     ['HARVCAT','SILVSYS','HARVMTHD','SGR','DSTBFU'],            'polygon',  'A1.2',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=64'],
#     "NDB":  ["Natural Disturbance",                     ['NDEPCAT','VOLCON','VOLHWD','DSTBFU'],                     'polygon',  'A1.1',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=61'],
#     "PRT":  ["Protection Treatment",                    ['TRTMTHD1'],                                               'polygon',  'A1.8',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=96'],
#     "RDS":  ["Road Construction and Road Use",          ['ROADID','CONSTRCT','DECOM','ACCESS','MAINTAIN','MONITOR'],'arc',      'A1.3',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=72'],
#     "RGN":  ["Regeneration Treatment",                  ['TRTMTHD1','TRTCAT1'],                                     'polygon',  'A1.5',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=82'],
#     "SCT":  ["Slash and Chip Treatment",                ['SLASHPIL','CHIPPIL','BURN','MECHANIC','REMOVAL'],         'arc',      'A1.12',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=110'],
#     "SGR":  ["Silvicultural Ground Rule Update",        ['SGR'],                                                    'polygon',  'A1.11',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=109'],
#     "SIP":  ["Site Preparation Treatment",              ['TRTMTHD1'],                                               'polygon',  'A1.6',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=88'],
#     "TND":  ["Tending Treatment",                       ['TRTMTHD1'],                                               'polygon',  'A1.7',         'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=92'],
#     "WTX":  ["Water Crossings",                         ['WATXID','WATXTYPE','CONSTRCT','MONITOR','REMOVE','ROADID'],'point',   'A1.4',        'https://dr6j45jk9xcmk.cloudfront.net/documents/2834/fim-tech-spec-2013-aoda.pdf#page=78']
#         }

AWS_new = {
# Dictionary of lists of lists
# Layer acronym            name                        order  mandatory fields                                              Data Type   Tech Spec  Tech Spec URL
    "AGP":  ["01Existing Forestry Aggregate Pits",        1,  ['PITID', 'PITOPEN', 'PITCLOSE', 'CAT9APP'],                    'point',    '4.2.19'],
    "SAC":  ["04Scheduled Area Of Concern",               4,  ['AOCID', 'AOCTYPE'],                                           'polygon',  '4.2.8'],
    "SAG":  ["05Scheduled Aggregate Extraction",          5,  ['AWS_YR', 'AGAREAID'],                                         'polygon',  '4.2.14'],
    "SEA":  ["06Scheduled Establishment Assessment",      6,  ['AWS_YR', 'YRDEP', 'TARGETFU', 'TARGETYD'],                    'polygon',  '4.2.20'],
    "SHR":  ["07Scheduled Harvest",                       7,  ['AWS_YR', 'BLOCKID', 'SILVSYS', 'HARVCAT','FUELWOOD'],         'polygon',  '4.2.7'],
    "SOR":  ["08Scheduled Operational Road Boundaries",   8,  ['AWS_YR', 'ORBID'],                                            'polygon',  '4.2.11'],
    "SPT":  ["09Scheduled Protection Treatment",          9,  ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.18'],
    "SRA":  ["03Scheduled Existing Road Activities",      3,  ['AWS_YR', 'ROADID', 'ROADCLAS','TRANS','ACCESS',
                                                            'DECOM','CONTROL1'],                                            'arc',      '4.2.12'],
    "SRC":  ["01Scheduled Road Corridors",                1,  ['AWS_YR', 'ROADID', 'ROADCLAS','TRANS','ACYEAR',
                                                            'ACCESS','DECOM','INTENT','MAINTAIN','MONITOR','CONTROL1'],     'polygon',  '4.2.10'],
    "SRG":  ["10Scheduled Regeneration Treatments",       10, ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.16'],
    "SRP":  ["11Scheduled Residual Patches",              11, ['RESID'],                                                      'polygon',  '4.2.9'],
    "SSP":  ["12Scheduled Site Preparation Treatments",   12, ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.15'],
    "STT":  ["13Scheduled Tending Treatments",            13, ['AWS_YR', 'TRTMTHD1'],                                         'polygon',  '4.2.17'],
    "SWC":  ["02Scheduled Water Crossing Activities",     2,  ['AWS_YR', 'WATXID', 'WATXTYPE','TRANS','ROADID'],              'point',    '4.2.13']
    }

# AWS_old = {
# # Dictionary of lists of lists
# # Layer acronym            name                           mandatory fields                                  Data Type   Tech Spec       Tech Spec URL
#     "AGP":  ["Existing Forestry Aggregate Pits",        ['PIT_ID', 'PIT_OPEN', 'PITCLOSE', 'CAT9APP'],      'point',    'A1.14',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=112'   ],
#     "SAC":  ["Scheduled Area Of Concern",               ['AOCID', 'AOCTYPE'],                               'polygon',  'A1.2',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=79'    ],
#     "SAG":  ["Scheduled Aggregate Extraction",          ['AWS_YR', 'AGAREAID'],                             'polygon',  'A1.9',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=102'   ],
#     "SHR":  ["Scheduled Harvest",                       ['AWS_YR', 'SILVSYS', 'HARVCAT', 'FUELWOOD'],       'polygon',  'A1.1',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=75'    ],
#     "SNW":  ["Scheduled Non-Water AOC Crossing",        ['AWS_YR', 'AOCXID', 'ROADID'],                     'arc',      'A1.8',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=100'   ],
#     "SOR":  ["Scheduled Operational Road Boundaries",   ['AWS_YR', 'ORBID'],                                'polygon',  'A1.5',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=87'    ],
#     "SPT":  ["Scheduled Protection Treatment",          ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.13',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=110'   ],
#     "SRA":  ["Scheduled Existing Road Activities",      ['AWS_YR', 'ROADID', 'ROADCLAS'],                   'arc',      'A1.6',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=89'    ],
#     "SRC":  ["Scheduled Road Corridors",                ['AWS_YR', 'ROADID', 'ROADCLAS'],                   'polygon',  'A1.4',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=82'    ],
#     "SRG":  ["Scheduled Regeneration Treatments",       ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.11',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=106'   ],
#     "SRP":  ["Scheduled Residual Patches",              ['AWS_YR', 'RESID'],                                'polygon',  'A1.3',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=80'    ],
#     "SSP":  ["Scheduled Site Preparation Treatments",   ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.10',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=104'   ],
#     "STT":  ["Scheduled Tending Treatments",            ['AWS_YR', 'TRTMTHD1'],                             'polygon',  'A1.12',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=108'   ],
#     "SWC":  ["Scheduled Water Crossing Activities",     ['AWS_YR', 'WATXID', 'WATXTYPE', 'ROADID'],         'point',    'A1.7',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2839/fim-tech-spec-work-schedule.pdf#page=95'    ]
#     }



FMP_new = {
# Lyr acronym            name                           mandatory fields                                            Data type   Tech Spec       Tech Spec URL

    "AOC":  ["03Area of Concern",                         3,  ["AOCID","AOCTYPE"],                                        'polygon',  '4.2.8'],

    "BMI":  ["04Base Model Inventory",                    4,  ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                            'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                            'OYRORG', 'OSPCOMP', 'OLEADSPC', 'OAGE', 'OHT', 'OCCLO',
                                                            'OSTKG', 'OSC', 'UYRORG', 'USPCOMP', 'ULEADSPC', 'UAGE',
                                                            'UHT', 'UCCLO', 'USTKG', 'USC', 'INCIDSPC', 'VERT', 'HORIZ',
                                                            'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'ACCESS2', 'MGMTCON1',
                                                            'MGMTCON2', 'MGMTCON3', 'YRORG', 'SPCOMP', 'LEADSPC',
                                                            'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED', 'SMZ',
                                                            'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD'],     'polygon',  '4.1.4'],

    "ERU":  ["02Existing Road Use Management Strategies", 2,  ['ROADID','ROADCLAS','TRANS','ACYEAR','ACCESS','DECOM',
                                                            'INTENT','MAINTAIN','MONITOR','RESPONS','CONTROL1'],        'arc',      '4.2.12'],

    "FDP":  ["05Forecast Depletions",                     5,  ['FSOURCE','FYRDEP','FDEVSTAGE'],                           'polygon',  '4.1.8'],

    "IMP":  ["06Tree Improvement",                        6,  ['IMPROVE'],                                                'polygon',  '4.2.15'],

    "OPI":  ["07Operational Planning Inventory",          7,  ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                            'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                            'INCIDSPC', 'VERT', 'HORIZ',
                                                            'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'ACCESS2', 'MGMTCON1',
                                                            'MGMTCON2', 'MGMTCON3', 'YRORG', 'SPCOMP', 'LEADSPC',
                                                            'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED', 'SMZ',
                                                            'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD',
                                                            'OMZ', 'SGR'],                                              'polygon',  '4.1.4'],

    "ORB":  ["08Operational Road Boundaries",             8,  ['ORBID'],                                                  'polygon',  '4.2.11'],

    "PAG":  ["09Planned Aggregate Extraction Areas",      9,  ['AGAREAID'],                                               'polygon',  '4.2.14'],

    "PCI":  ["10Planning Composite",                      10, ['POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE',
                                                            'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE',
                                                            'OYRORG', 'OSPCOMP', 'OLEADSPC', 'OAGE', 'OHT', 'OCCLO',
                                                            'OSTKG', 'OSC', 'UYRORG', 'USPCOMP', 'ULEADSPC', 'UAGE',
                                                            'UHT', 'UCCLO', 'USTKG', 'USC', 'INCIDSPC', 'VERT', 
                                                            'HORIZ', 'PRI_ECO', 'SEC_ECO', 'ACCESS1', 'MGMTCON1'],      'polygon',  '4.1.4'],

    "PHR":  ["11Planned Harvest",                         11, ['BLOCKID','SILVSYS','HARVCAT'],                            'polygon',  '4.2.7'],

    "PRC":  ["12Planned Road Corridors",                  12, ['ROADID','ROADCLAS','TRANS','ACYEAR','ACCESS','DECOM',
                                                            'INTENT','MAINTAIN','MONITOR','CONTROL1','CONTROL2'],       'polygon',  '4.2.10'],

    "PRP":  ["13Planned Residual Patches",                13, ['RESID'],                                                  'polygon',  '4.2.9'],

    "WXI":  ["01Existing Road Water Crossing Inventory",  1,  ['WATXID','WATXTYPE','RESPONS','ROADID'],                   'point',    '4.2.13']
        }



# FMP_old = {
# # Lyr acronym            name                           mandatory fields                                            Data Type   Tech Spec       Tech Spec URL

#     "AOC":  ["Area of Concern",                         ["AOCID","AOCTYPE"],                                        'polygon',    'A1.5',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=169'],
#     "BMI":  ["Base Model Inventory",                    ['POLYID','POLYTYPE','OWNER','YRUPD','SOURCE','FORMOD',
#                                                         'DEVSTAGE','YRDEP','SPCOMP','YRORG','HT','STKG','SC',
#                                                         'ECOSRC','ECOSITE1','ECOPCT1','ACCESS1','MGMTCON1',
#                                                         "MANAGED","SMZ","OMZ","PLANFU","AGESTR","AGE","AVAIL",
#                                                         "SILVSYS","NEXTSTG","SI","SISRC","SGR"],                    'polygon',  'A1.1, A1.2','https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=113'],

#     "ERU":  ["Existing Road Use Management Strategies", ['ROADID','ROADCLAS','ACYEAR','RESPONS'],                   'arc',        'A1.9',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=181'],
#     "FDP":  ["Forecast Depletions",                     ['FSOURCE','FYRDEP','FDEVSTAGE'],                           'polygon',    'A1.3',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=163'],
#     "ORB":  ["Operational Road Boundaries",             ['ORBID'],                                                  'polygon',    'A1.8',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=180'],
#     "PAG":  ["Planned Aggregate Extraction Areas",      ['AGAREAID'],                                               'polygon',    'A1.10',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=188'],
#     "PCC":  ["Planned Clearcuts",                       ['PCCID'],                                                  'polygon',    'A1.12',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=192'],
#     "PCM":  ["Planning Composite",                      ['POLYID','POLYTYPE','OWNER','YRUPD','SOURCE','FORMOD',
#                                                         'DEVSTAGE','YRDEP','SPCOMP','YRORG','HT','STKG','SC',
#                                                         'ECOSRC','ECOSITE1','ECOPCT1','ACCESS1','MGMTCON1'],        'polygon',  'A1.1',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=113'],

#     "PHR":  ["Planned Harvest",                         ['SILVSYS','HARVCAT','FUELWOOD'],                           'polygon',    'A1.4',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=166'],
#     "PRC":  ["Planned Road Corridors",                  ['TERM','ROADID','ROADCLAS','ACYEAR'],                      'polygon',    'A1.7',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=172'],
#     "PRP":  ["Planned Residual Patches",                ['RESID'],                                                  'polygon',    'A1.6',     'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=171'],
#     "PRT":  ["Planned Renewal and Tending",             ['TERM'],                                                   'polygon',    'A1.11',    'https://dr6j45jk9xcmk.cloudfront.net/documents/2836/fim-tech-spec-forest-management-planning.pdf#page=189']
#         }