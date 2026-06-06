const std = @import("std");

const max_file_size = 1024 * 1024;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

test "tests README keeps the current Phase 1 reminder packet aligned with closure note" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    const packet_paths = [_][]const u8{
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
        "zigux/tests/build.zig",
        "zigux/tests/phase1_helpers.zig",
        "zigux/tests/phase1_helpers_build.zig",
        "zigux/tests/phase1_host_tools_smoke.zig",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        "zigux/tests/README.md",
    };

    try expectContains(tests_readme, "current direct-readback Phase 1 reminder packet");
    try expectContains(closure_note, "The currently reviewable Phase 1 reminder packet is:");
    try expectContains(closure_note, "`PHASE1_CURRENT_REMINDER_PACKET=");

    inline for (packet_paths) |path| {
        try expectContains(tests_readme, path);
        try expectContains(closure_note, path);
    }

    try expectContains(validator, "REQUIRED_FILES = (");
    try expectContains(validator, "TESTS_README_REL");
    try expectContains(validator, "PHASE1_CLOSURE_REL");
    try expectContains(validator, "SHARED_REMINDER_CHECKER_REL");
}

test "tests README preserves narrow shared Phase 1 route wording" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    const smoke_route = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";
    const replay_route = "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig";

    try expectContains(tests_readme, "current shared Phase 1 smoke route");
    try expectContains(tests_readme, smoke_route);
    try expectContains(tests_readme, "current focused Phase 1 helper replay route");
    try expectContains(tests_readme, replay_route);

    try expectContains(closure_note, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(closure_note, replay_route);
    try expectContains(validator, "\"shared_tests_route\"");
    try expectContains(validator, smoke_route);
}

test "tests README keeps broader closure companions parked instead of active proof" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const broader_companions = [_][]const u8{
        "scripts/zigux/validate-phase1.py",
        "scripts/zigux/check-phase1-parity.py",
        "zigux/tests/phase1_bench.zig",
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        "zigux/tests/phase1_helpers_c_harness.c",
    };

    try expectContains(tests_readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet");
    try expectContains(closure_note, "The older validator-first and replay-side closure companions remain broader closure-stack references");
    try expectContains(closure_note, "`PHASE1_CURRENT_GAP_PACKET=");
    try expectContains(validator, "\"gap_packet\"");

    inline for (broader_companions) |path| {
        try expectContains(tests_readme, path);
        try expectContains(closure_note, path);
    }

    try expectContains(tests_readme, "older Phase 1 wrapper names remain historical packet members");
    try expectContains(closure_note, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
    try expectContains(validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try expectNotContains(makefile, "phase1-validate:");
    try expectNotContains(makefile, "phase1-test:");
    try expectNotContains(makefile, "phase1-bench:");
    try expectNotContains(makefile, "phase1: phase1-validate");
}

test "tests README preserves helper-family split from lane sequencing" {
    const allocator = std.testing.allocator;
    const lane_note = try readRepoFile(allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer allocator.free(lane_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    const shared_parked = [_][]const u8{
        "tools/lib/argv_split.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    };
    const direct_anchor = [_][]const u8{
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    };

    try expectContains(tests_readme, "the nine shared-replay parked helpers reopen only for packet or fixture drift");
    try expectContains(tests_readme, "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers");
    try expectContains(lane_note, "`PHASE1_SHARED_REPLAY_PARKED_HELPERS=");
    try expectContains(lane_note, "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=");
    try expectContains(lane_note, "`PHASE1_LANE_ANTI_OVERLAP_RULE=");
    try expectContains(validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");

    inline for (shared_parked) |path| {
        try expectContains(tests_readme, path);
        try expectContains(lane_note, path);
        try expectContains(validator, path);
    }

    inline for (direct_anchor) |path| {
        try expectContains(tests_readme, path);
        try expectContains(lane_note, path);
        try expectContains(validator, path);
    }
}
