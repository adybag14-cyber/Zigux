#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")
EXPECTED_LANE_KEY = "P12-L17"
EXPECTED_PHASE = "Phase 12"
EXPECTED_TRACKED_PATHS = ["tools/lib/bpf/zigux_segments/pin_path.zig"]


def load_fixture(root: Path) -> dict[str, object]:
    return json.loads((root / FIXTURE_PATH).read_text(encoding="utf-8"))


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    missing_files: list[str] = []
    fixture = load_fixture(root)

    if fixture.get("lane_key") != EXPECTED_LANE_KEY:
        errors.append(
            f"{FIXTURE_PATH}: lane_key must stay `{EXPECTED_LANE_KEY}` for the parked libbpf snapshot packet"
        )
    if fixture.get("phase") != EXPECTED_PHASE:
        errors.append(f"{FIXTURE_PATH}: phase must stay `{EXPECTED_PHASE}`")

    tracked_paths = fixture.get("tracked_paths")
    if tracked_paths != EXPECTED_TRACKED_PATHS:
        errors.append(
            f"{FIXTURE_PATH}: tracked_paths must stay exactly {EXPECTED_TRACKED_PATHS!r} on current master"
        )

    tracked_file_count = fixture.get("tracked_file_count")
    if tracked_file_count != len(EXPECTED_TRACKED_PATHS):
        errors.append(
            f"{FIXTURE_PATH}: tracked_file_count must stay `{len(EXPECTED_TRACKED_PATHS)}`"
        )

    for rel in EXPECTED_TRACKED_PATHS:
        if not (root / rel).exists():
            missing_files.append(rel)

    return errors, missing_files


def expect_case(case: str, root: Path, expected_fragment: str) -> None:
    errors, missing_files = validate(root)
    combined = errors + [f"missing:{item}" for item in missing_files]
    if not any(expected_fragment in item for item in combined):
        raise AssertionError(f"{case}: expected `{expected_fragment}` in {combined!r}")


def run_self_test() -> None:
    fixture_text = json.dumps(
        {
            "lane_key": EXPECTED_LANE_KEY,
            "phase": EXPECTED_PHASE,
            "surveyed_commit": "5ccb94e1380d1f2e236c98d09bc52b2b5f6948c7",
            "tracked_file_count": 1,
            "tracked_paths": EXPECTED_TRACKED_PATHS,
        },
        indent=2,
    ) + "\n"

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_snapshot_") as tmp_dir:
        root = Path(tmp_dir)
        fixture_path = root / FIXTURE_PATH
        tracked_path = root / EXPECTED_TRACKED_PATHS[0]
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        tracked_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(fixture_text, encoding="utf-8")
        tracked_path.write_text("// fixture\n", encoding="utf-8")

        assert validate(root) == ([], [])

        wrong_lane = json.loads(fixture_text)
        wrong_lane["lane_key"] = "P12-L16"
        fixture_path.write_text(json.dumps(wrong_lane, indent=2) + "\n", encoding="utf-8")
        expect_case("wrong_lane", root, "lane_key")

        fixture_path.write_text(fixture_text, encoding="utf-8")
        wrong_count = json.loads(fixture_text)
        wrong_count["tracked_file_count"] = 2
        fixture_path.write_text(json.dumps(wrong_count, indent=2) + "\n", encoding="utf-8")
        expect_case("wrong_count", root, "tracked_file_count")

        fixture_path.write_text(fixture_text, encoding="utf-8")
        wrong_paths = json.loads(fixture_text)
        wrong_paths["tracked_paths"] = EXPECTED_TRACKED_PATHS + ["tools/lib/bpf/zigux_segments/cpu_mask.zig"]
        fixture_path.write_text(json.dumps(wrong_paths, indent=2) + "\n", encoding="utf-8")
        expect_case("wrong_paths", root, "tracked_paths")

        fixture_path.write_text(fixture_text, encoding="utf-8")
        tracked_path.unlink()
        expect_case("missing_file", root, "missing:tools/lib/bpf/zigux_segments/pin_path.zig")

    print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_SELF_TEST=pass")
    print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 12 libbpf snapshot fixture against the current tracked helper surface."
    )
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checker coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    errors, missing_files = validate(args.root)
    if errors or missing_files:
        print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE=fail")
        if errors:
            print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_ERRORS_START")
            for item in errors:
                print(item)
            print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_ERRORS_END")
        if missing_files:
            print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_MISSING_FILES_START")
            for item in missing_files:
                print(item)
            print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_MISSING_FILES_END")
        return 1

    print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE=pass")
    print(f"PHASE12_LIBBPF_SNAPSHOT_FIXTURE_TRACKED_FILE_COUNT={len(EXPECTED_TRACKED_PATHS)}")
    print("PHASE12_LIBBPF_SNAPSHOT_FIXTURE_SURFACE=tools/lib/bpf/zigux_segments/pin_path.zig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
