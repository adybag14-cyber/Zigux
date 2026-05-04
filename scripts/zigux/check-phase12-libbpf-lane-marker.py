#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
TRACKED_PATHS = [
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "zigux/tests/phase12_libbpf_segments.zig",
]
LANE_MARKER = "PHASE12_LANE_KEY=P12-L16"


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def check_lane_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in TRACKED_PATHS:
        path = root / rel_path
        if not path.exists():
            missing.append(f"missing_file:{rel_path}")
            continue
        marker_count = read_text(root, rel_path).count(LANE_MARKER)
        if marker_count != 1:
            missing.append(
                f"lane_marker:{rel_path}:expected=1:actual={marker_count}"
            )
    return missing


def build_self_test_tree(root: Path) -> None:
    write_text(
        root,
        TRACKED_PATHS[0],
        "# Phase 12 Libbpf Segment Survey\n\n"
        f"- `{LANE_MARKER}`\n",
    )
    write_text(
        root,
        TRACKED_PATHS[1],
        "const current_surveyed_commit = \"d62742e7ff0747ed15f71f67d505f68ea15ec7ab\";\n"
        f"// {LANE_MARKER}\n",
    )


def expect_contains(label: str, items: list[str], expected: str) -> None:
    if expected not in items:
        raise SystemExit(f"phase12-libbpf-lane-marker:self-test:{label}:{expected}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_lane_marker_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_tree(root)
        if check_lane_markers(root):
            raise SystemExit("phase12-libbpf-lane-marker:self-test:baseline")

        build_self_test_tree(root)
        (root / TRACKED_PATHS[0]).unlink()
        expect_contains(
            "missing_survey_note",
            check_lane_markers(root),
            f"missing_file:{TRACKED_PATHS[0]}",
        )

        build_self_test_tree(root)
        survey_note_path = root / TRACKED_PATHS[0]
        survey_note_path.write_text("# Phase 12\n", encoding="utf-8")
        expect_contains(
            "missing_survey_marker",
            check_lane_markers(root),
            f"lane_marker:{TRACKED_PATHS[0]}:expected=1:actual=0",
        )

        build_self_test_tree(root)
        survey_note_path = root / TRACKED_PATHS[0]
        survey_note_path.write_text(
            survey_note_path.read_text(encoding="utf-8") + f"\n- `{LANE_MARKER}`\n",
            encoding="utf-8",
        )
        expect_contains(
            "duplicate_survey_marker",
            check_lane_markers(root),
            f"lane_marker:{TRACKED_PATHS[0]}:expected=1:actual=2",
        )

        build_self_test_tree(root)
        segment_test_path = root / TRACKED_PATHS[1]
        segment_test_path.write_text(
            "const current_surveyed_commit = \"d62742e7ff0747ed15f71f67d505f68ea15ec7ab\";\n",
            encoding="utf-8",
        )
        expect_contains(
            "missing_segment_marker",
            check_lane_markers(root),
            f"lane_marker:{TRACKED_PATHS[1]}:expected=1:actual=0",
        )

        build_self_test_tree(root)
        segment_test_path = root / TRACKED_PATHS[1]
        segment_test_path.write_text(
            segment_test_path.read_text(encoding="utf-8") + f"// {LANE_MARKER}\n",
            encoding="utf-8",
        )
        expect_contains(
            "duplicate_segment_marker",
            check_lane_markers(root),
            f"lane_marker:{TRACKED_PATHS[1]}:expected=1:actual=2",
        )

    print("PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass")
    print("PHASE12_LIBBPF_LANE_MARKER_SELF_TEST_CASE_COUNT=6")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the explicit Phase 12 libbpf lane marker in the survey note and segment test."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthetic lane-marker replay checks.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing = check_lane_markers(ROOT)
    if missing:
        print("PHASE12_LIBBPF_LANE_MARKER=fail")
        print("PHASE12_LIBBPF_LANE_MARKER_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_LANE_MARKER_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_LANE_MARKER=pass")
    print(f"PHASE12_LIBBPF_LANE_MARKER_FILE_COUNT={len(TRACKED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
