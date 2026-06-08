const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn sectionBetween(start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, roadmap, start) orelse return error.MissingStartMarker;
    const after_start = roadmap[start_index..];
    const end_index = std.mem.indexOf(u8, after_start, end) orelse return error.MissingEndMarker;
    return after_start[0..end_index];
}

test "bootstrap status note preserves planning baseline boundary" {
    const note = try sectionBetween("## Bootstrap Status Note", "Positioning:");

    try requireContains(note, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try requireContains(note, "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try requireContains(note, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes");
    try requireContains(note, "before treating every later phase packet below as already materialized on `master`.");

    try requireNotContains(note, "already materialized on `master` without confirmation");
    try requireNotContains(note, "the roadmap alone is authoritative for current-state decisions");
}

test "bootstrap status note stays between purpose and positioning" {
    try requireOrder(roadmap, "## Purpose", "## Bootstrap Status Note");
    try requireOrder(roadmap, "## Bootstrap Status Note", "Positioning:");
    try requireOrder(roadmap, "Positioning:", "## Inputs Reviewed");

    const purpose_to_inputs = try sectionBetween("## Purpose", "## Inputs Reviewed");
    try requireContains(purpose_to_inputs, "## Bootstrap Status Note");
    try requireContains(purpose_to_inputs, "- `Zigux` is the product repo.");
}

test "bootstrap status note names all required current-state companions" {
    const note = try sectionBetween("## Bootstrap Status Note", "Positioning:");

    try requireContains(note, "`zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try requireContains(note, "the live repo tree");
    try requireContains(note, "`Documentation/zigux/README.md`");
    try requireContains(note, "active lane notes");

    try requireNotContains(note, "`zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` as the sole source");
    try requireNotContains(note, "skip active lane notes");
}

test "bootstrap status note aligns with alpha folder charter" {
    try requireContains(roadmap, "`zigux-alpha/` is the staging area for:");
    try requireContains(roadmap, "- roadmap and phase sequencing");
    try requireContains(roadmap, "`zigux-alpha/` is not the final home for:");
    try requireContains(roadmap, "- subsystem ports");

    try requireOrder(
        roadmap,
        "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
        "This roadmap is written for commit-and-push execution inside `Zigux`",
    );
}
