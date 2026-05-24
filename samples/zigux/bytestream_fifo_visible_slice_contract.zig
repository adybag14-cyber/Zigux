const std = @import("std");
const sample = @import("bytestream_fifo.zig");

test "bytestream fifo visible-slice contract keeps preview-boundary snapshots explicit" {
    var fifo = sample.BytestreamFifoSample{};

    const empty_visible = fifo.visibleSlices();
    try std.testing.expectEqual(@as(usize, 0), empty_visible.first.len);
    try std.testing.expectEqual(@as(usize, 0), empty_visible.second.len);
    try std.testing.expectEqual(@as(usize, 0), empty_visible.total_visible);
    try std.testing.expect(!empty_visible.wraps);

    var empty_snapshot: [4]u8 = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(@as(usize, 0), fifo.snapshotInto(empty_snapshot[0..]));
    try std.testing.expectEqualSlices(u8, &.{ 0xaa, 0xaa, 0xaa, 0xaa }, empty_snapshot[0..]);

    try fifo.init();
    const preview = try fifo.runPreviewBoundaryReplay();
    try std.testing.expectEqual(sample.SampleStage.initialized, preview.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, preview.stage_after_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, fifo.stage());

    const preview_visible = fifo.visibleSlices();
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9, 0, 1 }, preview_visible.first);
    try std.testing.expectEqual(@as(usize, 0), preview_visible.second.len);
    try std.testing.expectEqual(@as(usize, 10), preview_visible.total_visible);
    try std.testing.expect(!preview_visible.wraps);

    var truncated_snapshot: [6]u8 = [_]u8{0xbb} ** 6;
    try std.testing.expectEqual(@as(usize, truncated_snapshot.len), fifo.snapshotInto(truncated_snapshot[0..]));
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7 }, truncated_snapshot[0..]);

    var exact_snapshot: [12]u8 = [_]u8{0xcc} ** 12;
    try std.testing.expectEqual(@as(usize, 10), fifo.snapshotInto(exact_snapshot[0..]));
    try std.testing.expectEqualSlices(u8, &.{ 2, 3, 4, 5, 6, 7, 8, 9, 0, 1 }, exact_snapshot[0..10]);
    try std.testing.expectEqualSlices(u8, &.{ 0xcc, 0xcc }, exact_snapshot[10..12]);

    const preview_visible_after_snapshot = fifo.visibleSlices();
    try std.testing.expectEqualSlices(u8, preview_visible.first, preview_visible_after_snapshot.first);
    try std.testing.expectEqual(@as(usize, 0), preview_visible_after_snapshot.second.len);
    try std.testing.expectEqual(@as(usize, 10), preview_visible_after_snapshot.total_visible);
    try std.testing.expect(!preview_visible_after_snapshot.wraps);
}

test "bytestream fifo visible-slice contract keeps wrapped-window snapshots explicit" {
    var fifo = sample.BytestreamFifoSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, fifo.runWrappedPreviewReplay());

    try fifo.init();
    const wrapped = try fifo.runWrappedPreviewReplay();
    try std.testing.expectEqual(sample.SampleStage.initialized, wrapped.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, wrapped.stage_after_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, fifo.stage());

    const wrapped_visible = fifo.visibleSlices();
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6 }, wrapped_visible.first[0..8]);
    try std.testing.expectEqualSlices(u8, &.{ 200, 201, 202, 203 }, wrapped_visible.second);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_visible.total_visible);
    try std.testing.expect(wrapped_visible.wraps);

    var prefix_snapshot: [14]u8 = [_]u8{0xdd} ** 14;
    try std.testing.expectEqual(@as(usize, prefix_snapshot.len), fifo.snapshotInto(prefix_snapshot[0..]));
    try std.testing.expectEqualSlices(
        u8,
        &.{ 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 },
        prefix_snapshot[0..],
    );

    var full_snapshot: [34]u8 = [_]u8{0xee} ** 34;
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), fifo.snapshotInto(full_snapshot[0..]));
    try std.testing.expectEqualSlices(u8, &.{ 'o', 0, 1, 2, 3, 4, 5, 6 }, full_snapshot[0..8]);
    try std.testing.expectEqualSlices(u8, &.{ 200, 201, 202, 203 }, full_snapshot[28..32]);
    try std.testing.expectEqualSlices(u8, &.{ 0xee, 0xee }, full_snapshot[32..34]);

    const wrapped_visible_after_snapshot = fifo.visibleSlices();
    try std.testing.expectEqualSlices(u8, wrapped_visible.first, wrapped_visible_after_snapshot.first);
    try std.testing.expectEqualSlices(u8, wrapped_visible.second, wrapped_visible_after_snapshot.second);
    try std.testing.expectEqual(@as(usize, sample.fifo_capacity), wrapped_visible_after_snapshot.total_visible);
    try std.testing.expect(wrapped_visible_after_snapshot.wraps);
}
