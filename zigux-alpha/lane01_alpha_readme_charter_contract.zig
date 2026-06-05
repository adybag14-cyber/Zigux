const std = @import("std");

const readme = @embedFile("README.md");

const workspace_heading = "# zigux-alpha";
const purpose_marker = "`zigux-alpha` is the Zigux bootstrap workspace.";
const exists_heading = "It exists to hold:";
const boundary_marker = "It does not exist to become a permanent parallel subsystem tree.";
const rules_heading = "Rules";
const active_heading = "Active product surfaces";
const start_here_heading = "Start here";

const purpose_bullets = [_][]const u8{
    "- program-level planning",
    "- source maps",
    "- phase ledgers",
    "- validation and porting rules",
    "- first-commit sequencing for the Zigux product buildout",
};

const rule_markers = [_][]const u8{
    "- Keep product planning and bootstrap artifacts here first.",
    "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
    "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.",
    "- Treat ZAR as the research and proving repo and Zigux as the product repo.",
    "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.",
};

const active_surface_markers = [_][]const u8{
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
};

const start_here_markers = [_][]const u8{
    "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
    "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "- [Live Product Docs](../Documentation/zigux/README.md)",
    "- [Review Checklist](../Documentation/zigux/review-checklist.md)",
    "- [Freeze Map](../Documentation/zigux/freeze-map.md)",
    "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
};

test "README keeps the bootstrap workspace identity before the rules handoff" {
    try expectOrdered(workspace_heading, purpose_marker);
    try expectOrdered(purpose_marker, exists_heading);
    try expectOrdered(exists_heading, boundary_marker);
    try expectOrdered(boundary_marker, rules_heading);
}

test "README preserves the exact bootstrap workspace purpose roster" {
    const section = between(exists_heading, boundary_marker);

    try std.testing.expectEqual(@as(usize, purpose_bullets.len), countBulletLines(section));
    for (purpose_bullets) |marker| {
        try expectContains(section, marker);
    }
}

test "README keeps product code out of the alpha workspace" {
    const rules = between(rules_heading, active_heading);

    try std.testing.expectEqual(@as(usize, rule_markers.len), countBulletLines(rules));
    for (rule_markers) |marker| {
        try expectContains(rules, marker);
    }
    try expectContains(rules, "native Linux locations");
    try expectContains(rules, "small `zigux/` support root");
    try expectContains(rules, "Do not create `zigux-alpha/ports/`");
    try expectNotContains(rules, "Move actual product code into `zigux-alpha/ports/`");
}

test "README hands readers from alpha planning to live product surfaces" {
    const active = between(active_heading, start_here_heading);
    const start = readme[requireIndex(start_here_heading)..];

    try std.testing.expectEqual(@as(usize, active_surface_markers.len), countBulletLines(active));
    for (active_surface_markers) |marker| {
        try expectContains(active, marker);
    }

    try std.testing.expectEqual(@as(usize, start_here_markers.len), countBulletLines(start));
    for (start_here_markers) |marker| {
        try expectContains(start, marker);
    }
    try expectOrdered(active_heading, start_here_heading);
}

fn between(start_marker: []const u8, end_marker: []const u8) []const u8 {
    const start = requireIndex(start_marker) + start_marker.len;
    const end = std.mem.indexOfPos(u8, readme, start, end_marker) orelse
        @panic("required README end marker is missing");
    std.debug.assert(start < end);
    return readme[start..end];
}

fn countBulletLines(text: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.startsWith(u8, line, "- ")) {
            count += 1;
        }
    }
    return count;
}

fn requireIndex(needle: []const u8) usize {
    return std.mem.indexOf(u8, readme, needle) orelse
        @panic("required README marker is missing");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = requireIndex(before);
    const after_index = requireIndex(after);
    try std.testing.expect(before_index < after_index);
}
