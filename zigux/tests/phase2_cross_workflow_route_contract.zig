const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const makefile_path = "zigux/Makefile";

const cross_self_test = "run: zig run scripts/zigux/check_phase2_cross.zig -- --self-test";
const cross_check = "run: zig run scripts/zigux/check_phase2_cross.zig";
const alignment_self_test = "run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig -- --self-test";
const alignment_check = "run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig";
const workflow_routes_self_test = "run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test";
const workflow_routes_check = "run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig";
const phase2_cross_route = "run: make -C zigux phase2-cross";
const phase2_fixdep_route = "run: make -C zigux phase2-fixdep";
const required_routes_self_test = "run: zig run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test";
const make_phase2_cross_rule = "phase2-cross:";
const make_cross_checker = "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig";
const make_alignment_checker = "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig";

const forbidden_workflow_markers = [_][]const u8{
    "Detect Phase 2 cross-target scope changes",
    "--target ${{ matrix.zig_target }}",
    "phase2-cross:",
    "matrix.zig_target",
};

const OrderError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrder,
    ForbiddenMarkerPresent,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024)) catch |err| switch (err) {
        error.FileNotFound => blk: {
            const fallback = try std.mem.concat(allocator, u8, &.{ "../../", path });
            defer allocator.free(fallback);
            break :blk try std.Io.Dir.cwd().readFileAlloc(std.testing.io, fallback, allocator, .limited(1024 * 1024));
        },
        else => return err,
    };
}

fn requireOnceLine(text: []const u8, marker: []const u8) !usize {
    var matches: usize = 0;
    var found_index: usize = 0;
    var cursor: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            matches += 1;
            found_index = cursor;
        }
        cursor += line.len + 1;
    }

    if (matches == 0) return OrderError.MissingMarker;
    if (matches != 1) return OrderError.DuplicateMarker;
    return found_index;
}

fn requireBefore(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireOnceLine(text, before);
    const after_index = try requireOnceLine(text, after);
    if (before_index >= after_index) return OrderError.OutOfOrder;
}

fn requireForbiddenAbsent(text: []const u8, forbidden: []const u8) !void {
    if (std.mem.indexOf(u8, text, forbidden) != null) return OrderError.ForbiddenMarkerPresent;
}

fn validateWorkflow(text: []const u8) !void {
    try requireBefore(text, cross_self_test, cross_check);
    try requireBefore(text, cross_check, alignment_self_test);
    try requireBefore(text, alignment_self_test, alignment_check);
    try requireBefore(text, alignment_check, workflow_routes_self_test);
    try requireBefore(text, workflow_routes_self_test, workflow_routes_check);
    try requireBefore(text, phase2_fixdep_route, phase2_cross_route);
    try requireBefore(text, phase2_cross_route, required_routes_self_test);

    for (forbidden_workflow_markers) |marker| {
        try requireForbiddenAbsent(text, marker);
    }
}

fn validateMakefile(text: []const u8) !void {
    try requireBefore(text, make_phase2_cross_rule, make_cross_checker);
    try requireBefore(text, make_cross_checker, make_alignment_checker);
}

test "workflow keeps direct cross checks before workflow-route checker and make route" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try validateWorkflow(workflow);
}

test "makefile phase2-cross route stays direct-checker scoped" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try validateMakefile(makefile);
}

test "contract catches stale matrix job text and route misordering" {
    const good_workflow =
        \\run: zig run scripts/zigux/check_phase2_cross.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_cross.zig
        \\run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig
        \\run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig
        \\run: make -C zigux phase2-fixdep
        \\run: make -C zigux phase2-cross
        \\run: zig run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test
    ;
    try validateWorkflow(good_workflow);

    const stale_matrix = good_workflow ++ "\nDetect Phase 2 cross-target scope changes\n";
    try std.testing.expectError(OrderError.ForbiddenMarkerPresent, validateWorkflow(stale_matrix));

    const reordered =
        \\run: zig run scripts/zigux/check_phase2_cross.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_cross.zig
        \\run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig
        \\run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig
        \\run: make -C zigux phase2-cross
        \\run: make -C zigux phase2-fixdep
        \\run: zig run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test
    ;
    try std.testing.expectError(OrderError.OutOfOrder, validateWorkflow(reordered));
}

test "contract catches duplicate workflow and makefile markers" {
    const duplicate_workflow =
        \\run: zig run scripts/zigux/check_phase2_cross.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_cross.zig
        \\run: zig run scripts/zigux/check_phase2_cross.zig
        \\run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig
        \\run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test
        \\run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig
        \\run: make -C zigux phase2-fixdep
        \\run: make -C zigux phase2-cross
        \\run: zig run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test
    ;
    try std.testing.expectError(OrderError.DuplicateMarker, validateWorkflow(duplicate_workflow));

    const good_makefile =
        \\phase2-cross:
        \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig -- --self-test
        \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig
        \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig -- --self-test
        \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig
    ;
    try validateMakefile(good_makefile);

    const duplicate_makefile = good_makefile ++ "\n    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig\n";
    try std.testing.expectError(OrderError.DuplicateMarker, validateMakefile(duplicate_makefile));
}
