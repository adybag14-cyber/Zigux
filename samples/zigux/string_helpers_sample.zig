const std = @import("std");
const string_helpers = @import("string_helpers");

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    replay_complete,
    exited,
};

pub const SampleFocus = enum {
    newline_tolerant_matching,
    bounded_size_rendering,
    deterministic_escape_subset,
    non_allocating_runtime_safe,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const RenderedText = struct {
    bytes: [16]u8 = [_]u8{0} ** 16,
    len: usize = 0,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    comparable_match: bool,
    matched_index: i32,
    size_text: RenderedText,
    unescaped_text: RenderedText,
    escaped_text: RenderedText,
    checked_focus: []const SampleFocus,
};

pub const StringHelpersSample = struct {
    const Self = @This();

    stage_state: SampleStage = .cold,
    init_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "string_helpers_sample",
            .anchor = "lib/string_helpers.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn runAnchorReplay(self: *Self) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const values = [_]?[]const u8{ "disabled", "enabled", null, "ignored" };

        var size_text = RenderedText{};
        size_text.len = string_helpers.stringGetSize(
            1536,
            1,
            string_helpers.STRING_UNITS_2,
            &size_text.bytes,
        );

        var unescaped_text = RenderedText{};
        unescaped_text.len = string_helpers.stringUnescape(
            "line\\n",
            &unescaped_text.bytes,
            unescaped_text.bytes.len,
            string_helpers.UNESCAPE_SPACE,
        );

        var escaped_text = RenderedText{};
        escaped_text.len = string_helpers.stringEscapeMem(
            "\n",
            &escaped_text.bytes,
            string_helpers.ESCAPE_HEX,
            null,
        );

        self.stage_state = .replay_complete;

        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .comparable_match = string_helpers.sysfsStreq("mode", "mode\n"),
            .matched_index = string_helpers.sysfsMatchString(&values, values.len, "enabled\n"),
            .size_text = size_text,
            .unescaped_text = unescaped_text,
            .escaped_text = escaped_text,
            .checked_focus = &.{
                .newline_tolerant_matching,
                .bounded_size_rendering,
                .deterministic_escape_subset,
                .non_allocating_runtime_safe,
            },
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .replay_complete => {},
            else => return error.InvalidLifecycleTransition,
        }

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

test "string helper sample replay keeps the existing helper surface reviewable" {
    var sample = StringHelpersSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();
    const values = [_]?[]const u8{ "disabled", "enabled", null, "ignored" };

    try std.testing.expectEqualStrings("lib/string_helpers.c", replay.anchor);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.comparable_match);
    try std.testing.expectEqual(@as(i32, 1), replay.matched_index);
    try std.testing.expectEqual(string_helpers.EINVAL, string_helpers.matchString(&values, 2, "ignored"));
    try std.testing.expectEqualStrings("1.50 KiB", cStringPrefix(&replay.size_text.bytes));
    try std.testing.expectEqual(@as(usize, 8), replay.size_text.len);
    try std.testing.expectEqualSlices(u8, "line\n", replay.unescaped_text.bytes[0..replay.unescaped_text.len]);
    try std.testing.expectEqualSlices(u8, "\\x0a", replay.escaped_text.bytes[0..replay.escaped_text.len]);
    try std.testing.expectEqual(@as(usize, 4), replay.checked_focus.len);
}

test "string helper sample enforces simple lifecycle boundaries" {
    var sample = StringHelpersSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
    try sample.init();
    try sample.exit();
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
}
