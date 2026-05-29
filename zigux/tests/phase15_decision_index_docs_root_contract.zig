const std = @import("std");

const GovernanceSurface = struct {
    path: []const u8,
    required_terms: []const []const u8,
};

const surfaces = [_]GovernanceSurface{
    .{
        .path = "Documentation/zigux/README.md",
        .required_terms = &.{
            "Phase 15 notes",
            "Architecture Council",
            "freeze-map status change",
            "governance packet",
        },
    },
    .{
        .path = "Documentation/zigux/phase15-architecture-council-decision-index.md",
        .required_terms = &.{
            "PHASE15_STATUS=architecture_council_decision_index_landed",
            "PHASE15_LANE_KEY=P15-L09",
            "PHASE15_SLICE=decision-record-inventory",
            "approved status-bucket changes recorded on current `master`: none",
            "stay-in-C closeout decision records recorded on current `master`: none",
            "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
            "zero-decision inventory",
        },
    },
    .{
        .path = "Documentation/zigux/freeze-map.md",
        .required_terms = &.{
            "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change",
            "only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review",
        },
    },
    .{
        .path = "Documentation/zigux/review-checklist.md",
        .required_terms = &.{
            "Architecture Council decision",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "Documentation/zigux/phase15-study-only-anchor-accounting.md",
        },
    },
};

fn loadRepoFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit)) catch |err| switch (err) {
        error.FileNotFound => retry: {
            var rooted_path: [512]u8 = undefined;
            const candidate = try std.fmt.bufPrint(&rooted_path, "../../{s}", .{path});
            break :retry try std.Io.Dir.cwd().readFileAlloc(io, candidate, std.testing.allocator, .limited(limit));
        },
        else => err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 docs root explicitly carries the Architecture Council decision index" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const readme = try loadRepoFile(io_instance.io(), "Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "Phase 15 notes");
    try expectContains(readme, "Architecture Council");
    try expectContains(readme, "freeze-map status change");
    try expectContains(readme, "governance packet");
}

test "decision index keeps zero-decision posture separate from governance evidence" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const decision_index = try loadRepoFile(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-decision-index.md",
        20 * 1024,
    );
    defer std.testing.allocator.free(decision_index);

    try expectContains(decision_index, "Current decision inventory");
    try expectContains(decision_index, "approved status-bucket changes recorded on current `master`: none");
    try expectContains(decision_index, "stay-in-C closeout decision records recorded on current `master`: none");
    try expectContains(decision_index, "no freeze-map anchor has an Architecture Council approval for a status change on current `master`");
    try expectContains(decision_index, "blocker-accounting and governance truthfulness evidence rather than approval evidence");
    try expectContains(decision_index, "zero-decision inventory");
}

test "shared governance surfaces preserve the decision-index approval boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    for (surfaces) |surface| {
        const body = try loadRepoFile(io_instance.io(), surface.path, 128 * 1024);
        defer std.testing.allocator.free(body);

        for (surface.required_terms) |term| {
            try expectContains(body, term);
        }
    }
}
