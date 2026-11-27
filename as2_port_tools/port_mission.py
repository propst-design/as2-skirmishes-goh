"""Reusable AS2 -> Call to Arms: Gates of Hell skirmish mission porter.

Supports single-mission and multi-mission batch porting, full asset validation
against installed GoH .pak files, GoH mods/ installation, and .zip packaging.
"""

import argparse
import glob
import os
import re
import shutil
import zipfile
from pathlib import Path

from mappings import (
    BREED_MAP,
    ENV_MAP,
    LAND_TEX_MAP,
    MAP_ENTITY_MAP,
    MI_ENTITY_MAP,
    resolve_map_prop,
)

DEFAULT_AS2_ROOT = r"F:\SteamLibrary\steamapps\common\Men of War Assault Squad 2"
DEFAULT_AS2_PAK = os.path.join(DEFAULT_AS2_ROOT, "resource", "map.pak")
DEFAULT_GOH_ROOT = r"D:\SteamLibrary\steamapps\common\Call to Arms - Gates of Hell"

# Classic 4-mission pack (Germany, USSR, USA across Spring, Summer, Winter)
DEFAULT_BATCH = [
    ("map/single/02_ger-skirmish/04_ger-seelowheights/", "04_ger-seelowheights", "Seelow Heights"),
    ("map/single/04_rus-skirmish/04_rus-kursk/", "04_rus-kursk", "Kursk"),
    ("map/single/02_ger-skirmish/05_ger-kharkov/", "05_ger-kharkov", "Kharkov"),
    ("map/single/01_usa-skirmish/01b_usa-bocage/", "01b_usa-bocage", "Bocage"),
]


def index_goh_assets(goh_root: str):
    """Build exact sets of valid GoH entities, breeds, land textures, and environments."""
    goh_res = os.path.join(goh_root, "resource")
    paks = glob.glob(os.path.join(goh_res, "*.pak"))
    for sub in ["entity", "texture", "map", "interface", "sound"]:
        sd = os.path.join(goh_res, sub)
        if os.path.exists(sd):
            paks.extend(glob.glob(os.path.join(sd, "**", "*.pak"), recursive=True))

    entities = set()
    breeds = set()
    land_tex = set()
    envs = set()
    icons = set()
    music = set()

    for pak in paks:
        try:
            with zipfile.ZipFile(pak) as z:
                for n in z.namelist():
                    nl = n.lower()
                    if nl.endswith(".def"):
                        entities.add(os.path.splitext(os.path.basename(n))[0])
                        entities.add(os.path.basename(os.path.dirname(n)))
                    elif "/breed/" in nl and nl.endswith(".set"):
                        idx = nl.find("/breed/")
                        breeds.add(nl[idx + len("/breed/") : -4])
                    elif "land/" in nl and (nl.endswith(".dds") or nl.endswith(".tif")):
                        idx = nl.find("land/")
                        land_tex.add("/texture/" + nl[idx:-4])
                    elif "set/environment/" in nl and nl.endswith(".set"):
                        idx = nl.find("set/environment/")
                        envs.add(nl[idx + len("set/environment/") : -4])
                    elif nl.startswith("scene/unit_icon/") and nl.endswith("_00.tga"):
                        icons.add(Path(n).stem[:-3].lower())
                    elif nl.startswith("music/") and nl.endswith((".wav", ".mp3", ".ogg")):
                        music.add("/" + nl)
        except Exception:
            pass

    return {
        "entities": entities,
        "breeds": breeds,
        "land_tex": land_tex,
        "envs": envs,
        "icons": icons,
        "music": music,
    }


def resolve_land_texture(diff: str, goh_land_tex: set) -> str:
    if diff.lower() in goh_land_tex:
        return diff
    if diff in LAND_TEX_MAP:
        return LAND_TEX_MAP[diff]
    dl = diff.lower()
    if "snow" in dl or "winter" in dl or "ice" in dl:
        return "/texture/land/goh_winter/finland/dirty_snow"
    if "cobble" in dl or "asfalt" in dl or "town" in dl or "brick" in dl:
        return "/texture/land/goh_pavement/asphalt"
    if "dirt" in dl or "clay" in dl or "mud" in dl or "sand" in dl:
        return "/texture/land/goh_summer/euro/euro_dirt"
    if "rock" in dl or "stone" in dl or "cliff" in dl:
        return "/texture/land/goh_rock/stones_4"
    return "/texture/land/goh_spring/grass_spring"


def convert_materials(z: zipfile.ZipFile, prefix: str, goh_land_tex: set) -> str:
    """Convert AS2 mtl0.mtl..mtlN.mtl files into a single GoH .materials file."""
    mtl_files = []
    for info in z.infolist():
        if info.filename.startswith(prefix) and info.filename.endswith(".mtl"):
            base = os.path.basename(info.filename)
            m = re.match(r"mtl(\d+)\.mtl$", base)
            if m:
                mtl_files.append((int(m.group(1)), info.filename))
    mtl_files.sort()

    out_lines = ["{materials"]
    for idx_num, fname in mtl_files:
        raw = z.read(fname).decode("utf-8", errors="replace")
        diffuses = re.findall(r'\{diffuse\s+"([^"]+)"', raw)
        out_lines.append(f'\t{{"mtl{idx_num}"')
        for diff in diffuses:
            target = resolve_land_texture(diff, goh_land_tex)
            out_lines.append("\t\t{layer bump")
            out_lines.append(f'\t\t\t{{diffuse "{target}"}}')
            if (target + "_nm").lower() in goh_land_tex:
                out_lines.append(f'\t\t\t{{bump "{target}_nm"}}')
            if (target + "_sp").lower() in goh_land_tex:
                out_lines.append(f'\t\t\t{{specular "{target}_sp"}}')
            out_lines.append("\t\t}")
        out_lines.append("\t}")
    out_lines.append("}")
    return "\n".join(out_lines) + "\n"


def strip_top_blocks(text: str, block_names: tuple[str, ...]) -> tuple[str, int]:
    """Remove top-level tabbed blocks (e.g. {Inventory ...}, {Covers ...}) from 0.mi."""
    pat = re.compile(r"^\t\{(?:" + "|".join(block_names) + r")\b")
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        if pat.match(lines[i]):
            depth = lines[i].count("{") - lines[i].count("}")
            i += 1
            while i < len(lines) and depth > 0:
                depth += lines[i].count("{") - lines[i].count("}")
                i += 1
            removed += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), removed


def strip_speaker_extenders(text: str) -> tuple[str, int]:
    """Remove {Extender "speaker" ...} blocks referencing missing AS2 ambient sounds."""
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        if '{Extender "speaker"' in lines[i]:
            depth = lines[i].count("{") - lines[i].count("}")
            i += 1
            while i < len(lines) and depth > 0:
                depth += lines[i].count("{") - lines[i].count("}")
                i += 1
            removed += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), removed


def strip_clip_water(map_text: str) -> str:
    """Remove AS2-only {water ...} lines inside map {Clips}."""
    return re.sub(r"^\t+\{water\s+[^}]+\}\r?\n", "", map_text, flags=re.M)


def remap_reinforcement_icons(mi_text: str, goh_icons: set) -> tuple[str, int]:
    """Remap AS2 reinforcement {image ...} icons to verified GoH scene/unit_icon names."""
    count = 0

    def pick_icon(raw: str) -> str:
        low = raw.lower()
        if low in goh_icons:
            return raw
        # Check if it's a remapped vehicle/cannon in MI_ENTITY_MAP
        if raw in MI_ENTITY_MAP and MI_ENTITY_MAP[raw].lower() in goh_icons:
            return MI_ENTITY_MAP[raw]
        # Faction-specific infantry / menu icons
        fac = "ger"
        if "(rus)" in low or "rus_" in low or "_rus" in low:
            fac = "rus"
        elif "(usa)" in low or "usa_" in low or "_usa" in low:
            fac = "usa"
        if "bazook" in low:
            cand = f"bazooka({fac})"
        elif "at_rifle" in low:
            cand = f"atrifle({fac})"
        elif any(w in low for w in ["rifle", "home_guard", "elite", "special", "sniper", "medic", "officer", "radio", "miner", "tankman"]):
            cand = f"autorifle({fac})"
        else:
            cand = f"doctrine({fac})"
        return cand if cand in goh_icons else "doctrine(ger)"

    def repl(m):
        nonlocal count
        old = m.group(1)
        new = pick_icon(old)
        if new != old:
            count += 1
        return f'{{image "{new}"}}'

    new_text = re.sub(r'\{image\s+"?([^"\s\}]+)"?\}', repl, mi_text)
    return new_text, count


MUSIC_MAP = {
    "/music/skirmish_background_01.mp3": "/music/action_theme_1.wav",
    "/music/skirmish_background_02.mp3": "/music/action_theme_2.wav",
    "/music/skirmish_hero_ger.mp3": "/music/action_theme_3.wav",
    "/music/skirmish_hero_rus.mp3": "/music/action_theme_4.wav",
    "/music/skirmish_hero_usa.mp3": "/music/airborne_action_lvl2.wav",
    "/music/skirmish_progress.mp3": "/music/airborne_ambient.wav",
    "/music/skirmish_won.mp3": "/music/action_theme_8.wav",
    "/music/skirmish_lost.mp3": "/music/airborne_ambient_calm.wav",
}


def remap_music(mi_text: str, goh_music: set) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        old = m.group(1)
        if old.lower() in goh_music:
            return m.group(0)
        new = MUSIC_MAP.get(old, "/music/action_theme_1.wav")
        count += 1
        return f'{{start "{new}"}}'

    new_text = re.sub(r'\{start\s+"(/music/[^"]+)"\}', repl, mi_text)
    return new_text, count


def remap_map_entities(text: str, goh_entities: set) -> tuple[str, int, int]:
    remapped = 0
    fallbacks = set()

    def repl(m):
        nonlocal remapped
        old = m.group(1)
        if old in goh_entities:
            return m.group(0)
        new = resolve_map_prop(old, goh_entities)
        remapped += 1
        if old not in MAP_ENTITY_MAP:
            fallbacks.add((old, new))
        return f'{{Entity "{new}"'

    new_text = re.sub(r'\{Entity\s+"([^"]+)"', repl, text)
    return new_text, remapped, len(fallbacks)


def remap_mi_entities(text: str, goh_entities: set) -> tuple[str, int]:
    count = 0
    combined = {**MAP_ENTITY_MAP, **MI_ENTITY_MAP}

    def repl(m):
        nonlocal count
        old = m.group(1)
        if old in combined:
            count += 1
            return f'{{Entity "{combined[old]}"'
        if old not in goh_entities:
            # Handle any skirmish_flag_* variant dynamically
            if old.startswith("skirmish_flag"):
                count += 1
                return '{Entity "flag_skirmish"'
            new = resolve_map_prop(old, goh_entities)
            count += 1
            return f'{{Entity "{new}"'
        return m.group(0)

    new_text = re.sub(r'\{Entity\s+"([^"]+)"', repl, text)
    return new_text, count


def remap_text_humans(text: str, mapping: dict) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        old = m.group(1)
        if old in mapping:
            count += 1
            return f'{{Human "{mapping[old]}"'
        return m.group(0)

    new_text = re.sub(r'\{Human\s+"([^"]+)"', repl, text)
    return new_text, count


def remap_environments(text: str, goh_envs: set) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        old = m.group(1)
        if old.lower() in goh_envs:
            return m.group(0)
        new = ENV_MAP.get(old, "dynamic_campaign/summer/clear/midday_1")
        count += 1
        return f'{{Environment "{new}"'

    new_text = re.sub(r'\{Environment\s+"([^"]+)"', repl, text)
    return new_text, count


def convert_as2_lng_to_pot(
    as2_root: str,
    as2_prefix: str,
    campaign_id: str,
    mission_id: str,
) -> tuple[str, int]:
    """Convert AS2 localization.pak mission .lng file into GoH gettext .pot format."""
    loc_pak = os.path.join(as2_root, "localization.pak")
    rel = as2_prefix.rstrip("/")
    if rel.startswith("map/"):
        rel = rel[len("map/") :]
    lng_path = f"mission/{rel}.lng"

    entries = []
    if os.path.exists(loc_pak):
        with zipfile.ZipFile(loc_pak) as z:
            if lng_path in z.namelist():
                raw = z.read(lng_path).decode("utf-8", errors="replace")
                for m in re.finditer(r'\{\s*"([^"]+)"\s+"((?:\\.|[^"\\])*)"\s*\}', raw):
                    entries.append((m.group(1), m.group(2)))

    lines = [
        'msgid ""',
        'msgstr ""',
        f'"Project-Id-Version: Gates of Hell ({mission_id})\\n"',
        '"Language: en\\n"',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        "",
    ]
    for key, val in entries:
        val_escaped = val.replace("\r\n", "\\n").replace("\n", "\\n")
        lines.append(f'msgctxt "mission/single/{campaign_id}/{mission_id}/{key}"')
        lines.append(f'msgid "{val_escaped}"')
        lines.append('msgstr ""')
        lines.append("")
    return "\n".join(lines), len(entries)


def copy_as2_voiceovers(
    as2_root: str,
    as2_prefix: str,
    mod_dir: Path,
    campaign_id: str,
    mission_id: str,
) -> int:
    """Copy mission voiceover .wav files from AS2 resource/language.pak into the mod."""
    lang_pak = os.path.join(as2_root, "resource", "language.pak")
    rel = as2_prefix.rstrip("/")
    if rel.startswith("map/"):
        rel = rel[len("map/") :]
    src_prefix = f"sound/mission/{rel}/"
    dst_dir = mod_dir / "resource" / "sound" / "mission" / "single" / campaign_id / mission_id
    copied = 0
    if os.path.exists(lang_pak):
        with zipfile.ZipFile(lang_pak) as z:
            for n in z.namelist():
                if n.startswith(src_prefix) and not n.endswith("/"):
                    dst_dir.mkdir(parents=True, exist_ok=True)
                    (dst_dir / os.path.basename(n)).write_bytes(z.read(n))
                    copied += 1
    return copied


def ensure_mod_and_campaign_shell(
    mod_dir: Path,
    campaign_id: str,
    campaign_name: str,
    goh_root: str,
):
    """Create mod.info, campaign interface.set, campaign art, and campaign.pot."""
    mod_dir.mkdir(parents=True, exist_ok=True)
    mod_info = (
        "{mod\n"
        '\t{name "AS2 Classic Skirmishes"}\n'
        '\t{desc "Ports of classic Men of War: Assault Squad 2 skirmish missions (Seelow Heights, Kursk, Kharkov, Bocage) for Call to Arms: Gates of Hell."}\n'
        '\t{minGameVersion "1.000.0"}\n'
        '\t{maxGameVersion "2.000.0"}\n'
        "}\n"
    )
    (mod_dir / "mod.info").write_text(mod_info, encoding="utf-8")

    camp_dir = mod_dir / "resource" / "map" / "single" / campaign_id
    camp_dir.mkdir(parents=True, exist_ok=True)
    camp_interface = (
        "{location\n"
        "\t{side ger}\n"
        "\t{enableProgression 0}\n"
        "\t{background\n"
        '\t\t{media ""\n'
        '\t\t\t{file "/music/panzerlied" loop}\n'
        "\t\t}\n"
        "\t}\n"
        "}\n"
    )
    (camp_dir / "interface.set").write_text(camp_interface, encoding="utf-8")

    dlc1_pak = os.path.join(goh_root, "resource", "dlc1.pak")
    if os.path.exists(dlc1_pak):
        with zipfile.ZipFile(dlc1_pak) as z:
            for art in ["background.dds", "header.dds", "minimap.dds"]:
                src = f"map/single/02-ger_skirmish/{art}"
                if src in z.namelist():
                    (camp_dir / art).write_bytes(z.read(src))

    loc_camp_dir = (
        mod_dir / "localizations" / "default" / "interface" / "text" / "mission" / "single" / campaign_id
    )
    loc_camp_dir.mkdir(parents=True, exist_ok=True)
    camp_pot = (
        'msgid ""\n'
        'msgstr ""\n'
        '"Project-Id-Version: AS2 Skirmishes\\n"\n'
        '"Language: en\\n"\n'
        '"MIME-Version: 1.0\\n"\n'
        '"Content-Type: text/plain; charset=UTF-8\\n"\n'
        '"Content-Transfer-Encoding: 8bit\\n"\n\n'
        f'msgctxt "mission/single/{campaign_id}/campaign/title"\n'
        'msgid "1941-45"\n'
        'msgstr ""\n\n'
        f'msgctxt "mission/single/{campaign_id}/campaign/name"\n'
        f'msgid "{campaign_name}"\n'
        'msgstr ""\n'
    )
    (loc_camp_dir / "campaign.pot").write_text(camp_pot, encoding="utf-8")


def validate_port(mission_dir: Path, goh_idx: dict) -> dict:
    """Validate every entity, human breed, environment, land texture, and brace balance."""
    map_txt = (mission_dir / "map").read_text(encoding="utf-8")
    mi_txt = (mission_dir / "0.mi").read_text(encoding="utf-8")
    mat_txt = (mission_dir / ".materials").read_text(encoding="utf-8")

    map_ents = set(re.findall(r'\{Entity\s+"([^"]+)"', map_txt))
    mi_ents = set(re.findall(r'\{Entity\s+"([^"]+)"', mi_txt))
    mi_humans = set(re.findall(r'\{Human\s+"([^"]+)"', mi_txt))
    envs = set(re.findall(r'\{Environment\s+"([^"]+)"', map_txt + "\n" + mi_txt))
    texs = set(re.findall(r'\{(?:diffuse|bump|specular)\s+"([^"]+)"', mat_txt))
    icons = set(re.findall(r'\{image\s+"?([^"\s\}]+)"?\}', mi_txt))
    musics = set(re.findall(r'\{start\s+"(/music/[^"]+)"\}', mi_txt))

    brace_errors = []
    for fname in [".materials", "map", "0.mi", "interface.set"]:
        t = (mission_dir / fname).read_text(encoding="utf-8")
        if t.count("{") != t.count("}"):
            brace_errors.append(f"{fname}({t.count('{') - t.count('}')})")

    return {
        "missing_map_entities": sorted(e for e in map_ents if e not in goh_idx["entities"]),
        "missing_mi_entities": sorted(e for e in mi_ents if e not in goh_idx["entities"]),
        "missing_breeds": sorted(h for h in mi_humans if h.lower() not in goh_idx["breeds"]),
        "missing_envs": sorted(e for e in envs if e.lower() not in goh_idx["envs"]),
        "missing_textures": sorted(t for t in texs if t.lower() not in goh_idx["land_tex"]),
        "missing_icons": sorted(i for i in icons if i.lower() not in goh_idx["icons"]),
        "missing_music": sorted(m for m in musics if m.lower() not in goh_idx["music"]),
        "brace_errors": brace_errors,
        "counts": {
            "map_entities": len(map_ents),
            "mi_entities": len(mi_ents),
            "mi_humans": len(mi_humans),
            "envs": len(envs),
            "textures": len(texs),
            "icons": len(icons),
            "music": len(musics),
        },
    }


def port_single(
    z: zipfile.ZipFile,
    as2_root: str,
    as2_prefix: str,
    goh_root: str,
    goh_idx: dict,
    mod_dir: Path,
    campaign_id: str,
    mission_id: str,
    include_net_grs: bool = True,
) -> bool:
    print(f"\n=== Porting {mission_id} ({as2_prefix}) ===")
    mission_dir = mod_dir / "resource" / "map" / "single" / campaign_id / mission_id
    mission_dir.mkdir(parents=True, exist_ok=True)

    # 1. Binary terrain & preview art
    copy_files = ["map.ply", "minimap.dds", "preview.dds"]
    if include_net_grs:
        copy_files.extend(["map.net", "map.grs"])
    for fn in copy_files:
        src = as2_prefix + fn
        if src in z.namelist():
            (mission_dir / fn).write_bytes(z.read(src))

    # Header art from GoH dlc1
    dlc1_pak = os.path.join(goh_root, "resource", "dlc1.pak")
    if os.path.exists(dlc1_pak):
        with zipfile.ZipFile(dlc1_pak) as dz:
            for art in ["header.dds", "header_interface.png"]:
                src = f"map/single/02-ger_skirmish/1945-04-ger_berlin/{art}"
                if src in dz.namelist():
                    (mission_dir / art).write_bytes(dz.read(src))

    # 2. Materials
    mat_content = convert_materials(z, as2_prefix, goh_idx["land_tex"])
    (mission_dir / ".materials").write_text(mat_content, encoding="utf-8")

    # 3. Map file
    map_txt = z.read(as2_prefix + "map").decode("utf-8", errors="replace")
    map_txt = strip_clip_water(map_txt)
    map_txt, map_ent_n, fb_n = remap_map_entities(map_txt, goh_idx["entities"])
    map_txt, _ = remap_environments(map_txt, goh_idx["envs"])
    (mission_dir / "map").write_text(map_txt, encoding="utf-8")

    # 4. 0.mi file
    mi_txt = z.read(as2_prefix + "0.mi").decode("utf-8", errors="replace")
    mi_txt, stripped_n = strip_top_blocks(mi_txt, ("Inventory", "Covers"))
    mi_txt, spk_n = strip_speaker_extenders(mi_txt)
    mi_txt, mi_ent_n = remap_mi_entities(mi_txt, goh_idx["entities"])
    mi_txt, mi_hum_n = remap_text_humans(mi_txt, BREED_MAP)
    mi_txt, _ = remap_environments(mi_txt, goh_idx["envs"])
    mi_txt, icon_n = remap_reinforcement_icons(mi_txt, goh_idx["icons"])
    mi_txt, mus_n = remap_music(mi_txt, goh_idx["music"])
    (mission_dir / "0.mi").write_text(mi_txt, encoding="utf-8")

    # 5. Mission interface.set, localization .pot, and voiceovers
    (mission_dir / "interface.set").write_text("{location\n\t{level 0}\n\t{level_set 1}\n}\n", encoding="utf-8")
    loc_camp_dir = (
        mod_dir / "localizations" / "default" / "interface" / "text" / "mission" / "single" / campaign_id
    )
    loc_camp_dir.mkdir(parents=True, exist_ok=True)
    mission_pot, n_str = convert_as2_lng_to_pot(as2_root, as2_prefix, campaign_id, mission_id)
    (loc_camp_dir / f"{mission_id}.pot").write_text(mission_pot, encoding="utf-8")
    n_wav = copy_as2_voiceovers(as2_root, as2_prefix, mod_dir, campaign_id, mission_id)

    print(
        f"  Remapped: map={map_ent_n} (cat-fb={fb_n}), mi_ents={mi_ent_n}, humans={mi_hum_n}, "
        f"icons={icon_n}, music={mus_n}, stripped_blocks={stripped_n}, speakers={spk_n}, "
        f"strings={n_str}, wavs={n_wav}"
    )

    # 6. Validate
    report = validate_port(mission_dir, goh_idx)
    all_ok = True
    for key in [
        "missing_map_entities",
        "missing_mi_entities",
        "missing_breeds",
        "missing_envs",
        "missing_textures",
        "missing_icons",
        "missing_music",
        "brace_errors",
    ]:
        val = report[key]
        if val:
            all_ok = False
            print(f"  [FAIL] {key} ({len(val)}): {val[:15]}")
    if all_ok:
        print(f"  [OK] 0 missing refs, 0 brace errors ({report['counts']})")
    return all_ok


def package_zip(mod_dir: Path, zip_path: Path):
    """Create a distributable zip containing the mod folder (ready to extract into GoH mods/)."""
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(mod_dir.rglob("*")):
            if p.is_file():
                arc = Path(mod_dir.name) / p.relative_to(mod_dir)
                zf.write(p, arc.as_posix())
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nPackaged zip: {zip_path} ({size_mb:.2f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Port AS2 skirmish mission(s) to Gates of Hell.")
    parser.add_argument("--as2-pak", default=DEFAULT_AS2_PAK)
    parser.add_argument("--goh-root", default=DEFAULT_GOH_ROOT)
    parser.add_argument(
        "--mod-dir",
        default=r"c:\Users\wrrr0\Documents\Call to Arms mods\as2_skirmishes",
    )
    parser.add_argument("--campaign-id", default="09-as2_skirmishes")
    parser.add_argument("--campaign-name", default="AS2 Skirmishes")
    parser.add_argument("--batch", action="store_true", help="Port the full 4-mission classic pack")
    parser.add_argument("--as2-prefix", default="map/single/02_ger-skirmish/04_ger-seelowheights/")
    parser.add_argument("--mission-id", default="04_ger-seelowheights")
    parser.add_argument("--install", action="store_true", help="Copy built mod into GoH mods/ directory")
    parser.add_argument("--zip-out", default="", help="Optional path to write a distributable .zip")
    args = parser.parse_args()

    mod_dir = Path(args.mod_dir)
    as2_root = os.path.dirname(os.path.dirname(args.as2_pak))
    print("Indexing GoH assets...")
    goh_idx = index_goh_assets(args.goh_root)
    print(
        f"  GoH index: {len(goh_idx['entities'])} entities, "
        f"{len(goh_idx['breeds'])} breeds, {len(goh_idx['land_tex'])} land textures, "
        f"{len(goh_idx['envs'])} environments"
    )

    ensure_mod_and_campaign_shell(mod_dir, args.campaign_id, args.campaign_name, args.goh_root)

    missions = DEFAULT_BATCH if args.batch else [(args.as2_prefix, args.mission_id, args.mission_id)]
    all_ok = True
    with zipfile.ZipFile(args.as2_pak) as z:
        for prefix, mid, _mname in missions:
            ok = port_single(z, as2_root, prefix, args.goh_root, goh_idx, mod_dir, args.campaign_id, mid)
            all_ok = all_ok and ok

    if all_ok and args.install:
        dst = Path(args.goh_root) / "mods" / mod_dir.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(mod_dir, dst)
        print(f"\nInstalled mod to: {dst}")

    if all_ok and args.zip_out:
        package_zip(mod_dir, Path(args.zip_out))

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
