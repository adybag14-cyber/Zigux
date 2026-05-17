#!/usr/bin/env python3
"""Guard the bounded Phase 4 local-only perf packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
SURVEY = Path("zigux/tests/phase4_perf_baseline_survey.zig")

MANIFEST_MARKERS = (
    '"lane_key": "P4-L20"',
    '"phase": "Phase 4"',
    '"owner": "Validation and Perf Team"',
    '"rollback_owner": "Validation and Perf Team"',
    '"decision_owner": "Validation and Perf Team"',
    '"coordination_owners": [',
    '"ABI and Runtime Team"',
    '"Shared Subsystems Pod"',
    '"shared_ci_perf_promotion_status": "pending"',
    '"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"',
    '"linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"',
    '"acceptable_limit_status": "approved_local_only"',
    '"acceptable_limit_metric": "median_elapsed_ns"',
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
)

SURVEY_MARKERS = (
    'test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {',
    'try requireMarkerCount("\\"acceptable_limit_iterations\\": 4", 1);',
    'try requireMarkerCount("\\"acceptable_limit_sample_count\\": 7", 1);',
    'try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));',
    'try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));',
    'test "phase4 perf baseline survey keeps dedicated local-only ownership and command evidence explicit" {',
    'try requireMarker("\\"owner\\": \\"Validation and Perf Team\\"");',
    'try requireMarker("\\"linux_style_wrapper\\": \\"make -C zigux phase4-perf-baseline-survey\\"");',
    'try requireMarker("\\"checksum\\": 5216946504564592253");',
    'try requireMarker("\\"checksum\\": 7942141539243507472");',
    'try requireMarker("\\"final_first_zero\\": 109");',
    'test "phase4 perf baseline survey keeps the dedicated packet contract reviewable" {',
    'try requireMarker("\\"id\\": \\"phase4-perf-baseline-shared-promotion-decision\\"");',
    'try requireMarker("\\"status\\": \\"shared CI perf promotion pending\\"");',
    'try requireMarker("\\"coordination_owners\\": [");',
)

EXPECTED_FINAL_FIRST_ZERO_COUNT = 2
EXPECTED_SELF_TEST_CASES = 16


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str, missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate_root(root: Path) -> list[str]:
    missing: list[str] = []

    manifest = root / MANIFEST
    if not manifest.is_file():
        missing.append(f"file:{MANIFEST.as_posix()}")
    else:
        manifest_text = read_text(manifest)
        require_markers(manifest_text, MANIFEST_MARKERS, "manifest_marker", missing)
        final_first_zero_count = manifest_text.count('"final_first_zero": 109')
        if final_first_zero_count != EXPECTED_FINAL_FIRST_ZERO_COUNT:
            missing.append(
                'manifest_count:"final_first_zero": 109:'
                f"expected={EXPECTED_FINAL_FIRST_ZERO_COUNT}:actual={final_first_zero_count}"
            )

    survey = root / SURVEY
    if not survey.is_file():
        missing.append(f"file:{SURVEY.as_posix()}")
    else:
        survey_text = read_text(survey)
        require_markers(survey_text, SURVEY_MARKERS, "survey_marker", missing)

    return missing


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def build_fixture_tree(root: Path) -> None:
    source_root = Path(__file__).resolve().parents[2]
    write_text(root / MANIFEST, read_text(source_root / MANIFEST))
    write_text(root / SURVEY, read_text(source_root / SURVEY))


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-perf-baseline-packet-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1
        cases = 1

        manifest = root / MANIFEST
        survey = root / SURVEY

        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"acceptable_limit_iterations": 4',
                '"acceptable_limit_iterations": 5',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"acceptable_limit_iterations": 4'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest iteration-count drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"',
                '"benchmark_command": "zig build phase4-bitmap-diff-other --build-file zigux/tests/phase4_build.zig"',
            ),
        )
        if not expect_failure(
            root,
            'manifest_marker:"benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"',
        ):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest benchmark-command drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"acceptable_limit_max_elapsed_ns": 12288',
                '"acceptable_limit_max_elapsed_ns": 16384',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"acceptable_limit_max_elapsed_ns": 12288'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest acceptable-limit drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"final_first_zero": 109',
                '"final_first_zero": 110',
            ),
        )
        if not expect_failure(root, 'manifest_count:"final_first_zero": 109:expected=2:actual=1'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest replay-count drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"sample_count_note": "seven monotonic samples"',
                '"sample_count_note": "eight monotonic samples"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"sample_count_note": "seven monotonic samples"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest sample-count note drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"decision_owner": "Validation and Perf Team"',
                '"decision_owner": "ABI and Runtime Team"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"decision_owner": "Validation and Perf Team"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest decision-owner drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"rollback_owner": "Validation and Perf Team"',
                '"rollback_owner": "ABI and Runtime Team"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"rollback_owner": "Validation and Perf Team"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest rollback-owner drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            read_text(manifest).replace(
                '"ABI and Runtime Team"',
                '"ABI and Replay Team"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"ABI and Runtime Team"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest coordination-owner drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"acceptable_limit_status": "approved_local_only"',
                '"acceptable_limit_status": "pending_review"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"acceptable_limit_status": "approved_local_only"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest acceptable-limit status drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"acceptable_limit_metric": "median_elapsed_ns"',
                '"acceptable_limit_metric": "mean_elapsed_ns"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"acceptable_limit_metric": "median_elapsed_ns"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest acceptable-limit metric drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"shared_ci_perf_promotion_status": "pending"',
                '"shared_ci_perf_promotion_status": "approved"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"shared_ci_perf_promotion_status": "pending"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest shared-ci-promotion-status drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            manifest,
            replace_once(
                read_text(manifest),
                '"status": "shared CI perf promotion pending"',
                '"status": "shared CI perf promotion approved"',
            ),
        )
        if not expect_failure(root, 'manifest_marker:"status": "shared CI perf promotion pending"'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("manifest promotion-status drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(
                read_text(survey),
                'try requireMarker("\\"id\\": \\"phase4-perf-baseline-shared-promotion-decision\\"");',
                'try requireMarker("\\"id\\": \\"phase4-perf-baseline-other-decision\\"");',
            ),
        )
        if not expect_failure(root, 'survey_marker:try requireMarker("\\"id\\": \\"phase4-perf-baseline-shared-promotion-decision\\"");'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("survey promotion-decision drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(
                read_text(survey),
                'try requireMarker("\\"owner\\": \\"Validation and Perf Team\\"");',
                'try requireMarker("\\"owner\\": \\"ABI and Runtime Team\\"");',
            ),
        )
        if not expect_failure(root, 'survey_marker:try requireMarker("\\"owner\\": \\"Validation and Perf Team\\"");'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("survey owner drift case did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(
            survey,
            replace_once(
                read_text(survey),
                'try requireMarker("\\"linux_style_wrapper\\": \\"make -C zigux phase4-perf-baseline-survey\\"");',
                'try requireMarker("\\"linux_style_wrapper\\": \\"make -C zigux phase4-perf-baseline\\"");',
            ),
        )
        if not expect_failure(root, 'survey_marker:try requireMarker("\\"linux_style_wrapper\\": \\"make -C zigux phase4-perf-baseline-survey\\"");'):
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print("survey wrapper drift case did not fail closed")
            return 1
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass")
    print(f"PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve()
    missing = validate_root(root)
    if missing:
        print("PHASE4_PERF_BASELINE_PACKET_CHECK=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE4_PERF_BASELINE_PACKET_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())