"""Verified AS2 -> Gates of Hell asset mapping tables.

Every target entity, breed, land texture, and environment in this file is
validated against the local Call to Arms - Gates of Hell .pak index by
port_mission.py.
"""

import re

# 1. Mission units, vehicles, cannons, fortifications, and skirmish helpers (0.mi)
MI_ENTITY_MAP = {
    # German vehicles & trucks
    "blitz3_6art": "blitz3_6_art_ammo",
    "blitz3_6eng": "blitz3_6_engineering",
    "steyr_rso": "blitz3_6",
    "kubel_mgun": "kubelwagen_mg",
    "sdkfz223": "sdkfz222a",
    "sdkfz234": "sdkfz234_2",
    "sdkfz251_1": "sdkfz251d_1",
    "welberwind": "wirbelwind",
    "marder_3h": "marder3m",
    "pz2l": "panzer2l",
    "pz3": "panzer3m",
    "pz3f": "panzer3f",
    "pz3n": "panzer3n",
    "pz4g": "panzer4g",
    "pz4h": "panzer4h",
    "pz5g": "panzer5g",
    "pz6e": "tiger1e",
    "pz6bh": "tiger2h",
    "ju-87": "bf110_e2",
    # German cannons, mortars, MGs
    "flak37": "37mm_flak37",
    "flak38": "20mm_flak38",
    "flak38_wheeled": "20mm_flak38",
    "mg42_stan_fix": "mg42_lafette",
    "pak36": "37mm_pak36",
    "pak38": "50mm_pak38_late",
    "pak40": "75mm_pak40",
    "sfh18": "150mm_sfh18",
    "sgrw42": "120mm_sgrw42",
    # Soviet vehicles, aircraft, cannons, MGs
    "ba11": "ba10",
    "il-2": "il2_mod42",
    "is1": "is1_43",
    "is2": "is2_44",
    "isu122": "isu122s",
    "kv1": "kv1_42",
    "m3": "m3_lee_rus",
    "t34_1": "t3476_41",
    "t34_2": "t3476_43",
    "t34_3": "t3485_44",
    "zis5art": "zis5",
    "zsu37": "gaz_aaa_72k",
    "bm37": "82mm_bm37",
    "d1": "152mm_ml20",
    "degtyarev_stan_fix": "ds39_stand",
    "k61": "37mm_61k",
    "k61_fix": "37mm_61k",
    "m37": "45mm_m37",
    "zis2": "57mm_zis2_late",
    "zis3": "76mm_zis3",
    # USA vehicles, cannons, MGs (Liberation DLC)
    "bofors": "40mm_m1",
    "gmc_art": "cckw_art_ammo",
    "gmc_cckw": "cckw",
    "gmc_inf": "cckw_inf",
    "m10wolverine": "m10_gmc",
    "m18": "m18_hellcat",
    "m24": "m24_chaffee",
    "m26e4": "m26_pershing",
    "m3cannon": "57mm_m1",
    "m4a3_75": "m4a3_75_late",
    "m4a3e2_jumbo_76": "m4a3_76w",
    "m4a3e8": "m4a3_76w_field1",
    "m5": "m5_halftrack",
    "m5a1": "m5a1_stuart_late",
    "maxson": "50cal_quad_m45",
    "willysat": "willys_mb_50cal",
    # Fortifications (use LOW-PROFILE sandbags so AT guns shoot cleanly over them!)
    # sandbag_straight: z=13.3, sandbag_curved: z=8.3, sandbag_five: z=9.4
    "sandbag2": "sandbag_five",
    "sandbag2_round": "sandbag_curved",
    "sandbag_woodbeam1": "sandbag_straight",
    # Skirmish flags & helpers
    "skirmish_flag": "flag_skirmish",
    "skirmish_flag_5_victory": "flag_skirmish_1",
    "skirmish_flag_20_victory": "flag_skirmish_2",
    "skirmish_flag_30_infantry": "flag_skirmish_3",
    "skirmish_flag_250_victory": "flag_skirmish_4",
    "skirmish_flag_victory": "flag_skirmish_5",
    "skirmish_pointer": "arrow_friendly",
    "skirmish_target": "arrow_enemy",
}

# 2. Infantry / human breeds (0.mi)
BREED_MAP = {
    # German late-war
    "mp/ger/ap_miner": "mp/ger/late/miner-ap",
    "mp/ger/at_miner": "mp/ger/late/miner-at",
    "mp/ger/at_rifle": "mp/ger/late/antitank_1",
    "mp/ger/at_rifle2": "mp/ger/late/antitank_2",
    "mp/ger/bazooker": "mp/ger/late/antitank_1",
    "mp/ger/bazooker2": "mp/ger/late/antitank_2",
    "mp/ger/elite": "mp/ger/late/fallsch_1",
    "mp/ger/elite2": "mp/ger/late/fallsch_2",
    "mp/ger/elite3": "mp/ger/late/fallsch_3",
    "mp/ger/elite4": "mp/ger/late/fallsch_4",
    "mp/ger/elite5": "mp/ger/late/fallsch_mg",
    "mp/ger/elite6": "mp/ger/late/pioneer_1",
    "mp/ger/flamer": "mp/ger/late/begleitpio_flame",
    "mp/ger/flamer2": "mp/ger/late/begleitpio_flame",
    "mp/ger/home_guard": "mp/ger/late/volksg_1",
    "mp/ger/home_guard2": "mp/ger/late/volksg_2",
    "mp/ger/medic": "mp/ger/late/medic",
    "mp/ger/mgun": "mp/ger/late/begleitgren_mg",
    "mp/ger/oficer": "mp/ger/late/officer",
    "mp/ger/radioman": "mp/ger/late/signaller",
    "mp/ger/rifle": "mp/ger/late/begleitgren_rifle",
    "mp/ger/rifle2": "mp/ger/late/begleitgren_sa",
    "mp/ger/smg": "mp/ger/late/fusilier_smg",
    "mp/ger/smg2": "mp/ger/late/begleitgren_stg",
    "mp/ger/sniper": "mp/ger/late/sniper",
    "mp/ger/sniper2": "mp/ger/late/sniper2",
    "mp/ger/squadleader": "mp/ger/late/begleitgren_sl",
    "mp/ger/squadleader2": "mp/ger/late/begleitgren_sl_stg",
    "mp/ger/sturmovik": "mp/ger/late/begleitgren_stg",
    "mp/ger/sturmovik2": "mp/ger/late/begleitgren_rifle_pzf",
    "mp/ger/sturmovik3": "mp/ger/late/pioneer_2",
    "mp/ger/tankman": "mp/ger/late/tankman",
    "mp/ger/tankman2": "mp/ger/late/tankman_vet",
    # Soviet late-war
    "mp/rus/ap_miner": "mp/rus/late/miner-ap",
    "mp/rus/at_miner": "mp/rus/late/miner-at",
    "mp/rus/at_rifle": "mp/rus/late/antitank_ptrs",
    "mp/rus/at_rifle2": "mp/rus/late/antitank_ptrs",
    "mp/rus/bazooker": "mp/rus/late/antitank_1",
    "mp/rus/bazooker2": "mp/rus/late/antitank_2",
    "mp/rus/elite": "mp/rus/late/elite_guards_rifle",
    "mp/rus/elite2": "mp/rus/late/elite_guards_mg",
    "mp/rus/elite3": "mp/rus/late/elite_guards_senior_rifle",
    "mp/rus/elite4": "mp/rus/late/elite_guards_nco",
    "mp/rus/elite5": "mp/rus/late/assault-sap_1",
    "mp/rus/elite6": "mp/rus/late/assault-sap_2",
    "mp/rus/flamer": "mp/rus/late/flamer",
    "mp/rus/flamer2": "mp/rus/late/sapper_flamer",
    "mp/rus/home_guard": "mp/rus/late/conscript_rifle",
    "mp/rus/home_guard2": "mp/rus/late/conscript_nco",
    "mp/rus/medic": "mp/rus/late/medic",
    "mp/rus/mgun": "mp/rus/late/cav_mg",
    "mp/rus/oficer": "mp/rus/late/elite_guards_nco",
    "mp/rus/radioman": "mp/rus/late/signaller",
    "mp/rus/rifle": "mp/rus/late/cav_rifle",
    "mp/rus/rifle2": "mp/rus/late/cav_senior_rifle",
    "mp/rus/smg": "mp/rus/late/cav_smg_drum",
    "mp/rus/smg2": "mp/rus/late/cav_senior_smg",
    "mp/rus/sniper": "mp/rus/late/sniper",
    "mp/rus/squadleader": "mp/rus/late/elite_guards_nco",
    "mp/rus/squadleader2": "mp/rus/late/assault-sap_sl",
    "mp/rus/sturmovik": "mp/rus/late/assault-sap_1",
    "mp/rus/sturmovik2": "mp/rus/late/assault-sap_2",
    "mp/rus/sturmovik3": "mp/rus/late/assault-sap_3",
    "mp/rus/tankman": "mp/rus/late/tankman",
    "mp/rus/tankman2": "mp/rus/late/tankman_ace",
    # USA late-war (Liberation DLC)
    "mp/usa/ap_miner": "mp/usa/late/101st_demo",
    "mp/usa/at_miner": "mp/usa/late/101st_demo",
    "mp/usa/bazooker": "mp/usa/late/101st_at_m9",
    "mp/usa/bazooker2": "mp/usa/late/101st_at_m9a1",
    "mp/usa/elite": "mp/usa/late/101st_eng_rifle",
    "mp/usa/elite2": "mp/usa/late/101st_eng_smg",
    "mp/usa/elite3": "mp/usa/late/101st_bar",
    "mp/usa/elite4": "mp/usa/late/101st_eng_sl",
    "mp/usa/elite5": "mp/usa/late/101st_eng_at_m9a1",
    "mp/usa/elite6": "mp/usa/late/101st_demo",
    "mp/usa/flamer": "mp/usa/late/101st_eng_flamer",
    "mp/usa/flamer2": "mp/usa/late/101st_eng_flamer",
    "mp/usa/home_guard": "mp/usa/late/101st_carbine",
    "mp/usa/home_guard2": "mp/usa/late/101st_eng_rifle",
    "mp/usa/medic": "mp/usa/late/1st_special_medic",
    "mp/usa/mgun": "mp/usa/late/101st_bar",
    "mp/usa/oficer": "mp/usa/late/101st_company_com",
    "mp/usa/radioman": "mp/usa/late/101st_company_radio",
    "mp/usa/rifle": "mp/usa/late/101st_eng_rifle",
    "mp/usa/rifle2": "mp/usa/late/101st_carbine",
    "mp/usa/smg": "mp/usa/late/101st_eng_smg",
    "mp/usa/smg2": "mp/usa/late/101st_eng_sl_smg",
    "mp/usa/sniper": "mp/usa/late/101st_eng_rifle",
    "mp/usa/squadleader": "mp/usa/late/101st_eng_sl",
    "mp/usa/squadleader2": "mp/usa/late/101st_eng_sl_sgt",
    "mp/usa/sturmovik": "mp/usa/late/101st_eng_smg",
    "mp/usa/sturmovik2": "mp/usa/late/101st_bar",
    "mp/usa/sturmovik3": "mp/usa/late/101st_demo",
    "mp/usa/tankman": "mp/usa/late/101st_crew",
    "mp/usa/tankman2": "mp/usa/late/101st_crew",
    # Narrators / hints
    "special/hint": "narrator/assistant",
    "special/narrator_ger": "narrator/assistant",
    "special/narrator_rus": "narrator/assistant",
    "special/narrator_usa": "narrator/assistant",
}

# 3. Map props, buildings, foliage, roads, trenches (map)
MAP_ENTITY_MAP = {
    # Farm buildings & barns (real full-size GoH European/Ostfront farmhouses & barns!)
    "e_farm_112": "e_farm002",
    "e_farm_112a": "e_farm003",
    "e_farm_120": "eastern-europe_barns1",
    "e_farm_121ca": "e_farm004",
    "e_farm_122ca": "eastern-europe_farm",
    "e_farm_c3": "eastern-europe_house1",
    "e_farm_c4": "eastern-europe_house1",
    "e_farm_c5": "soviet_rural_house1",
    "e_farm_c7": "soviet_rural_house1",
    "e_farm_c9": "soviet_barn",
    "e_hangar_111": "hangar_01",
    "aerostrip": "clay_road",
    # Trees & bushes (all verified 0-missing-texture in GoH flora.pak)
    "ash_tree_bush1": "point-bush_small_g",
    "ash_tree_bush2": "point-bush_01_g",
    "ash_tree3": "ashtree1",
    "bush_curly": "bush_generic_5",
    "bush_curly_a": "bush_generic_5a",
    "bush_curly_b": "bush_generic_5b",
    "new_birch": "birch_adult_01",
    "new_tree2": "ashtree1",
    "new_tree3": "ashtree2",
    "new_tree33": "birch_tall_01",
    "pine": "pine1",
    "pine_small": "pine3",
    "pine_smallest": "pine4",
    # Grass, crops, reeds, petals (all verified 0-missing-texture in GoH flora.pak)
    "burn_grass1": "autumn_grass1",
    "burn_grass1#1": "autumn_grass1",
    "cane2": "tall-grass_01",
    "cane3": "tall-grass_01a",
    "farm_corn1": "b2corn01",
    "farm_corn2": "b2corn02",
    "farm_corn6": "b2corn03",
    "farm_corn7": "b2corn04",
    "grass1": "finland_grass_short1",
    "petals": "finland_grass_short2",
    "reed4": "finland_grass_weeds",
    "trava": "finland_grass_short3",
    "wheat_big": "wheat_bush",
    "wheat_new1": "gem2_wheat",
    # Roads & ground decals
    "back_road": "clay_road",
    "back_road_turn": "clay_road_turn",
    "road_sand5f1": "clay_road_02",
    "road_sand5f1#cross1_k": "clay_road_crossroad",
    "road_sand5w1": "clay_road_03",
    "road_sand5w1a": "clay_road_03_turn",
    "clay1": "clay_pile",
    "clay_11": "clay_tracks",
    "clay_111": "clay_tracks",
    "clay_11a": "clay_tracks_turn",
    "clay_11angle": "clay_rim_curved",
    "groove_sand": "clay_tracks",
    "groove_sand2": "clay_tracks_turn",
    "ground_clay5": "clay_road_03_spring",
    "ground_clay5a": "clay_road_03_turn_spring",
    "ground_clay5b": "clay_road_03_turn_a_spring",
    # Rocks, cliffs & stone walls
    "broken_wall_stones": "crash_stone1",
    "crash_wall2": "crash_brick1",
    "crash_wood1b": "crash_wood1",
    "rock_island1b_aut": "euro_cliff1",
    "rock_island3_aut": "euro_cliff2",
    "rockwall": "euro_cliff3",
    "rockwall1": "euro_cliff4",
    "rockwall2": "euro_cliff5",
    "rockwall3": "euro_cliff6",
    "rockwall4": "euro_cliff7",
    "rockwall5": "rock_brown_big",
    "stone_af1a": "landscape_rock_01",
    "stone_af1b": "landscape_rock_02",
    "stone_af1c": "landscape_rock_03",
    "stone_af1d": "landscape_rock_04",
    "stone_af1e": "landscape_rock_05",
    "stone_af1f": "landscape_rock_06",
    "stone_af1g": "granite_rock",
    # Trenches, bunkers & sandbags
    "dzot1": "forest_bunker_entrance",
    "sandbag3": "sandbag_five",
    "trench_ground2": "euro_log_trench_dirt_straight2",
    "trench_ground_exit2": "euro_log_trench_dirt_exit",
    "trench_ground_t": "euro_log_trench_dirt_intersection2",
    "trench_ground_turn": "euro_log_trench_dirt_turn3",
    "trench_ground_turn2": "euro_log_trench_dirt_turn4",
    "trench_tank_2_ls": "euro_log_trench_dirt_emplacement2_at",
    "trench_tank_2_rs": "euro_log_trench_dirt_emplacement2",
    "ditch_tank": "euro_log_trench_dirt_straight2",
    "ditch_tank_side": "euro_log_trench_dirt_end2",
    "ditch_tank_turn": "euro_log_trench_dirt_turn3",
    # Railway, wagons & station props (platform / platform_can are railway flatcars in AS2!)
    "platform": "wagon_plato",
    "platform_can": "wagon_plato",
    "rail_crossing_wood2": "rail_crossing_wood",
    "steam_locomotive": "wagon_tanker",
    "tendor": "wagon_plato",
    "tradevan_big": "wagon1",
    # Barrels, bags, haystacks, netting, misc entourage
    # bags_big / bags_big2 in AS2 are supply/grain sacks, NOT sandbags
    "bags_big": "crate_one",
    "bags_big2": "crate_one",
    "barrel_woods": "barrel1",
    "barrel_woods4": "barrel2",
    "barrel_woods6": "barrel3",
    "barrel_woods_small": "barrel4",
    "barrel_woods_small1": "barrel5",
    "bucket": "barrel4",
    "netting": "tent1",
    "netting1": "tent2",
    "shaft_euro": "euro_cargo_stack",
    "stack_euro": "euro_hay_stack1",
    "trash7": "crash_wood1",
    # Water & pools
    "pool2_b": "waterpool",
    "pool3": "waterpool",
    "trace_waves1a": "water_river_small",
    "water_river4": "water_river",
}

# Map props to OMIT completely instead of replacing with wrong-scale GoH 3D objects:
# - AS2 pebble/cliff-edge decals (stone_af1*, rockwall*, rock_island*) became huge GoH boulders/cliffs
# - AS2 trench overlays (trench_ground*, trench_tank*, ditch_tank*) have different pivots/sizes than GoH
#   while the actual trench ditches are already carved into map.net!
# - AS2 flat clay ground decals (ground_clay5*, clay_11*) became 3D road strips
SKIP_MAP_ENTITIES = {
    "stone_af1a", "stone_af1b", "stone_af1c", "stone_af1d", "stone_af1e", "stone_af1f", "stone_af1g",
    "rockwall", "rockwall1", "rockwall2", "rockwall3", "rockwall4", "rockwall5",
    "rock_island1b_aut", "rock_island3_aut",
    "trench_ground", "trench_ground2", "trench_ground_exit2", "trench_ground_t",
    "trench_ground_turn", "trench_ground_turn2", "trench_ground_mgun",
    "trench_tank_2_ls", "trench_tank_2_rs", "trench_cannon_2_ls", "trench_cannon_2_rs",
    "ditch_tank", "ditch_tank_side", "ditch_tank_turn",
    "ground_clay5", "ground_clay5a", "ground_clay5b",
    "clay_11", "clay_111", "clay_11a", "clay_11angle",
    "121_f3w1b", "121_f3w2b",
}

# Regex patterns for purely decorative AS2 ground decals, tracks, footprints, leaves,
# water lilies, winter rock/snow rims, and stumps that should be OMITTED cleanly
# (rather than turning into wrong-scale 3D roads, stone piles, or full trees).
SKIP_MAP_PATTERNS = [
    re.compile(r"^trace_", re.I),
    re.compile(r"^track_snow", re.I),
    re.compile(r"^leaves\d", re.I),
    re.compile(r"^water_lily", re.I),
    re.compile(r"^sand_pebble", re.I),
    re.compile(r"^rocks\d+_w", re.I),
    re.compile(r"^stouns", re.I),
    re.compile(r"^stone_4a$", re.I),
    re.compile(r"^ground_clay", re.I),
    re.compile(r"^clay_s\d", re.I),
    re.compile(r"^rough_earth", re.I),
    re.compile(r"^mound_steep", re.I),
    re.compile(r"^thawed_soil", re.I),
    re.compile(r"^snow_rim", re.I),
    re.compile(r"^hill_snow", re.I),
    re.compile(r"^aerostrip", re.I),
    re.compile(r"^stub_", re.I),
    re.compile(r"^\d{3}$"),
]


def should_skip_map_prop(name: str) -> bool:
    base = name.split("#")[0]
    if name in SKIP_MAP_ENTITIES or base in SKIP_MAP_ENTITIES:
        return True
    return any(p.search(base) for p in SKIP_MAP_PATTERNS)


# Category-based fallback rules ONLY for scenery props in `map` that aren't in MAP_ENTITY_MAP
# Every fallback target here is verified to exist in GoH!
MAP_PROP_FALLBACK_RULES = [
    (re.compile(r"sandbag", re.I), "sandbag_five"),
    (re.compile(r"fence|hedge|wire", re.I), "fence-wood_3"),
    (re.compile(r"crater", re.I), "crater_medium"),
    (re.compile(r"birch", re.I), "birch_adult_01"),
    (re.compile(r"pine|fir|spruce", re.I), "pine2"),
    (re.compile(r"tree|oak|ash|apple|poplar|topol|willow|orchard", re.I), "ashtree1"),
    (re.compile(r"bush|shrub|vine|^pla\d|plant", re.I), "point-bush_small_g"),
    (re.compile(r"wheat|corn|weat", re.I), "gem2_wheat"),
    (re.compile(r"grass|reed|cane|flower|dried|weed|fern|clover|sunflover", re.I), "finland_grass_short1"),
    (re.compile(r"road|asf|cobble|street|path", re.I), "clay_road"),
    (re.compile(r"rail|station", re.I), "railroad5"),
    (re.compile(r"water|river|pool|bog|pond", re.I), "waterpool"),
    (re.compile(r"rock|stone|cliff|clay", re.I), "crash_stone1"),
    (re.compile(r"barn|shed|farm|hangar", re.I), "eastern-europe_barns1"),
    (re.compile(r"house|home|building|cottage|mill|church", re.I), "eastern-europe_house1"),
    (re.compile(r"barrel", re.I), "barrel1"),
    (re.compile(r"box|crate|chest|cart|telega|trailer", re.I), "crate_one"),
    (re.compile(r"hay|stack", re.I), "euro_hay_stack1"),
    (re.compile(r"tent|camp|net", re.I), "tent1"),
    (re.compile(r"bunker|dzot|pillbox", re.I), "forest_bunker_entrance"),
    (re.compile(r"crash|destroy|ruin|trash|rubble|debris|brick|beam|log|wood|timber|post", re.I), "crash_wood1"),
    (re.compile(r"snow|ice", re.I), "clay_winter"),
]


def resolve_map_prop(name: str, goh_entities: set) -> str:
    """Resolve an AS2 map scenery entity name to a verified GoH entity."""
    if name in goh_entities:
        return name
    if name in MAP_ENTITY_MAP:
        return MAP_ENTITY_MAP[name]
    # Strip #variant suffix if base exists in GoH or MAP_ENTITY_MAP
    base = name.split("#")[0]
    if base in goh_entities:
        return base
    if base in MAP_ENTITY_MAP:
        return MAP_ENTITY_MAP[base]
    for pat, target in MAP_PROP_FALLBACK_RULES:
        if pat.search(name):
            return target
    return "crash_stone1"


# 4. Land textures (AS2 mtl*.mtl -> GoH .materials)
LAND_TEX_MAP = {
    # Dirt / roads
    "/texture/land/dirt/clay_1f_road": "/texture/land/goh_summer/euro/euro_dirt_dry",
    "/texture/land/dirt/clay_2": "/texture/land/goh_summer/euro/euro_dirt",
    "/texture/land/dirt/clay_new1": "/texture/land/goh_summer/euro/dirt_euro1",
    "/texture/land/dirt/clay_new1f2": "/texture/land/goh_summer/euro/dirt_euro1",
    "/texture/land/dirt/clay_new2 q1": "/texture/land/goh_summer/euro/euro_dirt",
    "/texture/land/dirt/clay_new21": "/texture/land/goh_summer/euro/euro_dirt_moist",
    "/texture/land/dirt/clay_pitt2": "/texture/land/goh_summer/euro/euro_dirt_dry",
    "/texture/land/dirt/muddy_3": "/texture/land/goh_summer/euro/euro_dirt_wet",
    "/texture/land/dirt/soil_1_trash2": "/texture/land/goh_spring/soil",
    # Winter dirt / fields / snow (Kharkov)
    "/texture/land/dirt/.winter/clay_snow2": "/texture/land/goh_spring/soil_snow",
    "/texture/land/dirt/.winter/muddy_win_2": "/texture/land/goh_spring/muddy_win_1_snow",
    "/texture/land/fields/.winter/fieldsnow_1": "/texture/land/goh_winter/finland/dirty_snow",
    "/texture/land/fields/.winter/fieldsnow_3": "/texture/land/goh_winter/finland/dirty_snow_dry",
    "/texture/land/winter/ice_crust3": "/texture/land/goh_winter/finland/ice_clean",
    "/texture/land/winter/snow_1a": "/texture/land/goh_winter/finland/high_snow_1",
    "/texture/land/winter/snow_trace": "/texture/land/goh_winter/finland/high_snow_2",
    # Fields / grass
    "/texture/land/fields/cornfield": "/texture/land/goh_summer/euro/euro_field1",
    "/texture/land/fields/cornfield_2": "/texture/land/goh_summer/euro/euro_field1",
    "/texture/land/fields/cornfield_2a": "/texture/land/goh_summer/euro/euro_field1",
    "/texture/land/fields/field_01": "/texture/land/goh_summer/euro/euro_field1",
    "/texture/land/fields/field_02": "/texture/land/goh_summer/euro/euro_field1",
    "/texture/land/fields/field_1": "/texture/land/goh_summer/euro/euro_field1",
    "/texture/land/fields/field_57": "/texture/land/goh_spring/soil",
    "/texture/land/fields/fieldgrass1": "/texture/land/goh_spring/grass_spring",
    "/texture/land/fields/fieldgrass2": "/texture/land/goh_spring/grass_spring",
    "/texture/land/fields/fieldgrass3": "/texture/land/goh_spring/grass_spring_var",
    "/texture/land/fields/fieldgrass4": "/texture/land/goh_spring/grass_spring_var",
    "/texture/land/fields/stubble_field3": "/texture/land/goh_spring/grass_dry_var1",
    "/texture/land/fields/stubble_field3a": "/texture/land/goh_spring/grass_brown",
    "/texture/land/fields/stubble_field_growed": "/texture/land/goh_spring/grass_spring",
    "/texture/land/fields/tillage_green1d": "/texture/land/goh_spring/soil",
    "/texture/land/grass/forestfloor1": "/texture/land/goh_summer/balcans/forest_balcans",
    "/texture/land/grass/gramma_111": "/texture/land/goh_spring/grass_07",
    "/texture/land/grass/gramma_111_vic1": "/texture/land/goh_spring/grass_07",
    "/texture/land/grass/gramma_12": "/texture/land/goh_spring/grass_spring",
    "/texture/land/grass/gramma_8": "/texture/land/goh_spring/grass_spring_var",
    "/texture/land/grass/gramma_8d": "/texture/land/goh_spring/grass_dry_var1",
    "/texture/land/grass/grass_flowers1": "/texture/land/goh_summer/balcans/grass_balcans",
    "/texture/land/grass/grass_pebb3": "/texture/land/goh_summer/balcans/rocky_moss_balcans",
    "/texture/land/grass/steppe_2a": "/texture/land/goh_spring/grass_dry_var1",
    "/texture/land/leaves/foliage_forest1": "/texture/land/goh_summer/balcans/forest_balcans",
    "/texture/land/leaves/foliage_ongrass": "/texture/land/goh_summer/balcans/forest_balcans",
    # Rock / town
    "/texture/land/rock/cliffy_1": "/texture/land/goh_rock/stones_4",
    "/texture/land/rock/cliffy_grass2": "/texture/land/goh_summer/balcans/rocky_moss_balcans",
    "/texture/land/rock/pebble_redish": "/texture/land/goh_rock/stones_6",
    "/texture/land/rock/rock1a3": "/texture/land/goh_rock/stones_4",
    "/texture/land/rock/stone_02_grey": "/texture/land/goh_rock/stones_4",
    "/texture/land/town/asfalt_ground3a": "/texture/land/goh_pavement/asphalt",
    "/texture/land/town/asfalt_road2": "/texture/land/goh_pavement/asphalt_a1",
    "/texture/land/town/destroy_2a": "/texture/land/goh_pavement/tiles_destroyed",
    "/texture/land/town/qgarden_9b": "/texture/land/goh_summer/euro/cobbles",
}

# 5. Environments
ENV_MAP = {
    "skirmish/ger-seelowheights": "dynamic_campaign/spring/cloudy/midday_1",
    "skirmish/rus-kursk": "dynamic_campaign/summer/clear/midday_1",
    "skirmish/ger-kharkov": "dynamic_campaign/winter/clear/midday_1",
    "skirmish/usa-bocage": "dynamic_campaign/summer/clear/morning_01",
    "skirmish/usa-omaha": "dynamic_campaign/summer/clear/morning_01",
}
