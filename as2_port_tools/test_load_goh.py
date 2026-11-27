"""Real Gates of Hell engine load-test harness for ported AS2 skirmish missions.

Temporarily activates `as2_skirmishes:0` in the user's GoH options.set (always
restoring the exact original file in a finally block), launches call_to_arms_ed.exe
with -map for each mission, waits for page_scene_editor or a crash/exception,
and inspects game.log for exceptions, missing entities, or load failures.
"""

import argparse
import re
import subprocess
import time
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


def run_one(map_arg: str, timeout_s: int = 35) -> dict:
    # Clear or note log mtime
    start_ts = time.time()
    proc = subprocess.Popen(
        [str(ED_EXE), "-edit", map_arg],
        cwd=str(BIN_DIR),
    )
    loaded_scene = False
    exception_text = ""
    warnings = []
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
                    # Give it 3 extra seconds to finish any post-activate ticks
                    time.sleep(3.0)
                    txt = LOG_FILE.read_text(encoding="utf-8", errors="replace")
                    if "***************** Exception *****************" in txt:
                        pos = txt.find("***************** Exception *****************")
                        exception_text = txt[pos : pos + 1000]
                    else:
                        loaded_scene = True
                    break
            if proc.poll() is not None:
                break
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)

    # Collect warnings/errors from log
    if LOG_FILE.exists():
        txt = LOG_FILE.read_text(encoding="utf-8", errors="replace")
        for line in txt.splitlines():
            if any(k in line.lower() for k in ["can't spawn", "not found", "error", "failed", "missing", "exception", "world:", "load map"]):
                if "xml: error" not in line.lower() and "story" not in line.lower():
                    warnings.append(line)

    return {
        "map_arg": map_arg,
        "loaded_scene": loaded_scene,
        "exception": exception_text,
        "warnings": warnings[:20],
        "warning_count": len(warnings),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--missions", nargs="*", default=DEFAULT_MISSIONS)
    parser.add_argument("--timeout", type=int, default=110)
    args = parser.parse_args()

    orig_opt = OPT_FILE.read_text(encoding="utf-8")
    all_ok = True
    try:
        OPT_FILE.write_text(enable_mod_in_options(orig_opt), encoding="utf-8")
        for m in args.missions:
            print(f"\n=== Testing {m} ===")
            res = run_one(m, timeout_s=args.timeout)
            if res["exception"]:
                all_ok = False
                print("  [CRASH] Exception:")
                print(res["exception"])
            elif res["loaded_scene"]:
                print(f"  [PASS] Loaded page_scene_editor! (warnings={res['warning_count']})")
                for w in res["warnings"][:8]:
                    print("    WARN:", w)
            else:
                all_ok = False
                print(f"  [TIMEOUT/EXIT] Did not reach page_scene_editor (warnings={res['warning_count']})")
                for w in res["warnings"][:8]:
                    print("    WARN:", w)
    finally:
        OPT_FILE.write_text(orig_opt, encoding="utf-8")
        print("\nRestored original options.set")

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
