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
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "scripts/zigux/validate-phase13-release.py",
    "zigux/Makefile",
]

SLICE_MARKERS = [
    "devm_arch_phys_wc_add()",
    "device-tree walking",
    "live arch memtype reservation or removal side effects",
]

SURVEY_MARKERS = [
    "phase13-devres-arch-phys-wc-token-planner",
    "blocked `phase13-devres-live-dma-backed-helpers`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "helper-only DMA/scatterlist boundary",
]

BUILD_MARKERS = [
    'b.path("../../lib/devres.zig")',
    'b.path("phase13_devres.zig")',
    'b.path("phase13_devres_reviewability.zig")',
    'b.path("phase13_devres_dma_coherent.zig")',
    "const phase13_devres_tests = b.addTest(.{",
    "const phase13_devres_reviewability_tests = b.addTest(.{",
    "const phase13_devres_dma_coherent_tests = b.addTest(.{",
    "test_step.dependOn(&run_phase13_devres_tests.step);",
    "test_step.dependOn(&run_phase13_devres_reviewability_tests.step);",
    "test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
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
    "const reported_size = if (input.report_size) translated_size else null;",
    ".fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
]

DEVRES_TEST_MARKERS = [
    'test "phase13 devres propagates pretty-name allocation failure through devm_of_iomap planning" {',
    "try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);",
    "try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);",
    "try std.testing.expectEqual(@as(?u64, 0x10), failure.reported_size);",
    "try std.testing.expect(!failure.requests_region);",
    "try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);",
]

MANIFEST_SUMMARY_KEYS = [
    "preexisting_phase13_devres_test_present",
    "preexisting_phase13_devres_reviewability_present",
    "preexisting_phase13_devres_survey_present",
]

MANIFEST_GAP_STATUSES = {
    "phase13-devres-live-dma-backed-helpers": "blocked_on_dma_state",
    "phase13-devres-live-scatterlist-ownership": "blocked_on_scatterlist_state",
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
    summary = manifest.get("survey_summary", {})
    for key in MANIFEST_SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase13-devres-manifest-summary:{key}")

    statuses = {
        gap.get("id"): gap.get("status")
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_status in MANIFEST_GAP_STATUSES.items():
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
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "scripts/zigux/validate-phase13-release.py": "\n".join(RELEASE_MARKERS) + "\n",
        "zigux/tests/phase13_devres_manifest.json": json.dumps(
            {
                "survey_summary": {key: True for key in MANIFEST_SUMMARY_KEYS},
                "gaps": [
                    {"id": gap_id, "status": status}
                    for gap_id, status in MANIFEST_GAP_STATUSES.items()
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
                "phase13-devres-slice:device-tree walking",
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
                "phase13-devres-survey:blocked `phase13-devres-live-dma-backed-helpers`",
                "phase13-devres-survey:blocked `phase13-devres-live-scatterlist-ownership`",
                "phase13-devres-survey:helper-only DMA/scatterlist boundary",
            ],
            "survey_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "lib/devres.zig", "fail_pretty_name_allocation: bool = false,\n")
        assert_only(
            validate(root),
            [
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
                "phase13-build:const phase13_devres_tests = b.addTest(.{",
                "phase13-build:const phase13_devres_reviewability_tests = b.addTest(.{",
                "phase13-build:const phase13_devres_dma_coherent_tests = b.addTest(.{",
                "phase13-build:test_step.dependOn(&run_phase13_devres_tests.step);",
                "phase13-build:test_step.dependOn(&run_phase13_devres_reviewability_tests.step);",
                "phase13-build:test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
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
                "phase13-devres-manifest-summary:preexisting_phase13_devres_test_present",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_reviewability_present",
                "phase13-devres-manifest-summary:preexisting_phase13_devres_survey_present",
                "phase13-devres-manifest-gap:phase13-devres-live-dma-backed-helpers",
                "phase13-devres-manifest-gap:phase13-devres-live-scatterlist-ownership",
            ],
            "manifest_guard_failed",
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

        (root / "zigux/tests/phase13_devres_dma_coherent.zig").unlink()
        assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_devres_dma_coherent.zig"],
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