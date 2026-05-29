const std = @import("std");

const DocSurface = struct {
    path: []const u8,
    bytes: []const u8,
};

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const closeout_fields = [_][]const u8{
    "required approver set",
    "rollback owner",
    "evidence archive path",
    "automatic return-to-blocked trigger",
    "retired_from_active_discussion",
    "reopen triggers",
    "trigger-specific evidence refresh",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit)) catch |err| switch (err) {
        error.FileNotFound => blk: {
            const repo_relative = try std.mem.concat(std.testing.allocator, u8, &.{ "../../", path });
            defer std.testing.allocator.free(repo_relative);
            break :blk try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), repo_relative, std.testing.allocator, .limited(limit));
        },
        else => err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAll(surface: DocSurface, needles: []const []const u8) !void {
    _ = surface.path;
    for (needles) |needle| try expectContains(surface.bytes, needle);
}

test "freeze-map closeout contract keeps the shared anchor inventory aligned" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const study_accounting = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 48 * 1024);
    defer std.testing.allocator.free(study_accounting);

    const shared_surfaces = [_]DocSurface{
        .{ .path = "Documentation/zigux/README.md", .bytes = docs_root },
        .{ .path = "Documentation/zigux/review-checklist.md", .bytes = review_checklist },
        .{ .path = "Documentation/zigux/freeze-map.md", .bytes = freeze_map },
    };

    for (shared_surfaces) |surface| {
        try expectAll(surface, freeze_in_c_anchors[0..]);
        try expectAll(surface, study_only_anchors[0..]);
        try expectContains(surface.bytes, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    }

    try expectAll(.{ .path = "Documentation/zigux/phase15-study-only-anchor-accounting.md", .bytes = study_accounting }, study_only_anchors[0..]);
    try expectContains(freeze_map, "Study / Boundary Only");
    try expectContains(review_checklist, "study-only boundary context rather than runtime-substrate or bridge-readiness evidence");
    try expectContains(docs_root, "bounded below any Architecture Council approval claim");
}

test "freeze-map status-review fields stay visible from checklist to policy" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 96 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 64 * 1024);
    defer std.testing.allocator.free(decision_template);

    const policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 64 * 1024);
    defer std.testing.allocator.free(policy);

    const shared_review_surfaces = [_]DocSurface{
        .{ .path = "Documentation/zigux/review-checklist.md", .bytes = review_checklist },
        .{ .path = "Documentation/zigux/freeze-map.md", .bytes = freeze_map },
        .{ .path = "Documentation/zigux/phase15-architecture-council-review-process.md", .bytes = review_process },
        .{ .path = "Documentation/zigux/phase15-architecture-council-decision-record-template.md", .bytes = decision_template },
        .{ .path = "Documentation/zigux/phase15-indefinite-c-policy.md", .bytes = policy },
    };

    for (shared_review_surfaces) |surface| {
        try expectContains(surface.bytes, "current status bucket");
        try expectContains(surface.bytes, "requested decision bucket");
        try expectContains(surface.bytes, "validation gate summary");
        try expectContains(surface.bytes, "latest blocker disposition");
    }

    try expectAll(.{ .path = "Documentation/zigux/freeze-map.md", .bytes = freeze_map }, closeout_fields[0..]);
    try expectAll(.{ .path = "Documentation/zigux/phase15-indefinite-c-policy.md", .bytes = policy }, closeout_fields[0..]);
    try expectContains(review_checklist, "stay-in-C closeout prompts");
    try expectContains(decision_template, "Stay-In-C Closeout");
}

test "closeout contract rejects silent approval and silent reopen paths" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 64 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(docs_root, "keep the Phase 15 reminder bounded below any Architecture Council approval claim");
    try expectContains(docs_root, "any freeze-map status change");
    try expectContains(review_checklist, "avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision");
    try expectContains(freeze_map, "There is no silent exception path around the stay-in-C policy");
    try expectContains(policy, "There is no silent exception path around the indefinite-C policy");
    try expectContains(policy, "If the exception note cannot explain why dated master readback is insufficient");
}
