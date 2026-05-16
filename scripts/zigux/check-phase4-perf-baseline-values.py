#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


MANIFEST_REL = Path("zigux/tests/phase4_perf_baseline_manifest.json")
SURVEY_REL = Path("zigux/tests/phase4_perf_baseline_survey.zig")

MANIFEST_MARKERS = [
    '"acceptable_limit_iterations": 4',
    '"acceptable_limit_sample_count": 7',
    '"acceptable_limit_max_elapsed_ns": 12288',
    '"sample_count_note": "seven monotonic samples"',
    '"id": "phase4-perf-baseline-bitmap-command-evidence"',
    '"iterations": 1',
    '"checksum": 5216946504564592253',
    '"iterations": 4',
    '"checksum": 7942141539243507472',
    '"status": "shared CI perf promotion pending"',
    '"owner": "Validation and Perf Team"',
    '"coordination_owners": [\n    "ABI and Runtime Team",\n    "Shared Subsystems Pod"\n  ]',
]

MANIFEST_MARKER_COUNTS = {
    '"final_first_zero": 109': 2,
}

SURVEY_MARKERS = [
    'test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {',
    'try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 2);',
    'try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 2);',
    'try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));',
    'try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));',
    '\\"acceptable_limit_max_elapsed_ns\\": 12288',
    '\\"checksum\\": 5216946504564592253',
    '\\"checksum\\": 7942141539243507472',
    '\\"final_first_zero\\": 109',
    'test "phase4 perf baseline survey keeps reversible delivery evidence explicit" {',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def append_missing_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def append_missing_marker_counts(
    missing: list[str], label: str, text: str, expected_counts: dict[str, int]
) -> None:
    for marker, count in expected_counts.items():
        actual = text.count(marker)
        if actual != count:
            missing.append(f"{label}:{marker}:expected={count}:actual={actual}")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []

    manifest = root / MANIFEST_REL
    if not manifest.is_file():
        missing.append(f"file:{MANIFEST_REL.as_posix()}")
    else:
        manifest_text = read_text(manifest)
        append_missing_markers(missing, "manifest_marker", manifest_text, MANIFEST_MARKERS)
        append_missing_marker_counts(
            missing, "manifest_count", manifest_text, MANIFEST_MARKER_COUNTS
        )

    survey = root / SURVEY_REL
    if not survey.is_file():
        missing.append(f"file:{SURVEY_REL.as_posix()}")
    else:
        survey_text = read_text(survey)
        append_missing_markers(missing, "survey_marker", survey_text, SURVEY_MARKERS)

    return missing


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_REL,
        """{
  "lane_key": "P4-L20",
  "phase": "Phase 4",
  "owner": "Validation and Perf Team",
  "rollback_owner": "Validation and Perf Team",
  "decision_owner": "Validation and Perf Team",
  "coordination_owners": [
    "ABI and Runtime Team",
    "Shared Subsystems Pod"
  ],
  "shared_ci_perf_promotion_status": "pending",
  "local_only_posture_note": "The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.",
  "bitmap": {
    "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey",
    "acceptable_limit_status": "approved_local_only",
    "acceptable_limit_metric": "median_elapsed_ns",
    "acceptable_limit_iterations": 4,
    "acceptable_limit_sample_count": 7,
    "acceptable_limit_max_elapsed_ns": 12288,
    "evidence": [
      {
        "id": "phase4-perf-baseline-bitmap-acceptable-limit",
        "kind": "acceptable_limit",
        "metric": "median_elapsed_ns",
        "status": "approved_local_only",
        "sample_count_note": "seven monotonic samples",
        "max_elapsed_ns": 12288
      },
      {
        "id": "phase4-perf-baseline-bitmap-command-evidence",
        "kind": "threshold_replay",
        "runs": [
          {
            "iterations": 1,
            "checksum": 5216946504564592253,
            "final_first_zero": 109
          },
          {
            "iterations": 4,
            "checksum": 7942141539243507472,
            "final_first_zero": 109
          }
        ]
      }
    ]
  },
  "promotion_decision": {
    "id": "phase4-perf-baseline-shared-promotion-decision",
    "status": "shared CI perf promotion pending",
    "owner": "Validation and Perf Team",
    "coordination_owners": [
      "ABI and Runtime Team",
      "Shared Subsystems Pod"
    ]
  }
}
""",
    )
    write_text(
        root / SURVEY_REL,
        """const std = @import("std");

test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {
    try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 2);
    try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 2);
    try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));
    try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));
}

test "phase4 perf baseline survey keeps coordination owners, the dedicated survey wrapper, both surface wrappers, and bitmap limits explicit" {
    try requireMarker("\\"acceptable_limit_max_elapsed_ns\\": 12288");
    try requireMarker("\\"checksum\\": 5216946504564592253");
    try requireMarker("\\"checksum\\": 7942141539243507472");
    try requireMarker("\\"final_first_zero\\": 109");
}

test "phase4 perf baseline survey keeps reversible delivery evidence explicit" {
    try requireMarker("keep scripts/zigux/check-phase4-perf-baseline-packet.py, zigux/tests/phase4_perf_baseline_manifest.json, zigux/tests/phase4_perf_baseline_survey.zig aligned");
}
""",
    )


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-perf-values-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)

        if validate_root(root):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        manifest = root / MANIFEST_REL
        survey = root / SURVEY_REL

        write_text(
            manifest,
            replace_once(read_text(manifest), '"acceptable_limit_sample_count": 7', '"acceptable_limit_sample_count": 8'),
        )
        if not expect_failure(root, 'manifest_marker:"acceptable_limit_sample_count": 7'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("manifest sample-count drift case did not fail closed")
            return 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(read_text(manifest), '"checksum": 5216946504564592253', '"checksum": 5216946504564592254'),
        )
        if not expect_failure(root, 'manifest_marker:"checksum": 5216946504564592253'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("manifest first checksum drift case did not fail closed")
            return 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(read_text(manifest), '"final_first_zero": 109', '"final_first_zero": 110'),
        )
        if not expect_failure(root, 'manifest_count:"final_first_zero": 109:expected=2:actual=1'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("manifest final-first-zero drift case did not fail closed")
            return 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(
                read_text(survey),
                'try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 2);',
                'try requireMarkerCount("\\"acceptable_limit_iterations\\": 5", 2);',
            ),
        )
        if not expect_failure(root, 'survey_marker:try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 2);'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("survey iteration-count drift case did not fail closed")
            return 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(
                read_text(survey),
                'try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 2);',
                'try requireMarkerCount("\\"acceptable_limit_sample_count\\": 8", 2);',
            ),
        )
        if not expect_failure(root, 'survey_marker:try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 2);'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("survey sample-count drift case did not fail closed")
            return 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(read_text(survey), '\\"checksum\\": 7942141539243507472', '\\"checksum\\": 7942141539243507473'),
        )
        if not expect_failure(root, 'survey_marker:\\"checksum\\": 7942141539243507472'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("survey checksum drift case did not fail closed")
            return 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(read_text(survey), '\\"final_first_zero\\": 109', '\\"final_first_zero\\": 110'),
        )
        if not expect_failure(root, 'survey_marker:\\"final_first_zero\\": 109'):
            print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=fail")
            print("survey final-first-zero drift case did not fail closed")
            return 1

    print("PHASE4_PERF_BASELINE_VALUES_SELF_TEST=pass")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 4 perf-baseline value packet for exact survey and manifest replay markers."
    )
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve()
    missing = validate_root(root)
    if missing:
        print("PHASE4_PERF_BASELINE_VALUES_CHECK=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE4_PERF_BASELINE_VALUES_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
