#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux/tests/phase11_build.zig"
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase11_build_inventory.json"
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"

BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase11-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
FORBIDDEN_BUILD_MARKERS = [
    "phase11_hvc_console_survey_tests",
    "run_phase11_hvc_console_survey_tests.step",
]
DEDICATED_SURVEY_REPLAYS = [
    "zigux/tests/phase11_hvc_console_survey.zig",
]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_inventory() -> dict[str, object]:
    build_text = BUILD_PATH.read_text(encoding="utf-8")
    return {
        "build_test_names": BUILD_TEST_NAME_RE.findall(build_text),
        "shared_test_depend_steps": BUILD_DEPEND_STEP_RE.findall(build_text),
        "forbidden_markers": FORBIDDEN_BUILD_MARKERS,
        "dedicated_survey_replays": DEDICATED_SURVEY_REPLAYS,
    }


def main() -> int:
    _ = load_json(FIXTURE_PATH)
    generated = render_inventory()

    with tempfile.TemporaryDirectory(prefix="zigux_phase11_inventory_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase11_build_inventory.json"
        actual_path.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ARTIFACT_DIFF_PATH),
                "--mode",
                "json",
                str(FIXTURE_PATH),
                str(actual_path),
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode != 0:
        print("PHASE11_BUILD_INVENTORY=fail")
        return result.returncode

    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
