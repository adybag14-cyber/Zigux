const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "Lane 01 roadmap keeps the 15-workstream ownership model explicit" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "## Workstreams and Ownership Model");
    try expectContains(roadmap, "The bundle supports a 15-workstream execution model.");
    try expectContains(roadmap, "Core workstreams:");
    try expectContains(roadmap, "- Architecture Council");
    try expectContains(roadmap, "- PMO / Release Management");
    try expectContains(roadmap, "- Host Tools Alpha Pod");
    try expectContains(roadmap, "- Toolchain and Kbuild Team");
    try expectContains(roadmap, "- ABI and Runtime Team");
    try expectContains(roadmap, "- Validation and Perf Team");
    try expectContains(roadmap, "- Developer Enablement");
    try expectContains(roadmap, "- Kernel Leaf Libraries Pod");
    try expectContains(roadmap, "- Repo Tooling Pod");
    try expectContains(roadmap, "- Runtime Pilot Pod");
    try expectContains(roadmap, "- Virtio Driver Pod");
    try expectContains(roadmap, "- Simple Drivers Pod");
    try expectContains(roadmap, "- Complex Drivers and Infra Pod");
    try expectContains(roadmap, "- Shared Subsystems Pod");
    try expectContains(roadmap, "- Core-Adjacent Pod");
}

test "Lane 01 roadmap requires ownership metadata before active commit series" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "For Zigux, that means every active commit series should declare:");
    try expectContains(roadmap, "- owner");
    try expectContains(roadmap, "- phase");
    try expectContains(roadmap, "- status bucket");
    try expectContains(roadmap, "- validation gate");
    try expectContains(roadmap, "- rollback owner");
}

test "Lane 01 roadmap keeps workstream ownership between freeze map and risk register" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectBefore(roadmap, "## Freeze Map for Near- and Mid-Term Planning", "## Workstreams and Ownership Model");
    try expectBefore(roadmap, "## Workstreams and Ownership Model", "## Risk Register That Must Drive Prioritization");
    try expectBefore(roadmap, "- those experiments should not be represented as near-term Zigux delivery commitments", "## Workstreams and Ownership Model");
    try expectBefore(roadmap, "- rollback owner", "## Risk Register That Must Drive Prioritization");
}
