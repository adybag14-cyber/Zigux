const std = @import("std");

const Section = struct {
    name: []const u8,
    marker: []const u8,
};

const required_sections = [_]Section{
    .{ .name = "licensing", .marker = "## Licensing and Reuse Policy" },
    .{ .name = "non-negotiable-rules", .marker = "## Non-Negotiable Product Rules" },
    .{ .name = "zar-feed", .marker = "## How ZAR Should Feed Zigux" },
};

const rule_markers = [_][]const u8{
    "These rules are consistent across the bundle and should govern every Zigux commit series.",
    "1. No flag-day rewrite.",
    "- Zigux grows through mixed-language coexistence.",
    "- C remains in place until each bounded area proves parity and maintainability.",
    "2. No mirror-tree sprawl.",
    "- Do not build a fake parallel kernel under a generic Zigux namespace.",
    "- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.",
    "3. Co-locate product code with Linux ownership.",
    "- Host-side helper ports belong beside current files such as `tools/lib/*.zig`.",
    "- Runtime helper ports belong beside current files such as `lib/*.zig`.",
    "- Driver pilots belong in current subsystem trees such as `drivers/virtio/*.zig`.",
    "4. Keep the Zigux support root small.",
    "- The support root exists for boundary code, not for duplicating Linux subsystems.",
    "  - `zigux/kernel/`",
    "  - `zigux/helpers/`",
    "  - `zigux/bindings/`",
    "  - `zigux/uapi/`",
    "  - `zigux/tests/`",
    "  - `zigux/unsafe/`",
    "5. Port leaf helpers before shared runtime helpers.",
    "- Port shared runtime helpers before drivers.",
    "- Port simple drivers before high-throughput queueing and DMA-heavy drivers.",
    "6. Validation is mandatory before expansion.",
    "- Every approved target needs parity tests.",
    "- Every sensitive path needs a perf threshold.",
    "- Every migration needs a rollback owner.",
    "7. Wrapper-first or dual-implementation is the default where semantics are risky.",
    "- Build tooling",
    "- ABI/export surfaces",
    "- allocators",
    "- atomics and barriers",
    "- MMIO",
    "- virtio rings",
    "- DMA-sensitive drivers",
    "- tracing and queueing infrastructure",
    "8. Deep-core freeze is real.",
    "- Do not move these into active delivery before the roadmap says so:",
    "  - `kernel/sched/core.c`",
    "  - `mm/page_alloc.c`",
    "  - `kernel/rcu/tree.c`",
    "  - `net/core/skbuff.c`",
    "- Treat `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as boundary-study targets first, not rewrite targets.",
    "9. Human review remains mandatory.",
    "- Follow Linux process expectations.",
    "- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const prefixes = [_][]const u8{ "", "../", "../../" };
    for (prefixes) |prefix| {
        const candidate = if (prefix.len == 0)
            path
        else
            try std.mem.concat(std.testing.allocator, u8, &.{ prefix, path });
        defer if (prefix.len != 0) std.testing.allocator.free(candidate);

        return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), candidate, std.testing.allocator, .limited(limit)) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }

    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSectionOrder(haystack: []const u8) !void {
    var previous: ?usize = null;
    for (required_sections) |section| {
        const current = std.mem.indexOf(u8, haystack, section.marker) orelse return error.MissingRoadmapSection;
        if (previous) |position| {
            try std.testing.expect(current > position);
        }
        previous = current;
    }
}

test "lane 01 roadmap keeps non-negotiable rules in the bootstrap charter sequence" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectSectionOrder(roadmap);
}

test "lane 01 roadmap preserves the non-negotiable product rules packet" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024);
    defer std.testing.allocator.free(roadmap);

    inline for (rule_markers) |marker| {
        try expectContains(roadmap, marker);
    }
}
