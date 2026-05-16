#!/usr/bin/env python3
"""Guard the shared Phase 13 devres lifetime packet in lib/devres.zig."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


ROOT = Path("/workspace")
DEVRES = Path("lib/devres.zig")

DESCRIPTOR_MARKERS = [
    '.provides_ioremap_lifetime_planning = true',
    '.provides_ioremap_plain_wrapper_planning = true',
    '.provides_ioremap_uc_wrapper_planning = true',
    '.provides_ioremap_wc_wrapper_planning = true',
    '.provides_ioremap_np_wrapper_planning = true',
    '.provides_release_pointer_match = true',
    '.provides_iounmap_call_planning = true',
    '.provides_arch_io_wc_memtype_planning = true',
    '.provides_arch_phys_wc_token_planning = true',
    '.touches_live_device_lists = false',
    '.touches_live_mmio = false',
    '.touches_live_arch_memtype = false',
]

WRAPPER_SPECS = {
    "planManagedIoremapAcquirePlain": ".kind = .plain",
    "planManagedIoremapAcquireUc": ".kind = .uncached",
    "planManagedIoremapAcquireWc": ".kind = .write_combined",
    "planManagedIoremapAcquireNp": ".kind = .non_posted",
}

TEST_MARKERS = [
    'test "phase13 devres plain ioremap wrapper preserves the managed lifetime path"',
    'test "phase13 devres plain ioremap wrapper frees the release record on map failure"',
    'test "phase13 devres uncached ioremap wrapper preserves the managed lifetime path"',
    'test "phase13 devres uncached ioremap wrapper frees the release record on map failure"',
    'test "phase13 devres wc ioremap wrapper preserves the managed lifetime path"',
    'test "phase13 devres wc ioremap wrapper frees the release record on map failure"',
    'test "phase13 devres non-posted ioremap wrapper preserves the managed lifetime path"',
    'test "phase13 devres non-posted ioremap wrapper frees the release record on map failure"',
    'test "phase13 devres iounmap plan warns on release pointer mismatch"',
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_block(source: str, name: str) -> str | None:
    pattern = rf"pub fn {re.escape(name)}\b(.*?)(?=\npub fn |\ntest \"|\n}};\n|\Z)"
    match = re.search(pattern, source, flags=re.S)
    if not match:
        return None
    return match.group(0)


def expect_markers(errors: list[str], source: str, prefix: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f"{prefix}:missing_marker:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    devres_path = root / DEVRES

    if not devres_path.exists():
        return [f"missing:{DEVRES.as_posix()}"]

    source = read(devres_path)
    expect_markers(errors, source, "descriptor", DESCRIPTOR_MARKERS)

    acquire = extract_block(source, "planManagedIoremapAcquire")
    if acquire is None:
        errors.append("lifetime:missing_fn:planManagedIoremapAcquire")
    else:
        expect_markers(
            errors,
            acquire,
            "lifetime:planManagedIoremapAcquire",
            [
                "if (!input.release_record_allocated) {",
                "return error.OutOfMemory;",
                ".added_to_devres = false",
                ".release_record_retained = false",
                ".release_record_freed = true",
                ".should_unmap_on_detach = false",
                ".added_to_devres = true",
                ".release_record_retained = true",
                ".release_record_freed = false",
                ".should_unmap_on_detach = true",
            ],
        )

    for fn_name, kind_marker in WRAPPER_SPECS.items():
        block = extract_block(source, fn_name)
        if block is None:
            errors.append(f"wrapper:missing_fn:{fn_name}")
            continue
        expect_markers(
            errors,
            block,
            f"wrapper:{fn_name}",
            [
                "return planManagedIoremapAcquire(.{",
                kind_marker,
                ".release_record_allocated = input.release_record_allocated",
                ".mapped_address = input.mapped_address",
            ],
        )

    iounmap = extract_block(source, "planManagedIounmap")
    if iounmap is None:
        errors.append("iounmap:missing_fn:planManagedIounmap")
    else:
        expect_markers(
            errors,
            iounmap,
            "iounmap",
            [
                "const release_matches = ioremapReleaseMatches(tracked_address, candidate_address);",
                ".release_matches = release_matches",
                ".warns_on_release_miss = !release_matches",
            ],
        )
        if "iounmap(" in iounmap:
            errors.append("iounmap:unexpected_live_call:iounmap(")

    memtype = extract_block(source, "planArchIoReserveMemtypeWc")
    if memtype is None:
        errors.append("memtype:missing_fn:planArchIoReserveMemtypeWc")
    else:
        expect_markers(
            errors,
            memtype,
            "memtype",
            [
                "if (!input.release_record_allocated) {",
                "return error.OutOfMemory;",
                ".error_code = input.reserve_result",
                ".added_to_devres = false",
                ".release_record_retained = false",
                ".release_record_freed = true",
                ".should_release_on_detach = false",
                ".added_to_devres = true",
                ".release_record_retained = true",
                ".release_record_freed = false",
                ".should_release_on_detach = true",
            ],
        )

    phys_wc = extract_block(source, "planArchPhysWcAdd")
    if phys_wc is None:
        errors.append("phys_wc:missing_fn:planArchPhysWcAdd")
    else:
        expect_markers(
            errors,
            phys_wc,
            "phys_wc",
            [
                "if (!input.release_record_allocated) {",
                "return error.OutOfMemory;",
                ".error_code = input.token_result",
                ".added_to_devres = false",
                ".release_record_retained = false",
                ".release_record_freed = true",
                ".should_remove_on_detach = false",
                ".token = input.token_result",
                ".added_to_devres = true",
                ".release_record_retained = true",
                ".release_record_freed = false",
                ".should_remove_on_detach = true",
            ],
        )

    expect_markers(errors, source, "tests", TEST_MARKERS)
    return errors


BASELINE_DEVRES = """const std = @import(\"std\");

pub const ModuleDescriptor = struct {
    provides_ioremap_lifetime_planning: bool,
    provides_ioremap_plain_wrapper_planning: bool,
    provides_ioremap_uc_wrapper_planning: bool,
    provides_ioremap_wc_wrapper_planning: bool,
    provides_ioremap_np_wrapper_planning: bool,
    provides_release_pointer_match: bool,
    provides_iounmap_call_planning: bool,
    provides_arch_io_wc_memtype_planning: bool,
    provides_arch_phys_wc_token_planning: bool,
    touches_live_device_lists: bool,
    touches_live_mmio: bool,
    touches_live_arch_memtype: bool,
};

pub const ManagedIoremapAcquireInput = struct {
    release_record_allocated: bool,
    mapped_address: ?usize,
};

pub const ManagedIoremapAcquireWrapperInput = struct {
    release_record_allocated: bool,
    mapped_address: ?usize,
};

pub const ManagedMemtypeReserveInput = struct {
    release_record_allocated: bool,
    reserve_result: i32,
};

pub const ManagedPhysWcAddInput = struct {
    release_record_allocated: bool,
    token_result: i32,
};

pub const DevresHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .provides_ioremap_lifetime_planning = true,
            .provides_ioremap_plain_wrapper_planning = true,
            .provides_ioremap_uc_wrapper_planning = true,
            .provides_ioremap_wc_wrapper_planning = true,
            .provides_ioremap_np_wrapper_planning = true,
            .provides_release_pointer_match = true,
            .provides_iounmap_call_planning = true,
            .provides_arch_io_wc_memtype_planning = true,
            .provides_arch_phys_wc_token_planning = true,
            .touches_live_device_lists = false,
            .touches_live_mmio = false,
            .touches_live_arch_memtype = false,
        };
    }

    pub fn planManagedIoremapAcquire(input: ManagedIoremapAcquireInput) !void {
        if (!input.release_record_allocated) {
            return error.OutOfMemory;
        }
        if (input.mapped_address == null) {
            _ = .{
                .added_to_devres = false,
                .release_record_retained = false,
                .release_record_freed = true,
                .should_unmap_on_detach = false,
            };
        }
        _ = .{
            .added_to_devres = true,
            .release_record_retained = true,
            .release_record_freed = false,
            .should_unmap_on_detach = true,
        };
    }

    pub fn planManagedIoremapAcquirePlain(input: ManagedIoremapAcquireWrapperInput) !void {
        return planManagedIoremapAcquire(.{
            .kind = .plain,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn planManagedIoremapAcquireUc(input: ManagedIoremapAcquireWrapperInput) !void {
        return planManagedIoremapAcquire(.{
            .kind = .uncached,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn planManagedIoremapAcquireWc(input: ManagedIoremapAcquireWrapperInput) !void {
        return planManagedIoremapAcquire(.{
            .kind = .write_combined,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn planManagedIoremapAcquireNp(input: ManagedIoremapAcquireWrapperInput) !void {
        return planManagedIoremapAcquire(.{
            .kind = .non_posted,
            .release_record_allocated = input.release_record_allocated,
            .mapped_address = input.mapped_address,
        });
    }

    pub fn planManagedIounmap(tracked_address: usize, candidate_address: usize) void {
        const release_matches = ioremapReleaseMatches(tracked_address, candidate_address);
        _ = .{
            .release_matches = release_matches,
            .warns_on_release_miss = !release_matches,
        };
    }

    pub fn planArchIoReserveMemtypeWc(input: ManagedMemtypeReserveInput) !void {
        if (!input.release_record_allocated) {
            return error.OutOfMemory;
        }
        if (input.reserve_result < 0) {
            _ = .{
                .error_code = input.reserve_result,
                .added_to_devres = false,
                .release_record_retained = false,
                .release_record_freed = true,
                .should_release_on_detach = false,
            };
        }
        _ = .{
            .added_to_devres = true,
            .release_record_retained = true,
            .release_record_freed = false,
            .should_release_on_detach = true,
        };
    }

    pub fn planArchPhysWcAdd(input: ManagedPhysWcAddInput) !void {
        if (!input.release_record_allocated) {
            return error.OutOfMemory;
        }
        if (input.token_result < 0) {
            _ = .{
                .error_code = input.token_result,
                .added_to_devres = false,
                .release_record_retained = false,
                .release_record_freed = true,
                .should_remove_on_detach = false,
            };
        }
        _ = .{
            .token = input.token_result,
            .added_to_devres = true,
            .release_record_retained = true,
            .release_record_freed = false,
            .should_remove_on_detach = true,
        };
    }
};

test \"phase13 devres plain ioremap wrapper preserves the managed lifetime path\" {}
test \"phase13 devres plain ioremap wrapper frees the release record on map failure\" {}
test \"phase13 devres uncached ioremap wrapper preserves the managed lifetime path\" {}
test \"phase13 devres uncached ioremap wrapper frees the release record on map failure\" {}
test \"phase13 devres wc ioremap wrapper preserves the managed lifetime path\" {}
test \"phase13 devres wc ioremap wrapper frees the release record on map failure\" {}
test \"phase13 devres non-posted ioremap wrapper preserves the managed lifetime path\" {}
test \"phase13 devres non-posted ioremap wrapper frees the release record on map failure\" {}
test \"phase13 devres iounmap plan warns on release pointer mismatch\" {}
"""


def seed_fixture_tree(root: Path) -> None:
    write(root / DEVRES, BASELINE_DEVRES)


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_shared_lifetime_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")

        seed_fixture_tree(root)
        broken = read(root / DEVRES).replace(
            ".kind = .non_posted,",
            ".kind = .write_combined,",
            1,
        )
        write(root / DEVRES, broken)
        assert_only(
            validate(root),
            ["wrapper:planManagedIoremapAcquireNp:missing_marker:.kind = .non_posted"],
            "wrapper_kind_drift_failed",
        )

        seed_fixture_tree(root)
        broken = read(root / DEVRES).replace(
            '.error_code = input.reserve_result,',
            '',
            1,
        )
        write(root / DEVRES, broken)
        assert_only(
            validate(root),
            ["memtype:missing_marker:.error_code = input.reserve_result"],
            "memtype_failure_drift_failed",
        )

        seed_fixture_tree(root)
        broken = read(root / DEVRES).replace(
            'test "phase13 devres iounmap plan warns on release pointer mismatch" {}',
            "",
            1,
        )
        write(root / DEVRES, broken)
        assert_only(
            validate(root),
            [
                'tests:missing_marker:test "phase13 devres iounmap plan warns on release pointer mismatch"'
            ],
            "test_marker_drift_failed",
        )

    print("PHASE13_DEVRES_SHARED_LIFETIME_PACKET_SELF_TEST=pass")
    print("PHASE13_DEVRES_SHARED_LIFETIME_PACKET_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 13 devres shared lifetime packet stays explicit."
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

    print("PHASE13_DEVRES_SHARED_LIFETIME_PACKET=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
