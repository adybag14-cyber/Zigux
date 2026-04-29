from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validate_phase3_core import (
    ABI_REQUIRED_DOC_MARKERS,
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_MANIFEST_FILES,
    ABI_REQUIRED_SOURCE_MARKERS,
    Phase3Paths,
    discover_phase3_slices,
    render_wrapper_stub,
    validate_abi_expected_fixture,
    validate_manifest,
    validate_slices,
    validate_source_markers,
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        paths = Phase3Paths(
            root=root,
            docs_dir=root / "Documentation" / "zigux",
            scripts_dir=root / "scripts" / "zigux",
            tests_dir=root / "zigux" / "tests",
            fixtures_dir=root / "zigux" / "tests" / "fixtures",
        )
        fixture_dir = paths.fixtures_dir / "phase3_alpha"
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, fixture_dir):
            path.mkdir(parents=True, exist_ok=True)

        (paths.docs_dir / "phase3-alpha-slice.md").writeText = None
        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_alpha_dump.zig").write_text("// alpha dump\n", encoding="utf-8", newline="\n")
        (fixture_dir / "expected.json").write_text("{}", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_c_harness.c").write_text("// alpha harness\n", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-slice",
                    "files": [
                        "Documentation/zigux/phase3-alpha-slice.md",
                        "zigux/tests/phase3_alpha_dump.zig",
                        "zigux/tests/fixtures/phase3_alpha/expected.json",
                        "zigux/tests/fixtures/phase3_alpha/phase3_alpha_c_harness.c",
                    ],
                    "file_count": 4,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / "phase3-beta-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=beta-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug beta",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        beta_fixture_dir = paths.fixtures_dir / "phase3_beta"
        beta_fixture_dir.mkdir(parents=True, exist_ok=True)
        (paths.tests_dir / "phase3_beta_dump.zig").write_text("// beta dump\n", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "expected.json").write_text("{}", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "phase3_beta_c_harness.c").write_text("// beta harness\n", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "phase3_beta_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "beta-slice",
                    "files": [
                        "Documentation/zigux/phase3-beta-slice.md",
                        "zigux/tests/phase3_beta_dump.zig",
                        "zigux/tests/fixtures/phase3_beta/expected.json",
                        "zigux/tests/fixtures/phase3_beta/phase3_beta_c_harness.c",
                    ],
                    "file_count": 4,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )

        for rel in ABI_REQUIRED_MANIFEST_FILES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("// abi boundary\n", encoding="utf-8", newline="\n")

        (root / "zigux" / "helpers" / "layout_assert.zig").write_text(
            'test "phase3 layout assertions cover canonical bindings" {\n'
            '    comptime {\n'
            '        assertOffset(abi.InteropPolicy, "unsafe_scope", 2);\n'
            "    }\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "kernel" / "export_shim.zig").write_text(
            "pub fn header(flags: u16) abi.BoundaryHeader {\n"
            "    _ = flags;\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {\n"
            "    _ = boundary_header;\n"
            "    return true;\n"
            "}\n\n"
            "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {\n"
            "    return status;\n"
            "}\n\n"
            'test "phase3 export shim keeps failure encoding explicit" {}\n'
            'test "phase3 export shim normalizes explicit status decoding" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "uapi" / "version.zig").write_text(
            "pub const abi_version: u16 = abi.ABI_VERSION;\n\n"
            "pub fn boundaryHeader(flags: u16) Header {\n"
            "    _ = flags;\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn isCompatible(header: Header) bool {\n"
            "    _ = header;\n"
            "    return true;\n"
            "}\n\n"
            'test "phase3 uapi version follows abi version" {}\n'
            'test "phase3 uapi boundary header stays explicit and compatible" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "panic_policy.zig").write_text(
            "pub fn actionFor(mode: abi.PanicMode) Action {\n"
            "    _ = mode;\n"
            "    return .abort_now;\n"
            "}\n\n"
            'test "phase3 panic policy stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "allocator_policy.zig").write_text(
            "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {\n"
            "    _ = mode;\n"
            "    return .caller_prepared;\n"
            "}\n\n"
            'test "phase3 allocator policy stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "atomic.zig").write_text(
            "const std = @import(\"std\");\n\n"
            "pub fn load(comptime T: type, ptr: *const T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn store(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) void {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "}\n\n"
            "pub fn exchange(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn fetchAdd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn fetchSub(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn fetchAnd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn fetchOr(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn fetchXor(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {\n"
            "    _ = .{ T, ptr, value, order };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn compareExchange(\n"
            "    comptime T: type,\n"
            "    ptr: *T,\n"
            "    expected_value: T,\n"
            "    new_value: T,\n"
            "    comptime success_order: std.builtin.AtomicOrder,\n"
            "    comptime failure_order: std.builtin.AtomicOrder,\n"
            ") ?T {\n"
            "    _ = .{ T, ptr, expected_value, new_value, success_order, failure_order };\n"
            "    return null;\n"
            "}\n\n"
            'test "phase3 atomic wrappers behave predictably" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "barrier.zig").write_text(
            "pub fn acquire() void {}\n"
            "pub fn release() void {}\n"
            "pub fn full() void {}\n\n"
            'test "phase3 barrier wrappers stay local to each barrier probe" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "helpers" / "mmio.zig").write_text(
            "const abi = @import(\"abi_bindings\");\n"
            "const narrow = @import(\"narrow_unsafe\");\n\n"
            "pub fn range(base_addr: usize, length: u32, stride: u32) abi.MmioRange {\n"
            "    _ = .{ base_addr, length, stride };\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 {\n"
            "    _ = .{ scope, base_addr, offset };\n"
            "    return 0;\n"
            "}\n\n"
            "pub fn write16Scoped(\n"
            "    scope: narrow.UnsafeScopeTag,\n"
            "    base_addr: usize,\n"
            "    offset: usize,\n"
            "    value: u16,\n"
            ") narrow.ScopeError!void {\n"
            "    _ = .{ scope, base_addr, offset, value };\n"
            "}\n\n"
            "pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 {\n"
            "    _ = .{ scope, base_addr, offset };\n"
            "    return 0;\n"
            "}\n\n"
            "pub fn write32(base_addr: usize, offset: usize, value: u32) void {\n"
            "    _ = .{ base_addr, offset, value };\n"
            "}\n\n"
            'test "phase3 mmio wrapper uses bounded volatile access" {}\n'
            'test "phase3 mmio wrapper keeps declared scope explicit across widths" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "unsafe" / "narrow.zig").write_text(
            "pub const UnsafeScopeTag = enum(u8) {\n"
            "    none = 0,\n"
            "    volatile_mmio = 1,\n"
            "    raw_pointer_bridge = 2,\n"
            "};\n\n"
            'test "phase3 narrow unsafe scope stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_export_uapi.zig").write_text(
            'test "phase3 export shim and uapi stay aligned" {\n'
            "    try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));\n"
            "    try std.testing.expect(!export_shim.isCompatibleHeader(undersized_header));\n"
            "    try std.testing.expect(!uapi_version.isCompatible(mismatched_version_header));\n"
            "    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_low_level_wrappers.zig").write_text(
            'test "phase3 low-level wrappers stay inside the documented ABI surface" {\n'
            "    const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);\n"
            "    _ = mismatch;\n"
            "    barrier.acquire();\n"
            "    barrier.release();\n"
            "    barrier.full();\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Scoped(.none, base, 0, 0x99));\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Scoped(.raw_pointer_bridge, base, 0));\n"
            "    try mmio.write32Scoped(.volatile_mmio, base, 4, 0xaabbccdd);\n"
            "    _ = .{\n"
            "        atomic.fetchOr(u32, &value, 0b1000, .seq_cst),\n"
            "        atomic.fetchAnd(u32, &value, 0b0111, .seq_cst),\n"
            "        atomic.fetchXor(u32, &value, 0b1111, .seq_cst),\n"
            "    };\n"
            "}\n"
            'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_policy_unsafe.zig").write_text(
            'test "phase3 policy helpers stay ABI aligned" {}\n'
            'test "phase3 policy gate enforces the declared unsafe scope" {}\n',
            encoding="utf-8",
            newline="\n",
        )

        (paths.tests_dir / "build.zig").write_text(
            'const phase3_test_step = b.step("phase3-test", "Run Phase 3 tests");\n'
            'const phase3_alpha_dump_step = b.step("phase3-alpha-dump", "Run Phase 3 alpha dump");\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_export_uapi_build.zig").write_text(
            'const phase3_export_uapi_step = b.step("phase3-export-uapi-test", "Run Phase 3 export shim and uapi smoke tests");\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_policy_unsafe_build.zig").write_text(
            'const phase3_policy_unsafe_step = b.step("phase3-policy-unsafe-test", "Run focused Phase 3 policy and unsafe substrate tests");\n',
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_low_level_wrappers_build.zig").write_text(
            'const phase3_low_level_step = b.step("phase3-low-level-wrappers-test", "Run focused Phase 3 low-level wrapper tests");\n',
            encoding="utf-8",
            newline="\n",
        )

        abi_manifest_path = root / "tmp" / "abi_manifest.json"
        abi_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        partial_abi_manifest_files = list(ABI_REQUIRED_MANIFEST_FILES[:-8])
        abi_manifest_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "abi-slice",
                    "files": partial_abi_manifest_files,
                    "file_count": len(partial_abi_manifest_files),
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        abi_issues: list[str] = []
        validate_manifest(root, abi_manifest_path, "abi", abi_issues)
        assert abi_issues == [
            "abi:manifest_missing_required_file=zigux/tests/phase3_abi.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_export_uapi_build.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_export_uapi.zig",
            "abi:manifest_missing_required_file=zigux/tests/phase3_abi_dump.zig",
            "abi:manifest_missing_required_file=zigux/tests/fixtures/phase3_abi/expected.json",
            "abi:manifest_missing_required_file=zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
            "abi:manifest_missing_required_file=Documentation/zigux/phase3-export-uapi-boundary-survey.md",
            "abi:manifest_missing_required_file=scripts/zigux/validate-phase3-export-uapi-survey.py",
        ]

        abi_manifest_path.write_text(
            json.dumps({"phase": "Phase 3", "status": "ready", "slice": "abi-slice", "files": list(ABI_REQUIRED_MANIFEST_FILES), "file_count": len(ABI_REQUIRED_MANIFEST_FILES)}),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_manifest(root, abi_manifest_path, "abi", []) is not None

        abi_doc_path = root / "tmp" / "phase3-abi-slice.md"
        abi_doc_path.write_text(
            "\n".join([
                "PHASE3_STATUS=ready",
                "PHASE3_SLICE=abi-slice",
                *ABI_REQUIRED_DOC_MARKERS,
                "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
                "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                "",
            ]),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_slices(root, []) == []

        abi_expected_fixture = root / "zigux" / "tests" / "fixtures" / "phase3_abi" / "expected.json"
        abi_expected_fixture.write_text(
            json.dumps({"constants": dict(ABI_REQUIRED_EXPECTED_CONSTANTS)}),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_abi_expected_fixture(root, []) is None

        abi_expected_drift = json.loads(abi_expected_fixture.read_text(encoding="utf-8"))
        del abi_expected_drift["constants"]["panic_abort"]
        abi_expected_fixture.write_text(
            json.dumps(abi_expected_drift),
            encoding="utf-8",
            newline="\n",
        )
        abi_expected_issues: list[str] = []
        validate_abi_expected_fixture(root, abi_expected_issues)
        assert abi_expected_issues == [
            "abi:expected_constant=panic_abort:None",
        ]
        abi_expected_fixture.write_text(
            json.dumps({"constants": dict(ABI_REQUIRED_EXPECTED_CONSTANTS)}),
            encoding="utf-8",
            newline="\n",
        )

        mmio_path = root / "zigux" / "helpers" / "mmio.zig"
        original_mmio = mmio_path.read_text(encoding="utf-8")
        missing_mmio_marker = ABI_REQUIRED_SOURCE_MARKERS["zigux/helpers/mmio.zig"][2]
        mmio_path.write_text(original_mmio.replace(missing_mmio_marker + "\n", "", 1), encoding="utf-8", newline="\n")
        abi_source_issues: list[str] = []
        validate_source_markers(root, "abi", abi_source_issues)
        assert abi_source_issues == [
            f"abi:missing_source_marker=zigux/helpers/mmio.zig:{missing_mmio_marker}",
        ]
        mmio_path.write_text(original_mmio, encoding="utf-8", newline="\n")

        low_level_path = root / "zigux" / "tests" / "phase3_low_level_wrappers.zig"
        original_low_level = low_level_path.read_text(encoding="utf-8")
        missing_low_level_marker = ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_low_level_wrappers.zig"][1]
        low_level_path.write_text(
            original_low_level.replace("    " + missing_low_level_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        abi_source_issues = []
        validate_source_markers(root, "abi", abi_source_issues)
        assert abi_source_issues == [
            f"abi:missing_source_marker=zigux/tests/phase3_low_level_wrappers.zig:{missing_low_level_marker}",
        ]
        low_level_path.write_text(original_low_level, encoding="utf-8", newline="\n")

        (root / "zigux" / "helpers" / "panic_policy.zig").write_text(
            "pub fn actionFor(mode: abi.PanicMode) Action {\n"
            "    _ = mode;\n"
            "    return .abort_now;\n"
            "}\n\n"
            'test "phase3 panic policy stays explicit" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        discovered = discover_phase3_slices(paths)
        alpha = [entry for entry in discovered if entry.slug == "alpha"]
        assert len(alpha) == 1
        assert validate_slices(root, alpha) == []

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    return 0
