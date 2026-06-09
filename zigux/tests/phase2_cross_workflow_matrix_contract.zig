const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }
    return count;
}

test "workflow keeps cross checker sequence before cross make route" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    const direct_self_test = "Self-test current Phase 2 cross checker";
    const direct_check = "Check current Phase 2 direct cross-route packet";
    const alignment_self_test = "Self-test current Phase 2 cross selftest alignment checker";
    const alignment_check = "Check current Phase 2 cross alignment packet";
    const make_route = "Run current Phase 2 cross make route";

    try requireContains(workflow, "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-phase2-cross.py");
    try requireContains(workflow, "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try requireContains(workflow, "make -C zigux phase2-cross");

    try requireOrdered(workflow, direct_self_test, direct_check);
    try requireOrdered(workflow, direct_check, alignment_self_test);
    try requireOrdered(workflow, alignment_self_test, alignment_check);
    try requireOrdered(workflow, alignment_check, make_route);
}

test "workflow keeps cross route inside Phase 2 aggregate run band" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try requireOrdered(
        workflow,
        "Run current Phase 2 fixdep make route",
        "Run current Phase 2 cross make route",
    );
    try requireOrdered(
        workflow,
        "Run current Phase 2 cross make route",
        "Run current Phase 2 genksyms make route",
    );
    try requireOrdered(
        workflow,
        "Run current Phase 2 cross make route",
        "Run current Phase 2 aggregate make route",
    );
}

test "fixture keeps current two-target matrix boundary" {
    const allocator = std.testing.allocator;
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try requireContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(fixture, "\"archive_target_scope\"");
    try requireContains(fixture, "\"target\": \"x86_64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"archive_required\"");
    try requireContains(fixture, "\"target\": \"aarch64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expect(std.mem.indexOf(u8, fixture, "riscv64-linux") == null);
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(fixture, "\"target\": "));
}

test "workflow and fixture stay route-aligned" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    const route = "make -C zigux phase2-cross";
    try requireContains(workflow, route);
    try requireContains(fixture, route);
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixture, route));
}
