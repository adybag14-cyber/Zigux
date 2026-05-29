const std = @import("std");

const checker_source = @embedFile("check-phase1-bench.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "bench expectation JSON keeps duplicate-key tracking wired into parsing" {
    try expectContains("class DuplicateTrackingDict");
    try expectContains("self.duplicate_keys");
    try expectContains("if key in self and key not in self.duplicate_keys");
    try expectContains("json.loads(text, object_pairs_hook=DuplicateTrackingDict)");

    try expectBefore("class DuplicateTrackingDict", "def load_expectations_text");
    try expectBefore("def load_expectations_text", "def validate_expectations");
}

test "bench expectation validation reports duplicate key classes before set checks" {
    try expectBefore("expectations_duplicate_keys", "expectations_status");
    try expectBefore("expectations_duplicate_iteration_keys", "expectations_missing_iterations");
    try expectBefore("expectations_duplicate_exact_checksum_keys", "expectations_missing_exact_checksums");
    try expectBefore("expectations_duplicate_checksums", "expectations_missing_checksums");
}

test "checker self-test and diagnostics preserve duplicate-guard coverage" {
    try expectContains("duplicate_checksum_expectations");
    try expectContains("duplicate_root_expectations");
    try expectContains("expectations_duplicate_keys");
    try expectContains("expectations_duplicate_checksums");
    try expectContains("expectations_duplicate_exact_checksum_keys");
    try expectContains("expectations_duplicate_iteration_keys");
}
