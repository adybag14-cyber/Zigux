#!/usr/bin/env python3
"""Guard the bounded Phase 1 find_bit checker packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

VALIDATOR_REL = Path("scripts/zigux/check-phase1-find-bit-validator-anchors.py")
BENCH_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
REVIEW_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

REQUIRED_FILES = (
    VALIDATOR_REL,
    BENCH_REL,
    REVIEW_REL,
    LANE_NOTE_REL,
)

VALIDATOR_MARKERS = {
    "bench_anchor_rel": 'FIND_BIT_BENCH_ANCHOR_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    "lane_note_rel": 'LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    "closure_rel": 'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    "docs_readme_rel": 'DOCS_README_REL = Path("Documentation/zigux/README.md")',
    "scripts_readme_rel": 'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    "self_test_result": 'print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass")',
    "self_test_count": 'print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}")',
}

BENCH_MARKERS = {
    "validator_source_line": '    "find_next_past_end": "findNextBit(&empty, 7, 11)",',
    "clump_source_line": '    "find_clump8_past_end": "findNextClump8(&clump, &empty, 8, 8)",',
    "tail_source_line": '    "find_last_tail_single_word": "try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));",',
    "self_test_result": 'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")',
    "self_test_count": 'print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")',
}

REVIEW_MARKERS = {
    "smoke_rel": 'SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")',
    "manifest_rel": 'MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")',
    "fixture_rel": 'FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")',
    "lane_lines": "EXPECTED_LANE_LINES = [",
    "self_test_result": 'print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")',
    "self_test_count": 'print(f"PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")',
}

LANE_MARKERS = {
    "validator_checker": "`scripts/zigux/check-phase1-find-bit-validator-anchors.py`",
    "bench_checker": "`scripts/zigux/check-phase1-find-bit-bench-anchors.py`",
    "review_checker": "`scripts/zigux/check-phase1-find-bit-review-packet.py`",
    "next_safe_step": "`PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    validator = load_text(root, VALIDATOR_REL)
    for key, marker in VALIDATOR_MARKERS.items():
        failures.extend(require_exact_occurrence(validator, f"validator:{key}", marker))

    bench = load_text(root, BENCH_REL)
    for key, marker in BENCH_MARKERS.items():
        failures.extend(require_exact_occurrence(bench, f"bench:{key}", marker))

    review = load_text(root, REVIEW_REL)
    for key, marker in REVIEW_MARKERS.items():
        failures.extend(require_exact_occurrence(review, f"review:{key}", marker))

    lane_note = load_text(root, LANE_NOTE_REL)
    for key, marker in LANE_MARKERS.items():
        failures.extend(require_exact_occurrence(lane_note, f"lane:{key}", marker))

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS.values()) + "\n")
    write_file(root, BENCH_REL, "\n".join(BENCH_MARKERS.values()) + "\n")
    write_file(root, REVIEW_REL, "\n".join(REVIEW_MARKERS.values()) + "\n")
    write_file(root, LANE_NOTE_REL, "\n".join(LANE_MARKERS.values()) + "\n")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def duplicate_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(marker, marker + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[Path, str, str] | None, list[str]]] = [
        ("success", None, []),
    ]

    for key, marker in VALIDATOR_MARKERS.items():
        cases.append(
            (
                f"validator_remove:{key}",
                (VALIDATOR_REL, marker, "remove"),
                [f"validator:{key}:expected=1:actual=0"],
            )
        )
        cases.append(
            (
                f"validator_duplicate:{key}",
                (VALIDATOR_REL, marker, "duplicate"),
                [f"validator:{key}:expected=1:actual=2"],
            )
        )

    for key, marker in BENCH_MARKERS.items():
        cases.append(
            (
                f"bench_remove:{key}",
                (BENCH_REL, marker, "remove"),
                [f"bench:{key}:expected=1:actual=0"],
            )
        )
        cases.append(
            (
                f"bench_duplicate:{key}",
                (BENCH_REL, marker, "duplicate"),
                [f"bench:{key}:expected=1:actual=2"],
            )
        )

    for key, marker in REVIEW_MARKERS.items():
        cases.append(
            (
                f"review_remove:{key}",
                (REVIEW_REL, marker, "remove"),
                [f"review:{key}:expected=1:actual=0"],
            )
        )
        cases.append(
            (
                f"review_duplicate:{key}",
                (REVIEW_REL, marker, "duplicate"),
                [f"review:{key}:expected=1:actual=2"],
            )
        )

    for key, marker in LANE_MARKERS.items():
        cases.append(
            (
                f"lane_remove:{key}",
                (LANE_NOTE_REL, marker, "remove"),
                [f"lane:{key}:expected=1:actual=0"],
            )
        )
        cases.append(
            (
                f"lane_duplicate:{key}",
                (LANE_NOTE_REL, marker, "duplicate"),
                [f"lane:{key}:expected=1:actual=2"],
            )
        )

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path.as_posix()}",
                (relative_path, "", "missing"),
                [f"missing_file:{relative_path.as_posix()}"],
            )
        )

    for name, mutation, expected_failures in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-checker-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                relative_path, marker, kind = mutation
                target = root / relative_path
                if kind == "remove":
                    remove_marker(target, marker)
                elif kind == "duplicate":
                    duplicate_marker(target, marker)
                elif kind == "missing":
                    target.unlink()

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_FIND_BIT_CHECKER_PACKET_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif failures != expected_failures:
                print("PHASE1_FIND_BIT_CHECKER_PACKET_SELF_TEST=fail")
                print(f"self-test:{name}:expected={expected_failures!r}")
                print(f"self-test:{name}:actual={failures!r}")
                return 1

    print("PHASE1_FIND_BIT_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_CHECKER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_CHECKER_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_CHECKER_PACKET=pass")
    print(f"PHASE1_FIND_BIT_CHECKER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
