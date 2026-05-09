#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "lib/devres.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "scripts/zigux/validate-phase13-release.py",
    "zigux/Makefile",
]

SLICE_MARKERS = [
    "devm_arch_phys_wc_add()",
    "devm_ioremap_np()",
    "keep the `devm_iounmap()` and `devm_ioport_unmap()` pointer matches exact",
    "device-tree walking",
    "live ioport mappings or broader ioport-helper ownership",
    "live arch memtype reservation or removal side effects",
]

SURVEY_MARKERS = [
    "phase13-devres-arch-phys-wc-token-planner",
    "blocked `phase13-devres-live-mmio-side-effects`",
    "blocked `phase13-devres-live-dma-backed-helpers`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-device-tree-walk`",
    "blocked `phase13-devres-live-arch-memtype-state`",
    "helper-only DMA/scatterlist boundary",
    "keeps `devm_iounmap()` and `devm_ioport_unmap()` pointer matching exact",
    "devm_ioremap_uc()",
    "devm_ioremap_wc()",
    "devm_ioremap_np()",
    "devm_ioport_unmap()",
    "devm_ioremap_resource_wc()",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
]

BUILD_MARKERS = [
    'b.path("../../lib/devres.zig")',
    'b.path("phase13_devres.zig")',
    'b.path("phase13_devres_reviewability.zig")',
    'b.path("phase13_devres_dma_coherent.zig")',
    'b.path("phase13_devres_boundary_evidence.zig")',
    "const phase13_devres_tests = b.addTest(.{",
    "const phase13_devres_reviewability_tests = b.addTest(.{",
    "const phase13_devres_dma_coherent_tests = b.addTest(.{",
    "const phase13_devres_boundary_evidence_tests = b.addTest(.{",
    "test_step.dependOn(&run_phase13_devres_tests.step);",
    "test_step.dependOn(&run_phase13_devres_reviewability_tests.step);",
    "test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
    "test_step.dependOn(&run_phase13_devres_boundary_evidence_tests.step);",
]

DMA_REVIEWABILITY_MARKERS = [
    'test \\\"phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership\\\"',
    'test \\\"phase13 devres coherent-dma boundary note keeps dma-backed helpers and scatter-gather ownership out of scope\\\"',
    '\\\"preexisting_phase13_devres_test_present\\\": true',
    '\\\"preexisting_phase13_devres_reviewability_present\\\": true',
    '\\\"preexisting_phase13_devres_survey_present\\\": true',
    '\\\"id\\\": \\\"phase13-devres-live-dma-backed-helpers\\\"',
    '\\\"id\\\": \\\"phase13-devres-live-scatterlist-ownership\\\"',
    '\\\"status\\\": \\\"blocked_on_dma_state\\\"',
    '\\\"status\\\": \\\"blocked_on_scatterlist_state\\\"',
]

BOUNDARY_EVIDENCE_MARKERS = [
    'test "phase13 devres boundary evidence keeps dma and scatterlist blockers aligned" {',
    'const boundary_gate = findGap(manifest.gaps, "phase13-devres-boundary-evidence-gate") orelse return error.MissingBoundaryGate;',
    'try std.testing.expectEqualStrings("zigux/tests/phase13_devres_boundary_evidence.zig", boundary_gate.zigux_destination);',
    'try expectContains(boundary_gate.why_now, "manifest, slice note, and survey note");',
    'const dma_block = findGap(manifest.gaps, "phase13-devres-live-dma-backed-helpers") orelse return error.MissingDmaBlock;',
    'const scatterlist_block = findGap(manifest.gaps, "phase13-devres-live-scatterlist-ownership") orelse return error.MissingScatterlistBlock;',
    'try expectContains(survey_note, "zigux/tests/phase13_devres_boundary_evidence.zig");',
    'try expectContains(survey_note, "exact boundary evidence");',
]

MAKE_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet.py",
]

RELEASE_MARKERS = [
    '"zigux/tests/phase13_devres.zig",',
    '"zigux/tests/phase13_devres_manifest.json",',
]

DEVRES_HELPER_MARKERS = [
    "fail_pretty_name_allocation: bool = false,",
    "provides_ioport_unmap_call_planning = true,",
    "pub fn ioremapReleaseMatches(tracked_address: usize, candidate_address: usize) bool {",
    "return tracked_address == candidate_address;",
    "pub fn planManagedIoportUnmap(tracked_address: usize, candidate_address: usize) ManagedIoportUnmapPlan {",
    "const reported_size = if (input.report_size) translated_size else null;",
    ".fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
]

DEVRES_TEST_MARKERS = [
    'test "phase13 devres uncached ioremap wrapper preserves the managed lifetime path" {',
    'test "phase13 devres write-combined ioremap wrapper forces the WC lifetime path" {',
    'test "phase13 devres write-combined ioremap wrapper frees the release record on map failure" {',
    'test "phase13 devres release matching stays pointer-exact" {',
    "try std.testing.expect(devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4000));",
    'test "phase13 devres WC resource wrapper preserves the requested WC mapping type" {',
    'test "phase13 devres propagates pretty-name allocation failure through devm_of_iomap planning" {',
    "try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);",
    "try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);",
    "try std.testing.expectEqual(@as(?u64, 0x10), failure.reported_size);",
    "try std.testing.expect(!failure.requests_region);",
    "try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);",
]

MANIFEST_EXPECTED_LANE_KEY = "P13-L10"
MANIFEST_EXPECTED_SURVEYED_COMMIT = "032c57dbde9a95ad6e28ad891cca54bd2e3bfcf1"
MANIFEST_SUMMARY_KEYS = [
    "preexisting_phase13_devres_test_present",
    "preexisting_phase13_devres_reviewability_present",
    "preexisting_phase13_devres_dma_coherent_present",
    "preexisting_phase13_devres_boundary_evidence_present",
    "preexisting_phase13_devres_survey_present",
]

MANIFEST_GAP_STATUS_EXPECTATIONS = {
    "phase13-devres-boundary-evidence-gate": "starter_landed",
    "phase13-devres-live-mmio-side-effects": "blocked_on_live_mmio_state",
    "phase13-devres-live-dma-backed-helpers": "blocked_on_dma_state",
    "phase13-devres-live-scatterlist-ownership": "blocked_on_scatterlist_state",
    "phase13-devres-live-device-tree-walk": "blocked_on_device_tree_state",
    "phase13-devres-live-arch-memtype-state": "blocked_on_arch_memtype_state",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_manifest(text: str) -> list[str]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"phase13-devres-manifest:json:{exc.msg}"]

    issues: list[str] = []
    if manifest.get("lane_key") != MANIFEST_EXPECTED_LANE_KEY:
        issues.append("phase13-devres-manifest-lane-key")
    if manifest.get("surveyed_commit") != MANIFEST_EXPECTED_SURVEYED_COMMIT:
        issues.append("phase13-devres-manifest-surveyed-commit")

    summary = manifest.get("survey_summary", {})
    for key in MANIFEST_SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase13-devres-manifest-summary:{key}")

    statuses = {
        gap.get("id"): gap.get("status")
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_status in MANIFEST_GAP_STATUS_EXPECTATIONS.items():
        if gap_id not in statuses:
            issues.append(f"phase13-devres-manifest-gap:{gap_id}")
        elif statuses[gap_id] != expected_status:
            issues.append(f"phase13-devres-manifest-gap-status:{gap_id}")
    return issues


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    checks = [
        ("Documentation/zigux/phase13-devres-slice.md", SLICE_MARKERS, "phase13-devres-slice"),
        ("Documentation/zigux/phase13-devres-survey.md", SURVEY_MARKERS, "phase13-devres-survey"),
        ("lib/devres.zig", DEVRES_HELPER_MARKERS, "devres-helper"),
        ("zigux/tests/phase13_build.zig", BUILD_MARKERS, "phase13-build"),
        ("zigux/tests/phase13_devres.zig", DEVRES_TEST_MARKERS, "phase13-devres-test"),
        ("zigux/tests/phase13_devres_dma_coherent.zig", DMA_REVIEWABILITY_MARKERS, "phase13-devres-dma-coherent"),
        ("zigux/tests/phase13_devres_boundary_evidence.zig", BOUNDARY_EVIDENCE_MARKERS, "phase13-devres-boundary-evidence"),
        ("zigux/Makefile", MAKE_MARKERS, "makefile"),
        ("scripts/zigux/validate-phase13-release.py", RELEASE_MARKERS, "phase13-release-validator"),
    ]

    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))

    issues.extend(validate_manifest(read_text(root / "zigux/tests/phase13_devres_manifest.json")))
    return issues


def seed_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "// stub\n")

    writes = {
        "Documentation/zigux/phase13-devres-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase13-devres-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "lib/devres.zig": "\n".join(DEVRES_HELPER_MARKERS) + "\n",
        "zigux/tests/phase13_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase13_devres.zig": "\n".join(DEVRES_TEST_MARKERS) + "\n",
        "zigux/tests/phase13_devres_dma_coherent.zig": "\n".join(DMA_REVIEWABILITY_MARKERS) + "\n",
        "zigux/tests/phase13_devres_boundary_evidence.zig": "\n".join(BOUNDARY_EVIDENCE_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "scripts/zigux/validate-phase13-release.py": "\n".join(RELEASE_MARKERS) + "\n",
        "zigux/tests/phase13_devres_manifest.json": json.dumps(
            {
                "lane_key": MANIFEST_EXPECTED_LANE_KEY,
                "surveyed_commit": MANIFEST_EXPECTED_SURVEYED_COMMIT,
                "survey_summary": {key: True for key in MANIFEST_SUMMARY_KEYS},
                "gaps": [
                    {"id": gap_id, "status": status}
                    for gap_id, status in MANIFEST_GAP_STATUS_EXPECTATIONS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    }
    for rel, text in writes.items():
        write_text(root / rel, text)


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise SystemExit(f"phase13-devres-packet-self-test:{label}:got={got_text}:want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-devres-slice.md", "devm_arch_phys_wc_add()\n")
        assert_only(
            validate(root),
            [
                "phase13-devres-slice:devm_ioremap_np()",
                "phase13-devres-slice:keep the `devm_iounmap()` and `devm_ioport_unmap()` pointer matches exact",
                "phase13-devres-slice:device-tree walking",
                "phase13-devres-slice:live ioport mappings or broader ioport-helper ownership",
                "phase13-devres-slice:live arch memtype reservation or removal side effects",
            ],
            "slice_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-devres-survey.md", "phase13-devres-arch-phys-wc-token-planner\n")
        assert_only(
            validate(root),
            [
                "phase13-devres-survey:blocked `phase13-devres-live-mmio-side-effects`",
                "phase13-devres-survey:blocked `phase13-devres-live-dma-backed-helpers`",
                "phase13-devres-survey:blocked `phase13-devres-live-scatterlist-ownership`",
                "phase13-devres-survey:blocked `phase13-devres-live-device-tree-walk`",
                "phase13-devres-survey:blocked `phase13-devres-live-arch-memtype-state`",
                "phase13-devres-survey:helper-only DMA/scatterlist boundary",
                "phase13-devres-survey:keeps `devm_iounmap()` and `devm_ioport_unmap()` pointer matching exact",
                "phase13-devres-survey:devm_ioremap_uc()",
                "phase13-devres-survey:devm_ioremap_wc()",
                "phase13-devres-survey:devm_ioremap_np()",
                "phase13-devres-survey:devm_ioport_unmap()",
                "phase13-devres-survey:devm_ioremap_resource_wc()",
                "phase13-devres-survey:zigux/tests/phase13_devres_boundary_evidence.zig",
            ],
            "survey_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "lib/devres.zig", "fail_pretty_name_allocation: bool = false,\n")
        assert_only(
            validate(root),
            [
                "devres-helper:provides_ioport_unmap_call_planning = true,",
                "devres-helper:pub fn ioremapReleaseMatches(tracked_address: usize, candidate_address: usize) bool {",
                "devres-helper:return tracked_address == candidate_address;",
                "devres-helper:pub fn planManagedIoportUnmap(tracked_address: usize, candidate_address: usize) ManagedIoportUnmapPlan {",
                "devres-helper:const reported_size = if (input.report_size) translated_size else null;",
                "devres-helper:.fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
            ],
            "devres_helper_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_build.zig", 'b.path("phase13_devres.zig")\n')
        assert_only(
            validate(root),
            [
                'phase13-build:b.path("../../lib/devres.zig")',
                'phase13-build:b.path("phase13_devres_reviewability.zig")',
                'phase13-build:b.path("phase13_devres_dma_coherent.zig")',
                'phase13-build:b.path("phase13_devres_boundary_evidence.zig")',
                "phase13-build:const phase13_devres_tests = b.addTest(.{",
                "phase13-build:const phase13_devres_reviewability_tests = b.addTest(.{",
                "phase13-build:const phase13_devres_dma_coherent_tests = b.addTest(.{",
                "phase13-build:const phase13_devres_boundary_evidence_tests = b.addTest(.{",
                "phase13-build:test_step.dependOn(&run_phase13_devres_tests.step);",
                "phase13-build:test_step.dependOn(&run_phase13_devres_reviewability_tests.step);",
                "phase13-build:test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
                "phase13-build:test_step.dependOn(&run_phase13_devres_boundary_evidence_tests.step);",
            ],
            "build_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_devres.zig",
            'test "phase13 devres propagates pretty-name allocation failure through devm_of_iomap planning" {\n}\n',
        )
        assert_only(
            validate(root),
            [
                'phase13-devres-test:test "phase13 devres uncached ioremap wrapper preserves the managed lifetime path" {',
                'phase13-devres-test:test "phase13 devres write-combined ioremap wrapper forces the WC lifetime path" {',
                'phase13-devres-test:test "phase13 devres write-combined ioremap wrapper frees the release record on map failure" {',
                'phase13-devres-test:test "phase13 devres release matching stays pointer-exact" {',
                "phase13-devres-test:try std.testing.expect(devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4000));",
                'phase13-devres-test:test "phase13 devres WC resource wrapper preserves the requested WC mapping type" {',
                "phase13-devres-test:try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);",
                "phase13-devres-test:try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);",
                "phase13-devres-test:try std.testing.expectEqual(@as(?u64, 0x10), failure.reported_size);",
                "phase13-devres-test:try std.testing.expect(!failure.requests_region);",
                "phase13-devres-test:try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);",
            ],
            "devres_test_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/tests/phase13_devres_manifest.json", json.dumps({"survey_summary": {}}, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "phase13-devres-manifest-lane-key",
                "phase13-devres-manifest-surveyed-commit",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_test_present",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_reviewability_present",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_dma_coherent_present",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_boundary_evidence_present",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_survey_present",
                "phase13-devres-manifest-gap:phase13-devres-boundary-evidence-gate",
                "phase13-devres-manifest-gap:phase13-devres-live-mmio-side-effects",
                "phase13-devres-manifest-gap:phase13-devres-live-dma-backed-helpers",
                "phase13-devres-manifest-gap:phase13-devres-live-scatterlist-ownership",
                "phase13-devres-manifest-gap:phase13-devres-live-device-tree-walk",
                "phase13-devres-manifest-gap:phase13-devres-live-arch-memtype-state",
            ],
            "manifest_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_devres_manifest.json",
            json.dumps(
                {
                    "lane_key": "P13-L11",
                    "surveyed_commit": "7a4454d0474106972cad7e164b79293bd54a40c6",
                    "survey_summary": {key: True for key in MANIFEST_SUMMARY_KEYS},
                    "gaps": [
                        {"id": gap_id, "status": status}
                        for gap_id, status in MANIFEST_GAP_STATUS_EXPECTATIONS.items()
                    ],
                },
                indent=2,
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "phase13-devres-manifest-lane-key",
                "phase13-devres-manifest-surveyed-commit",
            ],
            "manifest_metadata_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_devres_dma_coherent.zig",
            'test "phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership" {}\n',
        )
        assert_only(
            validate(root),
            [
                'phase13-devres-dma-coherent:test \\\"phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership\\\"',
                'phase13-devres-dma-coherent:test \\\"phase13 devres coherent-dma boundary note keeps dma-backed helpers and scatter-gather ownership out of scope\\\"',
                'phase13-devres-dma-coherent:\\\"preexisting_phase13_devres_test_present\\\": true',
                'phase13-devres-dma-coherent:\\\"preexisting_phase13_devres_reviewability_present\\\": true',
                'phase13-devres-dma-coherent:\\\"preexisting_phase13_devres_survey_present\\\": true',
                'phase13-devres-dma-coherent:\\\"id\\\": \\\"phase13-devres-live-dma-backed-helpers\\\"',
                'phase13-devres-dma-coherent:\\\"id\\\": \\\"phase13-devres-live-scatterlist-ownership\\\"',
                'phase13-devres-dma-coherent:\\\"status\\\": \\\"blocked_on_dma_state\\\"',
                'phase13-devres-dma-coherent:\\\"status\\\": \\\"blocked_on_scatterlist_state\\\"',
            ],
            "dma_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_devres_boundary_evidence.zig",
            'test "phase13 devres boundary evidence keeps dma and scatterlist blockers aligned" {}\n',
        )
        assert_only(
            validate(root),
            [
                'phase13-devres-boundary-evidence:const boundary_gate = findGap(manifest.gaps, "phase13-devres-boundary-evidence-gate") orelse return error.MissingBoundaryGate;',
                'phase13-devres-boundary-evidence:try std.testing.expectEqualStrings("zigux/tests/phase13_devres_boundary_evidence.zig", boundary_gate.zigux_destination);',
                'phase13-devres-boundary-evidence:try expectContains(boundary_gate.why_now, "manifest, slice note, and survey note");',
                'phase13-devres-boundary-evidence:const dma_block = findGap(manifest.gaps, "phase13-devres-live-dma-backed-helpers") orelse return error.MissingDmaBlock;',
                'phase13-devres-boundary-evidence:const scatterlist_block = findGap(manifest.gaps, "phase13-devres-live-scatterlist-ownership") orelse return error.MissingScatterlistBlock;',
                'phase13-devres-boundary-evidence:try expectContains(survey_note, "zigux/tests/phase13_devres_boundary_evidence.zig");',
                'phase13-devres-boundary-evidence:try expectContains(survey_note, "exact boundary evidence");',
            ],
            "boundary_evidence_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase13_devres_boundary_evidence.zig").unlink()
        assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_devres_boundary_evidence.zig"],
            "required_file_guard_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_PACKET=pass")
    print(f"PHASE13_DEVRES_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shipped Phase 13 devres packet surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(f"PHASE13_DEVRES_PACKET_ISSUE={issue}")
        return 1

    print("PHASE13_DEVRES_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
