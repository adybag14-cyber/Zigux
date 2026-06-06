const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase2 = sectionBetween(
    roadmap,
    "## Phase 2: Toolchain and Kbuild Enablement",
    "## Phase 3: ABI and Interop Substrate",
);

fn sectionBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) []const u8 {
    @setEvalBranchQuota(20_000);
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse @panic("missing section start");
    const tail = haystack[start..];
    const end = std.mem.indexOf(u8, tail[start_marker.len..], end_marker) orelse @panic("missing section end");
    return tail[0 .. start_marker.len + end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 contract is scoped to the toolchain and kbuild packet" {
    try expectContains(phase2, "Primary product goal:");
    try expectContains(phase2, "make Zigux buildable, reproducible, and acceptable inside Linux-style workflows");
    try expectContains(phase2, "Required Zigux features:");
    try expectContains(phase2, "Recommended Zigux destinations:");

    try expectNotContains(phase2, "define the permanent C/Zigux boundary");
    try expectNotContains(phase2, "mixed-language helper build path");
}

test "phase2 pins the Linux tooling anchors" {
    const anchors = [_][]const u8{
        "`scripts/basic/fixdep.c`",
        "`scripts/genksyms/genksyms.c`",
        "`scripts/kconfig/conf.c`",
        "`scripts/kconfig/confdata.c`",
    };

    for (anchors) |anchor| {
        try expectContains(phase2, anchor);
    }
}

test "phase2 preserves the toolchain validation feature packet" {
    const features = [_][]const u8{
        "compiler pinning and upgrade policy",
        "deterministic artifact checks",
        "selected dual implementations",
        "wrapper-first path for parser-heavy tooling",
        "cross-arch build matrix",
    };

    for (features) |feature| {
        try expectContains(phase2, feature);
    }
}

test "phase2 preserves approved Zigux destinations and ZAR transfer rule" {
    const destinations = [_][]const u8{
        "`scripts/zigux/fixdep.zig`",
        "`scripts/zigux/genksyms.zig`",
        "`scripts/zigux/kconfig/conf_bridge.zig`",
        "`scripts/zigux/kconfig/confdata_bridge.zig`",
        "`zigux/Makefile`",
    };

    for (destinations) |destination| {
        try expectContains(phase2, destination);
    }

    try expectContains(phase2, "freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior.");
}
