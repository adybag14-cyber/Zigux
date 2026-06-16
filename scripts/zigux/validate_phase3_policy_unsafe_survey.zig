const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_UNSAFE_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig",
    "PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig",
    "PHASE3_UNSAFE_POLICY_SCOPE=helper-local-unsafe-scope-relay-over-the-shared-narrow-decoder-plus-access-boundary-surface-and-permit-audit-aliases",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig",
    "PHASE3_POLICY_UNSAFE_SURVEY_GATE=zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig",
    "PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json",
    "PHASE3_POLICY_PACKET_GATE=zig run scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "PHASE3_POLICY_PACKET_TEST_GATE=zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "PHASE3_POLICY_DUMP_GATE=zig run scripts\\zigux/check_phase3_policy_dump.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_GATE=zig run scripts\\zigux/check_phase3_policy_unsafe_replay.zig",
    "PHASE3_POLICY_PACKET_MAKE_GATE=make -C zigux phase3-policy-starter-packet-test",
    "PHASE3_POLICY_DUMP_MAKE_GATE=make -C zigux phase3-policy-dump",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_MAKE_GATE=make -C zigux phase3-policy-unsafe-test",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-or-the-dedicated-policy-unsafe-survey-gate-drift-again",
    "The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.",
    "PHASE3_POLICY_UNSAFE_REPLAY_PATH=zigux/tests/phase3_policy_unsafe.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_BUILD_PATH=zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_TEST_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "Current `master` also keeps `zigux/Makefile` plus `.github/workflows/zigux-bootstrap.yml` explicit with both the direct `zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig` replay and the returned `make -C zigux phase3-policy-unsafe-test` wrapper, so this survey should treat those support routes as current bounded packet evidence rather than leaving the dedicated policy-unsafe replay implicit behind the Zig-only route.",
};

const SELF_TEST_CASES = [_][]const u8{
    "missing survey gate markermarker",
    "missing policy-unsafe replay gate markermarker",
    "missing low-level wrapper test gate markermarker",
    "missing policy-unsafe make gate markermarker",
    "missing next-step markermarker",
    "missing dedicated replay path markermarker",
    "missing dedicated replay build markermarker",
    "missing policy-unsafe workflow paragraphmarker",
    "layout assert blob driftblobPHASE3_LAYOUT_ASSERT_BLOB_SHA",
    "panic policy blob driftblobPHASE3_PANIC_POLICY_BLOB_SHA",
    "allocator policy blob driftblobPHASE3_ALLOCATOR_POLICY_BLOB_SHA",
    "mmio policy blob driftblobPHASE3_MMIO_BLOB_SHA",
    "unsafe policy raw-bridge require alias driftmarker",
    "narrow const-slice marker driftmarker",
    "missing policy replay consequence proofmarker",
    "missing raw-pointer window replay proofmarker",
    "missing policy replay build routemarker",
    "missing policy-unsafe make routemarker",
    "missing policy-unsafe workflow routemarker",
    "missing policy dump raw-bridge linemarker",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
