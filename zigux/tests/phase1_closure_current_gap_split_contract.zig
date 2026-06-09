const std = @import("std");
const testing = std.testing;

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const tests_readme_path = "zigux/tests/README.md";
const validator_path = "scripts/zigux/validate-phase1-closure.py";

const current_packet_marker =
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`";

const gap_packet_marker =
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

const current_packet_paths = [_][]const u8{
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
};

const gap_packet_paths = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "phase1 closure note keeps narrow current packet and broader gap packet split" {
    const closure_note = try readRepoFile(testing.allocator, closure_note_path);
    defer testing.allocator.free(closure_note);

    try requireContains(closure_note, current_packet_marker);
    try requireContains(closure_note, gap_packet_marker);
    try requireContains(closure_note, "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.");

    for (current_packet_paths) |path| {
        try requireContains(closure_note, path);
    }
    for (gap_packet_paths) |path| {
        try requireContains(closure_note, path);
    }

    try testing.expect(countOccurrences(closure_note, "`PHASE1_CURRENT_REMINDER_PACKET=") == 1);
    try testing.expect(countOccurrences(closure_note, "`PHASE1_CURRENT_GAP_PACKET=") == 1);
}

test "tests README preserves direct-readback packet and parked companion wording" {
    const tests_readme = try readRepoFile(testing.allocator, tests_readme_path);
    defer testing.allocator.free(tests_readme);

    try requireContains(tests_readme, "current direct-readback Phase 1 reminder packet:");
    try requireContains(tests_readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet");
    try requireContains(tests_readme, "current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`");
    try requireContains(tests_readme, "nine shared-replay parked helpers reopen only for packet or fixture drift");

    for (current_packet_paths) |path| {
        try requireContains(tests_readme, path);
    }
    for (gap_packet_paths) |path| {
        try requireContains(tests_readme, path);
    }
}

test "validator owns exact current and gap markers without promoting gap files into required inputs" {
    const validator = try readRepoFile(testing.allocator, validator_path);
    defer testing.allocator.free(validator);

    try requireContains(validator, "\"reminder_packet\":");
    try requireContains(validator, "\"gap_packet\":");
    try requireContains(validator, current_packet_marker);
    try requireContains(validator, gap_packet_marker);

    for (current_packet_paths) |path| {
        try requireContains(validator, path);
    }
    for (gap_packet_paths) |path| {
        try requireContains(validator, path);
        try testing.expect(std.mem.count(u8, validator, path) == 1);
    }

    try requireNotContains(validator, "Path(\"scripts/zigux/validate-phase1.py\")");
    try requireNotContains(validator, "Path(\"scripts/zigux/check-phase1-parity.py\")");
    try requireNotContains(validator, "Path(\"zigux/tests/phase1_bench.zig\")");
    try requireNotContains(validator, "Path(\"zigux/tests/fixtures/phase1_bench_expectations.json\")");
    try requireNotContains(validator, "Path(\"zigux/tests/fixtures/phase1_helpers_c_harness.c\")");
}
