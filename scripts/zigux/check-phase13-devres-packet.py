#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "lib/devres.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_devres_reviewability.zig",
    "scripts/zigux/validate-phase13-release.py",
    "zigux/Makefile",
]

SLICE_REQUIRED_MARKERS = [
    "This bounded Phase 13 slice starts `lib/devres.zig` with a pure helper-first foothold anchored to `lib/devres.c`.",
    "devm_of_iomap()` bridge as a pure planner",
    "devm_arch_io_reserve_memtype_wc()",
    "This slice does not claim live `devres_alloc_node()` ownership",
]

DEVRES_REQUIRED_MARKERS = [
    "pub const ManagedMemtypeReserveInput = struct",
    "pub const DeviceTreeIomapInput = struct",
    "fail_pretty_name_allocation: bool = false,",
    ".fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
    ".provides_arch_io_wc_memtype_planning = true,",
    "pub fn planDeviceTreeIomap",
    "pub fn planArchIoReserveMemtypeWc",
]

TEST_REQUIRED_MARKERS = [
    'test "phase13 devres plans devm_of_iomap around translated resources and optional size reporting"',
    'test "phase13 devres preserves translated size when devm_of_iomap hits downstream remap failure"',
    'test "phase13 devres retains memtype release records on successful WC reservation"',
    'test "phase13 devres rejects memtype planning when the release record cannot be allocated"',
]

REVIEWABILITY_REQUIRED_MARKERS = [
    'test "phase13 devres reviewability packet records the helper-only DMA/scatterlist boundary"',
    '"zigux/tests/phase13_devres_manifest.json"',
    '"Documentation/zigux/phase13-devres-survey.md"',
    '"phase13-devres-reviewability-gate"',
    '"phase13-devres-live-scatterlist-ownership"',
]

BUILD_REQUIRED_MARKERS = [
    'b.path("../../lib/devres.zig")',
    'b.path("phase13_devres.zig")',
    'const phase13_devres_tests = b.addTest(.{',
    "test_step.dependOn(&run_phase13_devres_tests.step);",
]

VALIDATOR_REQUIRED_MARKERS = [
    '"zigux/tests/phase13_devres.zig",',
    '"zigux/tests/phase13_devres_manifest.json",',
]

MAKE_REQUIRED_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _collect_missing_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    issues.extend(_collect_missing_markers(_read(root / "Documentation/zigux/phase13-devres-slice.md"), SLICE_REQUIRED_MARKERS, "phase13-devres-slice"))
    issues.extend(_collect_missing_markers(_read(root / "lib/devres.zig"), DEVRES_REQUIRED_MARKERS, "lib-devres"))
    issues.extend(_collect_missing_markers(_read(root / "zigux/tests/phase13_devres.zig"), TEST_REQUIRED_MARKERS, "phase13-devres-test"))
    issues.extend(_collect_missing_markers(_read(root / "zigux/tests/phase13_devres_reviewability.zig"), REVIEWABILITY_REQUIRED_MARKERS, "phase13-devres-reviewability"))
    issues.extend(_collect_missing_markers(_read(root / "zigux/tests/phase13_build.zig"), BUILD_REQUIRED_MARKERS, "phase13-build"))
    issues.extend(_collect_missing_markers(_read(root / "scripts/zigux/validate-phase13-release.py"), VALIDATOR_REQUIRED_MARKERS, "phase13-release-validator"))
    issues.extend(_collect_missing_markers(_read(root / "zigux/Makefile"), MAKE_REQUIRED_MARKERS, "makefile"))
    return issues


def _seed_fixture_tree(root: Path) -> None:
    _write(root / "Documentation/zigux/phase13-devres-slice.md", "\n".join(SLICE_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/phase13-devres-survey.md", "# survey stub\n")
    _write(root / "lib/devres.zig", "\n".join(DEVRES_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/phase13_devres.zig", "\n".join(TEST_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/phase13_build.zig", "\n".join(BUILD_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/phase13_devres_manifest.json", "{}\n")
    _write(root / "zigux/tests/phase13_devres_reviewability.zig", "\n".join(REVIEWABILITY_REQUIRED_MARKERS) + "\n")
    _write(root / "scripts/zigux/validate-phase13-release.py", "\n".join(VALIDATOR_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/Makefile", "\n".join(MAKE_REQUIRED_MARKERS) + "\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase13-devres-packet-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_packet_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text("phase13-test:\n\t@true\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "makefile:phase13-validate:",
                "makefile:scripts/zigux/validate-phase13-release.py",
                "makefile:scripts/zigux/check-phase13-devres-packet.py",
            ],
            "makefile_route_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        validator_path = root / "scripts/zigux/validate-phase13-release.py"
        validator_path.write_text("# stub\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                'phase13-release-validator:"zigux/tests/phase13_devres.zig",',
                'phase13-release-validator:"zigux/tests/phase13_devres_manifest.json",',
            ],
            "validator_marker_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / "lib/devres.zig").unlink()
        _assert_only(validate(root), ["missing_file:lib/devres.zig"], "required_file_guard_failed")
        _seed_fixture_tree(root)
        case_count += 1

        devres_test_path = root / "zigux/tests/phase13_devres.zig"
        devres_test_path.write_text(TEST_REQUIRED_MARKERS[0] + "\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                'phase13-devres-test:test "phase13 devres preserves translated size when devm_of_iomap hits downstream remap failure"',
                'phase13-devres-test:test "phase13 devres retains memtype release records on successful WC reservation"',
                'phase13-devres-test:test "phase13 devres rejects memtype planning when the release record cannot be allocated"',
            ],
            "devres_test_marker_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        reviewability_path = root / "zigux/tests/phase13_devres_reviewability.zig"
        reviewability_path.write_text(REVIEWABILITY_REQUIRED_MARKERS[0] + "\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                'phase13-devres-reviewability:"zigux/tests/phase13_devres_manifest.json"',
                'phase13-devres-reviewability:"Documentation/zigux/phase13-devres-survey.md"',
                'phase13-devres-reviewability:"phase13-devres-reviewability-gate"',
                'phase13-devres-reviewability:"phase13-devres-live-scatterlist-ownership"',
            ],
            "reviewability_marker_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        devres_path = root / "lib/devres.zig"
        devres_path.write_text("pub const DeviceTreeIomapInput = struct\npub fn planDeviceTreeIomap\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "lib-devres:pub const ManagedMemtypeReserveInput = struct",
                "lib-devres:fail_pretty_name_allocation: bool = false,",
                "lib-devres:.fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
                "lib-devres:.provides_arch_io_wc_memtype_planning = true,",
                "lib-devres:pub fn planArchIoReserveMemtypeWc",
            ],
            "devres_marker_guard_failed",
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
