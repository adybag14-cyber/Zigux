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
REVIEWABILITY_PATH = "zigux/tests/phase13_devres_reviewability.zig"
BOUNDARY_REPLAY_PATH = "zigux/tests/phase13_devres_boundary_evidence.zig"
DMA_REPLAY_PATH = "zigux/tests/phase13_devres_dma_coherent.zig"

EXPECTED_LANE = "P13-L01"
EXPECTED_COMMIT = "master-readback-2026-05-14"
EXPECTED_GAP_COUNT = 17
EXPECTED_STARTER_COUNT = 11
EXPECTED_BLOCKED_COUNT = 6

EXPECTED_GAPS = {
    "phase13-make-target": "starter_landed",
    "phase13-devres-helper-starter": "starter_landed",
    "phase13-devres-slice-note": "starter_landed",
    "phase13-devres-survey-note": "starter_landed",
    "phase13-devres-test-gate": "starter_landed",
    "phase13-devres-reviewability-gate": "starter_landed",
    "phase13-devres-boundary-evidence-gate": "starter_landed",
    "phase13-devres-iounmap-planner": "starter_landed",
    "phase13-devres-of-iomap-planner": "starter_landed",
    "phase13-devres-arch-io-wc-memtype-planner": "starter_landed",
    "phase13-devres-arch-phys-wc-token-planner": "starter_landed",
    "phase13-devres-live-mmio-mappings": "blocked_on_live_mmio_state",
    "phase13-devres-live-region-reservation": "blocked_on_live_mmio_state",
    "phase13-devres-live-release-region-mutation": "blocked_on_live_mmio_state",
    "phase13-devres-live-device-tree-walk": "blocked_on_live_device_tree_state",
    "phase13-devres-live-arch-memtype-state": "blocked_on_live_arch_memtype_state",
    "phase13-devres-live-scatterlist-ownership": "blocked_on_live_scatterlist_state",
}

SLICE_MARKERS = [
    "devm_iounmap()",
    "devm_ioremap_uc()",
    "devm_ioremap_wc()",
    "devm_ioremap_np()",
    "devm_of_iomap()",
    "devm_arch_io_reserve_memtype_wc()",
    "devm_arch_phys_wc_add()",
]

SURVEY_MARKERS = [
    EXPECTED_COMMIT,
    f"`{EXPECTED_LANE}`",
    "devm_ioremap_np()",
    "devm_iounmap()",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "direct boundary-evidence replay",
    "phase13-devres-live-region-reservation",
    "phase13-devres-live-release-region-mutation",
    "phase13-devres-live-device-tree-walk",
    "phase13-devres-live-arch-memtype-state",
    "helper-only DMA/scatterlist boundary",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
]

HELPER_MARKERS = [
    ".provides_iounmap_call_planning = true",
    ".provides_ioremap_np_wrapper_planning = true",
    "pub const ManagedIounmapPlan",
    "pub fn planManagedIounmap(",
    ".warns_on_release_miss = !release_matches",
    "pub fn planManagedIoremapAcquireNp(",
    "pub fn planManagedIoremapResource(",
    ".requests_region = true",
    ".releases_region_on_remap_failure = true",
    "pub fn planDeviceTreeIomap(",
    "pub fn planArchIoReserveMemtypeWc(",
    "pub fn planArchPhysWcAdd(",
]

REPLAY_MARKERS = [
    'phase13 devres release matching stays pointer-exact',
    'phase13 devres plans a managed iounmap call and warns on release misses',
    'phase13 devres non-posted ioremap wrapper forces the NP lifetime path',
    'phase13 devres non-posted ioremap wrapper frees the release record on map failure',
    'planManagedIounmap(0x4000, 0x4000)',
    'planManagedIounmap(0x4000, 0x4010)',
    'miss.warns_on_release_miss',
]

REVIEWABILITY_MARKERS = [
    EXPECTED_COMMIT,
    'preexisting_phase13_devres_boundary_evidence_present',
    'try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_boundary_evidence_present);',
    'preexisting_phase13_devres_dma_coherent_present',
    'try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_dma_coherent_present);',
    'const direct_replay = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "zigux/tests/phase13_devres.zig", std.testing.allocator, .limited(40 * 1024));',
    'try std.testing.expect(descriptor.provides_ioremap_plain_wrapper_planning);',
    'try std.testing.expect(descriptor.provides_ioremap_np_wrapper_planning);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "devm_ioremap_np()") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, direct_replay, "phase13 devres non-posted ioremap wrapper forces the NP lifetime path") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, direct_replay, "phase13 devres non-posted ioremap wrapper frees the release record on map failure") != null);',
    '"phase13-devres-boundary-evidence-gate"',
    'try expectGap(manifest, "phase13-devres-slice-note", "starter_landed", "Documentation/zigux/phase13-devres-slice.md", "`devm_ioremap_np()`");',
    'try expectGap(manifest, "phase13-devres-test-gate", "starter_landed", "zigux/tests/phase13_devres.zig", "`devm_iounmap()` planner");',
    'try expectGap(manifest, "phase13-devres-test-gate", "starter_landed", "zigux/tests/phase13_devres.zig", "`devm_ioremap_np()`");',
    'try std.testing.expect(std.mem.indexOf(u8, direct_replay, "phase13 devres plans a managed iounmap call and warns on release misses") != null);',
    'try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);',
    'try std.testing.expectEqual(@as(usize, 11), starter_landed_count);',
    'try std.testing.expectEqual(@as(usize, 6), blocked_count);',
]

BOUNDARY_REPLAY_MARKERS = [
    'phase13 devres boundary evidence keeps the manifest-backed blocked surfaces explicit',
    'phase13-devres-boundary-evidence-gate',
    'live release-region mutation',
    'live device-tree walking',
    'live arch memtype state transitions',
    'phase13 devres planners keep blocked arch memtype boundaries in detach-bookkeeping form',
]

DMA_REPLAY_MARKERS = [
    '"preexisting_phase13_devres_dma_coherent_present": true',
    '"phase13-devres-live-scatterlist-ownership"',
    '"blocked_on_live_scatterlist_state"',
    'adjacent coherent-DMA evidence shard',
    'helper-only DMA/scatterlist boundary',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def require_file(root: Path, rel: str, errors: list[str]) -> Path | None:
    path = root / rel
    if not path.is_file():
        errors.append(f'missing:{rel}')
        return None
    return path


def require_markers(source: str, prefix: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f'{prefix}:missing_marker:{marker}')


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = require_file(root, MANIFEST_PATH, errors)
    slice_path = require_file(root, SLICE_PATH, errors)
    survey_path = require_file(root, SURVEY_PATH, errors)
    helper_path = require_file(root, HELPER_PATH, errors)
    replay_path = require_file(root, REPLAY_PATH, errors)
    reviewability_path = require_file(root, REVIEWABILITY_PATH, errors)
    boundary_replay_path = require_file(root, BOUNDARY_REPLAY_PATH, errors)
    dma_replay_path = require_file(root, DMA_REPLAY_PATH, errors)
    if errors:
        return errors

    manifest_text = read_text(manifest_path)
    slice_text = read_text(slice_path)
    survey_text = read_text(survey_path)
    helper_text = read_text(helper_path)
    replay_text = read_text(replay_path)
    reviewability_text = read_text(reviewability_path)
    boundary_replay_text = read_text(boundary_replay_path)
    dma_replay_text = read_text(dma_replay_path)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f'manifest:json_decode:{exc.msg}']

    if manifest.get('lane_key') != EXPECTED_LANE:
        errors.append(f"manifest:lane_key_mismatch:{manifest.get('lane_key')}")
    if manifest.get('surveyed_commit') != EXPECTED_COMMIT:
        errors.append(f"manifest:surveyed_commit_mismatch:{manifest.get('surveyed_commit')}")

    gaps = manifest.get('gaps')
    if not isinstance(gaps, list):
        errors.append('manifest:gaps_missing')
        gaps = []
    if len(gaps) != EXPECTED_GAP_COUNT:
        errors.append(f'manifest:gaps_count_mismatch:{len(gaps)}')

    seen_gaps = {gap.get('id'): gap.get('status') for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        if seen_gaps.get(gap_id) != status:
            errors.append(f'manifest:gap_status_mismatch:{gap_id}:{seen_gaps.get(gap_id)}')

    starter_count = sum(1 for value in seen_gaps.values() if value == 'starter_landed')
    blocked_count = len(seen_gaps) - starter_count
    if starter_count != EXPECTED_STARTER_COUNT:
        errors.append(f'manifest:starter_count_mismatch:{starter_count}')
    if blocked_count != EXPECTED_BLOCKED_COUNT:
        errors.append(f'manifest:blocked_count_mismatch:{blocked_count}')

    require_markers(slice_text, 'slice', SLICE_MARKERS, errors)
    require_markers(survey_text, 'survey', SURVEY_MARKERS, errors)
    require_markers(helper_text, 'helper', HELPER_MARKERS, errors)
    require_markers(replay_text, 'replay', REPLAY_MARKERS, errors)
    require_markers(reviewability_text, 'reviewability', REVIEWABILITY_MARKERS, errors)
    require_markers(boundary_replay_text, 'boundary_replay', BOUNDARY_REPLAY_MARKERS, errors)
    require_markers(dma_replay_text, 'dma_replay', DMA_REPLAY_MARKERS, errors)
    return errors


def render_manifest_fixture() -> str:
    fixture = {
        'lane_key': EXPECTED_LANE,
        'surveyed_commit': EXPECTED_COMMIT,
        'gaps': [
            {'id': gap_id, 'status': status}
            for gap_id, status in EXPECTED_GAPS.items()
        ],
    }
    return json.dumps(fixture, indent=2) + '\n'


def seed_fixture_tree(root: Path) -> None:
    write_text(root / MANIFEST_PATH, render_manifest_fixture())
    write_text(root / SLICE_PATH, '\n'.join(SLICE_MARKERS) + '\n')
    write_text(root / SURVEY_PATH, '\n'.join(SURVEY_MARKERS) + '\n')
    write_text(root / HELPER_PATH, '\n'.join(HELPER_MARKERS) + '\n')
    write_text(root / REPLAY_PATH, '\n'.join(REPLAY_MARKERS) + '\n')
    write_text(root / REVIEWABILITY_PATH, '\n'.join(REVIEWABILITY_MARKERS) + '\n')
    write_text(root / BOUNDARY_REPLAY_PATH, '\n'.join(BOUNDARY_REPLAY_MARKERS) + '\n')
    write_text(root / DMA_REPLAY_PATH, '\n'.join(DMA_REPLAY_MARKERS) + '\n')


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}:expected={expected}:actual={actual}')


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix='zigux_phase13_devres_alignment_') as temp_dir:
        root = Path(temp_dir)
        seed_fixture_tree(root)
        assert_only(validate(root), [], 'baseline_failed')
        case_count += 1

        seed_fixture_tree(root)
        (root / BOUNDARY_REPLAY_PATH).unlink()
        assert_only(validate(root), [f'missing:{BOUNDARY_REPLAY_PATH}'], 'missing_boundary_replay_failed')
        case_count += 1

        seed_fixture_tree(root)
        (root / REPLAY_PATH).unlink()
        assert_only(validate(root), [f'missing:{REPLAY_PATH}'], 'missing_direct_replay_failed')
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest['gaps'] = manifest['gaps'][:-1]
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + '\n')
        assert_only(validate(root), [
            'manifest:gaps_count_mismatch:16',
            'manifest:gap_status_mismatch:phase13-devres-live-scatterlist-ownership:None',
            'manifest:blocked_count_mismatch:5',
        ], 'manifest_gap_count_failed')
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, 'broken\n')
        missing = validate(root)
        expected = [f'survey:missing_marker:{marker}' for marker in SURVEY_MARKERS]
        assert_only(missing, expected, 'survey_missing_markers_failed')
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SLICE_PATH,
            '\n'.join(
                marker
                for marker in SLICE_MARKERS
                if marker != 'devm_ioremap_np()'
            ) + '\n',
        )
        assert_only(
            validate(root),
            ['slice:missing_marker:devm_ioremap_np()'],
            'slice_missing_np_wrapper_marker_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            '\n'.join(
                marker
                for marker in HELPER_MARKERS
                if marker != 'pub fn planManagedIoremapAcquireNp('
            ) + '\n',
        )
        assert_only(
            validate(root),
            ['helper:missing_marker:pub fn planManagedIoremapAcquireNp('],
            'helper_missing_np_wrapper_marker_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            '\n'.join(
                marker
                for marker in HELPER_MARKERS
                if marker != '.releases_region_on_remap_failure = true'
            ) + '\n',
        )
        assert_only(
            validate(root),
            ['helper:missing_marker:.releases_region_on_remap_failure = true'],
            'helper_missing_marker_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            '\n'.join(
                marker
                for marker in REPLAY_MARKERS
                if marker != 'phase13 devres non-posted ioremap wrapper forces the NP lifetime path'
            ) + '\n',
        )
        assert_only(
            validate(root),
            ['replay:missing_marker:phase13 devres non-posted ioremap wrapper forces the NP lifetime path'],
            'replay_missing_np_wrapper_marker_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            '\n'.join(
                marker
                for marker in REPLAY_MARKERS
                if marker != 'miss.warns_on_release_miss'
            ) + '\n',
        )
        assert_only(
            validate(root),
            ['replay:missing_marker:miss.warns_on_release_miss'],
            'replay_missing_release_miss_marker_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REVIEWABILITY_PATH,
            '\n'.join(
                marker
                for marker in REVIEWABILITY_MARKERS
                if marker != 'try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_boundary_evidence_present);'
            ) + '\n',
        )
        assert_only(
            validate(root),
            [
                'reviewability:missing_marker:try std.testing.expect(manifest.survey_summary.preexisting_phase13_devres_boundary_evidence_present);'
            ],
            'reviewability_missing_boundary_summary_assertion_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REVIEWABILITY_PATH,
            '\n'.join(
                marker
                for marker in REVIEWABILITY_MARKERS
                if marker != 'try expectGap(manifest, "phase13-devres-test-gate", "starter_landed", "zigux/tests/phase13_devres.zig", "`devm_ioremap_np()`");'
            ) + '\n',
        )
        assert_only(
            validate(root),
            [
                'reviewability:missing_marker:try expectGap(manifest, "phase13-devres-test-gate", "starter_landed", "zigux/tests/phase13_devres.zig", "`devm_ioremap_np()`");'
            ],
            'reviewability_missing_np_gap_assertion_failed',
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REVIEWABILITY_PATH,
            '\n'.join(
                marker
                for marker in REVIEWABILITY_MARKERS
                if marker != 'try expectGap(manifest, "phase13-devres-test-gate", "starter_landed", "zigux/tests/phase13_devres.zig", "`devm_iounmap()` planner");'
            ) + '\n',
        )
        assert_only(
            validate(root),
            [
                'reviewability:missing_marker:try expectGap(manifest, "phase13-devres-test-gate", "starter_landed", "zigux/tests/phase13_devres.zig", "`devm_iounmap()` planner");'
            ],
            'reviewability_missing_direct_replay_gap_assertion_failed',
        )
        case_count += 1

    print('PHASE13_DEVRES_ALIGNMENT_SELF_TEST=pass')
    print(f'PHASE13_DEVRES_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Check that the Phase 13 devres survey packet stays aligned with its current manifest-backed replay.')
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root to validate.')
    parser.add_argument('--self-test', action='store_true', help='Run checker self-tests.')
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print('PHASE13_DEVRES_ALIGNMENT=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
