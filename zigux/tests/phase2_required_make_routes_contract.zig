const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-required-make-routes.py";

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MissingExpectedMarker;
        cursor += found + needle.len;
    }
}

test "phase2 required make routes checker keeps policy driven route expansion" {
    const checker = try readFile(checker_path, 512 * 1024);
    defer testing.allocator.free(checker);

    try expectContains(checker, "CURRENT_REQUIRED_MAKE_ROUTES = (");
    inline for (.{
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    }) |route| {
        try expectContains(checker, route);
    }

    try expectInOrder(checker, &.{
        "load_required_make_routes",
        "format_route_marker",
        "format_workflow_route_line",
        "format_makefile_target_line",
        "collect_required_route_makefile_issues",
    });
    try expectContains(checker, "required_make_routes");
    try expectContains(checker, "MISSING_REQUIRED_ROUTE_PHONY_TARGET");
    try expectContains(checker, "MISSING_REQUIRED_ROUTE_TARGET");
    try expectContains(checker, "DUPLICATE_REQUIRED_ROUTE_TARGET");
    try expectContains(checker, "duplicate required_make_routes");
}

test "phase2 required make routes checker preserves workflow makefile and surface vocabulary" {
    const checker = try readFile(checker_path, 512 * 1024);
    defer testing.allocator.free(checker);

    try expectContains(checker, "WORKFLOW_LINES = (");
    try expectContains(checker, "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test");
    try expectContains(checker, "run: python3 scripts/zigux/check-phase2-required-make-routes.py");
    try expectContains(checker, "REQUIRED_PHASE2_PHONY_LINE");
    try expectContains(checker, ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");

    try expectInOrder(checker, &.{
        "TOOLCHAIN_ALLOWED_RECIPE_LINES = (",
        "check-zig-toolchain.py --self-test",
        "check-phase2-toolchain-pinning.py",
        "check-phase2-toolchain-pin-scope.py",
        "TOOLCHAIN_OVERLAP_FRAGMENTS = (",
    });
    try expectContains(checker, "TOOLCHAIN_ROUTE_OVERLAP");
    try expectContains(checker, "FULL_ROUTE_SURFACE_CODES = (");
    try expectContains(checker, "POLICY_ROUTE_SURFACE_CODES = (");
    try expectContains(checker, "POLICY_SUMMARY_SURFACE_CODES = (");
}

test "phase2 required make routes checker keeps public output and self-test envelope stable" {
    const checker = try readFile(checker_path, 512 * 1024);
    defer testing.allocator.free(checker);

    try expectContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST_CASE_COUNT=");
    try expectContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES=invalid");
    try expectContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES=fail");
    try expectContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES=pass");
    try expectContains(checker, "PHASE2_REQUIRED_POLICY_PATH=");
    try expectContains(checker, "PHASE2_REQUIRED_MAKEFILE_PATH=");
    try expectContains(checker, "PHASE2_REQUIRED_ROUTE_LIST=");
    try expectContains(checker, "PHASE2_CURRENT_PACKET_ROUTE_COUNT=");
    try expectContains(checker, "PHASE2_TOOLCHAIN_ROUTE_RECIPE_COUNT=");
    try expectContains(checker, "PHASE2_TOOLCHAIN_ROUTE_BOUNDARY=bounded");
    try expectContains(checker, "PHASE2_REQUIRED_ROUTE_STATUS=present");

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT =");
    try expectContains(checker, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    try expectContains(checker, "extra_route = \"phase2-future\"");
    try expectContains(checker, "policy_path.write_text(\"{not-json}\\\\n\", encoding=\"utf-8\")");
    try expectNotContains(checker, "PHASE2_REQUIRED_MAKE_ROUTES=closed");
}
