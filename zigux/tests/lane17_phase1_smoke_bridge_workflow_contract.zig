const std = @import("std");

const workflow_path = @import("options").workflow_path;

const phase3_test = "        run: zig build phase3-test --build-file zigux/tests/build.zig";
const phase3_dump = "        run: zig build phase3-dump --build-file zigux/tests/build.zig";
const phase1_smoke = "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";
const phase4_reality_selftest = "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test";
const phase4_reality_check = "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py";

test "phase 3 shared routes hand back through phase 1 smoke before phase 4" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try expectUniqueLine(workflow, phase3_test);
    try expectUniqueLine(workflow, phase3_dump);
    try expectUniqueLine(workflow, phase1_smoke);
    try expectUniqueLine(workflow, phase4_reality_selftest);
    try expectUniqueLine(workflow, phase4_reality_check);

    try expectOrdered(workflow, &.{
        phase3_test,
        phase3_dump,
        phase1_smoke,
        phase4_reality_selftest,
        phase4_reality_check,
    });
}

test "contract rejects a missing phase 1 shared smoke bridge" {
    const sample =
        phase3_test ++ "\n" ++
        phase3_dump ++ "\n" ++
        phase4_reality_selftest ++ "\n" ++
        phase4_reality_check ++ "\n";

    try std.testing.expectError(error.MissingMarker, checkWorkflow(sample));
}

test "contract rejects phase 1 smoke before phase 3 dump completes" {
    const sample =
        phase3_test ++ "\n" ++
        phase1_smoke ++ "\n" ++
        phase3_dump ++ "\n" ++
        phase4_reality_selftest ++ "\n" ++
        phase4_reality_check ++ "\n";

    try std.testing.expectError(error.OutOfOrderMarker, checkWorkflow(sample));
}

test "contract rejects phase 4 checks before phase 1 smoke" {
    const sample =
        phase3_test ++ "\n" ++
        phase3_dump ++ "\n" ++
        phase4_reality_selftest ++ "\n" ++
        phase1_smoke ++ "\n" ++
        phase4_reality_check ++ "\n";

    try std.testing.expectError(error.OutOfOrderMarker, checkWorkflow(sample));
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn checkWorkflow(workflow: []const u8) !void {
    try expectUniqueLine(workflow, phase3_test);
    try expectUniqueLine(workflow, phase3_dump);
    try expectUniqueLine(workflow, phase1_smoke);
    try expectUniqueLine(workflow, phase4_reality_selftest);
    try expectUniqueLine(workflow, phase4_reality_check);

    try expectOrdered(workflow, &.{
        phase3_test,
        phase3_dump,
        phase1_smoke,
        phase4_reality_selftest,
        phase4_reality_check,
    });
}

fn expectUniqueLine(text: []const u8, marker: []const u8) !void {
    _ = try lineStartOfUnique(text, marker);
}

fn expectOrdered(text: []const u8, markers: []const []const u8) !void {
    var previous: ?usize = null;
    for (markers) |marker| {
        const found = try lineStartOfUnique(text, marker);
        if (previous) |last| {
            if (found <= last) return error.OutOfOrderMarker;
        }
        previous = found;
    }
}

fn lineStartOfUnique(text: []const u8, marker: []const u8) !usize {
    var count: usize = 0;
    var line_start: usize = 0;
    var found_start: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, line, marker)) {
            count += 1;
            found_start = line_start;
        }
        line_start += line.len + 1;
    }

    if (count == 0) return error.MissingMarker;
    if (count != 1) return error.DuplicateMarker;
    return found_start;
}
