#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile


VALIDATOR_SPEC_RE = re.compile(
    r'"phase11_dw_wdt_manifest\.json": \("([^"]+)", "drivers/watchdog/dw_wdt\.c", (\d+), \[\], \["phase11-dw-wdt-platform-and-pm"\]\),'
)


def find_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "zigux/tests/phase11_dw_wdt_manifest.json").exists():
            return candidate
    raise SystemExit("phase11-dw-manifest-alignment:repo_root_not_found")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / ".scratch/check-phase11-dw-manifest-alignment.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def expect_failure(root: Path, expected_marker: str) -> None:
    result = run_check(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-dw-manifest-alignment-self-test:unexpected_pass:{expected_marker}")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            "phase11-dw-manifest-alignment-self-test:"
            f"missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_dw_manifest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        script_copy = root / ".scratch/check-phase11-dw-manifest-alignment.py"
        write_text(script_copy, read_text(Path(__file__)))

        manifest = {
            "lane_key": "P11-L12",
            "phase": "Phase 11",
            "surveyed_commit": "b2deef651d140045bdfb1d3675a3c18fde80de0e",
            "anchor": "drivers/watchdog/dw_wdt.c",
            "gaps": [{"id": "phase11-dw-wdt-platform-and-pm", "status": "blocked_on_driver_scaffold"}],
        }
        write_text(root / "zigux/tests/phase11_dw_wdt_manifest.json", json.dumps(manifest, indent=2) + "\n")
        write_text(
            root / "Documentation/zigux/phase11-dw-wdt-survey.md",
            "# Phase 11 DesignWare Watchdog Survey\n\n"
            "lane key remains `P11-L12`\n"
            "reviewed against live `master` `b2deef651d140045bdfb1d3675a3c18fde80de0e`\n",
        )
        write_text(
            root / "scripts/zigux/validate-phase11.py",
            'MANIFEST_SPECS = {\n'
            '    "phase11_dw_wdt_manifest.json": ("P11-L12", "drivers/watchdog/dw_wdt.c", 12, [], ["phase11-dw-wdt-platform-and-pm"]),\n'
            '}\n',
        )

        baseline = run_check(root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-dw-manifest-alignment-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        write_text(
            root / "scripts/zigux/validate-phase11.py",
            'MANIFEST_SPECS = {\n'
            '    "phase11_dw_wdt_manifest.json": ("P11-L11", "drivers/watchdog/dw_wdt.c", 12, [], ["phase11-dw-wdt-platform-and-pm"]),\n'
            '}\n',
        )
        expect_failure(root, "phase11_dw_wdt_validator_lane_key:P11-L11!=P11-L12")

        write_text(
            root / "scripts/zigux/validate-phase11.py",
            'MANIFEST_SPECS = {\n'
            '    "phase11_dw_wdt_manifest.json": ("P11-L12", "drivers/watchdog/dw_wdt.c", 12, [], ["phase11-dw-wdt-platform-and-pm"]),\n'
            '}\n',
        )
        write_text(
            root / "Documentation/zigux/phase11-dw-wdt-survey.md",
            "# Phase 11 DesignWare Watchdog Survey\n\nlane key remains `P11-L12`\n",
        )
        expect_failure(root, "phase11_dw_wdt_survey_doc_commit:b2deef651d140045bdfb1d3675a3c18fde80de0e")

        write_text(
            root / "Documentation/zigux/phase11-dw-wdt-survey.md",
            "# Phase 11 DesignWare Watchdog Survey\n\n"
            "reviewed against live `master` `b2deef651d140045bdfb1d3675a3c18fde80de0e`\n",
        )
        expect_failure(root, "phase11_dw_wdt_survey_doc_lane_key:`P11-L12`")

    print("PHASE11_DW_MANIFEST_ALIGNMENT_SELF_TEST=pass")
    print("PHASE11_DW_MANIFEST_ALIGNMENT_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    root = find_root()
    manifest_path = root / "zigux/tests/phase11_dw_wdt_manifest.json"
    survey_doc_path = root / "Documentation/zigux/phase11-dw-wdt-survey.md"
    validator_path = root / "scripts/zigux/validate-phase11.py"

    manifest = load_manifest(manifest_path)
    survey_doc = read_text(survey_doc_path)
    validator_text = read_text(validator_path)
    missing: list[str] = []

    lane_key = manifest.get("lane_key")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(lane_key, str):
        missing.append("phase11_dw_wdt_manifest:lane_key")
    if not isinstance(surveyed_commit, str):
        missing.append("phase11_dw_wdt_manifest:surveyed_commit")

    if isinstance(surveyed_commit, str):
        if surveyed_commit not in survey_doc:
            missing.append(f"phase11_dw_wdt_survey_doc_commit:{surveyed_commit}")

    if isinstance(lane_key, str) and f"`{lane_key}`" not in survey_doc:
        missing.append(f"phase11_dw_wdt_survey_doc_lane_key:`{lane_key}`")

    validator_match = VALIDATOR_SPEC_RE.search(validator_text)
    if validator_match is None:
        missing.append("phase11_dw_wdt_validator_spec:missing")
    elif isinstance(lane_key, str):
        validator_lane_key = validator_match.group(1)
        if validator_lane_key != lane_key:
            missing.append(
                f"phase11_dw_wdt_validator_lane_key:{validator_lane_key}!={lane_key}"
            )

    if missing:
        print("PHASE11_DW_MANIFEST_ALIGNMENT=fail")
        print("PHASE11_DW_MANIFEST_ALIGNMENT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_DW_MANIFEST_ALIGNMENT_MISSING_END")
        return 1

    print("PHASE11_DW_MANIFEST_ALIGNMENT=pass")
    print(f"PHASE11_DW_MANIFEST_ALIGNMENT_LANE_KEY={lane_key}")
    print(f"PHASE11_DW_MANIFEST_ALIGNMENT_SURVEYED_COMMIT={surveyed_commit}")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(main())
