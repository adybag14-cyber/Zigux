const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const bootstrap_commits = [_][]const u8{
    "`docs(zigux-alpha): establish roadmap and folder charter`",
    "`docs(Documentation/zigux): add program charter and freeze map`",
    "`build(scripts/zigux): add toolchain pinning and version checks`",
    "`test(zigux/tests): add differential harness scaffolding`",
};

const phase1_commits = [_][]const u8{
    "`feat(tools/lib): add bitmap.zig host helper port`",
    "`feat(tools/lib): add find_bit.zig host helper port`",
    "`feat(tools/lib): add string.zig host helper port`",
    "`feat(tools/lib): add rbtree.zig host helper port`",
    "`test(tools/lib): add golden-output parity gates for alpha helper ports`",
};

const phase2_commits = [_][]const u8{
    "`feat(scripts/zigux): add fixdep dual implementation`",
    "`feat(scripts/zigux): add genksyms dual implementation`",
    "`feat(scripts/zigux): add kconfig bridge scaffolding`",
    "`ci(zigux): add cross-arch build and artifact diff matrix`",
};

const phase5_commits = [_][]const u8{
    "`feat(samples/zigux): add reference samples for fifo, kobject, kretprobe, and trace events`",
    "`docs(Documentation/zigux): add sample-backed review guide`",
};

fn sequenceSection() ![]const u8 {
    const start = std.mem.indexOf(u8, roadmap, "## First Commit and Push Sequence for Zigux") orelse return error.MissingSequenceStart;
    const end = std.mem.indexOfPos(u8, roadmap, start, "## Recommended Validation Gates") orelse return error.MissingSequenceEnd;
    return roadmap[start..end];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn expectOrderedList(haystack: []const u8, markers: []const []const u8) !void {
    var previous_index: ?usize = null;

    for (markers) |marker| {
        const marker_index = std.mem.indexOf(u8, haystack, marker) orelse return error.MissingMarker;
        if (previous_index) |index| {
            try testing.expect(index < marker_index);
        }
        previous_index = marker_index;
    }
}

test "roadmap keeps the first commit sequence as a bounded bootstrap packet" {
    try expectOrdered(roadmap, "## Risk Register That Must Drive Prioritization", "## First Commit and Push Sequence for Zigux");
    try expectOrdered(roadmap, "## First Commit and Push Sequence for Zigux", "## Recommended Validation Gates");

    const section = try sequenceSection();
    try expectContains(section, "This is the recommended near-term commit train after this roadmap lands.");
    try expectContains(section, "### Bootstrap commits");
    try expectContains(section, "### Phase 1 commits");
    try expectContains(section, "### Phase 2 commits");
    try expectContains(section, "### Phase 3 and 4 commits");
    try expectContains(section, "### Phase 5 commits");
}

test "roadmap keeps bootstrap before host helpers and phase2 scripts" {
    const section = try sequenceSection();

    try expectOrdered(section, "### Bootstrap commits", "### Phase 1 commits");
    try expectOrdered(section, "### Phase 1 commits", "### Phase 2 commits");
    try expectOrdered(section, "### Phase 2 commits", "### Phase 3 and 4 commits");
    try expectOrdered(section, "### Phase 3 and 4 commits", "### Phase 5 commits");

    try expectOrderedList(section, &bootstrap_commits);
    try expectOrderedList(section, &phase1_commits);
    try expectOrderedList(section, &phase2_commits);
    try expectOrderedList(section, &phase5_commits);

    try expectOrdered(section, bootstrap_commits[bootstrap_commits.len - 1], phase1_commits[0]);
    try expectOrdered(section, phase1_commits[phase1_commits.len - 1], phase2_commits[0]);
    try expectOrdered(section, phase2_commits[phase2_commits.len - 1], phase5_commits[0]);
    try expectContains(section, "Do not schedule Phase 10+ commits until the earlier gates are actually green.");
}

test "roadmap sequence keeps docs, tooling, and validation destinations explicit" {
    const section = try sequenceSection();

    try expectContains(section, "- add `zigux-alpha/README.md`");
    try expectContains(section, "- add this roadmap");
    try expectContains(section, "- create `Documentation/zigux/README.md`");
    try expectContains(section, "- create `Documentation/zigux/review-checklist.md`");
    try expectContains(section, "- create `Documentation/zigux/freeze-map.md`");
    try expectContains(section, "- create `scripts/zigux/`");
    try expectContains(section, "- add Zig toolchain version policy");
    try expectContains(section, "- add deterministic version-check helper");
    try expectContains(section, "- create `zigux/tests/`");
    try expectContains(section, "- add bitmap and atomic parity harness scaffolds");
    try expectContains(section, "- add artifact-diff scaffolds for host-side tools");
}
