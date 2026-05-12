#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/phase13_devres_manifest.json"
SLICE_PATH = "Documentation/zigux/phase13-devres-slice.md"
SURVEY_PATH = "Documentation/zigux/phase13-devres-survey.md"
HELPER_PATH = "lib/devres.zig"
REPLAY_PATH = "zigux/tests/phase13_devres.zig"

STALE_SLICE_MARKER = "PHASE13_SLICE=devres-dma-scatterlist-boundary-survey"
SURVEYED_COMMIT_PREFIX = "reviewed against live `master` `"
STALE_CHECKER_WARNING = (
    "older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift"
)

MANIFEST_TO_SURVEY_MARKERS = {
    '"id": "phase13-devres-arch-phys-wc-token-planner"': "devm_arch_phys_wc_add()",
    '"id": "phase13-devres-live-scatterlist-ownership"': "helper-only DMA/scatterlist boundary",
}

IOUNMAP_SLICE_MARKERS = [
    "devm_iounmap()",
]

IOUNMAP_SURVEY_MARKERS = [
    "devm_iounmap()",
]

IOUNMAP_HELPER_MARKERS = [
    ".provides_iounmap_call_planning = true",
    "pub const ManagedIounmapPlan = struct {",
    "pub fn ioremapReleaseMatches(",
    "pub fn planManagedIounmap(",
    ".warns_on_release_miss = !release_matches",
]

IOUNMAP_REPLAY_MARKERS = [
    'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
    "const exact = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4000);",
    "const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);",
    "try std.testing.expect(miss.warns_on_release_miss);",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contains_manifest_expectation(source: str, key: str, value: str) -> bool:
    plain = f'"{key}": "{value}"'
    escaped = plain.replace('"', '\\"')
    return plain in source or escaped in source


def require_file(root: Path, rel: str, errors: list[str]) -> Path | None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing:{rel}")
        return None
    return path


def require_markers(source: str, prefix: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f"{prefix}:missing_marker:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = require_file(root, MANIFEST_PATH, errors)
    slice_path = require_file(root, SLICE_PATH, errors)
    survey_path = require_file(root, SURVEY_PATH, errors)
    helper_path = require_file(root, HELPER_PATH, errors)
    replay_path = require_file(root, REPLAY_PATH, errors)
    if errors:
        return errors

    manifest_text = read_text(manifest_path)
    slice_text = read_text(slice_path)
    survey_text = read_text(survey_path)
    helper_text = read_text(helper_path)
    replay_text = read_text(replay_path)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest:json_decode:{exc.msg}"]

    lane_key = manifest.get("lane_key")
    if not isinstance(lane_key, str) or not lane_key:
        errors.append("manifest:lane_key_missing")
    elif not contains_manifest_expectation(replay_text, "lane_key", lane_key):
        errors.append(f"replay:lane_key_mismatch:{lane_key}")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        errors.append("manifest:surveyed_commit_missing")
    else:
        if not contains_manifest_expectation(replay_text, "surveyed_commit", surveyed_commit):
            errors.append(f"replay:surveyed_commit_mismatch:{surveyed_commit}")
        if f"{SURVEYED_COMMIT_PREFIX}{surveyed_commit}`" not in survey_text:
            errors.append(f"survey:surveyed_commit_mismatch:{surveyed_commit}")

    if STALE_SLICE_MARKER in survey_text:
        errors.append("survey:stale_slice_label")

    for manifest_marker, survey_marker in MANIFEST_TO_SURVEY_MARKERS.items():
        if manifest_marker in manifest_text and survey_marker not in survey_text:
            errors.append(f"survey:missing_marker:{survey_marker}")

    if STALE_CHECKER_WARNING not in survey_text:
        errors.append("survey:missing_stale_checker_warning")

    require_markers(slice_text, "slice", IOUNMAP_SLICE_MARKERS, errors)
    require_markers(survey_text, "survey", IOUNMAP_SURVEY_MARKERS, errors)
    require_markers(helper_text, "helper", IOUNMAP_HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", IOUNMAP_REPLAY_MARKERS, errors)

    return errors


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P13-L01",
                "surveyed_commit": "46a78c958bba5c1eb819b3213a6409f81ee7ab22",
                "gaps": [
                    {"id": "phase13-devres-arch-phys-wc-token-planner"},
                    {"id": "phase13-devres-live-scatterlist-ownership"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / SLICE_PATH,
        "\n".join(
            [
                "# Phase 13 devres Slice",
                "- keep the `devm_iounmap()` pointer match exact",
            ]
        )
        + "\n",
    )
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 13 devres Survey",
                "- `PHASE13_SLICE=devres-helper-mmio-safety-survey`",
                "- reviewed against live `master` `46a78c958bba5c1eb819b3213a6409f81ee7ab22`",
                "- `devm_iounmap()` stays helper-first",
                "- `devm_arch_phys_wc_add()` remains helper-first",
                "- keep the helper-only DMA/scatterlist boundary explicit",
                "- older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift",
            ]
        )
        + "\n",
    )
    write_text(
        root / HELPER_PATH,
        "\n".join(
            [
                "pub const ModuleDescriptor = struct {",
                "    provides_iounmap_call_planning: bool,",
                "};",
                ".provides_iounmap_call_planning = true",
                "pub const ManagedIounmapPlan = struct {",
                "    warns_on_release_miss: bool,",
                "};",
                "pub fn ioremapReleaseMatches(",
                "pub fn planManagedIounmap(",
                "    .warns_on_release_miss = !release_matches",
            ]
        )
        + "\n",
    )
    write_text(
        root / REPLAY_PATH,
        "\n".join(
            [
                'test "phase13 devres manifest records the current helper packet" {',
                '  try expectContains(manifest_text, "\\"lane_key\\": \\"P13-L01\\"");',
                '  try expectContains(manifest_text, "\\"surveyed_commit\\": \\"46a78c958bba5c1eb819b3213a6409f81ee7ab22\\"");',
                "}",
                'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
                "  const exact = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4000);",
                "  const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);",
                "  try std.testing.expect(miss.warns_on_release_miss);",
                "}",
            ]
        )
        + "\n",
    )


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise SystemExit(f"phase13-devres-alignment-self-test:{label}:got={got_text}:want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_alignment_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(root / SURVEY_PATH, STALE_SLICE_MARKER + "\n")
        assert_only(
            validate(root),
            [
                "survey:surveyed_commit_mismatch:46a78c958bba5c1eb819b3213a6409f81ee7ab22",
                "survey:stale_slice_label",
                "survey:missing_marker:devm_arch_phys_wc_add()",
                "survey:missing_marker:helper-only DMA/scatterlist boundary",
                "survey:missing_stale_checker_warning",
                "survey:missing_marker:devm_iounmap()",
            ],
            "stale_slice_label_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            'try expectContains(manifest_text, "\\"lane_key\\": \\"P13-L05\\"");\n'
            'try expectContains(manifest_text, "\\"surveyed_commit\\": \\"46a78c958bba5c1eb819b3213a6409f81ee7ab22\\"");\n'
            'test "phase13 devres plans a managed iounmap call and warns on release misses" {\n'
            "  const exact = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4000);\n"
            "  const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);\n"
            "  try std.testing.expect(miss.warns_on_release_miss);\n"
            "}\n",
        )
        assert_only(validate(root), ["replay:lane_key_mismatch:P13-L01"], "lane_key_mismatch_failed")
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            'try expectContains(manifest_text, "\\"lane_key\\": \\"P13-L01\\"");\n'
            'try expectContains(manifest_text, "\\"surveyed_commit\\": \\"10369315cba5d146a7c6c4c6480ef9d279dc490f\\"");\n'
            'test "phase13 devres plans a managed iounmap call and warns on release misses" {\n'
            "  const exact = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4000);\n"
            "  const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);\n"
            "  try std.testing.expect(miss.warns_on_release_miss);\n"
            "}\n",
        )
        assert_only(
            validate(root),
            ["replay:surveyed_commit_mismatch:46a78c958bba5c1eb819b3213a6409f81ee7ab22"],
            "surveyed_commit_mismatch_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SLICE_PATH,
            "# Phase 13 devres Slice\n- helper-only token planner\n",
        )
        assert_only(
            validate(root),
            ["slice:missing_marker:devm_iounmap()"],
            "slice_iounmap_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(
                [
                    "pub const ModuleDescriptor = struct {",
                    "    provides_iounmap_call_planning: bool,",
                    "};",
                    ".provides_iounmap_call_planning = true",
                    "pub const ManagedIounmapPlan = struct {",
                    "    warns_on_release_miss: bool,",
                    "};",
                    "pub fn ioremapReleaseMatches(",
                    "    .warns_on_release_miss = !release_matches",
                ]
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:pub fn planManagedIounmap("],
            "helper_iounmap_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            "\n".join(
                [
                    'test "phase13 devres manifest records the current helper packet" {',
                    '  try expectContains(manifest_text, "\\"lane_key\\": \\"P13-L01\\"");',
                    '  try expectContains(manifest_text, "\\"surveyed_commit\\": \\"46a78c958bba5c1eb819b3213a6409f81ee7ab22\\"");',
                    "}",
                    'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
                    "  const exact = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4000);",
                    "  try std.testing.expect(exact.release_matches);",
                    "}",
                ]
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "replay:missing_marker:const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);",
                "replay:missing_marker:try std.testing.expect(miss.warns_on_release_miss);",
            ],
            "replay_iounmap_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SURVEY_PATH,
            "\n".join(
                [
                    "# Phase 13 devres Survey",
                    "- `PHASE13_SLICE=devres-helper-mmio-safety-survey`",
                    "- reviewed against live `master` `46a78c958bba5c1eb819b3213a6409f81ee7ab22`",
                    "- `devm_arch_phys_wc_add()` remains helper-first",
                    "- keep the helper-only DMA/scatterlist boundary explicit",
                    "- older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift",
                ]
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["survey:missing_marker:devm_iounmap()"],
            "survey_iounmap_marker_failed",
        )
        case_count += 1

    print(f"PHASE13_DEVRES_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 devres survey packet stays aligned with its manifest-backed replay."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE13_DEVRES_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
