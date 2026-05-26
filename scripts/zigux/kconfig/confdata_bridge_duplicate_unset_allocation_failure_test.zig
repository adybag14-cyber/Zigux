const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

fn parseConfigDuplicateUnsetAllocationFailureHarness(allocator: std.mem.Allocator) !void {
    var summary = try confdata_bridge.parseConfig(allocator,
        \\CONFIG_ALPHA="stable"
        \\# CONFIG_ALPHA is not set
        \\# CONFIG_ALPHA is not set
        \\CONFIG_BETA=7
        \\
    );
    defer confdata_bridge.deinitSummary(allocator, &summary);
}

test "confdata bridge preserves duplicate unset ownership on allocation failure" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        parseConfigDuplicateUnsetAllocationFailureHarness,
        .{},
    );
}
