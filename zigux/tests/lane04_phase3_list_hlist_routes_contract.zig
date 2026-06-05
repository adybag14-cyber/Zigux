const std = @import("std");

const build_zig = @embedFile("build.zig");
const packet_build_zig = @embedFile("phase3_list_hlist_starter_packet_build.zig");
const packet_zig = @embedFile("phase3_list_hlist_starter_packet.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
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

test "shared tests root exposes the list/hlist starter route exactly once" {
    try expectContains(
        build_zig,
        "fn addPhase3ListHListStarterPacket(",
    );
    try expectContains(
        build_zig,
        ".root_source_file = b.path(\"phase3_list_hlist_starter_packet.zig\")",
    );
    try expectContains(
        build_zig,
        "root_module.addImport(\"list_view\", list_view);",
    );
    try expectContains(
        build_zig,
        "root_module.addImport(\"hlist_view\", hlist_view);",
    );
    try expectContains(
        build_zig,
        ".name = \"phase3-list-hlist-starter-packet\"",
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        countOccurrences(build_zig, "const phase3_list_hlist_step = b.step("),
    );
    try expectContains(
        build_zig,
        "\"Run the shared Phase 3 list/hlist starter packet from zigux/tests\"",
    );
}

test "phase3 aggregate routes keep list/hlist in the shared harness" {
    try expectContains(
        build_zig,
        "const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket(",
    );
    try expectContains(
        build_zig,
        "phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    );
    try expectContains(
        build_zig,
        "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    );
    try expectOrdered(
        build_zig,
        "const phase3_test_step = b.step(",
        "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    );
    try expectOrdered(
        build_zig,
        "const smoke_step = b.step(",
        "smoke_step.dependOn(phase3_test_step);",
    );
    try expectOrdered(
        build_zig,
        "const test_step = b.step(",
        "test_step.dependOn(phase3_test_step);",
    );
}

test "packet-local wrapper keeps the same standalone route vocabulary" {
    try expectContains(
        packet_build_zig,
        ".root_source_file = b.path(\"../helpers/list_view.zig\")",
    );
    try expectContains(
        packet_build_zig,
        ".root_source_file = b.path(\"../helpers/hlist_view.zig\")",
    );
    try expectContains(
        packet_build_zig,
        ".root_source_file = b.path(\"phase3_list_hlist_starter_packet.zig\")",
    );
    try expectContains(
        packet_build_zig,
        ".name = \"phase3-list-hlist-starter-packet\"",
    );
    try expectContains(
        packet_build_zig,
        "b.step(\n        \"phase3-list-hlist-starter-packet\"",
    );
    try expectContains(
        packet_build_zig,
        "\"Run the shared Phase 3 list/hlist starter packet\"",
    );
}

test "starter packet keeps list and hlist witness names reviewable" {
    try expectContains(
        packet_zig,
        "test \"list starter packet keeps a sentinel-only list empty and reviewable\"",
    );
    try expectContains(
        packet_zig,
        "test \"list starter packet keeps circular ordering and broken backlinks explicit\"",
    );
    try expectContains(
        packet_zig,
        "test \"hlist starter packet keeps empty heads and bounded chains explicit\"",
    );
    try expectContains(
        packet_zig,
        "test \"hlist starter packet reports the first broken prev-link witness\"",
    );
    try expectContains(packet_zig, "list_view.ListView.init(&head)");
    try expectContains(packet_zig, "hlist_view.HListView.init(&head)");
}
