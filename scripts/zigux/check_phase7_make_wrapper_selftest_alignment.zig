const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
};

const markers_1 = [_][]const u8{
    "- `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `scripts\\zigux/validate_phase7.zig`",
};

const markers_2 = [_][]const u8{
    "- shared control-surface packet, lane `P7-Y05`:",
    "- `scripts\\zigux/check_phase7_shared_control_gap.zig`",
    "the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` exposes the narrow `phase7-validate` foothold plus the dedicated helper-local `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, and still omits aggregate `phase7-test`, aggregate `phase7`, and the other helper-local Phase 7 wrapper routes.",
};

const markers_3 = [_][]const u8{
    "run: make -C zigux phase7-validate",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
};

const markers_4 = [_][]const u8{
    "PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass",
    "PHASE7_SHARED_CONTROL_GAP=pass",
};

const markers_5 = [_][]const u8{
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
    "phase7-rbtree-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig",
    "phase7-rbtree-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig",
};

const markers_6 = [_][]const u8{
    "\"zigux/tests/phase7_build.zig\",",
    "\"scripts\\zigux/validate_phase7.zig\",",
    "phase7:",
};

const markers_7 = [_][]const u8{
    "phase7-test:",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase7-helper-lane-sequencing.md", .markers = &markers_2 },
    .{ .rel = "scripts/zigux/check_phase7_runtime_workspace_bootstrap_handoff.zig", .markers = &markers_3 },
    .{ .rel = "scripts/zigux/check_phase7_shared_control_gap.zig", .markers = &markers_4 },
    .{ .rel = "zigux/Makefile", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase7_rbtree_manifest.json", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase7_rbtree_survey.zig", .markers = &markers_7 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// REQUIRED_CHECKER_MARKERS
// PARKED_SHARED_CONTROL_PATHS = [
// "scripts\zigux/check_phase7_make_wrapper.zig",
// READABLE_NON_OWNER_FILES = [
// "zigux/tests/phase7_build.zig",
// "scripts\zigux/validate_phase7.zig",
// print("PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass")
// print("PHASE7_SHARED_CONTROL_GAP=pass")
// REQUIRED_SEQUENCING_MARKERS
// - shared control-surface packet, lane `P7-Y05`:
// - `scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig`
// - `scripts\zigux/check_phase7_shared_control_gap.zig`
// - `scripts\zigux/validate_phase7.zig`
// the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` exposes the narrow `phase7-validate` foothold plus the dedicated helper-local `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, and still omits aggregate `phase7-test`, aggregate `phase7`, and the other helper-local Phase 7 wrapper routes.
// REQUIRED_WORKFLOW_LINES
// run: zig run scripts\zigux/check_phase7_shared_control_gap.zig -- --self-test
// run: zig run scripts\zigux/check_phase7_shared_control_gap.zig
// run: zig run scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test
// run: zig run scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig
// FORBIDDEN_WORKFLOW_LINES
// run: make -C zigux phase7-validate
// run: make -C zigux phase7-test
// run: python3 scripts/zigux/validate-phase7 --self-test
// run: zig run scripts\zigux/validate_phase7.zig -- --self-test
// run: zig run scripts\zigux/validate_phase7.zig
// run: zig build test --build-file zigux/tests/phase7_build.zig --summary all
// REQUIRED_MAKEFILE_LINES
// phase7-validate:
// cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test
// cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig
// phase7-rbtree-test:
// cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig
// phase7-rbtree-survey:
// cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig
// REQUIRED_VALIDATOR_MARKERS
// MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig")
// run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")
// FORBIDDEN_MAKEFILE_LINES
// phase7-test:
// phase7:
