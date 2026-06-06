const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-phase2-cross.py");
const alignment_source = @embedFile("check-phase2-cross-selftest-alignment.py");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn countExactLine(source: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, source, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn requireExactLineOnce(source: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), countExactLine(source, needle));
}

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, testing.allocator, .limited(limit));
}

test "direct cross checker keeps route and fixture contract markers" {
    try requireContains(checker_source, "Guard the rematerialized Phase 2 direct cross-route packet.");
    try requireContains(checker_source, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try requireContains(checker_source, "MAKEFILE = ROOT / \"zigux\" / \"Makefile\"");
    try requireContains(checker_source, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try requireContains(checker_source, "ROUTE = \"make -C zigux phase2-cross\"");
    try requireContains(checker_source, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try requireContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(checker_source, "print(\"PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass\")");
    try requireContains(checker_source, "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")");
    try requireContains(checker_source, "print(f\"PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}\")");
    try requireContains(checker_source, "print(f\"PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}\")");

    try requireOrder(checker_source, "MAKEFILE_LINES = (", "EXPECTED_FIXTURE_PHASE = \"Phase 2\"");
    try requireOrder(checker_source, "archive_required_targets: set[str] = set()", "if archive_required_targets != set(archive_target_scope):");
    try requireOrder(checker_source, "if args.self_test:", "issues = collect_issues(args.root.resolve())");
}

test "make wrapper exposes the phase2 cross route exactly once" {
    const makefile_source = try readRepoFile("zigux/Makefile", 1024 * 1024);
    defer testing.allocator.free(makefile_source);

    try requireExactLineOnce(makefile_source, "phase2-cross:");
    try requireExactLineOnce(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try requireExactLineOnce(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try requireExactLineOnce(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try requireExactLineOnce(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");

    try requireOrder(makefile_source, "phase2-cross:", "phase2-genksyms: phase2-toolchain");
    try requireOrder(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");
}

test "cross target fixture stays a two-target Phase 2 matrix" {
    const cross_targets_fixture = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 128 * 1024);
    defer testing.allocator.free(cross_targets_fixture);

    try requireContains(cross_targets_fixture, "\"phase\": \"Phase 2\"");
    try requireContains(cross_targets_fixture, "\"status\": \"active\"");
    try requireContains(cross_targets_fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(cross_targets_fixture, "\"archive_target_scope\": [");
    try requireContains(cross_targets_fixture, "\"x86_64-linux\"");
    try requireContains(cross_targets_fixture, "\"aarch64-linux\"");
    try requireContains(cross_targets_fixture, "\"validation_mode\": \"archive_required\"");
    try requireContains(cross_targets_fixture, "\"validation_mode\": \"route_contract_only\"");

    try requireOrder(cross_targets_fixture, "\"archive_target_scope\": [", "\"cross_targets\": [");
    try requireOrder(cross_targets_fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
    try testing.expectEqual(@as(usize, 2), countExactLine(cross_targets_fixture, "\"route\": \"make -C zigux phase2-cross\""));
}

test "alignment guard ties docs reminders back to the same supported matrix" {
    try requireContains(alignment_source, "CROSS_TARGETS = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try requireContains(alignment_source, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try requireContains(alignment_source, "ROUTE = \"make -C zigux phase2-cross\"");
    try requireContains(alignment_source, "\"phase2-cross\",");
    try requireContains(alignment_source, "\"python3 scripts/zigux/check-phase2-cross.py --self-test\"");
    try requireContains(alignment_source, "\"python3 scripts/zigux/check-phase2-cross.py\"");
    try requireContains(alignment_source, "\"zigux/tests/fixtures/phase2_cross_targets.json\"");
    try requireContains(alignment_source, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");

    try requireOrder(alignment_source, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")", "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    try requireOrder(alignment_source, "def load_expected_fixture(root: Path) -> dict[str, object]:", "def collect_fixture_issues(payload: object, root: Path) -> list[tuple[str, str]]:");
}
