#!/usr/bin/env python3
"""Fail-closed checker for Phase 12 libbpf lane-marker drift."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Iterable


MANIFEST_REL_PATH = Path("zigux/tests/phase12_libbpf_manifest.json")
SURVEY_NOTE_REL_PATH = Path("Documentation/zigux/phase12-libbpf-segment-survey.md")
VERIFY_SHARD_NOTE_REL_PATH = Path("Documentation/zigux/phase12-libbpf-verify-shard-note.md")
SEGMENT_TEST_REL_PATH = Path("zigux/tests/phase12_libbpf_segments.zig")
SEGMENT_TEST_NOTE_MARKER = '"Documentation/zigux/phase12-libbpf-segment-survey.md"'
VERIFY_SHARD_NOTE_CHECKER_MARKER = '- lane-marker guard: `scripts/zigux/check-phase12-libbpf-lane-marker.py`'
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load_manifest_packet(root: Path) -> dict[str, str]:
    payload = json.loads((root / MANIFEST_REL_PATH).read_text(encoding="utf-8"))
    lane_key = payload.get("lane_key")
    phase = payload.get("phase")
    surveyed_commit = payload.get("surveyed_commit")
    if not isinstance(lane_key, str) or not lane_key:
        raise SystemExit("invalid Phase 12 libbpf lane_key")
    if phase != "Phase 12":
        raise SystemExit("invalid Phase 12 libbpf phase")
    if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
        raise SystemExit("invalid Phase 12 libbpf surveyed_commit")
    return {
        "lane_key": lane_key,
        "phase": phase,
        "surveyed_commit": surveyed_commit,
    }


def expected_lane_marker_text(lane_key: str) -> str:
    return f"PHASE12_LANE_KEY={lane_key}"


def expected_segment_assertion_text(lane_key: str) -> str:
    return f'try std.testing.expectEqualStrings("{lane_key}", manifest.lane_key);'


def exact_count_errors(label: str, text: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count == 1:
        return []
    if count == 0:
        return [f"{label}:{marker}"]
    return [f"{label}_count:{marker}:expected=1:actual={count}"]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    manifest_path = root / MANIFEST_REL_PATH
    if not manifest_path.is_file():
        return [f"missing_file:{MANIFEST_REL_PATH.as_posix()}"]

    manifest_packet = load_manifest_packet(root)
    lane_marker = expected_lane_marker_text(manifest_packet["lane_key"])
    segment_assertion = expected_segment_assertion_text(manifest_packet["lane_key"])

    survey_note_path = root / SURVEY_NOTE_REL_PATH
    if not survey_note_path.is_file():
        missing.append(f"missing_file:{SURVEY_NOTE_REL_PATH.as_posix()}")
        survey_note = ""
    else:
        survey_note = survey_note_path.read_text(encoding="utf-8")

    verify_note_path = root / VERIFY_SHARD_NOTE_REL_PATH
    if not verify_note_path.is_file():
        missing.append(f"missing_file:{VERIFY_SHARD_NOTE_REL_PATH.as_posix()}")
        verify_note = ""
    else:
        verify_note = verify_note_path.read_text(encoding="utf-8")

    segment_test_path = root / SEGMENT_TEST_REL_PATH
    if not segment_test_path.is_file():
        missing.append(f"missing_file:{SEGMENT_TEST_REL_PATH.as_posix()}")
        segment_test = ""
    else:
        segment_test = segment_test_path.read_text(encoding="utf-8")

    missing.extend(exact_count_errors("survey_note", survey_note, lane_marker))
    missing.extend(exact_count_errors("verify_shard_note", verify_note, VERIFY_SHARD_NOTE_CHECKER_MARKER))
    missing.extend(exact_count_errors("segment_test", segment_test, SEGMENT_TEST_NOTE_MARKER))
    missing.extend(exact_count_errors("segment_test", segment_test, lane_marker))
    missing.extend(exact_count_errors("segment_test", segment_test, segment_assertion))
    return missing


def check_lane_marker(root: Path) -> int:
    missing = collect_missing_markers(root)
    if missing:
        print("PHASE12_LIBBPF_LANE_MARKER=fail")
        for item in missing:
            print(item)
        return 1
    print("PHASE12_LIBBPF_LANE_MARKER=pass")
    return 0


def build_self_test_tree(root: Path) -> None:
    (root / MANIFEST_REL_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_NOTE_REL_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / VERIFY_SHARD_NOTE_REL_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SEGMENT_TEST_REL_PATH.parent).mkdir(parents=True, exist_ok=True)

    (root / MANIFEST_REL_PATH).write_text(
        json.dumps(
            {
                "lane_key": "P12-L16",
                "phase": "Phase 12",
                "surveyed_commit": "c0ae127363e3d4e5feeb36efb665a12ece3392c7",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / SURVEY_NOTE_REL_PATH).write_text(
        "# Phase 12 Libbpf Segment Survey\n"
        "PHASE12_LANE_KEY=P12-L16\n",
        encoding="utf-8",
    )
    (root / VERIFY_SHARD_NOTE_REL_PATH).write_text(
        "# Phase 12 Libbpf Verify Shard Note\n"
        "- lane-marker guard: `scripts/zigux/check-phase12-libbpf-lane-marker.py`\n",
        encoding="utf-8",
    )
    (root / SEGMENT_TEST_REL_PATH).write_text(
        'const survey_path = "Documentation/zigux/phase12-libbpf-segment-survey.md";\n'
        'try std.testing.expect(std.mem.containsAtLeast(u8, survey_text, 1, "PHASE12_LANE_KEY=P12-L16"));\n'
        'try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);\n',
        encoding="utf-8",
    )


def expect_failure(root: Path, marker: str) -> None:
    missing = collect_missing_markers(root)
    if marker not in missing:
        raise SystemExit(f"phase12-libbpf-lane-marker:self-test:{marker}")


def run_self_test() -> int:
    cases = 6
    with tempfile.TemporaryDirectory(prefix="phase12-libbpf-lane-marker-") as tmp:
        root = Path(tmp)

        build_self_test_tree(root)
        if collect_missing_markers(root):
            raise SystemExit("phase12-libbpf-lane-marker:self-test:aligned_packet")

        build_self_test_tree(root)
        survey_path = root / SURVEY_NOTE_REL_PATH
        survey_path.write_text("# Phase 12 Libbpf Segment Survey\n", encoding="utf-8")
        expect_failure(root, "survey_note:PHASE12_LANE_KEY=P12-L16")

        build_self_test_tree(root)
        verify_path = root / VERIFY_SHARD_NOTE_REL_PATH
        verify_path.write_text("# Phase 12 Libbpf Verify Shard Note\n", encoding="utf-8")
        expect_failure(root, "verify_shard_note:- lane-marker guard: `scripts/zigux/check-phase12-libbpf-lane-marker.py`")

        build_self_test_tree(root)
        segment_path = root / SEGMENT_TEST_REL_PATH
        segment_path.write_text(
            segment_path.read_text(encoding="utf-8").replace(SEGMENT_TEST_NOTE_MARKER, "survey.md"),
            encoding="utf-8",
        )
        expect_failure(root, f"segment_test:{SEGMENT_TEST_NOTE_MARKER}")

        build_self_test_tree(root)
        segment_path = root / SEGMENT_TEST_REL_PATH
        segment_path.write_text(
            segment_path.read_text(encoding="utf-8").replace("PHASE12_LANE_KEY=P12-L16", ""),
            encoding="utf-8",
        )
        expect_failure(root, "segment_test:PHASE12_LANE_KEY=P12-L16")

        build_self_test_tree(root)
        segment_path = root / SEGMENT_TEST_REL_PATH
        segment_path.write_text(
            segment_path.read_text(encoding="utf-8").replace(
                'try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);\n',
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(root, 'segment_test:try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);')

        build_self_test_tree(root)
        segment_path = root / SEGMENT_TEST_REL_PATH
        segment_path.write_text(
            segment_path.read_text(encoding="utf-8")
            + 'try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);\n',
            encoding="utf-8",
        )
        expect_failure(
            root,
            'segment_test_count:try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);:expected=1:actual=2',
        )

    print("PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass")
    print(f"PHASE12_LIBBPF_LANE_MARKER_SELF_TEST_CASES={cases}")
    return 0


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return check_lane_marker(Path(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
