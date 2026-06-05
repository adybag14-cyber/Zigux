const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const section_heading = "## Workstreams and Ownership Model";
const previous_heading = "## Freeze Map for Near- and Mid-Term Planning";
const next_heading = "## Risk Register That Must Drive Prioritization";

const workstream_markers = [_][]const u8{
    "- Architecture Council",
    "- PMO / Release Management",
    "- Host Tools Alpha Pod",
    "- Toolchain and Kbuild Team",
    "- ABI and Runtime Team",
    "- Validation and Perf Team",
    "- Developer Enablement",
    "- Kernel Leaf Libraries Pod",
    "- Repo Tooling Pod",
    "- Runtime Pilot Pod",
    "- Virtio Driver Pod",
    "- Simple Drivers Pod",
    "- Complex Drivers and Infra Pod",
    "- Shared Subsystems Pod",
    "- Core-Adjacent Pod",
};

const declaration_markers = [_][]const u8{
    "- owner",
    "- phase",
    "- status bucket",
    "- validation gate",
    "- rollback owner",
};

test "workstreams section remains between freeze map and risk register" {
    try expectOrdered(previous_heading, section_heading);
    try expectOrdered(section_heading, next_heading);
}

test "workstreams section preserves the fifteen workstream execution model" {
    const section = workstreamsSection();

    try expectContains(section, "The bundle supports a 15-workstream execution model.");
    try expectContains(section, "Core workstreams:");
    for (workstream_markers) |marker| {
        try expectContains(section, marker);
    }
}

test "workstreams section rejects stale aggregate workstream counts" {
    const section = workstreamsSection();
    const core_roster = coreWorkstreamRoster(section);

    try std.testing.expectEqual(@as(usize, workstream_markers.len), countBulletLines(core_roster));
    try expectContains(section, "The bundle supports a 15-workstream execution model.");
    try expectNotContains(section, "17-workstream");
    try expectNotContains(section, "workstreams: `17`");
}

test "workstreams section preserves active commit series declarations" {
    const section = workstreamsSection();

    try expectContains(section, "For Zigux, that means every active commit series should declare:");
    for (declaration_markers) |marker| {
        try expectContains(section, marker);
    }
}

fn workstreamsSection() []const u8 {
    const start = requireIndex(section_heading);
    const end = requireIndex(next_heading);
    std.debug.assert(start < end);
    return roadmap[start..end];
}

fn coreWorkstreamRoster(section: []const u8) []const u8 {
    const start_marker = "Core workstreams:\n";
    const end_marker = "\n\nFor Zigux, that means every active commit series should declare:";
    const start = (std.mem.indexOf(u8, section, start_marker) orelse
        @panic("core workstream roster start is missing")) + start_marker.len;
    const end = std.mem.indexOfPos(u8, section, start, end_marker) orelse
        @panic("core workstream roster end is missing");
    return section[start..end];
}

fn countBulletLines(text: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.startsWith(u8, line, "- ")) {
            count += 1;
        }
    }
    return count;
}

fn requireIndex(needle: []const u8) usize {
    return std.mem.indexOf(u8, roadmap, needle) orelse
        @panic("required roadmap marker is missing");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = requireIndex(before);
    const after_index = requireIndex(after);
    try std.testing.expect(before_index < after_index);
}
