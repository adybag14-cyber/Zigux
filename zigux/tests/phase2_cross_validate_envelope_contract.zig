const std = @import("std");
const testing = std.testing;

const validate_phase2_path = "scripts/zigux/validate-phase2.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try testing.expect(first_index < second_index);
}

test "validate-phase2 keeps the direct cross packet in required paths and workflow lines" {
    const allocator = testing.allocator;
    const validator = try readRepoFile(allocator, validate_phase2_path);
    defer allocator.free(validator);

    try expectContains(validator, "\"scripts/zigux/check-phase2-cross.py\",");
    try expectContains(validator, "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\",");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_cross_targets.json\",");

    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-cross.py --self-test\",");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-cross.py\",");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\",");
    try expectContains(validator, "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\",");

    try expectBefore(
        validator,
        "\"run: python3 scripts/zigux/check-phase2-cross.py --self-test\",",
        "\"run: python3 scripts/zigux/check-phase2-cross.py\",",
    );
    try expectBefore(
        validator,
        "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\",",
        "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\",",
    );
}

test "validate-phase2 derives the cross make route from policy and exposes validator counts" {
    const allocator = testing.allocator;
    const validator = try readRepoFile(allocator, validate_phase2_path);
    defer allocator.free(validator);

    try expectContains(validator, "DEFAULT_REQUIRED_MAKE_ROUTES = (");
    try expectContains(validator, "\"phase2-cross\",");
    try expectContains(validator, "def load_required_make_routes(root: Path) -> tuple[str, ...]:");
    try expectContains(validator, "def expected_workflow_route_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(validator, "return tuple(f\"run: make -C zigux {route}\"");
    try expectContains(validator, "def expected_makefile_dynamic_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(validator, "validate_prereqs = tuple(route for route in required_make_routes if route != \"phase2-validate\")");
    try expectContains(validator, "required_phase2_phony_line(required_make_routes)");

    try expectContains(validator, "PHASE2_VALIDATION=pass");
    try expectContains(validator, "PHASE2_VALIDATION=fail");
    try expectContains(validator, "PHASE2_VALIDATION_WORKFLOW_LINE_COUNT=");
    try expectContains(validator, "PHASE2_VALIDATION_REQUIRED_PATH_COUNT=");
}

test "validate-phase2 self-test guards cross route drift through dynamic workflow and required path loops" {
    const allocator = testing.allocator;
    const validator = try readRepoFile(allocator, validate_phase2_path);
    defer allocator.free(validator);

    try expectContains(validator, "expected_case_count = (");
    try expectContains(validator, "+ len(required_workflow_route_lines)");
    try expectContains(validator, "for marker in required_workflow_route_lines:");
    try expectContains(validator, "expect_issue(root, (\"MISSING_WORKFLOW_LINE\", marker))");
    try expectContains(validator, "expect_issue(root, (\"DUPLICATE_WORKFLOW_LINE\", f\"{marker}:count=2\"))");
    try expectContains(validator, "for rel in REQUIRED_PATHS[:-1]:");
    try expectContains(validator, "expect_issue(root, (\"MISSING_REQUIRED_PATH\", rel))");
    try expectContains(validator, "assert checks == expected_case_count");
    try expectContains(validator, "PHASE2_VALIDATION_SELF_TEST=pass");
    try expectContains(validator, "PHASE2_VALIDATION_SELF_TEST_CASE_COUNT=");
}

test "phase2 cross fixture remains the validator boundary for two supported route targets" {
    const allocator = testing.allocator;
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
}
