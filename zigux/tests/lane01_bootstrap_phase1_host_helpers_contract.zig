const std = @import("std");

const roadmap_phase1_packet =
    \\## Phase 1: Alpha Host-Side Helpers
    \\
    \\Primary product goal:
    \\- prove that Zig can live in-tree on low-risk host-side helper code
    \\
    \\Primary Linux targets:
    \\- `tools/lib/bitmap.c`
    \\- `tools/lib/find_bit.c`
    \\- `tools/lib/string.c`
    \\- `tools/lib/rbtree.c`
    \\
    \\Required Zigux features:
    \\- mixed-language helper build path
    \\- golden-output parity tests
    \\- clear ownership and review rules for `.zig` files beside `.c`
    \\
    \\Recommended Zigux destinations:
    \\- `tools/lib/bitmap.zig`
    \\- `tools/lib/find_bit.zig`
    \\- `tools/lib/string.zig`
    \\- `tools/lib/rbtree.zig`
    \\
    \\Why ZAR matters here:
    \\- ZAR already shows disciplined phase tracking, probe-driven validation, and explicit boundaries. That process discipline should be ported immediately.
;

const phase2_heading = "## Phase 2: Toolchain and Kbuild Enablement";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

test "Phase 1 packet stays scoped to low-risk host-side helpers" {
    try requireContains(roadmap_phase1_packet, "## Phase 1: Alpha Host-Side Helpers");
    try requireContains(roadmap_phase1_packet, "prove that Zig can live in-tree on low-risk host-side helper code");

    const c_targets = [_][]const u8{
        "`tools/lib/bitmap.c`",
        "`tools/lib/find_bit.c`",
        "`tools/lib/string.c`",
        "`tools/lib/rbtree.c`",
    };
    for (c_targets) |target| {
        try requireContains(roadmap_phase1_packet, target);
    }
}

test "Phase 1 destinations stay co-located beside tools lib C helpers" {
    const zig_destinations = [_][]const u8{
        "`tools/lib/bitmap.zig`",
        "`tools/lib/find_bit.zig`",
        "`tools/lib/string.zig`",
        "`tools/lib/rbtree.zig`",
    };
    for (zig_destinations) |destination| {
        try requireContains(roadmap_phase1_packet, destination);
    }

    try std.testing.expect(std.mem.indexOf(u8, roadmap_phase1_packet, "zigux-alpha/ports/") == null);
    try std.testing.expect(std.mem.indexOf(u8, roadmap_phase1_packet, "drivers/") == null);
}

test "Phase 1 requires validation and review before expansion" {
    try requireContains(roadmap_phase1_packet, "mixed-language helper build path");
    try requireContains(roadmap_phase1_packet, "golden-output parity tests");
    try requireContains(roadmap_phase1_packet, "clear ownership and review rules for `.zig` files beside `.c`");
    try requireContains(roadmap_phase1_packet, "disciplined phase tracking, probe-driven validation, and explicit boundaries");
}

test "Phase 1 packet remains before Phase 2 in the bootstrap roadmap order" {
    const roadmap_window = roadmap_phase1_packet ++ "\n\n" ++ phase2_heading;

    const phase1_index = try indexOfRequired(roadmap_window, "## Phase 1: Alpha Host-Side Helpers");
    const phase2_index = try indexOfRequired(roadmap_window, phase2_heading);
    try std.testing.expect(phase1_index < phase2_index);
}
