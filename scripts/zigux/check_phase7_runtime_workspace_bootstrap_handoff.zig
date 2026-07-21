const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF=pass";
pub const self_test_pass_marker = "PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_SELF_TEST=pass";

const WORKFLOW_REQUIRED_ORDER = [_][]const u8{
    "run: zig test zigux/tests/runtime_trace_events_survey.zig",
    "run: zig run scripts/zigux/check_phase7_shared_control_gap.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase7_shared_control_gap.zig",
    "run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "run: zig run scripts/zigux/check_phase10_bootstrap_route.zig -- --self-test",
};

const WORKFLOW_PHASE7_HOOKS = [_][]const u8{
    "run: zig run scripts/zigux/check_phase7_shared_control_gap.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase7_shared_control_gap.zig",
    "run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
};

const WORKFLOW_FORBIDDEN_LINES = [_][]const u8{
    "run: make -C zigux phase7-validate",
    "run: zig run scripts/zigux/validate_phase7.zig -- --self-test",
    "run: zig run scripts/zigux/validate_phase7.zig",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
};

const VALIDATOR_REQUIRED_ORDER = [_][]const u8{
    "run_checker_self_test(root, CHECKER_PATH)",
    "run_checker(root, CHECKER_PATH)",
    "run_checker_self_test(root, BUILD_WIRING_CHECKER_PATH)",
    "run_checker(root, BUILD_WIRING_CHECKER_PATH)",
    "run_checker_self_test(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH)",
    "run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, \"--root\")",
    "run_checker_self_test(root, CMDLINE_PACKET_CHECKER_PATH)",
    "run_checker(root, CMDLINE_PACKET_CHECKER_PATH)",
    "run_checker_self_test(root, ARGV_SPLIT_PACKET_CHECKER_PATH)",
    "run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)",
    "run_checker_self_test(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)",
    "run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, \"--root\")",
    "run_checker_self_test(root, RBTREE_PARITY_PACKET_CHECKER_PATH)",
    "run_checker(root, RBTREE_PARITY_PACKET_CHECKER_PATH)",
};

const MAKEFILE_REQUIRED_LINES = [_][]const u8{
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
};

const MAKEFILE_FORBIDDEN_LINES = [_][]const u8{
    "phase7-test:",
    "phase7:",
};

const BUILD_TEST_STEP_ORDER = [_][]const u8{
    "test_step.dependOn(&run_string_helpers_tests.step);",
    "test_step.dependOn(&run_string_helpers_survey_tests.step);",
    "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
    "test_step.dependOn(&run_string_helpers_format_boundary_tests.step);",
    "test_step.dependOn(&run_cmdline_tests.step);",
    "test_step.dependOn(&run_cmdline_survey_tests.step);",
    "test_step.dependOn(&run_argv_split_tests.step);",
    "test_step.dependOn(&run_argv_split_survey_tests.step);",
    "test_step.dependOn(&run_rbtree_tests.step);",
    "test_step.dependOn(&run_rbtree_survey_tests.step);",
};

const CATALOG_REQUIRED_SNIPPETS = [_][]const u8{
    "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.",
    "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_required_order_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_workflow_required_order_path);
    const text_workflow_required_order = try guard.readUtf8File(io, allocator, text_workflow_required_order_path);
    defer allocator.free(text_workflow_required_order);
    for (WORKFLOW_REQUIRED_ORDER) |marker| try guard.requireMarker(text_workflow_required_order, marker);
    const text_workflow_phase7_hooks_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_workflow_phase7_hooks_path);
    const text_workflow_phase7_hooks = try guard.readUtf8File(io, allocator, text_workflow_phase7_hooks_path);
    defer allocator.free(text_workflow_phase7_hooks);
    for (WORKFLOW_PHASE7_HOOKS) |marker| try guard.requireMarker(text_workflow_phase7_hooks, marker);
    const text_workflow_forbidden_lines_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_workflow_forbidden_lines_path);
    const text_workflow_forbidden_lines = try guard.readUtf8File(io, allocator, text_workflow_forbidden_lines_path);
    defer allocator.free(text_workflow_forbidden_lines);
    for (WORKFLOW_FORBIDDEN_LINES) |marker| try guard.requireExactLineCount(text_workflow_forbidden_lines, marker, 1);
    const text_validator_required_order_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_validator_required_order_path);
    const text_validator_required_order = try guard.readUtf8File(io, allocator, text_validator_required_order_path);
    defer allocator.free(text_validator_required_order);
    for (VALIDATOR_REQUIRED_ORDER) |marker| try guard.requireMarker(text_validator_required_order, marker);
    const text_makefile_required_lines_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_makefile_required_lines_path);
    const text_makefile_required_lines = try guard.readUtf8File(io, allocator, text_makefile_required_lines_path);
    defer allocator.free(text_makefile_required_lines);
    for (MAKEFILE_REQUIRED_LINES) |marker| try guard.requireExactLineCount(text_makefile_required_lines, marker, 1);
    const text_makefile_forbidden_lines_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_makefile_forbidden_lines_path);
    const text_makefile_forbidden_lines = try guard.readUtf8File(io, allocator, text_makefile_forbidden_lines_path);
    defer allocator.free(text_makefile_forbidden_lines);
    for (MAKEFILE_FORBIDDEN_LINES) |marker| try guard.requireExactLineCount(text_makefile_forbidden_lines, marker, 1);
    const text_build_test_step_order_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_build_test_step_order_path);
    const text_build_test_step_order = try guard.readUtf8File(io, allocator, text_build_test_step_order_path);
    defer allocator.free(text_build_test_step_order);
    for (BUILD_TEST_STEP_ORDER) |marker| try guard.requireMarker(text_build_test_step_order, marker);
    const text_catalog_required_snippets_path = try guard.joinPath(allocator, root, ".");
    defer allocator.free(text_catalog_required_snippets_path);
    const text_catalog_required_snippets = try guard.readUtf8File(io, allocator, text_catalog_required_snippets_path);
    defer allocator.free(text_catalog_required_snippets);
    for (CATALOG_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_catalog_required_snippets, marker);
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
