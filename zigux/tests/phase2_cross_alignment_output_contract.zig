const std = @import("std");

const alignment_checker_path = ".github/../scripts/zigux/check-phase2-cross-selftest-alignment.py";
const cross_fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

test "alignment checker keeps public pass and count output envelope" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, alignment_checker_path);
    defer allocator.free(source);

    try expectContains(source, "PHASE2_CROSS_ALIGNMENT=pass");
    try expectContains(source, "PHASE2_CROSS_ALIGNMENT=fail");
    try expectContains(source, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(source, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=");
    try expectContains(source, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=");
    try expectContains(source, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try expectContains(source, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
    try expectOrdered(source, "issues = collect_issues(args.root.resolve())", "print(\"PHASE2_CROSS_ALIGNMENT=pass\")");
    try expectOrdered(source, "expected_fixture = load_expected_fixture(args.root.resolve())", "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
}

test "alignment checker pins supported target boundary and dynamic mode split" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, alignment_checker_path);
    defer allocator.free(source);
    const fixture = try readFile(allocator, cross_fixture_path);
    defer allocator.free(fixture);

    try expectContains(source, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(source, "\"archive_required\" if target in seen_scope else \"route_contract_only\"");
    try expectContains(source, "unsupported archive_target_scope targets");
    try expectContains(source, "INVALID_CROSS_TARGET_MATRIX");
    try expectContains(source, "INVALID_CROSS_TARGET_FIXTURE_FIELD");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
}

test "alignment checker keeps cross route and stale matrix exclusions review visible" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, alignment_checker_path);
    defer allocator.free(source);

    try expectContains(source, "ROUTE = \"make -C zigux phase2-cross\"");
    try expectContains(source, "MAKEFILE_LINES = (");
    try expectContains(source, "\"phase2-cross:\"");
    try expectContains(source, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\"");
    try expectContains(source, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\"");
    try expectContains(source, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    try expectContains(source, "\"phase2-cross\"");
    try expectContains(source, "archive_target_scope");
    try expectContains(source, "required_make_routes");
    try std.testing.expect(countOccurrences(source, "riscv64-linux") == 1);
}
