const std = @import("std");

const roadmap_path = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md";

const phase8_heading = "## Phase 8: Userspace-Adjacent Tooling Expansion";
const phase7_heading = "## Phase 7: In-Kernel Leaf Libraries";
const phase9_heading = "## Phase 9: Runtime Pilot Modules";

const required_phase8_lines = [_][]const u8{
    "## Phase 8: Userspace-Adjacent Tooling Expansion",
    "Primary product goal:",
    "- prove Zigux inside serious repo-hosted tooling, not just tiny helpers",
    "Primary Linux anchors:",
    "- `tools/lib/subcmd/exec-cmd.c`",
    "- `tools/lib/subcmd/help.c`",
    "- `tools/lib/symbol/kallsyms.c`",
    "- `tools/lib/bpf/libbpf.c`",
    "Required Zigux features:",
    "- helper-first expansion",
    "- segmented plan for large consumers like libbpf",
    "- output-stable tooling behavior",
    "Recommended Zigux destinations:",
    "- `tools/lib/subcmd/*.zig`",
    "- `tools/lib/symbol/*.zig`",
    "- `tools/lib/bpf/zigux_segments/`",
};

fn readRoadmap(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, roadmap_path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingNeedle;
    const after_first = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[after_first..], needle) == null);
    return first;
}

test "roadmap phase 8 tooling packet keeps its current truth markers" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    for (required_phase8_lines) |line| {
        try requireContains(roadmap, line);
    }
}

test "roadmap phase 8 remains ordered between phase 7 and phase 9" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    const phase7 = try requireExactlyOnce(roadmap, phase7_heading);
    const phase8 = try requireExactlyOnce(roadmap, phase8_heading);
    const phase9 = try requireExactlyOnce(roadmap, phase9_heading);

    try std.testing.expect(phase7 < phase8);
    try std.testing.expect(phase8 < phase9);
}

test "roadmap phase 8 stays bounded to userspace tooling expansion" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    const phase8 = std.mem.indexOf(u8, roadmap, phase8_heading) orelse return error.MissingPhase8;
    const phase9 = std.mem.indexOf(u8, roadmap, phase9_heading) orelse return error.MissingPhase9;
    try std.testing.expect(phase8 < phase9);

    const section = roadmap[phase8..phase9];

    try requireContains(section, "tools/lib/subcmd/exec-cmd.c");
    try requireContains(section, "tools/lib/subcmd/help.c");
    try requireContains(section, "tools/lib/symbol/kallsyms.c");
    try requireContains(section, "tools/lib/bpf/libbpf.c");
    try requireContains(section, "tools/lib/bpf/zigux_segments/");

    try std.testing.expect(std.mem.indexOf(u8, section, "drivers/virtio") == null);
    try std.testing.expect(std.mem.indexOf(u8, section, "kernel/sched/core.c") == null);
    try std.testing.expect(std.mem.indexOf(u8, section, "full parity") == null);
}
