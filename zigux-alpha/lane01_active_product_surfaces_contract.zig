const std = @import("std");

const readme = @embedFile("README.md");

const active_heading = "Active product surfaces\n";
const start_here_heading = "\nStart here\n";

const expected_surfaces = [_][]const u8{
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
};

test "active product surfaces packet is present and ordered" {
    const packet = activeProductSurfacesPacket();

    var cursor: usize = 0;
    for (expected_surfaces) |surface| {
        const relative = std.mem.indexOf(u8, packet[cursor..], surface) orelse return error.MissingActiveSurface;
        cursor += relative + surface.len;
    }
}

test "active product surfaces are unique" {
    const packet = activeProductSurfacesPacket();

    for (expected_surfaces) |surface| {
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(packet, surface));
    }
}

test "packet stays after rules and before start here" {
    const rules_index = std.mem.indexOf(u8, readme, "Rules\n") orelse return error.MissingRulesHeading;
    const active_index = std.mem.indexOf(u8, readme, active_heading) orelse return error.MissingActiveHeading;
    const start_here_index = std.mem.indexOf(u8, readme, start_here_heading) orelse return error.MissingStartHereHeading;
    const windows_note_index = std.mem.indexOf(u8, readme, "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.") orelse return error.MissingWindowsNote;

    try std.testing.expect(rules_index < windows_note_index);
    try std.testing.expect(windows_note_index < active_index);
    try std.testing.expect(active_index < start_here_index);
}

fn activeProductSurfacesPacket() []const u8 {
    const active_index = std.mem.indexOf(u8, readme, active_heading) orelse return "";
    const packet_start = active_index + active_heading.len;
    const relative_end = std.mem.indexOf(u8, readme[packet_start..], start_here_heading) orelse return "";
    return readme[packet_start .. packet_start + relative_end];
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative| {
        count += 1;
        cursor += relative + needle.len;
    }
    return count;
}
