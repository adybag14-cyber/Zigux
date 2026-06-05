const std = @import("std");
const testing = std.testing;

const readme = @embedFile("README.md");

const rules_heading = "Rules\n";
const active_surfaces_heading = "Active product surfaces\n";
const windows_note = "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.";
const mirror_tree_rule = "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.";
const native_location_rule = "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.";

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn lastIndexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.lastIndexOf(u8, haystack, needle) orelse error.MissingMarker;
}

test "windows filesystem note remains inside the README rules packet" {
    const rules_index = try indexOfRequired(readme, rules_heading);
    const active_surfaces_index = try indexOfRequired(readme, active_surfaces_heading);
    const windows_note_index = try indexOfRequired(readme, windows_note);

    try testing.expect(rules_index < windows_note_index);
    try testing.expect(windows_note_index < active_surfaces_index);
    try testing.expectEqual(windows_note_index, try lastIndexOfRequired(readme, windows_note));
}

test "windows note stays paired with the no mirror tree rule" {
    const mirror_rule_index = try indexOfRequired(readme, mirror_tree_rule);
    const windows_note_index = try indexOfRequired(readme, windows_note);
    const active_surfaces_index = try indexOfRequired(readme, active_surfaces_heading);

    try testing.expect(mirror_rule_index < windows_note_index);
    try testing.expect(windows_note_index < active_surfaces_index);
}

test "rules packet keeps product code out of zigux-alpha" {
    const native_location_index = try indexOfRequired(readme, native_location_rule);
    const mirror_rule_index = try indexOfRequired(readme, mirror_tree_rule);
    const windows_note_index = try indexOfRequired(readme, windows_note);

    try testing.expect(native_location_index < mirror_rule_index);
    try testing.expect(mirror_rule_index < windows_note_index);
    try testing.expect(std.mem.indexOf(u8, readme, "Create `zigux-alpha/ports/`") == null);
}
