const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn roadmapSection(title: []const u8, next_title: []const u8) []const u8 {
    const start = std.mem.indexOf(u8, roadmap, title) orelse unreachable;
    const after_start = start + title.len;
    const relative_end = std.mem.indexOf(u8, roadmap[after_start..], next_title) orelse unreachable;
    return roadmap[start .. after_start + relative_end];
}

test "zigux-alpha scope stays a bootstrap staging area" {
    const section = roadmapSection("## zigux-alpha Scope", "## Product Features by Phase");

    try requireContains(section, "`zigux-alpha/` is the staging area for:");
    try requireContains(section, "- roadmap and phase sequencing");
    try requireContains(section, "- source mapping");
    try requireContains(section, "- validation strategy");
    try requireContains(section, "- freeze map");
    try requireContains(section, "- first commit ledger");
    try requireContains(section, "- workstream ownership");
}

test "zigux-alpha scope rejects permanent subsystem ownership" {
    const section = roadmapSection("## zigux-alpha Scope", "## Product Features by Phase");

    try requireContains(section, "`zigux-alpha/` is not the final home for:");
    try requireContains(section, "- subsystem ports");
    try requireContains(section, "- runtime helpers");
    try requireContains(section, "- drivers");
    try requireContains(section, "- bindings");
    try requireContains(section, "- UAPI shims");
}

test "approved product destinations stay outside the bootstrap folder" {
    const section = roadmapSection("## zigux-alpha Scope", "## Product Features by Phase");

    try requireContains(section, "Those should eventually land in:");
    try requireContains(section, "- `tools/lib/*.zig`");
    try requireContains(section, "- `scripts/zigux/`");
    try requireContains(section, "- `zigux/`");
    try requireContains(section, "- `Documentation/zigux/`");
    try requireContains(section, "- `samples/zigux/`");
    try requireContains(section, "- `lib/*.zig`");
    try requireContains(section, "- `drivers/*/*.zig`");
    try requireContains(section, "- `fs/*.zig`");
    try requireContains(section, "- `security/*/*.zig`");
}
