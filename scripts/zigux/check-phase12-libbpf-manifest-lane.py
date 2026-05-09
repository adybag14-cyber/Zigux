#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase12_libbpf_manifest.json"
SEGMENTS_TEST_PATH = "zigux/tests/phase12_libbpf_segments.zig"
REVIEWABILITY_TEST_PATH = "zigux/tests/phase12_libbpf_reviewability.zig"


def read_text(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.exists():
        raise FileNotFoundError(rel_path)
    return path.read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict[str, str]:
    text = read_text(root, MANIFEST_PATH)
    data = json.loads(text)
    return {
        "lane_key": data["lane_key"],
        "phase": data["phase"],
        "surveyed_commit": data["surveyed_commit"],
    }


def expected_markers(manifest: dict[str, str]) -> dict[str, list[str]]:
    lane_key = manifest["lane_key"]
    phase = manifest["phase"]
    surveyed_commit = manifest["surveyed_commit"]
    return {
        SEGMENTS_TEST_PATH: [
            f'try std.testing.expectEqualStrings("{lane_key}", manifest.lane_key);',
            f'try std.testing.expectEqualStrings("{phase}", manifest.phase);',
            f'try std.testing.expectEqualStrings("{surveyed_commit}", manifest.surveyed_commit);',
        ],
        REVIEWABILITY_TEST_PATH: [
            f'try std.testing.expectEqualStrings("{lane_key}", manifest.lane_key);',
            f'try std.testing.expectEqualStrings("{phase}", manifest.phase);',
            f'try std.testing.expectEqualStrings("{surveyed_commit}", manifest.surveyed_commit);',
        ],
    }


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    try:
        manifest = load_manifest(root)
    except FileNotFoundError as exc:
        return [f"missing_file:{exc.args[0]}"]
    except KeyError as exc:
        return [f"missing_manifest_key:{exc.args[0]}"]
    except json.JSONDecodeError:
        return [f"invalid_json:{MANIFEST_PATH}"]

    markers_by_file = expected_markers(manifest)
    for rel_path, markers in markers_by_file.items():
        try:
            text = read_text(root, rel_path)
        except FileNotFoundError as exc:
            failures.append(f"missing_file:{exc.args[0]}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel_path}:{marker}")

    return failures


def write(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_root(root: Path) -> None:
    manifest = {
        "lane_key": "P12-L16",
        "phase": "Phase 12",
        "surveyed_commit": "c0ae127363e3d4e5feeb36efb665a12ece3392c7",
    }
    write(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    markers_by_file = expected_markers(manifest)
    for rel_path, markers in markers_by_file.items():
        write(root, rel_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase12-libbpf-manifest-lane-") as tmp:
        root = Path(tmp)
        build_fixture_root(root)

        failures = validate(root)
        if failures:
            print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        failures = validate(root)
        if failures != [f"missing_file:{MANIFEST_PATH}"]:
            print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        build_fixture_root(root)
        case_count += 1

        segments_path = root / SEGMENTS_TEST_PATH
        segments_text = segments_path.read_text(encoding="utf-8")
        segments_path.write_text(
            segments_text.replace("P12-L16", "P12-L14", 1),
            encoding="utf-8",
        )
        failures = validate(root)
        expected = f'{SEGMENTS_TEST_PATH}:try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);'
        if expected not in failures:
            print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        build_fixture_root(root)
        case_count += 1

        segments_text = segments_path.read_text(encoding="utf-8")
        phase_marker = 'try std.testing.expectEqualStrings("Phase 12", manifest.phase);'
        segments_path.write_text(segments_text.replace(phase_marker, "", 1), encoding="utf-8")
        failures = validate(root)
        expected = f"{SEGMENTS_TEST_PATH}:{phase_marker}"
        if expected not in failures:
            print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        build_fixture_root(root)
        case_count += 1

        reviewability_path = root / REVIEWABILITY_TEST_PATH
        reviewability_text = reviewability_path.read_text(encoding="utf-8")
        commit_marker = 'try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", manifest.surveyed_commit);'
        reviewability_path.write_text(
            reviewability_text.replace("c0ae127363e3d4e5feeb36efb665a12ece3392c7", "deadbeef", 1),
            encoding="utf-8",
        )
        failures = validate(root)
        expected = f"{REVIEWABILITY_TEST_PATH}:{commit_marker}"
        if expected not in failures:
            print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        build_fixture_root(root)
        case_count += 1

        reviewability_text = reviewability_path.read_text(encoding="utf-8")
        lane_marker = 'try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);'
        reviewability_path.write_text(reviewability_text.replace(lane_marker, "", 1), encoding="utf-8")
        failures = validate(root)
        expected = f"{REVIEWABILITY_TEST_PATH}:{lane_marker}"
        if expected not in failures:
            print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

    print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=pass")
    print(f"PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 12 libbpf manifest lane markers still match the paired Zig tests."
    )
    parser.add_argument("root", nargs="?", default=DEFAULT_ROOT, type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_LIBBPF_MANIFEST_LANE=fail")
        print("PHASE12_LIBBPF_MANIFEST_LANE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_LIBBPF_MANIFEST_LANE_FAILURES_END")
        return 1

    print("PHASE12_LIBBPF_MANIFEST_LANE=pass")
    print("PHASE12_LIBBPF_MANIFEST_LANE_MARKER_COUNT=6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
