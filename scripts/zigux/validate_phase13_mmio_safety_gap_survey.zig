const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE13_MMIO_SAFETY_SURVEY=pass";
pub const self_test_pass_marker = "PHASE13_MMIO_SAFETY_SURVEY_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md = [_][]const u8{
    "P13_L01_SCOPE=this lane stays inside the iomap/mmio safety surface survey and compares the current Zigux MMIO helper against the roadmap rule that approved MMIO wrappers must keep the unsafe surface narrow, reviewable, and validation-backed",
    "P13_L01_REPO_EVIDENCE=direct current-head readback reaches zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, zigux/tests/phase3_low_level_wrappers.zig, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, and scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "P13_L01_ROADMAP_RULE=the roadmap keeps MMIO inside the approved atomic/barrier/MMIO wrapper family and requires wrapper-first handling plus a narrow unsafe surface rather than open-ended raw access",
    "P13_L01_FINDING_RANGE_IS_DESCRIPTIVE_ONLY=MmioRange is currently a descriptive blessed-window record, not an active access boundary, because later MMIO reads and writes do not consume the range object when they touch registers",
    "P13_L01_FINDING_NO_RANGE_BACKED_ACCESSORS=zigux/helpers/mmio.zig currently exposes range constructors and width-specific base-plus-offset helpers, but it does not yet expose range-backed read, write, exchange, or masked-update entry points that enforce length and stride at access time",
    "P13_L01_FINDING_WIDTH_HELPERS_BYPASS_WINDOW_REVIEW=the width-specific helpers validate alignment and interop policy, but they still operate on a raw base address plus offset, so they bypass any previously blessed MmioRange length or stride review surface",
    "P13_L01_FINDING_SURVEY_PACKET_OVERSTATES_CLOSURE=the existing low-level-wrapper survey truthfully lists the landed MMIO helper surface, but it does not keep these remaining range-enforcement gaps explicit, which makes the MMIO packet read closer to closed than the safety boundary actually is",
    "P13_L01_CONCLUSION=current master has landed the roadmap-approved MMIO wrapper leafs, but it has not yet closed the narrower safety gap where a blessed MMIO window should remain the object that later accessors validate against",
    "P13_L01_NEXT_STEP=add range-backed MMIO accessors that consume MmioRange at read/write time, reject out-of-range or stride-breaking offsets, and extend the focused low-level-wrapper replay so the survey can be tightened from gap-reporting to landed safety proof",
};

const REQUIRED_MARKERS__zigux_helpers_mmio_zig = [_][]const u8{
    "pub const MmioRange = extern struct {",
    "pub fn rangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) PolicyError!MmioRange {",
    "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {",
    "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
    "pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read16InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u16 {",
    "pub fn write16InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
    "pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {",
    "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
    "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
};

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub fn permitsVolatileMmio(scope: abi.UnsafeScope) bool {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn allowsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
    "pub const AccessBoundary = enum {",
    ".volatile_mmio_window",
    "pub fn permitsVolatileMmio(scope: UnsafeScopeTag) bool {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_zig = [_][]const u8{
    "test \"phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates\" {",
    "const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);",
    "try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-low-level-wrapper-boundary-survey_md = [_][]const u8{
    "Current `master` also keeps `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, `rangeInteropPolicyByte()`, and the width-specific `read8InteropPolicyBytes()`/`write8InteropPolicyBytes()`/`read16InteropPolicyBytes()`/`write16InteropPolicyBytes()`/`read32InteropPolicyByte()`/`write32InteropPolicyByte()`/`read64InteropPolicyBytes()`/`write64InteropPolicyBytes()` entrypoints directly readable in `zigux/helpers/mmio.zig`, so the bounded low-level-wrapper survey should treat those MMIO range and width-specific wrappers as landed helper-local evidence rather than collapsing MMIO coverage to the generic typed accessors alone.",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-low-level-wrapper-survey_py = [_][]const u8{
    "MMIO_PATH: (",
    "\"pub const MmioRange = extern struct {\",",
    "\"pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) PolicyError!MmioRange {\",",
    "\"pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {\",",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-iomap-mmio-safety-gap-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md_path);
    const text_required_markers__documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-iomap-mmio-safety-gap-survey_md, marker);
    const text_required_markers__zigux_helpers_mmio_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/mmio/zig");
    defer allocator.free(text_required_markers__zigux_helpers_mmio_zig_path);
    const text_required_markers__zigux_helpers_mmio_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_mmio_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_mmio_zig);
    for (REQUIRED_MARKERS__zigux_helpers_mmio_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_mmio_zig, marker);
    const text_required_markers__zigux_helpers_unsafe_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    const text_required_markers__zigux_helpers_unsafe_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_unsafe_policy_zig, marker);
    const text_required_markers__zigux_unsafe_narrow_zig_path = try guard.joinPath(allocator, root, "zigux/unsafe/narrow/zig");
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig_path);
    const text_required_markers__zigux_unsafe_narrow_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_unsafe_narrow_zig_path);
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig);
    for (REQUIRED_MARKERS__zigux_unsafe_narrow_zig) |marker| try guard.requireMarker(text_required_markers__zigux_unsafe_narrow_zig, marker);
    const text_required_markers__zigux_tests_phase3_low_level_wrappers_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/low/level/wrappers/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_low_level_wrappers_zig_path);
    const text_required_markers__zigux_tests_phase3_low_level_wrappers_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_low_level_wrappers_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_low_level_wrappers_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_low_level_wrappers_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_low_level_wrappers_zig, marker);
    const text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-low-level-wrapper-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md, marker);
    const text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase3-low-level-wrapper-survey/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py_path);
    const text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase3-low-level-wrapper-survey_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
