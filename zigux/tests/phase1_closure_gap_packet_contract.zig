const std = @import("std");
const testing = std.testing;

const max_file_size = 1024 * 1024;

fn repoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_file_size));
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, needle) == null);
}

fn requireOnce(text: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = text;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try testing.expectEqual(@as(usize, 1), count);
}

fn requireBefore(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

fn sliceBetween(text: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, text, start) orelse return error.MissingStartMarker;
    const body_start = start_index + start.len;
    const end_index = std.mem.indexOfPos(u8, text, body_start, end) orelse return error.MissingEndMarker;
    return text[body_start..end_index];
}

test "phase1 closure note keeps broader closure companions parked as the gap packet" {
    const closure = try repoFile(testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure);

    const current_packet = "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md";
    const broader_section = "## Broader Closure Companions";
    const validation_section = "## Closure Validation";
    const gap_packet =
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

    try requireOnce(closure, gap_packet);
    try requireContains(
        closure,
        "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
    );
    try requireContains(
        closure,
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them.",
    );
    try requireBefore(closure, current_packet, broader_section);
    try requireBefore(closure, broader_section, gap_packet);
    try requireBefore(closure, gap_packet, validation_section);

    const broader_companions = try sliceBetween(closure, broader_section, validation_section);
    try requireContains(broader_companions, "- `scripts/zigux/validate-phase1.py`");
    try requireContains(broader_companions, "- `scripts/zigux/check-phase1-parity.py`");
    try requireContains(broader_companions, "- `zigux/tests/phase1_bench.zig`");
    try requireContains(broader_companions, "- `zigux/tests/fixtures/phase1_bench_expectations.json`");
    try requireContains(broader_companions, "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`");
}

test "phase1 closure validation stays narrowed away from old phase1 wrapper routes" {
    const closure = try repoFile(testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure);
    const validator = try repoFile(testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator);

    try requireContains(
        closure,
        "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`",
    );
    try requireContains(validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try requireContains(validator, "\"phase1-validate:\"");
    try requireContains(validator, "\"phase1-test:\"");
    try requireContains(validator, "\"phase1-bench:\"");
    try requireContains(validator, "\"phase1:\"");
    try requireContains(validator, "\"forbidden_phase1_makefile_route\"");
    try requireContains(validator, "EXPECTED_MAKEFILE_MARKERS = (");
    try requireContains(validator, "\"phase14-validate:\"");
}

test "phase1 validator requires current reminder surfaces without promoting gap files" {
    const validator = try repoFile(testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator);

    const required_files = try sliceBetween(validator, "REQUIRED_FILES = (", ")\n\nEXPECTED_HELPERS");
    try requireContains(required_files, "PHASE1_CLOSURE_REL");
    try requireContains(required_files, "SHARED_REMINDER_CHECKER_REL");
    try requireContains(required_files, "TESTS_BUILD_REL");
    try requireContains(required_files, "PHASE1_SMOKE_REL");
    try requireContains(required_files, "MANIFEST_REL");
    try requireContains(required_files, "ZIGUX_MAKEFILE_REL");
    try requireAbsent(required_files, "validate-phase1.py");
    try requireAbsent(required_files, "check-phase1-parity.py");
    try requireAbsent(required_files, "phase1_bench_expectations.json");
    try requireAbsent(required_files, "phase1_helpers_c_harness.c");

    try requireContains(validator, "\"gap_packet\"");
    try requireContains(validator, "\"missing_route_summary_guard\"");
    try requireContains(validator, "\"missing_shared_tests_route\"");
    try requireContains(validator, "\"old_next_step_marker\"");
    try requireContains(validator, "\"forbidden_old_marker\"");
}
