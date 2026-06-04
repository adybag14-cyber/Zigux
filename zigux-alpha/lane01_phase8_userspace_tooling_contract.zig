const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase7_heading = "## Phase 7: In-Kernel Leaf Libraries";
const phase8_heading = "## Phase 8: Userspace-Adjacent Tooling Expansion";
const phase9_heading = "## Phase 9: Runtime Pilot Modules";

test "Phase 8 remains ordered between Phase 7 and Phase 9" {
    const phase7 = requireIndex(phase7_heading);
    const phase8 = requireIndex(phase8_heading);
    const phase9 = requireIndex(phase9_heading);

    try std.testing.expect(phase7 < phase8);
    try std.testing.expect(phase8 < phase9);
}

test "Phase 8 product goal stays serious tooling focused" {
    const phase8 = phaseBody();

    try expectContains(phase8, "Primary product goal:");
    try expectContains(
        phase8,
        "- prove Zigux inside serious repo-hosted tooling, not just tiny helpers",
    );
}

test "Phase 8 keeps the userspace-adjacent tooling anchor roster" {
    const phase8 = phaseBody();

    try expectContains(phase8, "Primary Linux anchors:");
    try expectOrdered(phase8, &.{
        "- `tools/lib/subcmd/exec-cmd.c`",
        "- `tools/lib/subcmd/help.c`",
        "- `tools/lib/symbol/kallsyms.c`",
        "- `tools/lib/bpf/libbpf.c`",
    });
}

test "Phase 8 keeps output-stable tooling features and destinations" {
    const phase8 = phaseBody();

    try expectContains(phase8, "Required Zigux features:");
    try expectOrdered(phase8, &.{
        "- helper-first expansion",
        "- segmented plan for large consumers like libbpf",
        "- output-stable tooling behavior",
    });

    try expectContains(phase8, "Recommended Zigux destinations:");
    try expectOrdered(phase8, &.{
        "- `tools/lib/subcmd/*.zig`",
        "- `tools/lib/symbol/*.zig`",
        "- `tools/lib/bpf/zigux_segments/`",
    });
}

fn phaseBody() []const u8 {
    const start = requireIndex(phase8_heading);
    const end = requireIndex(phase9_heading);
    std.debug.assert(start < end);
    return roadmap[start..end];
}

fn requireIndex(needle: []const u8) usize {
    return std.mem.indexOf(u8, roadmap, needle) orelse
        @panic("required roadmap marker is missing");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var previous: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[previous..], needle) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{needle});
            return error.MissingMarker;
        };
        previous += relative + needle.len;
    }
}
