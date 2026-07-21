const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_VALIDATOR_COVERAGE_GAP=pass";
pub const self_test_pass_marker = "PHASE2_VALIDATOR_COVERAGE_GAP_SELF_TEST=pass";

const LIVE_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "run: make -C zigux phase2",
};

const LIVE_MAKEFILE_LINES = [_][]const u8{
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig",
    "phase2: phase2-validate",
};

const VALIDATOR_PRESENT_MARKERS = [_][]const u8{
    "\"scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig\",",
    "\"phase2-tools:\",",
    "\"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\",",
};

const VALIDATOR_GAP_MARKERS = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "run: make -C zigux phase2",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig -- --self-test\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig\",",
};

const DOC_MARKERS = [_][]const u8{
    "# Phase 2 Validator Coverage Gap",
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig`",
    "`make -C zigux phase2`",
    "current `master` already ships the bootstrap-workflow guard in the workflow and the Phase 2 tools make route",
    "the validator still does not require those exact workflow or makefile markers",
    "next bounded repo-tooling step is to widen `validate-phase2.py` so the shipped bootstrap-workflow guard and aggregate `phase2` route become validator-enforced",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_live_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_live_workflow_lines_path);
    const text_live_workflow_lines = try guard.readUtf8File(io, allocator, text_live_workflow_lines_path);
    defer allocator.free(text_live_workflow_lines);
    for (LIVE_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_live_workflow_lines, marker, 1);
    const text_live_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_live_makefile_lines_path);
    const text_live_makefile_lines = try guard.readUtf8File(io, allocator, text_live_makefile_lines_path);
    defer allocator.free(text_live_makefile_lines);
    for (LIVE_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_live_makefile_lines, marker, 1);
    const text_validator_present_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_present_markers_path);
    const text_validator_present_markers = try guard.readUtf8File(io, allocator, text_validator_present_markers_path);
    defer allocator.free(text_validator_present_markers);
    for (VALIDATOR_PRESENT_MARKERS) |marker| try guard.requireMarker(text_validator_present_markers, marker);
    const text_validator_gap_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_gap_markers_path);
    const text_validator_gap_markers = try guard.readUtf8File(io, allocator, text_validator_gap_markers_path);
    defer allocator.free(text_validator_gap_markers);
    for (VALIDATOR_GAP_MARKERS) |marker| try guard.requireMarker(text_validator_gap_markers, marker);
    const text_doc_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-validator-coverage-gap.md");
    defer allocator.free(text_doc_markers_path);
    const text_doc_markers = try guard.readUtf8File(io, allocator, text_doc_markers_path);
    defer allocator.free(text_doc_markers);
    for (DOC_MARKERS) |marker| try guard.requireMarker(text_doc_markers, marker);
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
