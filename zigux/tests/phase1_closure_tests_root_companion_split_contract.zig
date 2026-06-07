const std = @import("std");

const max_file_size = 256 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, rel_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, rel_path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "tests root keeps direct-readback Phase 1 reminder packet narrow" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "current direct-readback Phase 1 reminder packet:");
    try expectContains(readme, "`Documentation/zigux/phase1-closure.md`");
    try expectContains(readme, "`scripts/zigux/validate-phase1-closure.py`");
    try expectContains(readme, "`zigux/tests/build.zig`");
    try expectContains(readme, "`zigux/tests/phase1_helpers.zig`");
    try expectContains(readme, "`zigux/tests/phase1_host_tools_smoke.zig`");
    try expectContains(readme, "`zigux/tests/fixtures/phase1_helper_manifest.json`");
    try expectContains(readme, "`zigux/tests/README.md`");

    try expectOrder(
        readme,
        "current direct-readback Phase 1 reminder packet:",
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet:",
    );
}

test "tests root parks broader closure companions as companions rather than active proof" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet:");
    try expectContains(readme, "`scripts/zigux/validate-phase1.py`");
    try expectContains(readme, "`scripts/zigux/check-phase1-parity.py`");
    try expectContains(readme, "`zigux/tests/phase1_bench.zig`");
    try expectContains(readme, "`zigux/tests/fixtures/phase1_bench_expectations.json`");
    try expectContains(readme, "`zigux/tests/phase1_helpers_c_harness.c`");
    try expectContains(readme, "keep those paths framed as broader closure companions rather than as active tests-root proof");
    try expectContains(readme, "the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof");
}

test "closure note and validator agree on the parked gap packet" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    const gap_packet = "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

    try expectContains(closure_note, "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.");
    try expectContains(closure_note, gap_packet);
    try expectContains(validator, gap_packet);
    try expectContains(validator, "FORBIDDEN_MAKEFILE_MARKERS");
    try expectContains(validator, "\"phase1-validate:\"");
    try expectContains(validator, "\"phase1-test:\"");
    try expectContains(validator, "\"phase1-bench:\"");
    try expectContains(validator, "\"phase1:\"");
}

test "tests root keeps the executable Phase 1 closure routes intentionally small" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(readme);
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);

    try expectContains(readme, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(readme, "current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`");
    try expectContains(closure_note, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(closure_note, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectContains(closure_note, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
}
