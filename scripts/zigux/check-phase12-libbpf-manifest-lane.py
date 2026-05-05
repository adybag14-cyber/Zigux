#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = "zigux/tests/phase12_libbpf_manifest.json"
SEGMENT_TEST_PATH = "zigux/tests/phase12_libbpf_segments.zig"
REVIEWABILITY_PATH = "zigux/tests/phase12_libbpf_reviewability.zig"


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def check_alignment(root: Path) -> list[str]:
    missing: list[str] = []
    manifest_path = root / MANIFEST_PATH
    segment_test_path = root / SEGMENT_TEST_PATH
    reviewability_path = root / REVIEWABILITY_PATH

    if not manifest_path.exists():
        return [f"missing_file:{MANIFEST_PATH}"]
    if not segment_test_path.exists():
        return [f"missing_file:{SEGMENT_TEST_PATH}"]
    if not reviewability_path.exists():
        return [f"missing_file:{REVIEWABILITY_PATH}"]

    manifest = json.loads(read_text(root, MANIFEST_PATH))
    lane_key = manifest.get("lane_key")
    phase = manifest.get("phase")
    surveyed_commit = manifest.get("surveyed_commit")

    if not isinstance(lane_key, str) or not lane_key:
        missing.append("manifest:lane_key")
    if not isinstance(phase, str) or not phase:
        missing.append("manifest:phase")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        missing.append("manifest:surveyed_commit")

    segment_test = read_text(root, SEGMENT_TEST_PATH)
    reviewability = read_text(root, REVIEWABILITY_PATH)

    if isinstance(lane_key, str) and lane_key:
        lane_assertion = f'expectEqualStrings("{lane_key}", manifest.lane_key);'
        if lane_assertion not in segment_test:
            missing.append("segment_test:lane_key_assertion")

    if isinstance(phase, str) and phase:
        phase_assertion = f'expectEqualStrings("{phase}", manifest.phase);'
        if phase_assertion not in segment_test:
            missing.append("segment_test:phase_assertion")

    if isinstance(surveyed_commit, str) and surveyed_commit:
        commit_assertion = (
            f'expectEqualStrings("{surveyed_commit}", manifest.surveyed_commit);'
        )
        if commit_assertion not in segment_test:
            missing.append("segment_test:surveyed_commit_assertion")

    reviewability_markers = [
        "zigux/tests/phase12_libbpf_manifest.json",
        "phase12 libbpf reviewability gate matches the current zigux_segments file state",
        "phase12 libbpf reviewability gate cross-checks the legacy segment catalog",
    ]
    for marker in reviewability_markers:
        if marker not in reviewability:
            missing.append(f"reviewability:{marker}")

    return missing


def build_self_test_tree(root: Path) -> None:
    lane_key = "P12-L13"
    phase = "Phase 12"
    surveyed_commit = "c0ae127363e3d4e5feeb36efb665a12ece3392c7"
    write_text(
        root,
        MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": lane_key,
                "phase": phase,
                "surveyed_commit": surveyed_commit,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        SEGMENT_TEST_PATH,
        "\n".join(
            [
                'try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);',
                'try std.testing.expectEqualStrings("Phase 12", manifest.phase);',
                'try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", manifest.surveyed_commit);',
            ]
        )
        + "\n",
    )
    write_text(
        root,
        REVIEWABILITY_PATH,
        "\n".join(
            [
                'const manifest_path = "zigux/tests/phase12_libbpf_manifest.json";',
                'test "phase12 libbpf reviewability gate matches the current zigux_segments file state" {}',
                'test "phase12 libbpf reviewability gate cross-checks the legacy segment catalog" {}',
            ]
        )
        + "\n",
    )


def expect_contains(label: str, items: list[str], expected: str) -> None:
    if expected not in items:
        raise SystemExit(f"phase12-libbpf-manifest-lane:self-test:{label}:{expected}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_libbpf_manifest_lane_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_tree(root)
        if check_alignment(root):
            raise SystemExit("phase12-libbpf-manifest-lane:self-test:baseline")

        build_self_test_tree(root)
        (root / MANIFEST_PATH).unlink()
        expect_contains(
            "missing_manifest",
            check_alignment(root),
            f"missing_file:{MANIFEST_PATH}",
        )

        build_self_test_tree(root)
        manifest = json.loads(read_text(root, MANIFEST_PATH))
        manifest["lane_key"] = "P12-L99"
        write_text(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_contains(
            "lane_key_drift",
            check_alignment(root),
            "segment_test:lane_key_assertion",
        )

        build_self_test_tree(root)
        write_text(
            root,
            SEGMENT_TEST_PATH,
            read_text(root, SEGMENT_TEST_PATH).replace(
                'try std.testing.expectEqualStrings("Phase 12", manifest.phase);\n', ""
            ),
        )
        expect_contains(
            "missing_phase_assertion",
            check_alignment(root),
            "segment_test:phase_assertion",
        )

        build_self_test_tree(root)
        manifest = json.loads(read_text(root, MANIFEST_PATH))
        manifest["surveyed_commit"] = "deadbeef"
        write_text(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_contains(
            "surveyed_commit_drift",
            check_alignment(root),
            "segment_test:surveyed_commit_assertion",
        )

        build_self_test_tree(root)
        write_text(
            root,
            REVIEWABILITY_PATH,
            'test "phase12 libbpf reviewability gate matches the current zigux_segments file state" {}\n',
        )
        expect_contains(
            "missing_reviewability_marker",
            check_alignment(root),
            "reviewability:zigux/tests/phase12_libbpf_manifest.json",
        )

    print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST=pass")
    print("PHASE12_LIBBPF_MANIFEST_LANE_SELF_TEST_CASE_COUNT=6")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 12 libbpf manifest lane key, phase, and surveyed "
            "commit still line up with the paired Zig survey and reviewability tests."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run synthetic manifest-lane replay checks.",
    )
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root to inspect.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing = check_alignment(Path(args.root))
    if missing:
        print("PHASE12_LIBBPF_MANIFEST_LANE=fail")
        print("PHASE12_LIBBPF_MANIFEST_LANE_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_LIBBPF_MANIFEST_LANE_MISSING_END")
        return 1

    print("PHASE12_LIBBPF_MANIFEST_LANE=pass")
    print(
        "PHASE12_LIBBPF_MANIFEST_LANE_TRACKED_FILES="
        f"{','.join([MANIFEST_PATH, SEGMENT_TEST_PATH, REVIEWABILITY_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
