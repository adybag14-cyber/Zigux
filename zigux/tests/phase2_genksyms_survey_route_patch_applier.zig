const std = @import("std");

const bridge_self_test = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test\n";
const bridge_replay = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py\n";
const survey_self_test = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test\n";
const survey_replay = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\n";
const genksyms_zig_test = "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig\n";
const phase2_fixdep_header = "\nphase2-fixdep: phase2-toolchain\n";

const PatchError = error{
    MissingPhase2GenksymsRoute,
    MissingBridgeReplayAnchor,
    MissingGenksymsZigTestAnchor,
    SurveyRouteAlreadyPresent,
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

fn phase2GenksymsRoute(makefile: []const u8) PatchError![]const u8 {
    const header = "phase2-genksyms: phase2-toolchain\n";
    const start = if (std.mem.startsWith(u8, makefile, header))
        0
    else if (std.mem.indexOf(u8, makefile, "\n" ++ header)) |found|
        found + 1
    else
        return PatchError.MissingPhase2GenksymsRoute;
    const after_start = start;
    const end = std.mem.indexOfPos(u8, makefile, after_start, phase2_fixdep_header) orelse return PatchError.MissingPhase2GenksymsRoute;
    return makefile[after_start..end];
}

fn applySurveyRoutePatch(allocator: std.mem.Allocator, makefile: []const u8) ![]u8 {
    const route = try phase2GenksymsRoute(makefile);
    if (std.mem.indexOf(u8, route, "check-phase2-genksyms-dual-implementation-survey.py") != null) {
        return PatchError.SurveyRouteAlreadyPresent;
    }

    const anchor = bridge_replay ++ genksyms_zig_test;
    const anchor_index = std.mem.indexOf(u8, makefile, anchor) orelse return PatchError.MissingBridgeReplayAnchor;
    if (std.mem.indexOf(u8, route, genksyms_zig_test) == null) {
        return PatchError.MissingGenksymsZigTestAnchor;
    }

    const insertion_point = anchor_index + bridge_replay.len;
    return std.mem.concat(allocator, u8, &.{
        makefile[0..insertion_point],
        survey_self_test,
        survey_replay,
        makefile[insertion_point..],
    });
}

const live_missing_route =
    "phase2-genksyms: phase2-toolchain\n" ++
    bridge_self_test ++
    bridge_replay ++
    genksyms_zig_test ++
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig\n" ++
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig\n" ++
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test\n" ++
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py\n" ++
    phase2_fixdep_header;

test "patch inserts survey replay after bridge checker before genksyms Zig tests" {
    const patched = try applySurveyRoutePatch(std.testing.allocator, live_missing_route);
    defer std.testing.allocator.free(patched);

    const route = try phase2GenksymsRoute(patched);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(route, bridge_self_test));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(route, bridge_replay));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(route, survey_self_test));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(route, survey_replay));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(route, genksyms_zig_test));

    const bridge_index = std.mem.indexOf(u8, route, bridge_replay).?;
    const survey_self_index = std.mem.indexOf(u8, route, survey_self_test).?;
    const survey_replay_index = std.mem.indexOf(u8, route, survey_replay).?;
    const zig_test_index = std.mem.indexOf(u8, route, genksyms_zig_test).?;

    try std.testing.expect(bridge_index < survey_self_index);
    try std.testing.expect(survey_self_index < survey_replay_index);
    try std.testing.expect(survey_replay_index < zig_test_index);
}

test "patch refuses duplicate survey route" {
    const patched = try applySurveyRoutePatch(std.testing.allocator, live_missing_route);
    defer std.testing.allocator.free(patched);

    try std.testing.expectError(PatchError.SurveyRouteAlreadyPresent, applySurveyRoutePatch(std.testing.allocator, patched));
}

test "patch refuses missing bridge replay anchor" {
    const broken = try std.mem.replaceOwned(u8, std.testing.allocator, live_missing_route, bridge_replay, "");
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(PatchError.MissingBridgeReplayAnchor, applySurveyRoutePatch(std.testing.allocator, broken));
}

test "patch refuses a missing phase2-genksyms route" {
    try std.testing.expectError(PatchError.MissingPhase2GenksymsRoute, applySurveyRoutePatch(std.testing.allocator, "phase2: phase2-validate\n"));
}
