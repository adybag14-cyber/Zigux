const std = @import("std");

const validator_path = "scripts/zigux/validate-phase2-closure.py";

fn readValidator() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        validator_path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

test "phase2 closure validator publishes stable success envelope" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION=pass");
    try expectContains(validator, "PHASE2_CLOSURE_STATUS=parked");
    try expectContains(validator, "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure");
    try expectContains(validator, "PHASE2_CLOSURE_REMAINING_GAPS=");
    try expectOrdered(
        validator,
        "PHASE2_CLOSURE_VALIDATION=pass",
        "PHASE2_CLOSURE_REMAINING_GAPS=",
    );
}

test "phase2 closure validator self-test envelope stays explicit" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "def run_self_test() -> int:");
    try expectContains(validator, "checks_run = 0");
    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass");
    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}");
    try expectContains(validator, "parser.add_argument(\"--self-test\"");
    try expectContains(validator, "if args.self_test:");
    try std.testing.expect(countOccurrences(validator, "checks_run += 1") == 8);
    try expectOrdered(
        validator,
        "if args.self_test:",
        "issues = collect_issues(args.root.resolve())",
    );
}

test "phase2 closure validator fail-closed issue vocabulary is public" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    const issue_codes = [_][]const u8{
        "MISSING_REQUIRED_FILE",
        "INVALID_MANIFEST_SHAPE",
        "INVALID_GENKSYMS_MANIFEST_SHAPE",
        "UNEXPECTED_MANIFEST_GAPS",
        "MISSING_MANIFEST_SURFACE",
        "MISSING_CLOSURE_LINE",
        "MISSING_CLOSURE_MARKER",
        "MISSING_WORKFLOW_LINE",
        "DUPLICATE_WORKFLOW_LINE",
        "MISSING_MAKEFILE_LINE",
        "DUPLICATE_MAKEFILE_LINE",
    };

    for (issue_codes) |code| {
        try expectContains(validator, code);
    }

    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION=fail");
    try expectContains(validator, "print(f\"{code}_START\")");
    try expectContains(validator, "print(f\"{code}_END\")");
    try expectOrdered(validator, "def collect_issues(root: Path)", "def emit_issues");
    try expectOrdered(validator, "def emit_issues", "def build_self_test_root");
}

test "phase2 closure validator keeps manifest surfaces and optional archive paths explicit" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    const surface_keys = [_][]const u8{
        "\"review_surfaces\"",
        "\"closure_notes\"",
        "\"validators\"",
        "\"checkers\"",
        "\"bootstrap_helpers\"",
        "\"archive_support\"",
        "\"artifact_support\"",
        "\"bridge_helpers\"",
        "\"cross_route_support\"",
        "\"fixdep_support\"",
        "\"fixture_roster\"",
        "\"make_wrappers\"",
        "\"policy\"",
    };

    try expectContains(validator, "MANIFEST_SURFACE_KEYS = (");
    for (surface_keys) |key| {
        try expectContains(validator, key);
    }

    try expectContains(validator, "present_surfaces = manifest.get(\"present_surfaces\")");
    try expectContains(validator, "manifest_surface_values[key] = require_string_list(issues, manifest, key)");
    try expectContains(validator, "MISSING_MANIFEST_SURFACE");
    try expectContains(validator, "OPTIONAL_MANIFEST_SURFACE_PATHS = {");
    try expectOrdered(validator, "MANIFEST_SURFACE_KEYS = (", "for key in MANIFEST_SURFACE_KEYS:");
    try expectOrdered(validator, "OPTIONAL_MANIFEST_SURFACE_PATHS = {", "if value in OPTIONAL_MANIFEST_SURFACE_PATHS");
    try expectContains(validator, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(validator, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json");
}
