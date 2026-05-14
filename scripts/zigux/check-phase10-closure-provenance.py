#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
LEDGER_PATH = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"

LEDGER_SOURCE_MARKER = "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE"
LEDGER_LANE_MARKERS = {
    "core": "PHASE10_LEDGER_SURVEY_CORE_LANE",
    "ring": "PHASE10_LEDGER_SURVEY_RING_LANE",
    "input": "PHASE10_LEDGER_SURVEY_INPUT_LANE",
    "mmio": "PHASE10_LEDGER_SURVEY_MMIO_LANE",
}
LEDGER_COMMIT_MARKERS = {
    "core": "PHASE10_LEDGER_SURVEY_CORE_COMMIT",
    "ring": "PHASE10_LEDGER_SURVEY_RING_COMMIT",
    "input": "PHASE10_LEDGER_SURVEY_INPUT_COMMIT",
    "mmio": "PHASE10_LEDGER_SURVEY_MMIO_COMMIT",
}


def read_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def read_ledger_lines(root: Path) -> set[str]:
    return set((root / LEDGER_PATH).read_text(encoding="utf-8").splitlines())


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in (MANIFEST_PATH, LEDGER_PATH):
        if not (root / rel_path).exists():
            missing.append(rel_path)
    return missing


def collect_mismatches(root: Path) -> list[str]:
    manifest = read_manifest(root)
    provenance = manifest.get("survey_provenance")
    if not isinstance(provenance, dict):
        return ["manifest:survey_provenance"]

    ledger_lines = read_ledger_lines(root)
    mismatches: list[str] = []

    source = provenance.get("source")
    expected_source_line = f"{LEDGER_SOURCE_MARKER}={source}"
    if expected_source_line not in ledger_lines:
        mismatches.append(expected_source_line)

    lane_keys = provenance.get("lane_keys")
    if not isinstance(lane_keys, dict):
        mismatches.append("manifest:survey_provenance.lane_keys")
    else:
        for key, marker in LEDGER_LANE_MARKERS.items():
            value = lane_keys.get(key)
            expected_line = f"{marker}={value}"
            if expected_line not in ledger_lines:
                mismatches.append(expected_line)

    surveyed_commits = provenance.get("surveyed_commits")
    if not isinstance(surveyed_commits, dict):
        mismatches.append("manifest:survey_provenance.surveyed_commits")
    else:
        for key, marker in LEDGER_COMMIT_MARKERS.items():
            value = surveyed_commits.get(key)
            expected_line = f"{marker}={value}"
            if expected_line not in ledger_lines:
                mismatches.append(expected_line)

    return mismatches


def write_fixture(root: Path) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "phase": "Phase 10",
                "survey_provenance": {
                    "source": "manifest_derived",
                    "lane_keys": {
                        "core": "P10-L01",
                        "ring": "P10-L07",
                        "input": "P10-L13",
                        "mmio": "P10-L10",
                    },
                    "surveyed_commits": {
                        "core": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "ring": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                        "input": "cccccccccccccccccccccccccccccccccccccccc",
                        "mmio": "dddddddddddddddddddddddddddddddddddddddd",
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    ledger_path = root / LEDGER_PATH
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        "\n".join(
            [
                "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
                "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
                "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L07",
                "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
                "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L10",
                "PHASE10_LEDGER_SURVEY_CORE_COMMIT=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "PHASE10_LEDGER_SURVEY_RING_COMMIT=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=cccccccccccccccccccccccccccccccccccccccc",
                "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=dddddddddddddddddddddddddddddddddddddddd",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def expect_mismatch(root: Path, expected: str, label: str) -> None:
    mismatches = collect_mismatches(root)
    if expected not in mismatches:
        actual = ",".join(mismatches) if mismatches else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def expect_missing_file(root: Path, expected: str, label: str) -> None:
    missing = collect_missing_files(root)
    if expected not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_provenance_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing = collect_missing_files(root)
        mismatches = collect_mismatches(root)
        if missing or mismatches:
            raise SystemExit(
                "phase10-closure-provenance-self-test:baseline_failed:"
                f"files={','.join(missing) if missing else 'none'}:"
                f"mismatches={','.join(mismatches) if mismatches else 'none'}"
            )

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["source"] = "hand_written"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=hand_written",
            "phase10-closure-provenance-self-test:source_mismatch_not_detected",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["lane_keys"]["ring"] = "P10-L99"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L99",
            "phase10-closure-provenance-self-test:ring_lane_mismatch_not_detected",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["surveyed_commits"]["ring"] = (
            "9999999999999999999999999999999999999999"
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_RING_COMMIT=9999999999999999999999999999999999999999",
            "phase10-closure-provenance-self-test:ring_commit_mismatch_not_detected",
        )
        writeFixture = write_fixture
        writeFixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["survey_provenance"]["lane_keys"]["input"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_INPUT_LANE=None",
            "phase10-closure-provenance-self-test:missing_input_lane_not_detected",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["survey_provenance"]["surveyed_commits"]["mmio"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=None",
            "phase10-closure-provenance-self-test:missing_mmio_commit_not_detected",
        )
        write_fixture(root)

        ledger_path = root / LEDGER_PATH
        ledger_path.write_text(
            ledger_path.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_SURVEY_CORE_COMMIT=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_CORE_COMMIT=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "phase10-closure-provenance-self-test:missing_ledger_core_commit_not_detected",
        )
        write_fixture(root)

        manifest_path.unlink()
        expect_missing_file(
            root,
            MANIFEST_PATH,
            "phase10-closure-provenance-self-test:missing_manifest_not_detected",
        )
        write_fixture(root)

        ledger_path.unlink()
        expect_missing_file(
            root,
            LEDGER_PATH,
            "phase10-closure-provenance-self-test:missing_ledger_not_detected",
        )

    print("PHASE10_CLOSURE_PROVENANCE_CHECK_SELF_TEST=pass")
    print("PHASE10_CLOSURE_PROVENANCE_CHECK_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Phase 10 closure survey provenance stays mirrored between the manifest and ledger."
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_files(ROOT)
    if missing:
        print("PHASE10_CLOSURE_PROVENANCE_CHECK=fail")
        print("PHASE10_CLOSURE_PROVENANCE_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE10_CLOSURE_PROVENANCE_MISSING_FILES_END")
        return 1

    mismatches = collect_mismatches(ROOT)
    if mismatches:
        print("PHASE10_CLOSURE_PROVENANCE_CHECK=fail")
        print("PHASE10_CLOSURE_PROVENANCE_MISMATCHES_START")
        for item in mismatches:
            print(item)
        print("PHASE10_CLOSURE_PROVENANCE_MISMATCHES_END")
        return 1

    print("PHASE10_CLOSURE_PROVENANCE_CHECK=pass")
    print("PHASE10_CLOSURE_PROVENANCE_REQUIRED_FILE_COUNT=2")
    print(
        "PHASE10_CLOSURE_PROVENANCE_EXPECTED_FIELD_COUNT="
        f"{1 + len(LEDGER_LANE_MARKERS) + len(LEDGER_COMMIT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
