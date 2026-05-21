#!/usr/bin/env python3
"""Fail closed when Phase 10 closure-manifest summary counts drift."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"

COUNT_FIELDS = {
    "doc_count": "docs",
    "manifest_count": "manifests",
    "driver_count": "drivers",
    "test_count": "tests",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_drift(manifest: dict) -> list[str]:
    drift: list[str] = []
    for count_field, list_field in COUNT_FIELDS.items():
        listed = manifest.get(list_field)
        if not isinstance(listed, list) or not listed:
            drift.append(f"{list_field}:missing")
            continue

        count = manifest.get(count_field)
        if not isinstance(count, int):
            drift.append(f"{count_field}:missing")
            continue

        actual = len(listed)
        if count != actual:
            drift.append(f"{count_field}:{count}!=len({list_field}):{actual}")
    return drift


def validate(root: Path) -> tuple[list[str], list[str]]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return [MANIFEST_PATH], []
    return [], collect_drift(read_json(manifest_path))


def fixture_manifest() -> dict:
    return {
        "doc_count": 7,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 21,
        "docs": [f"doc-{index}" for index in range(7)],
        "manifests": [f"manifest-{index}" for index in range(4)],
        "drivers": [f"driver-{index}" for index in range(4)],
        "tests": [f"test-{index}" for index in range(21)],
    }


def write_fixture(root: Path) -> None:
    write_text(root / MANIFEST_PATH, json.dumps(fixture_manifest(), indent=2) + "\n")


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_manifest_counts_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(
                "phase10-manifest-counts-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"drift={','.join(drift) or 'none'}"
            )

        manifest_path = root / MANIFEST_PATH
        original = read_json(manifest_path)

        def write_manifest(data: dict) -> None:
            write_text(manifest_path, json.dumps(data, indent=2) + "\n")

        cases = 0

        broken = dict(original)
        broken["doc_count"] = 6
        write_manifest(broken)
        expect_contains(validate(root)[1], "doc_count:6!=len(docs):7", "phase10-manifest-counts-self-test")
        cases += 1

        broken = dict(original)
        broken["manifest_count"] = 5
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "manifest_count:5!=len(manifests):4",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["driver_count"] = 3
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "driver_count:3!=len(drivers):4",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["test_count"] = 20
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "test_count:20!=len(tests):21",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        del broken["doc_count"]
        write_manifest(broken)
        expect_contains(validate(root)[1], "doc_count:missing", "phase10-manifest-counts-self-test")
        cases += 1

        broken = dict(original)
        broken["tests"] = []
        write_manifest(broken)
        expect_contains(validate(root)[1], "tests:missing", "phase10-manifest-counts-self-test")
        cases += 1

        manifest_path.unlink()
        missing_files, drift = validate(root)
        if drift:
            actual = ",".join(drift)
            raise SystemExit(f"phase10-manifest-counts-self-test:unexpected_drift={actual}")
        if missing_files != [MANIFEST_PATH]:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-manifest-counts-self-test:"
                f"expected_missing={MANIFEST_PATH}:actual={actual}"
            )
        cases += 1

    print("PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 10 closure manifest summary-count packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print("PHASE10_CLOSURE_MANIFEST_COUNTS=fail")
        print("MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_END")
        return 1

    if drift:
        print("PHASE10_CLOSURE_MANIFEST_COUNTS=fail")
        print("PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_END")
        return 1

    print("PHASE10_CLOSURE_MANIFEST_COUNTS=pass")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_FIELD_COUNT={len(COUNT_FIELDS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
