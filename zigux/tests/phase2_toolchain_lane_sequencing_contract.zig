const std = @import("std");
const testing = std.testing;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    const prefixes = [_][]const u8{ "", "../", "../../" };
    for (prefixes) |prefix| {
        const candidate = try std.fmt.allocPrint(allocator, "{s}{s}", .{ prefix, path });
        defer allocator.free(candidate);
        var io_instance: std.Io.Threaded = .init(allocator, .{});
        defer io_instance.deinit();
        if (std.Io.Dir.cwd().readFileAlloc(io_instance.io(), candidate, allocator, .limited(1024 * 1024))) |contents| {
            return contents;
        } else |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        }
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 toolchain lane note keeps owner split explicit" {
    const note = try readRepoFile(testing.allocator, "Documentation/zigux/phase2-toolchain-lane-sequencing.md");
    defer testing.allocator.free(note);

    const lane_markers = [_][]const u8{
        "shared sequencing lane `P2-Y10`",
        "shared backlog truthfulness lane `P2-Y12`",
        "Makefile toolchain lane `P2-X09`",
        "`P2-Y02` owns fixdep",
        "`P2-L07`",
        "`P2-L10`",
        "`P2-L11`",
        "`P2-X05`",
        "`P2-L18`",
        "`P2-L19`",
        "`P2-Y07`",
        "`P2-L24`",
    };
    for (lane_markers) |marker| {
        try expectContains(note, marker);
    }

    try expectContains(note, "Future Phase 2 toolchain work should therefore prefer owner-map and review-surface truthfulness");
    try expectContains(note, "Prefer one Phase 2 lane at a time");
    try expectContains(note, "do not reopen the shared lane");
}

test "shared packet surfaces stay tied to docs manifests validators and make routes" {
    const note = try readRepoFile(testing.allocator, "Documentation/zigux/phase2-toolchain-lane-sequencing.md");
    defer testing.allocator.free(note);

    const shared_surfaces = [_][]const u8{
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-lane-sequencing.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
        "zigux/Makefile",
    };
    for (shared_surfaces) |surface| {
        try expectContains(note, surface);
    }

    const routes = [_][]const u8{
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-validate",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2",
    };
    for (routes) |route| {
        try expectContains(note, route);
    }
}

test "neighboring phase2 packet files mirror the lane sequencing boundary" {
    const bootstrap = try readRepoFile(testing.allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer testing.allocator.free(bootstrap);
    const review = try readRepoFile(testing.allocator, "Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(review);
    const manifest = try readRepoFile(testing.allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(manifest);
    const makefile = try readRepoFile(testing.allocator, "zigux/Makefile");
    defer testing.allocator.free(makefile);

    try expectContains(bootstrap, "make -C zigux phase2-toolchain");
    try expectContains(bootstrap, "make -C zigux phase2-cross");
    try expectContains(bootstrap, "make -C zigux phase2");
    try expectContains(review, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(review, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(review, "make -C zigux phase2-cross");
    try expectContains(manifest, "phase2_tool_manifest");
    try expectContains(manifest, "phase2-toolchain-bootstrap-notes.md");
    try expectContains(manifest, "make -C zigux phase2-tools");
    try expectContains(makefile, "phase2-toolchain");
    try expectContains(makefile, "phase2-validate");
    try expectContains(makefile, "phase2-cross");
    try expectContains(makefile, "phase2: phase2-validate");
}
