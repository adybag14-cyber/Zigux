const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const Manifest = struct {
    indefinite_c_requirements: []const Requirement,
};

fn expectContains(io: std.Io, path: []const u8, snippets: []const []const u8) !void {
    const contents = try std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(contents);

    for (snippets) |snippet| {
        try std.testing.expect(std.mem.indexOf(u8, contents, snippet) != null);
    }
}

test "phase 15 indefinite-C policy keeps lane-owner vocabulary aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(policy_doc);

    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "lane owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "named owner") == null);

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    var saw_recordkeeping = false;
    for (parsed.value.indefinite_c_requirements) |requirement| {
        if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;
            try std.testing.expectEqualStrings("lane owner", requirement.required_terms[3]);
        }
    }
    try std.testing.expect(saw_recordkeeping);

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", &.{
        "named owner for the lane",
        "lane ownership",
    });
    try expectContains(io_instance.io(), "Documentation/zigux/review-checklist.md", &.{
        "current lane owner responsible for keeping that blocked evidence packet up to date",
    });

    const archive_paths = [_][]const u8{
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
    };

    for (archive_paths) |path| {
        try expectContains(io_instance.io(), path, &.{
            "lane owner: `pending`",
            "ownership_or_validation_changed",
        });
    }
}
