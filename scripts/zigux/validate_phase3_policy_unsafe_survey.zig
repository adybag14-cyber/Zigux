const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_UNSAFE_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass",
    "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "PHASE3_POLICY_UNSAFE_SURVEY=pass",
};

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig",
    "PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig",
    "PHASE3_UNSAFE_POLICY_SCOPE=helper-local-unsafe-scope-relay-over-the-shared-narrow-decoder-plus-access-boundary-surface-and-permit-audit-aliases",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig",
    "PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json",
    "PHASE3_POLICY_PACKET_TEST_GATE=zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "PHASE3_POLICY_PACKET_MAKE_GATE=make -C zigux phase3-policy-starter-packet-test",
    "PHASE3_POLICY_DUMP_MAKE_GATE=make -C zigux phase3-policy-dump",
    "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_MAKE_GATE=make -C zigux phase3-policy-unsafe-test",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-or-the-dedicated-policy-unsafe-survey-gate-drift-again",
    "The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.",
    "PHASE3_POLICY_UNSAFE_REPLAY_PATH=zigux/tests/phase3_policy_unsafe.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_BUILD_PATH=zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_TEST_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "Current `master` also keeps `zigux/Makefile` plus `.github/workflows/zigux-bootstrap.yml` explicit with both the direct `zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig` replay and the returned `make -C zigux phase3-policy-unsafe-test` wrapper, so this survey should treat those support routes as current bounded packet evidence rather than leaving the dedicated policy-unsafe replay implicit behind the Zig-only route.",
};

const markers_1 = [_][]const u8{
    "\"phase\": \"Phase 3\"",
    "\"replay_routes\"",
    "zig run scripts/zigux/validate_phase3_policy_unsafe_survey.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_policy_unsafe_survey.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_1 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "="))
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len })
        else
            try guard.printLine(io, "{s}", .{marker});
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
