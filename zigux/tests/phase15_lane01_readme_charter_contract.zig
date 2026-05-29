const std = @import("std");

const readme_path = "../../zigux-alpha/README.md";

fn loadReadme(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, readme_path, allocator, .limited(128 * 1024));
}

fn expectContains(readme: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, readme, needle) != null);
}

fn expectOrdered(readme: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, readme, before) orelse return error.MissingBeforeAnchor;
    const after_index = std.mem.indexOf(u8, readme, after) orelse return error.MissingAfterAnchor;
    try std.testing.expect(before_index < after_index);
}

test "lane01 README keeps the bootstrap workspace charter bounded" {
    const readme = try loadReadme(std.testing.allocator);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "# zigux-alpha\n");
    try expectContains(readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(readme, "It exists to hold:");
    try expectContains(readme, "- program-level planning");
    try expectContains(readme, "- source maps");
    try expectContains(readme, "- phase ledgers");
    try expectContains(readme, "- validation and porting rules");
    try expectContains(readme, "- first-commit sequencing for the Zigux product buildout");
    try expectContains(readme, "It does not exist to become a permanent parallel subsystem tree.");
    try expectContains(readme, "- Keep product planning and bootstrap artifacts here first.");
    try expectContains(readme, "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.");
    try expectContains(readme, "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
    try expectContains(readme, "- Treat ZAR as the research and proving repo and Zigux as the product repo.");

    try expectOrdered(readme, "It exists to hold:", "It does not exist to become a permanent parallel subsystem tree.");
    try expectOrdered(readme, "It does not exist to become a permanent parallel subsystem tree.", "Rules\n");
    try expectOrdered(readme, "Rules\n", "Active product surfaces\n");
    try expectOrdered(readme, "Active product surfaces\n", "Start here\n");
}

test "lane01 README preserves the live-state ledger handoff rule" {
    const readme = try loadReadme(std.testing.allocator);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.");
    try expectContains(readme, "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.");

    try expectOrdered(
        readme,
        "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
        "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche",
    );
    try expectOrdered(
        readme,
        "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche",
        "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
    );
}

test "lane01 README keeps active surfaces and start links discoverable" {
    const readme = try loadReadme(std.testing.allocator);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.");
    try expectContains(readme, "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.");
    try expectContains(readme, "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.");
    try expectContains(readme, "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.");
    try expectContains(readme, "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.");

    try expectContains(readme, "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)");
    try expectContains(readme, "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)");
    try expectContains(readme, "- [Live Product Docs](../Documentation/zigux/README.md)");
    try expectContains(readme, "- [Review Checklist](../Documentation/zigux/review-checklist.md)");
    try expectContains(readme, "- [Freeze Map](../Documentation/zigux/freeze-map.md)");
    try expectContains(readme, "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)");

    try expectOrdered(readme, "Active product surfaces\n", "- `Documentation/zigux/README.md`");
    try expectOrdered(readme, "Start here\n", "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)");
}
