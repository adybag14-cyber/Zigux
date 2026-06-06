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

test "scripts README keeps the Phase 1 reminder packet aligned with closure authority" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

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
        "zigux/tests/README.md",
        "zigux/tests/build.zig",
        "zigux/tests/phase1_helpers.zig",
        "zigux/tests/phase1_helpers_build.zig",
        "zigux/tests/phase1_host_tools_smoke.zig",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    };

    try expectContains(scripts_readme, "Phase 1 flow - the current host-tools reminder packet");
    try expectContains(closure_note, "The currently reviewable Phase 1 reminder packet is:");
    try expectContains(closure_note, "`PHASE1_CURRENT_REMINDER_PACKET=");
    try expectContains(validator, "EXPECTED_CLOSURE_MARKERS = {");
    try expectContains(validator, "\"reminder_packet\"");

    inline for (packet_paths) |path| {
        try expectContains(scripts_readme, path);
        try expectContains(closure_note, path);
    }
}

test "scripts README preserves the shipped checker and route handoff list" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    const shipped_commands = [_][]const u8{
        "python3 scripts/zigux/validate-phase1-closure.py",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig",
    };

    inline for (shipped_commands) |command| {
        try expectContains(scripts_readme, command);
    }

    try expectContains(closure_note, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectContains(closure_note, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(closure_note, "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig");
    try expectContains(validator, "\"closure_validator\"");
    try expectContains(validator, "\"shared_tests_route\"");
}

test "scripts README keeps broader Phase 1 closure companions parked" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const parked_paths = [_][]const u8{
        "scripts/zigux/validate-phase1.py",
        "scripts/zigux/check-phase1-parity.py",
        "zigux/tests/phase1_bench.zig",
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        "zigux/tests/phase1_helpers_c_harness.c",
    };

    try expectContains(scripts_readme, "older validator-first, bench, and C-harness routes as historical packet members");
    try expectContains(closure_note, "The older validator-first and replay-side closure companions remain broader closure-stack references");
    try expectContains(closure_note, "`PHASE1_CURRENT_GAP_PACKET=");
    try expectContains(validator, "\"gap_packet\"");

    inline for (parked_paths) |path| {
        try expectContains(scripts_readme, path);
        try expectContains(closure_note, path);
    }

    try expectContains(scripts_readme, "older Phase 1 wrapper names stay historical reminder vocabulary");
    try expectContains(validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try expectNotContains(makefile, "phase1-validate:");
    try expectNotContains(makefile, "phase1-test:");
    try expectNotContains(makefile, "phase1-bench:");
    try expectNotContains(makefile, "phase1: phase1-validate");
}

test "scripts README preserves helper-family split and direct-anchor boundaries" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const lane_note = try readRepoFile(allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer allocator.free(lane_note);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

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

    try expectContains(scripts_readme, "the current direct-anchor tie-breakers stay helper-local");
    try expectContains(scripts_readme, "other nine closed helpers stay parked unless the shared replay or reminder packet drifts");
    try expectContains(lane_note, "`PHASE1_SHARED_REPLAY_PARKED_HELPERS=");
    try expectContains(lane_note, "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=");
    try expectContains(lane_note, "`PHASE1_LANE_ANTI_OVERLAP_RULE=");
    try expectContains(validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");

    inline for (shared_parked) |path| {
        try expectContains(scripts_readme, path);
        try expectContains(lane_note, path);
        try expectContains(validator, path);
    }

    inline for (direct_anchor) |path| {
        try expectContains(scripts_readme, path);
        try expectContains(lane_note, path);
        try expectContains(validator, path);
    }
}
