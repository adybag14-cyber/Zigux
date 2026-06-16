const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass";

const REQUIRED_CHECKER_MARKERS = [_][]const u8{
    "PARKED_SHARED_CONTROL_PATHS = [",
    "\"scripts\\zigux/check_phase7_make_wrapper.zig\",",
    "READABLE_NON_OWNER_FILES = [",
    "\"zigux/tests/phase7_build.zig\",",
    "\"scripts\\zigux/validate_phase7.zig\",",
    "print(\"PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass\")",
    "print(\"PHASE7_SHARED_CONTROL_GAP=pass\")",
};

const REQUIRED_SEQUENCING_MARKERS = [_][]const u8{
    "- shared control-surface packet, lane `P7-Y05`:",
    "- `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `scripts\\zigux/check_phase7_shared_control_gap.zig`",
    "- `scripts\\zigux/validate_phase7.zig`",
    "the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` exposes the narrow `phase7-validate` foothold plus the dedicated helper-local `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, and still omits aggregate `phase7-test`, aggregate `phase7`, and the other helper-local Phase 7 wrapper routes.",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase7_shared_control_gap.zig --self-test",
    "run: zig run scripts\\zigux/check_phase7_shared_control_gap.zig",
    "run: zig run scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
};

const FORBIDDEN_WORKFLOW_LINES = [_][]const u8{
    "run: make -C zigux phase7-validate",
    "run: make -C zigux phase7-test",
    "run: python3 scripts/zigux/validate-phase7 --self-test",
    "run: zig run scripts\\zigux/validate_phase7.zig --self-test",
    "run: zig run scripts\\zigux/validate_phase7.zig",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
    "phase7-rbtree-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig",
    "phase7-rbtree-survey:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase7-rbtree-survey --build-file zigux/tests/phase7_build.zig",
};

const REQUIRED_VALIDATOR_MARKERS = [_][]const u8{
    "MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path(\"scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig\")",
    "run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, \"--root\")",
};

const FORBIDDEN_MAKEFILE_LINES = [_][]const u8{
    "phase7-test:",
    "phase7:",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_checker_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_checker_markers_path);
    const text_required_checker_markers = try guard.readUtf8File(io, allocator, text_required_checker_markers_path);
    defer allocator.free(text_required_checker_markers);
    for (REQUIRED_CHECKER_MARKERS) |marker| try guard.requireMarker(text_required_checker_markers, marker);
    const text_required_sequencing_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_sequencing_markers_path);
    const text_required_sequencing_markers = try guard.readUtf8File(io, allocator, text_required_sequencing_markers_path);
    defer allocator.free(text_required_sequencing_markers);
    for (REQUIRED_SEQUENCING_MARKERS) |marker| try guard.requireMarker(text_required_sequencing_markers, marker);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
    const text_forbidden_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_forbidden_workflow_lines_path);
    const text_forbidden_workflow_lines = try guard.readUtf8File(io, allocator, text_forbidden_workflow_lines_path);
    defer allocator.free(text_forbidden_workflow_lines);
    for (FORBIDDEN_WORKFLOW_LINES) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_workflow_lines, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_required_validator_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_validator_markers_path);
    const text_required_validator_markers = try guard.readUtf8File(io, allocator, text_required_validator_markers_path);
    defer allocator.free(text_required_validator_markers);
    for (REQUIRED_VALIDATOR_MARKERS) |marker| try guard.requireMarker(text_required_validator_markers, marker);
    const text_forbidden_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_forbidden_makefile_lines_path);
    const text_forbidden_makefile_lines = try guard.readUtf8File(io, allocator, text_forbidden_makefile_lines_path);
    defer allocator.free(text_forbidden_makefile_lines);
    for (FORBIDDEN_MAKEFILE_LINES) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_makefile_lines, marker) != null) return guard.GuardError.MissingMarker;
    }
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
