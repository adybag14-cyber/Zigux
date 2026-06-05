const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase8_heading = "## Phase 8: Userspace-Adjacent Tooling Expansion";
const phase9_heading = "## Phase 9: Runtime Pilot Modules";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn sectionBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingSectionStart;
    const content_start = start_index + start.len;
    const relative_end = std.mem.indexOf(u8, haystack[content_start..], end) orelse return error.MissingSectionEnd;
    return haystack[content_start .. content_start + relative_end];
}

test "phase 8 userspace-adjacent tooling packet keeps its bounded goal" {
    const phase8 = try sectionBetween(roadmap, phase8_heading, phase9_heading);

    try requireContains(phase8, "Primary product goal:\n- prove Zigux inside serious repo-hosted tooling, not just tiny helpers");
    try requireContains(phase8, "Required Zigux features:");
    try requireContains(phase8, "- helper-first expansion");
    try requireContains(phase8, "- segmented plan for large consumers like libbpf");
    try requireContains(phase8, "- output-stable tooling behavior");
}

test "phase 8 userspace-adjacent tooling packet preserves Linux anchors" {
    const phase8 = try sectionBetween(roadmap, phase8_heading, phase9_heading);

    try requireContains(phase8, "Primary Linux anchors:");
    try requireContains(phase8, "- `tools/lib/subcmd/exec-cmd.c`");
    try requireContains(phase8, "- `tools/lib/subcmd/help.c`");
    try requireContains(phase8, "- `tools/lib/symbol/kallsyms.c`");
    try requireContains(phase8, "- `tools/lib/bpf/libbpf.c`");
}

test "phase 8 userspace-adjacent tooling packet keeps recommended destinations narrow" {
    const phase8 = try sectionBetween(roadmap, phase8_heading, phase9_heading);

    try requireContains(phase8, "Recommended Zigux destinations:");
    try requireContains(phase8, "- `tools/lib/subcmd/*.zig`");
    try requireContains(phase8, "- `tools/lib/symbol/*.zig`");
    try requireContains(phase8, "- `tools/lib/bpf/zigux_segments/`");

    try requireAbsent(phase8, "`zigux-alpha/ports/`");
    try requireAbsent(phase8, "mirror-tree");
}

test "phase 8 remains ordered after leaf libraries and before runtime pilots" {
    try requireBefore(roadmap, "## Phase 7: In-Kernel Leaf Libraries", phase8_heading);
    try requireBefore(roadmap, phase8_heading, phase9_heading);
    try requireBefore(roadmap, "- `lib/rbtree.zig`", phase8_heading);
    try requireBefore(roadmap, "- `tools/lib/bpf/zigux_segments/`", phase9_heading);
}
