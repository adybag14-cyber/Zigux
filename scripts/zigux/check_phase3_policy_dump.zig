const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_DUMP=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_DUMP_SELF_TEST=pass";

const REQUIRED_DOC_MARKERS = [_][]const u8{
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "make -C zigux phase3",
};

const REQUIRED_DUMP_MARKERS = [_][]const u8{
    "safe-default",
    "mmio-bug",
    "raw-bridge-warn",
    "reserved-invalid",
    "panic={s}",
    "allocator={s}",
    "init_flow={s}",
    "explicit_caller={any}",
    "owned_state={any}",
    "reset_on_init={any}",
    "unsafe={s}",
    "boundary={s}",
    "surface={s}",
    "typed_only={any}",
    "global_fallback={any}",
    "warn_only={any}",
    "mmio={any}",
    "raw_bridge={any}",
    "audit={any}",
    "bridge_read_ok={any}",
    "bridge_write_ok={any}",
    "narrow={s}",
    "narrow_boundary={s}",
    "narrow_surface={s}",
    "std.debug.print(",
};

const REQUIRED_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/panic_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/allocator_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    ".root_source_file = b.path(\"../unsafe/narrow.zig\"),",
    ".root_source_file = b.path(\"phase3_policy_dump.zig\"),",
    "\"phase3-policy-dump\"",
};

const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    "phase3-policy-dump:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
};

const REQUIRED_WORKFLOW_MARKERS = [_][]const u8{
    "Run current Phase 3 policy dump replay",
    "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Run current Phase 3 policy dump make wrapper",
    "run: make -C zigux phase3-policy-dump",
};

const EXPECTED_LINES = [_][]const u8{
    "safe-default|panic=abort|allocator=caller_provided|init_flow=caller_prepared|explicit_caller=true|owned_state=false|reset_on_init=false|unsafe=none|boundary=typed_safe|surface=safe_only|typed_only=true|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=none|narrow_boundary=typed_safe|narrow_surface=safe_only",
    "mmio-bug|panic=bug|allocator=kernel_heap|init_flow=helper_owned|explicit_caller=false|owned_state=true|reset_on_init=false|unsafe=volatile_mmio|boundary=volatile_mmio_window|surface=mmio_only|typed_only=false|global_fallback=true|warn_only=false|mmio=true|raw_bridge=false|audit=true|bridge_read_ok=false|bridge_write_ok=false|narrow=volatile_mmio|narrow_boundary=volatile_mmio_window|narrow_surface=mmio_only",
    "raw-bridge-warn|panic=warn|allocator=arena|init_flow=helper_owned_with_reset|explicit_caller=false|owned_state=true|reset_on_init=true|unsafe=raw_pointer_bridge|boundary=raw_pointer_bridge|surface=raw_pointer_bridge_only|typed_only=false|global_fallback=true|warn_only=true|mmio=false|raw_bridge=true|audit=true|bridge_read_ok=true|bridge_write_ok=true|narrow=raw_pointer_bridge|narrow_boundary=raw_pointer_bridge|narrow_surface=raw_pointer_bridge_only",
    "reserved-invalid|panic=invalid|allocator=invalid|init_flow=invalid|explicit_caller=false|owned_state=false|reset_on_init=false|unsafe=invalid|boundary=invalid|surface=invalid|typed_only=false|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=invalid|narrow_boundary=invalid|narrow_surface=invalid",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_doc_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_required_doc_markers_path);
    const text_required_doc_markers = try guard.readUtf8File(io, allocator, text_required_doc_markers_path);
    defer allocator.free(text_required_doc_markers);
    for (REQUIRED_DOC_MARKERS) |marker| try guard.requireMarker(text_required_doc_markers, marker);
    const text_required_dump_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_required_dump_markers_path);
    const text_required_dump_markers = try guard.readUtf8File(io, allocator, text_required_dump_markers_path);
    defer allocator.free(text_required_dump_markers);
    for (REQUIRED_DUMP_MARKERS) |marker| try guard.requireMarker(text_required_dump_markers, marker);
    const text_required_build_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_required_build_markers_path);
    const text_required_build_markers = try guard.readUtf8File(io, allocator, text_required_build_markers_path);
    defer allocator.free(text_required_build_markers);
    for (REQUIRED_BUILD_MARKERS) |marker| try guard.requireMarker(text_required_build_markers, marker);
    const text_required_makefile_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_required_makefile_markers_path);
    const text_required_makefile_markers = try guard.readUtf8File(io, allocator, text_required_makefile_markers_path);
    defer allocator.free(text_required_makefile_markers);
    for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_required_makefile_markers, marker);
    const text_required_workflow_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_required_workflow_markers_path);
    const text_required_workflow_markers = try guard.readUtf8File(io, allocator, text_required_workflow_markers_path);
    defer allocator.free(text_required_workflow_markers);
    for (REQUIRED_WORKFLOW_MARKERS) |marker| try guard.requireMarker(text_required_workflow_markers, marker);
    const text_expected_lines_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_expected_lines_path);
    const text_expected_lines = try guard.readUtf8File(io, allocator, text_expected_lines_path);
    defer allocator.free(text_expected_lines);
    for (EXPECTED_LINES) |marker| try guard.requireExactLineCount(text_expected_lines, marker, 1);
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
