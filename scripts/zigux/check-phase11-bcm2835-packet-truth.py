#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory


EXPECTED_LANE_KEY = "P11-L08"
MANIFEST_PATH = Path("zigux/tests/phase11_bcm2835_wdt_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-survey.md")
SLICE_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-slice.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md")

REQUIRED_SURVEY_MARKERS = (
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "archival packet identity remains `P11-L08`",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
)

REQUIRED_SLICE_MARKERS = (
    "Phase 11 BCM2835 Watchdog Slice",
    "The next honest bounded step inside the same Phase 11 family is no longer another note-only handoff.",
)

REQUIRED_MATRIX_MARKERS = (
    "PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful",
    "archival packet identity remains `P11-L08`",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
)

FORBIDDEN_MATRIX_MARKERS = (
    "current continuity tracked through `P11-L10`",
    "current continuity tracked through `P11-L12`",
)


def read_text(root: Path, relative: Path) -> str:
    target = root / relative
    return target.read_text(encoding="utf-8")


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}: missing marker: {marker}")
    return failures


def require_absent_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for marker in markers:
        if marker in text:
            failures.append(f"{label}: stale marker still present: {marker}")
    return failures


def check_repo(root: Path) -> list[str]:
    failures: list[str] = []

    manifest = json.loads(read_text(root, MANIFEST_PATH))
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(
            f"manifest: expected lane_key {EXPECTED_LANE_KEY}, found {manifest.get('lane_key')!r}"
        )
    if manifest.get("phase") != "Phase 11":
        failures.append(f"manifest: expected phase 'Phase 11', found {manifest.get('phase')!r}")

    survey_text = read_text(root, SURVEY_PATH)
    slice_text = read_text(root, SLICE_PATH)
    matrix_text = read_text(root, MATRIX_PATH)

    failures.extend(require_markers("survey", survey_text, REQUIRED_SURVEY_MARKERS))
    failures.extend(require_markers("slice", slice_text, REQUIRED_SLICE_MARKERS))
    failures.extend(require_markers("matrix", matrix_text, REQUIRED_MATRIX_MARKERS))
    failures.extend(require_absent_markers("matrix", matrix_text, FORBIDDEN_MATRIX_MARKERS))

    return failures


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_file(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "lane_key": "P11-L08",
                    "phase": "Phase 11",
                    "survey_summary": {
                        "bcm2835_wdt_survey_note_present": True,
                        "bcm2835_wdt_validation_matrix_present": True,
                    },
                },
                indent=2,
            )
            + "\n",
        )
        write_file(
            root / SURVEY_PATH,
            "# Phase 11 BCM2835 Watchdog Survey\n"
            "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed\n"
            "archival packet identity remains `P11-L08`\n"
            "zigux/tests/phase11_bcm2835_wdt_manifest.json\n",
        )
        write_file(
            root / SLICE_PATH,
            "# Phase 11 BCM2835 Watchdog Slice\n"
            "The next honest bounded step inside the same Phase 11 family is no longer another note-only handoff.\n",
        )
        write_file(
            root / MATRIX_PATH,
            "# Phase 11 BCM2835 Watchdog Validation Matrix\n"
            "PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful\n"
            "archival packet identity remains `P11-L08`\n"
            "zigux/tests/phase11_bcm2835_wdt_manifest.json\n",
        )
        failures = check_repo(root)
        if failures:
            for failure in failures:
                print(failure)
            return 1

        broken = root / MATRIX_PATH
        broken.write_text(
            broken.read_text(encoding="utf-8") + "current continuity tracked through `P11-L10`\n",
            encoding="utf-8",
        )
        failures = check_repo(root)
        if len(failures) != 1 or FORBIDDEN_MATRIX_MARKERS[0] not in failures[0]:
            print("self-test: expected exactly one stale-continuity failure")
            for failure in failures:
                print(failure)
            return 1

    print("PHASE11_BCM2835_PACKET_TRUTH_SELF_TEST=pass")
    print("PHASE11_BCM2835_PACKET_TRUTH_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the bcm2835 Phase 11 manifest-backed packet drifts on lane truthfulness."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = check_repo(args.repo_root)
    if failures:
        print("PHASE11_BCM2835_PACKET_TRUTH=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_BCM2835_PACKET_TRUTH=pass")
    print(f"PHASE11_BCM2835_PACKET_TRUTH_LANE_KEY={EXPECTED_LANE_KEY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
