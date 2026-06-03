const std = @import("std");
const testing = std.testing;

const readme =
    \\# zigux-alpha
    \\
    \\`zigux-alpha` is the Zigux bootstrap workspace.
    \\
    \\It exists to hold:
    \\- program-level planning
    \\- source maps
    \\- phase ledgers
    \\- validation and porting rules
    \\- first-commit sequencing for the Zigux product buildout
    \\
    \\It does not exist to become a permanent parallel subsystem tree.
    \\
    \\Rules
    \\- Keep product planning and bootstrap artifacts here first.
    \\- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
    \\- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.
    \\- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.
    \\- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.
    \\- Treat ZAR as the research and proving repo and Zigux as the product repo.
    \\- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.
    \\
    \\Active product surfaces
    \\- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
    \\- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.
    \\- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.
    \\- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.
    \\- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.
    \\
    \\Start here
    \\- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
    \\- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
    \\- [Live Product Docs](../Documentation/zigux/README.md)
    \\- [Review Checklist](../Documentation/zigux/review-checklist.md)
    \\- [Freeze Map](../Documentation/zigux/freeze-map.md)
    \\- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)
;

const expected_rules = [_][]const u8{
    "- Keep product planning and bootstrap artifacts here first.",
    "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
    "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.",
    "- Treat ZAR as the research and proving repo and Zigux as the product repo.",
    "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.",
};

test "Lane 01 README keeps one bounded Rules packet" {
    try testing.expectEqual(@as(usize, 1), count(readme, "\nRules\n"));
    try testing.expectEqual(@as(usize, 1), count(readme, "\nActive product surfaces\n"));
    try testing.expectEqual(@as(usize, 1), count(readme, "\nStart here\n"));

    const rules_start = try requireIndex(readme, "\nRules\n");
    const active_start = try requireIndex(readme, "\nActive product surfaces\n");
    const start_here = try requireIndex(readme, "\nStart here\n");

    try testing.expect(rules_start < active_start);
    try testing.expect(active_start < start_here);

    const rules_body = readme[rules_start..active_start];
    for (expected_rules) |line| {
        try testing.expectEqual(@as(usize, 1), count(rules_body, line));
    }
}

test "Rules packet preserves bootstrap-to-product boundary language" {
    const rules_start = try requireIndex(readme, "\nRules\n");
    const active_start = try requireIndex(readme, "\nActive product surfaces\n");
    const rules_body = readme[rules_start..active_start];

    try testing.expect(std.mem.indexOf(u8, rules_body, "product planning and bootstrap artifacts") != null);
    try testing.expect(std.mem.indexOf(u8, rules_body, "actual product code") != null);
    try testing.expect(std.mem.indexOf(u8, rules_body, "native Linux locations") != null);
    try testing.expect(std.mem.indexOf(u8, rules_body, "`zigux/` support root") != null);
    try testing.expect(std.mem.indexOf(u8, rules_body, "Do not create `zigux-alpha/ports/`") != null);
}

test "Rules packet stays complete and ordered" {
    const rules_start = try requireIndex(readme, "\nRules\n");
    const active_start = try requireIndex(readme, "\nActive product surfaces\n");
    const rules_body = readme[rules_start..active_start];

    var previous: usize = 0;
    for (expected_rules, 0..) |line, index| {
        const at = try requireIndex(rules_body, line);
        if (index != 0) {
            try testing.expect(previous < at);
        }
        previous = at;
    }
}

fn requireIndex(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.RequiredMarkerMissing;
}

fn count(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |found| {
        total += 1;
        offset += found + needle.len;
    }
    return total;
}
