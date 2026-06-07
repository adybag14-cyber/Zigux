const std = @import("std");
const testing = std.testing;

const shared_smoke_route = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";
const focused_replay_route = "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig";

const closure_note_markers =
    \\The current shared tests-root closure route is narrow on purpose:
    \\
    \\- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
    \\- `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
    \\
    \\- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
    \\- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
    \\- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`
;

const tests_readme_markers =
    \\  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
    \\  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
    \\  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
;

const validator_markers =
    \\TESTS_BUILD_REL = Path("zigux/tests/build.zig")
    \\PHASE1_HELPERS_REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
    \\PHASE1_HELPERS_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
    \\PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
    \\    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
;

const build_root_markers =
    \\fn addPhase1HostToolsSmoke(
    \\        .root_source_file = b.path("phase1_host_tools_smoke.zig"),
    \\        .name = "phase1-host-tools-smoke",
;

fn containsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

fn count(comptime haystack: []const u8, comptime needle: []const u8) usize {
    var total: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        total += 1;
        index = found + needle.len;
    }
    return total;
}

test "closure note keeps shared smoke and focused replay routes paired" {
    try containsAll(closure_note_markers, &.{
        "The current shared tests-root closure route is narrow on purpose:",
        shared_smoke_route,
        focused_replay_route,
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    });

    try testing.expect(count(closure_note_markers, shared_smoke_route) >= 2);
    try testing.expectEqual(@as(usize, 1), count(closure_note_markers, focused_replay_route));
}

test "tests README mirrors the active route pairing without reopening Phase 1" {
    try containsAll(tests_readme_markers, &.{
        "current shared Phase 1 smoke route",
        shared_smoke_route,
        "current focused Phase 1 helper replay route",
        focused_replay_route,
        "the thirteen helper ports remain closed through the committed manifest",
        "the nine shared-replay parked helpers reopen only for packet or fixture drift",
        "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`",
    });
}

test "closure validator required files keep both route sources materialized" {
    try containsAll(validator_markers, &.{
        "TESTS_BUILD_REL = Path(\"zigux/tests/build.zig\")",
        "PHASE1_HELPERS_REPLAY_REL = Path(\"zigux/tests/phase1_helpers.zig\")",
        "PHASE1_HELPERS_BUILD_REL = Path(\"zigux/tests/phase1_helpers_build.zig\")",
        "PHASE1_SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")",
        "\"shared_tests_route\": \"`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\"",
    });
}

test "tests build root still exposes the shared smoke route by name" {
    try containsAll(build_root_markers, &.{
        "fn addPhase1HostToolsSmoke(",
        ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")",
        ".name = \"phase1-host-tools-smoke\"",
    });
}
