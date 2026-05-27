const std = @import("std");

const bridge = @import("file_path_handle_bridge.zig");

test "phase8 file-path bridge keeps duplicate fdinfo fields and unknown keys stable" {
    const parsed = try bridge.parseFdinfoMapInfo(
        \\map_type: 14
        \\ignored_field: 999
        \\map_flags: 0x20
        \\map_extra: 0x01
        \\map_flags: 0x80
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
    );
    const summary = bridge.summarizeFdinfoMapInfo(parsed);

    try std.testing.expectEqual(@as(?u32, 14), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x80), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 0x01), parsed.map_extra);
    try std.testing.expectEqual(@as(usize, 6), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
    try std.testing.expect(summary.has_map_extra);
}

test "phase8 file-path bridge keeps terminated-prefix reuse planning stable" {
    const parsed = try bridge.parseFdinfoMapInfo(
        \\map_type: 14
        \\key_size: 4
        \\value_size: 8
        \\max_entries: 16
        \\map_flags: 0x80
        \\map_extra: 0x20
    );
    const retained = try bridge.summarizeReusedMapName("stats_map\x00retained-padding");
    try std.testing.expectEqual(
        bridge.ReusedMapNameDisposition.terminated_prefix,
        retained.disposition,
    );
    try std.testing.expectEqual(@as(?usize, 9), retained.terminator_index);
    try std.testing.expectEqualStrings("stats_map", retained.name);

    const reuse_attempt = try bridge.resolveReusePinnedMapAttempt(
        "stats_map\x00retained-padding",
        parsed,
    );
    try std.testing.expectEqual(
        bridge.ReusePinnedMapAttemptDisposition.ready_for_reopen_attempt,
        reuse_attempt.disposition,
    );
    try std.testing.expect(reuse_attempt.should_attempt_reopen);
    try std.testing.expectEqualStrings("stats_map", reuse_attempt.retained_name.?);

    const token_plan = bridge.planTokenPreparation(reuse_attempt);
    try std.testing.expectEqual(
        bridge.TokenPreparationDisposition.ready_for_token_open_attempt,
        token_plan.disposition,
    );
    try std.testing.expect(token_plan.should_attempt_token_open);
}
