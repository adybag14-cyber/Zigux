const std = @import("std");

const closure_note_rel = "Documentation/zigux/phase1-closure.md";
const validator_source_rel = "scripts/zigux/validate-phase1-closure.py";

const current_packet_marker =
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`";

const gap_packet_marker =
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

const historical_gap_paths = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

const forbidden_phase1_make_routes = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn sectionBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStart;
    const body_start = start_index + start.len;
    const end_offset = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingEnd;
    return haystack[body_start .. body_start + end_offset];
}

fn readSourceFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(512 * 1024),
    );
}

test "closure note keeps current reminder and historical gap packets split" {
    const closure_note = try readSourceFile(std.testing.allocator, closure_note_rel);
    defer std.testing.allocator.free(closure_note);

    try requireOnce(closure_note, "## Current Reminder Packet");
    try requireOnce(closure_note, "## Broader Closure Companions");
    try requireOnce(closure_note, "## Closure Validation");
    try requireOnce(closure_note, current_packet_marker);
    try requireOnce(closure_note, gap_packet_marker);

    const current_section = try sectionBetween(
        closure_note,
        "## Current Reminder Packet",
        "## Helper-Local Direct Anchor Reminder",
    );
    const gap_section = try sectionBetween(
        closure_note,
        "## Broader Closure Companions",
        "## Closure Validation",
    );

    try requireContains(current_section, "scripts/zigux/validate-phase1-closure.py");
    try requireContains(current_section, "zigux/tests/phase1_host_tools_smoke.zig");
    for (historical_gap_paths) |path| {
        try requireAbsent(current_section, path);
        try requireContains(gap_section, path);
    }
}

test "validator checks gap marker without promoting historical files" {
    const validator_source = try readSourceFile(std.testing.allocator, validator_source_rel);
    defer std.testing.allocator.free(validator_source);

    try requireContains(validator_source, "\"reminder_packet\":");
    try requireContains(validator_source, "\"gap_packet\":");
    try requireOnce(validator_source, current_packet_marker);
    try requireOnce(validator_source, gap_packet_marker);

    const required_files = try sectionBetween(validator_source, "REQUIRED_FILES = (", ")\n\nEXPECTED_HELPERS");
    const delegated_checkers = try sectionBetween(validator_source, "DELEGATED_CHECKERS = (", ")\n\n\ndef repo_root");

    try requireContains(required_files, "PHASE1_CLOSURE_REL");
    try requireContains(required_files, "PHASE1_SMOKE_REL");
    try requireContains(required_files, "MANIFEST_REL");
    for (historical_gap_paths) |path| {
        try requireAbsent(required_files, path);
        try requireAbsent(delegated_checkers, path);
    }
}

test "validator self-test keeps stale gap and makefile reopen cases explicit" {
    const validator_source = try readSourceFile(std.testing.allocator, validator_source_rel);
    defer std.testing.allocator.free(validator_source);

    try requireContains(
        validator_source,
        "(\"old_next_step_marker\", lambda root: write_text(root / PHASE1_CLOSURE_REL",
    );
    try requireContains(
        validator_source,
        "(\"forbidden_old_marker\", lambda root: write_text(root / PHASE1_CLOSURE_REL",
    );
    try requireContains(
        validator_source,
        "(\"forbidden_phase1_makefile_route\", lambda root: write_text(root / ZIGUX_MAKEFILE_REL",
    );

    const expected_makefile_markers = try sectionBetween(
        validator_source,
        "EXPECTED_MAKEFILE_MARKERS = (",
        ")\n\nFORBIDDEN_MAKEFILE_MARKERS",
    );
    const forbidden_makefile_markers = try sectionBetween(
        validator_source,
        "FORBIDDEN_MAKEFILE_MARKERS = (",
        ")\n\nEXPECTED_FIND_BIT_REVIEW_ANCHORS",
    );

    try requireContains(expected_makefile_markers, "phase2-toolchain:");
    try requireContains(expected_makefile_markers, "phase14-validate:");
    for (forbidden_phase1_make_routes) |route| {
        try requireContains(forbidden_makefile_markers, route);
        try requireAbsent(expected_makefile_markers, route);
    }
}

test "narrow closure validation route stays current-master safe" {
    const closure_note = try readSourceFile(std.testing.allocator, closure_note_rel);
    defer std.testing.allocator.free(closure_note);

    try requireContains(
        closure_note,
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    );
    try requireContains(
        closure_note,
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    );
    try requireContains(
        closure_note,
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    );
    try requireAbsent(
        closure_note,
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    );
}
