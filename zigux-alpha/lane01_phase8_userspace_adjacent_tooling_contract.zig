const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase8 tooling expansion goal stays userspace adjacent" {
    try requireContains(roadmap, "## Phase 8: Userspace-Adjacent Tooling Expansion");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- prove Zigux inside serious repo-hosted tooling, not just tiny helpers");
}

test "phase8 keeps tooling anchor roster explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `tools/lib/subcmd/exec-cmd.c`");
    try requireContains(roadmap, "- `tools/lib/subcmd/help.c`");
    try requireContains(roadmap, "- `tools/lib/symbol/kallsyms.c`");
    try requireContains(roadmap, "- `tools/lib/bpf/libbpf.c`");
}

test "phase8 keeps helper-first and output-stable features explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- helper-first expansion");
    try requireContains(roadmap, "- segmented plan for large consumers like libbpf");
    try requireContains(roadmap, "- output-stable tooling behavior");
}

test "phase8 destinations and neighboring phase order stay bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `tools/lib/subcmd/*.zig`");
    try requireContains(roadmap, "- `tools/lib/symbol/*.zig`");
    try requireContains(roadmap, "- `tools/lib/bpf/zigux_segments/`");

    try requireOrdered("## Phase 7: In-Kernel Leaf Libraries", "## Phase 8: Userspace-Adjacent Tooling Expansion");
    try requireOrdered("## Phase 8: Userspace-Adjacent Tooling Expansion", "## Phase 9: Runtime Pilot Modules");
}
