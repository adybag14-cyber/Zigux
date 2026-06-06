const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-required-make-routes.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const makefile_path = "zigux/Makefile";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectInOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "required make routes checker keeps phase2-cross in derived route rosters" {
    const checker = try readRepoFile(testing.allocator, checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "\"phase2-cross\",");
    try expectContains(checker, "CURRENT_REQUIRED_MAKE_ROUTES = (");
    try expectContains(checker, "CURRENT_POLICY_ROUTE_MARKERS = tuple(f\"`make -C zigux {route}`\" for route in CURRENT_REQUIRED_MAKE_ROUTES)");
    try expectContains(checker, "CURRENT_WORKFLOW_ROUTE_LINES = tuple(f\"run: make -C zigux {route}\" for route in CURRENT_REQUIRED_MAKE_ROUTES)");
    try expectContains(checker, "def format_makefile_target_line(route: str) -> str:");
    try expectContains(checker, "return f\"{route}:\"");

    try expectInOrder(checker, "\"phase2-kconfig\",", "\"phase2-cross\",");
    try expectInOrder(checker, "\"phase2-cross\",", "\"phase2-genksyms\",");
}

test "required make routes checker fail-closes on phase2-cross workflow and makefile drift" {
    const checker = try readRepoFile(testing.allocator, checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "for line in workflow_route_lines:");
    try expectContains(checker, "(\"MISSING_WORKFLOW_ROUTE_LINES\", line)");
    try expectContains(checker, "(\"DUPLICATE_WORKFLOW_ROUTE_LINES\", f\"{line}:count={count}\")");
    try expectContains(checker, "collect_required_route_makefile_issues");
    try expectContains(checker, "(\"MISSING_REQUIRED_ROUTE_PHONY_TARGET\", route)");
    try expectContains(checker, "(\"MISSING_REQUIRED_ROUTE_TARGET\", target_line)");
    try expectContains(checker, "(\"DUPLICATE_REQUIRED_ROUTE_TARGET\", f\"{route}:count={count}\")");
    try expectContains(checker, "extra_route = \"phase2-future\"");
    try expectContains(checker, "f\"run: make -C zigux {extra_route}\"");
    try expectContains(checker, "f\"`make -C zigux {extra_route}`\"");
}

test "toolchain route boundary explicitly excludes the phase2 cross checker packet" {
    const checker = try readRepoFile(testing.allocator, checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "TOOLCHAIN_ROUTE = \"phase2-toolchain\"");
    try expectContains(checker, "TOOLCHAIN_OVERLAP_FRAGMENTS = (");
    try expectContains(checker, "\"check-phase2-cross.py\",");
    try expectContains(checker, "\"check-phase2-cross-selftest-alignment.py\",");
    try expectContains(checker, "\"make -C zigux phase2-\",");
    try expectContains(checker, "(\"TOOLCHAIN_ROUTE_OVERLAP\", recipe_line)");
    try expectContains(checker, "\"\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\",");
    try expectContains(checker, "(\"TOOLCHAIN_ROUTE_OVERLAP\",");
}

test "policy fixture and makefile keep current two-target cross boundary" {
    const policy = try readRepoFile(testing.allocator, policy_path);
    defer testing.allocator.free(policy);
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);
    const makefile = try readRepoFile(testing.allocator, makefile_path);
    defer testing.allocator.free(makefile);

    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectContains(policy, "\"required_make_routes\": [");
    try expectContains(policy, "\"phase2-cross\"");

    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");

    try expectContains(makefile, "phase2-cross:");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}
