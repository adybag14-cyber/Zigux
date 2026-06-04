const std = @import("std");

const ledger = @embedFile("BOOTSTRAP_COMMIT_LEDGER.md");
const readme = @embedFile("README.md");
const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "bootstrap ledger keeps folder charter as first commit train entry" {
    try requireContains(ledger, "# Zigux Alpha Bootstrap Commit Ledger");
    try requireContains(ledger, "This ledger turns the roadmap into the first product commit train.");
    try requireContains(ledger, "1. `docs(zigux-alpha): establish roadmap and folder charter`");
    try requireContains(ledger, "- `zigux-alpha/README.md`");
    try requireContains(ledger, "- `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`");

    try requireBefore(
        ledger,
        "1. `docs(zigux-alpha): establish roadmap and folder charter`",
        "2. `docs(zigux): add documentation root, review checklist, and freeze map`",
    );
    try requireBefore(
        ledger,
        "2. `docs(zigux): add documentation root, review checklist, and freeze map`",
        "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
    );
}

test "alpha README keeps the ledger bounded and planning-only" {
    try requireContains(readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try requireContains(readme, "It does not exist to become a permanent parallel subsystem tree.");
    try requireContains(readme, "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.");
    try requireContains(readme, "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche");
    try requireContains(readme, "confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.");
    try requireContains(readme, "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.");
    try requireContains(readme, "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
    try requireContains(readme, "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.");
}

test "roadmap status note preserves live-state confirmation boundary" {
    try requireContains(roadmap, "## Bootstrap Status Note");
    try requireContains(roadmap, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try requireContains(roadmap, "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try requireContains(roadmap, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes");
    try requireContains(roadmap, "before treating every later phase packet below as already materialized on `master`.");
    try requireContains(roadmap, "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/`");
}
