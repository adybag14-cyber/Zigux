const std = @import("std");
const options = @import("phase1_tests_readme_direct_packet_contract_options");

const tests_readme_path = options.tests_readme_path;

const current_packet_paths = [_][]const u8{
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`zigux/tests/build.zig`",
    "`zigux/tests/phase1_helpers.zig`",
    "`zigux/tests/phase1_helpers_build.zig`",
    "`zigux/tests/phase1_host_tools_smoke.zig`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`zigux/tests/README.md`",
};

const broader_companions = [_][]const u8{
    "`scripts/zigux/validate-phase1.py`",
    "`scripts/zigux/check-phase1-parity.py`",
    "`zigux/tests/phase1_bench.zig`",
    "`zigux/tests/fixtures/phase1_bench_expectations.json`",
    "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
};

const direct_anchor_helpers = [_][]const u8{
    "`tools/lib/bitmap.zig`",
    "`tools/lib/find_bit.zig`",
    "`tools/lib/rbtree.zig`",
    "`tools/lib/string.zig`",
};

fn readTestsReadme() ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        tests_readme_path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "tests README preserves the current Phase 1 direct-readback packet and routes" {
    const readme = try readTestsReadme();
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "## Phase 1 host-tools review packet");
    try expectContains(readme, "current direct-readback Phase 1 reminder packet:");
    inline for (current_packet_paths) |path| {
        try expectContains(readme, path);
    }

    try expectContains(readme, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(readme, "current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`");
    try expectInOrder(
        readme,
        "`scripts/zigux/validate-phase1-closure.py`",
        "`zigux/tests/README.md`",
    );
    try expectInOrder(
        readme,
        "current shared Phase 1 smoke route:",
        "current focused Phase 1 helper replay route:",
    );
}

test "tests README keeps broader companions parked outside active tests-root proof" {
    const readme = try readTestsReadme();
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet");
    inline for (broader_companions) |path| {
        try expectContains(readme, path);
    }

    try expectContains(readme, "keep those paths framed as broader closure companions rather than as active tests-root proof");
    try expectContains(readme, "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof");
    try expectNotContains(readme, "current shared Phase 1 route: `make -C zigux phase1`");
    try expectNotContains(readme, "current Phase 1 bench route: `make -C zigux phase1-bench`");
}

test "tests README preserves the nine shared-replay and four direct-anchor helper split" {
    const readme = try readTestsReadme();
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "the thirteen helper ports remain closed through the committed manifest");
    try expectContains(readme, "the nine shared-replay parked helpers reopen only for packet or fixture drift");
    try expectContains(readme, "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`");
    inline for (direct_anchor_helpers) |helper| {
        try expectContains(readme, helper);
    }
}
