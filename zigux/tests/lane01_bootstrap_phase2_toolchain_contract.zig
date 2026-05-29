const std = @import("std");

const roadmap_paths = [_][]const u8{
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    "../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn readRoadmap() ![]u8 {
    for (roadmap_paths) |path| {
        return readRepoFile(path, 256 * 1024) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "lane 01 roadmap phase 2 keeps the toolchain and kbuild scope explicit" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "## Phase 2: Toolchain and Kbuild Enablement");
    try expectContains(roadmap, "Primary product goal:");
    try expectContains(roadmap, "make Zigux buildable, reproducible, and acceptable inside Linux-style workflows");
    try expectContains(roadmap, "Required Zigux features:");
    try expectContains(roadmap, "compiler pinning and upgrade policy");
    try expectContains(roadmap, "deterministic artifact checks");
    try expectContains(roadmap, "selected dual implementations");
    try expectContains(roadmap, "wrapper-first path for parser-heavy tooling");
    try expectContains(roadmap, "cross-arch build matrix");
}

test "lane 01 roadmap phase 2 preserves current target and destination roster" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "Primary Linux targets:");
    try expectContains(roadmap, "`scripts/basic/fixdep.c`");
    try expectContains(roadmap, "`scripts/genksyms/genksyms.c`");
    try expectContains(roadmap, "`scripts/kconfig/conf.c`");
    try expectContains(roadmap, "`scripts/kconfig/confdata.c`");

    try expectContains(roadmap, "Recommended Zigux destinations:");
    try expectContains(roadmap, "`scripts/zigux/fixdep.zig`");
    try expectContains(roadmap, "`scripts/zigux/genksyms.zig`");
    try expectContains(roadmap, "`scripts/zigux/kconfig/conf_bridge.zig`");
    try expectContains(roadmap, "`scripts/zigux/kconfig/confdata_bridge.zig`");
    try expectContains(roadmap, "`zigux/Makefile`");
}

test "lane 01 roadmap phase 2 stays after phase 1 and before phase 3" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectBefore(roadmap, "## Product Features by Phase", "## Phase 1: Alpha Host-Side Helpers");
    try expectBefore(roadmap, "## Phase 1: Alpha Host-Side Helpers", "## Phase 2: Toolchain and Kbuild Enablement");
    try expectBefore(roadmap, "## Phase 2: Toolchain and Kbuild Enablement", "## Phase 3: ABI and Interop Substrate");
    try expectBefore(roadmap, "## Phase 2: Toolchain and Kbuild Enablement", "## Recommended Validation Gates");
}

test "lane 01 roadmap phase 2 keeps ZAR process discipline bounded to Zigux build maturity" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "Why ZAR matters here:");
    try expectContains(roadmap, "freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior.");
    try expectContains(roadmap, "ZAR should not try to become Zigux.");
    try expectContains(roadmap, "own experimental surface, do not let it consume Zigux product bandwidth.");
}
