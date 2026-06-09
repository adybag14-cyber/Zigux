const std = @import("std");

const readme = @embedFile("README.md");
const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
const ledger = @embedFile("BOOTSTRAP_COMMIT_LEDGER.md");

const readme_markers = [_][]const u8{
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
    "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
};

const roadmap_markers = [_][]const u8{
    "## Bootstrap Status Note",
    "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
    "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
    "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
};

const ledger_markers = [_][]const u8{
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "## Scope Note",
    "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
};

test "alpha README preserves planning-only and live-doc handoff boundaries" {
    for (readme_markers) |marker| {
        try expectContains(readme, marker);
    }

    try expectOrdered(readme, "`zigux-alpha` is the Zigux bootstrap workspace.", "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.");
    try expectOrdered(readme, "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.", "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.");
}

test "roadmap keeps the bootstrap status note before phase materialization claims" {
    for (roadmap_markers) |marker| {
        try expectContains(roadmap, marker);
    }

    try expectOrdered(roadmap, "## Bootstrap Status Note", "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectOrdered(roadmap, "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.", "## zigux-alpha Scope");
}

test "ledger keeps early-train scope bounded to the broadened phase two tranche" {
    for (ledger_markers) |marker| {
        try expectContains(ledger, marker);
    }

    try expectOrdered(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`", "## Scope Note");
    try expectOrdered(ledger, "## Scope Note", "## Release-Planning Continuation");
    try expectOrdered(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.", "Documentation/zigux/phase12-release-sequencing.md");
}

test "charter files agree on roadmap-ledger-product-doc lookup order" {
    try expectContains(readme, "[ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)");
    try expectContains(readme, "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)");
    try expectContains(readme, "[Live Product Docs](../Documentation/zigux/README.md)");
    try expectOrdered(readme, "[ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)", "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)");
    try expectOrdered(readme, "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)", "[Live Product Docs](../Documentation/zigux/README.md)");

    try expectContains(roadmap, "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse
        @panic("ordered checker marker start is missing");
    const after_index = std.mem.indexOf(u8, haystack, after) orelse
        @panic("ordered checker marker end is missing");
    try std.testing.expect(before_index < after_index);
}
