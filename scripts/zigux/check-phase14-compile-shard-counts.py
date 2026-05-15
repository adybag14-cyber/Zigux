#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
VALID_COVERAGE = {
    "focused_and_full_bundle",
    "full_bundle_only",
}


def load_manifest(root: Path) -> dict[str, object]:
    loaded = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("manifest:top_level_type")
    return loaded



def expected_counts_from_compile_shards(compile_shards: object) -> dict[str, int]:
    if not isinstance(compile_shards, list):
        raise ValueError("manifest:compile_shards")

    counts = {
        "total": len(compile_shards),
        "focused_and_full_bundle": 0,
        "full_bundle_only": 0,
    }
    for index, shard in enumerate(compile_shards):
        if not isinstance(shard, dict):
            raise ValueError(f"manifest:compile_shards:{index}")
        coverage = shard.get("coverage")
        if not isinstance(coverage, str) or coverage not in VALID_COVERAGE:
            raise ValueError(f"manifest:compile_shards:{index}:coverage={coverage}")
        counts[coverage] += 1
    return counts



def validate_manifest(manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if manifest.get("phase") != "Phase 14":
        errors.append(f"manifest:phase={manifest.get('phase')}")

    try:
        expected_counts = expected_counts_from_compile_shards(manifest.get("compile_shards"))
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    compile_shard_counts = manifest.get("compile_shard_counts")
    if compile_shard_counts != expected_counts:
        errors.append("manifest:compile_shard_counts")
    return errors



def run_self_test() -> int:
    good_manifest = {
        "phase": "Phase 14",
        "compile_shards": [
            {"coverage": "full_bundle_only"},
            {"coverage": "full_bundle_only"},
            {"coverage": "full_bundle_only"},
            {"coverage": "full_bundle_only"},
            {"coverage": "full_bundle_only"},
            {"coverage": "focused_and_full_bundle"},
        ],
        "compile_shard_counts": {
            "total": 6,
            "focused_and_full_bundle": 1,
            "full_bundle_only": 5,
        },
    }
    if validate_manifest(good_manifest):
        print("PHASE14_COMPILE_SHARD_COUNT_SELF_TEST=fail")
        print("SELF_TEST_REASON=good_manifest_rejected")
        return 1

    bad_counts_manifest = dict(good_manifest)
    bad_counts_manifest["compile_shard_counts"] = {
        "total": 6,
        "focused_and_full_bundle": 1,
        "full_bundle_only": 4,
    }
    if validate_manifest(bad_counts_manifest) != ["manifest:compile_shard_counts"]:
        print("PHASE14_COMPILE_SHARD_COUNT_SELF_TEST=fail")
        print("SELF_TEST_REASON=bad_count_marker_mismatch")
        return 1

    bad_coverage_manifest = dict(good_manifest)
    bad_coverage_manifest["compile_shards"] = [{"coverage": "unexpected"}]
    if validate_manifest(bad_coverage_manifest) != ["manifest:compile_shards:0:coverage=unexpected"]:
        print("PHASE14_COMPILE_SHARD_COUNT_SELF_TEST=fail")
        print("SELF_TEST_REASON=bad_coverage_marker_mismatch")
        return 1

    print("PHASE14_COMPILE_SHARD_COUNT_SELF_TEST=pass")
    print("PHASE14_COMPILE_SHARD_COUNT_SELF_TEST_BAD_COUNT_MARKER=manifest:compile_shard_counts")
    print("PHASE14_COMPILE_SHARD_COUNT_SELF_TEST_BAD_COVERAGE_MARKER=manifest:compile_shards:0:coverage=unexpected")
    return 0



def run_validation(root: Path) -> int:
    try:
        manifest = load_manifest(root)
    except FileNotFoundError:
        print("PHASE14_COMPILE_SHARD_COUNT_VALIDATION=fail")
        print(f"MISSING_FILE={MANIFEST_PATH.as_posix()}")
        return 1
    except json.JSONDecodeError as exc:
        print("PHASE14_COMPILE_SHARD_COUNT_VALIDATION=fail")
        print(
            "JSON_ERROR="
            f"{MANIFEST_PATH.as_posix()}:{exc.lineno}:{exc.colno}:{exc.msg}"
        )
        return 1
    except ValueError as exc:
        print("PHASE14_COMPILE_SHARD_COUNT_VALIDATION=fail")
        print(str(exc))
        return 1

    errors = validate_manifest(manifest)
    if errors:
        print("PHASE14_COMPILE_SHARD_COUNT_VALIDATION=fail")
        print("PHASE14_COMPILE_SHARD_COUNT_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE14_COMPILE_SHARD_COUNT_ERRORS_END")
        return 1

    counts = manifest["compile_shard_counts"]
    print("PHASE14_COMPILE_SHARD_COUNT_VALIDATION=pass")
    print(f"PHASE14_COMPILE_SHARD_COUNT_TOTAL={counts['total']}")
    print(
        "PHASE14_COMPILE_SHARD_COUNT_FOCUSED="
        f"{counts['focused_and_full_bundle']}"
    )
    print(
        "PHASE14_COMPILE_SHARD_COUNT_FULL_BUNDLE_ONLY="
        f"{counts['full_bundle_only']}"
    )
    return 0



def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the checker's internal coverage checks",
    )
    return parser.parse_args(argv)



def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    return run_validation(ROOT)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
