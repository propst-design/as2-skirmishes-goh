"""Real Gates of Hell engine load-test & visual screenshot harness.

Temporarily activates `as2_skirmishes:0` in options.set (always restored in
finally), launches call_to_arms_ed.exe -edit for each mission, waits for
page_scene_editor, captures a PNG screenshot of the rendered viewport, and
summarizes exceptions + categorized warnings from game.log.
"""

import argparse
import re
import subprocess
import time
from collections import Counter
from pathlib import Path

BIN_DIR = Path(r"D:\SteamLibrary\steamapps\common\Call to Arms - Gates of Hell\binaries\x64")
ED_EXE = BIN_DIR / "call_to_arms_ed.exe"
GOH_DOCS = Path.home() / "Documents" / "My Games" / "gates of hell"
LOG_FILE = GOH_DOCS / "log" / "game.log"
OPT_FILE = GOH_DOCS / "profiles" / "53625315" / "options.set"

DEFAULT_MISSIONS = [
    "single/09-as2_skirmishes/04_ger-seelowheights/0.mi",
    "single/09-as2_skirmishes/04_rus-kursk/0.mi",
    "single/09-as2_skirmishes/05_ger-kharkov/0.mi",
    "single/09-as2_skirmishes/01b_usa-bocage/0.mi",
]


def enable_mod_in_options(orig_text: str, mod_id: str = "as2_skirmishes:0") -> str:
    if re.search(r"\{mods\b", orig_text):
        return re.sub(r"\{mods[\s\S]*?\}", f'{{mods\r\n\t\t"{mod_id}"\r\n\t}}', orig_text)
    idx = orig_text.rfind("}")
    return orig_text[:idx] + f'\t{{mods\r\n\t\t"{mod_id}"\r\n\t}}\r\n}}'


def capture_screenshot(out_png: Path) -> bool:
    """Capture primary desktop screenshot via built-in Windows .NET System.Drawing."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
        "$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height; "
        "$g = [System.Drawing.Graphics]::FromImage($bmp); "
        "$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size); "
        f"$bmp.Save('{out_png}', [System.Drawing.Imaging.ImageFormat]::Png); "
        "$g.Dispose(); $bmp.Dispose()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
    return r.returncode == 0 and out_png.exists()


def categorize_warnings(log_text: str) -> Counter:
    cats = Counter()
    samples = {}
    for line in log_text.splitlines():
        low = line.lower()
        if "xml: error" in low or "/story" in low:
            continue
        if "can't spawn entity" in low:
            m = re.search(r"can't spawn entity (\S+)", line)
            key = f"cant_spawn:{m.group(1)}" if m else "cant_spawn"
            cats[key] += 1
        elif "place " in low and "not found in" in low:
            m = re.search(r"Place (\S+) not found in ([^\[\s]+)", line)
            key = f"missing_seat:{m.group(2)}.{m.group(1)}" if m else "missing_seat"
            cats[key] += 1
        elif "local string not found" in low:
            cats["local_string_not_found"] += 1
            samples.setdefault("local_string_not_found", line)
        elif "edifice item failed" in low:
            cats["edifice_item_failed"] += 1
        elif "assertion failed" in low:
            cats["assertion_failed"] += 1
            samples.setdefault("assertion_failed", line)
        elif "link failed" in low:
            cats["link_failed"] += 1
    return cats, samples


def run_one(map_arg: str, timeout_s: int = 110, shot_dir: Path | None = None) -> dict:
    start_ts = time.time()
    proc = subprocess.Popen([str(ED_EXE), "-edit", map_arg], cwd=str(BIN_DIR))
    loaded_scene = False
    exception_text = ""
    shot_path = None
    try:
        while time.time() - start_ts < timeout_s:
            time.sleep(1.0)
            if LOG_FILE.exists() and LOG_FILE.stat().st_mtime >= start_ts:
                txt = LOG_FILE.read_text(encoding="utf-8", errors="replace")
                if "***************** Exception *****************" in txt:
                    pos = txt.find("***************** Exception *****************")
                    exception_text = txt[pos : pos + 1000]
                    break
                if "Activate page page_scene_editor" in txt:
                    # Wait 5s for scene rendering to settle before screenshot
                    time.sleep(5.0)
                    txt = LOG_FILE.read_text(encoding="utf-8", errors="replace")
                    if "***************** Exception *****************" in txt:
                        pos = txt.find("***************** Exception *****************")
                        exception_text = txt[pos : pos + 1000]
                    else:
                        loaded_scene = True
                        if shot_dir is not None:
                            slug = map_arg.split("/")[-2]
                            out_png = shot_dir / f"{slug}.png"
                            if capture_screenshot(out_png):
                                shot_path = str(out_png)
                    break
            if proc.poll() is not None:
                break
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)

    cats, samples = Counter(), {}
    if LOG_FILE.exists():
        txt = LOG_FILE.read_text(encoding="utf-8", errors="replace")
        cats, samples = categorize_warnings(txt)

    return {
        "map_arg": map_arg,
        "loaded_scene": loaded_scene,
        "exception": exception_text,
        "screenshot": shot_path,
        "warning_cats": cats,
        "warning_samples": samples,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--missions", nargs="*", default=DEFAULT_MISSIONS)
    parser.add_argument("--timeout", type=int, default=110)
    parser.add_argument("--screenshots", default="", help="Directory to save viewport PNGs")
    args = parser.parse_args()

    shot_dir = Path(args.screenshots) if args.screenshots else None
    orig_opt = OPT_FILE.read_text(encoding="utf-8")
    all_ok = True
    try:
        OPT_FILE.write_text(enable_mod_in_options(orig_opt), encoding="utf-8")
        for m in args.missions:
            print(f"\n=== Testing {m} ===")
            res = run_one(m, timeout_s=args.timeout, shot_dir=shot_dir)
            if res["exception"]:
                all_ok = False
                print("  [CRASH] Exception:")
                print(res["exception"])
            elif res["loaded_scene"]:
                print(f"  [PASS] Loaded page_scene_editor! screenshot={res['screenshot']}")
                for k, v in res["warning_cats"].most_common(12):
                    extra = f"  e.g. {res['warning_samples'][k]}" if k in res["warning_samples"] else ""
                    print(f"    {k}: x{v}{extra}")
            else:
                all_ok = False
                print("  [TIMEOUT/EXIT] Did not reach page_scene_editor")
                for k, v in res["warning_cats"].most_common(10):
                    print(f"    {k}: x{v}")
    finally:
        OPT_FILE.write_text(orig_opt, encoding="utf-8")
        print("\nRestored original options.set")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
