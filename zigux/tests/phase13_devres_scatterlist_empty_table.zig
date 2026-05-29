const std = @import("std");
const devres_scatterlist = @import("devres_scatterlist");

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        return error.MissingMarker;
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

test "phase13 devres scatterlist table teardown warns on initialized empty tables" {
    const plan = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistTableTeardown(.{
        .original_entries = 0,
        .mapped_entries = 0,
        .table_initialized = true,
        .release_record_present = true,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 0), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 0), plan.mapped_entries);
    try std.testing.expect(plan.table_initialized);
    try std.testing.expect(plan.release_record_present);
    try std.testing.expect(!plan.free_table_ready);
    try std.testing.expect(!plan.requires_unmap_before_free);
    try std.testing.expect(!plan.warns_on_missing_release_record);
    try std.testing.expect(plan.warns_on_empty_table);
    try std.testing.expect(!plan.warns_on_overmapped_release);
}

test "phase13 devres scatterlist empty-table replay stays helper-local" {
    const helper = try readRepoFile(std.testing.allocator, "lib/devres_scatterlist.zig");
    defer std.testing.allocator.free(helper);

    try requireContains(helper, "warns_on_empty_table: bool");
    try requireContains(helper, ".warns_on_empty_table = input.table_initialized and input.original_entries == 0");
    try requireContains(helper, ".touches_live_dma = false");
    try requireContains(helper, ".touches_live_scatterlist = false");
}
