const std = @import("std");

const Guard = struct {
    name: []const u8,
    checker_path: []const u8,
    marker: []const u8,
    helper: []const u8,
    required_phrases: []const []const u8,
};

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const lane_note_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const fixture_path = "zigux/tests/fixtures/phase1_helper_expected.json";
const smoke_route = "zigux/tests/phase1_host_tools_smoke.zig";

const find_bit_marker = "PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture";
const rbtree_marker = "PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route";

const guards = [_]Guard{
    .{
        .name = "find_bit",
        .checker_path = "scripts/zigux/check-phase1-find-bit-review-packet.py",
        .marker = find_bit_marker,
        .helper = "tools/lib/find_bit.zig",
        .required_phrases = &.{
            "helper-local find_bit anchors",
            "tail-clamped",
            "tail-inclusive-boundary",
            "closure note",
            "lane note",
            "manifest",
            "fixture",
        },
    },
    .{
        .name = "rbtree",
        .checker_path = "scripts/zigux/check-phase1-rbtree-review-packet.py",
        .marker = rbtree_marker,
        .helper = "tools/lib/rbtree.zig",
        .required_phrases = &.{
            "helper-local rbtree anchors",
            "duplicate-search",
            "cached-leftmost",
            "closure note",
            "lane note",
            "manifest",
            "fixture",
            "shared smoke route",
        },
    },
};

test "Phase 1 closure helper review guards stay exact and ordered" {
    try std.testing.expectEqualStrings("find_bit", guards[0].name);
    try std.testing.expectEqualStrings("rbtree", guards[1].name);

    for (guards) |guard| {
        try std.testing.expect(std.mem.startsWith(u8, guard.marker, "PHASE1_"));
        try std.testing.expect(std.mem.indexOf(u8, guard.marker, guard.checker_path) != null);
        try std.testing.expect(std.mem.indexOf(u8, guard.marker, guard.name) != null);

        for (guard.required_phrases) |phrase| {
            try std.testing.expect(std.mem.indexOf(u8, guard.marker, phrase) != null);
        }
    }
}

test "helper review guard checker paths remain one-to-one" {
    try std.testing.expectEqual(guards.len, 2);

    for (guards, 0..) |left, left_index| {
        for (guards, 0..) |right, right_index| {
            if (left_index == right_index) continue;
            try std.testing.expect(!std.mem.eql(u8, left.name, right.name));
            try std.testing.expect(!std.mem.eql(u8, left.checker_path, right.checker_path));
            try std.testing.expect(!std.mem.eql(u8, left.marker, right.marker));
        }
    }
}

test "review guard closure packet keeps explicit source surfaces" {
    for (guards) |guard| {
        try std.testing.expect(std.mem.endsWith(u8, guard.checker_path, "-review-packet.py"));
        try std.testing.expect(std.mem.endsWith(u8, guard.helper, ".zig"));

        try std.testing.expect(std.mem.indexOf(u8, guard.marker, closure_note_path) == null);
        try std.testing.expect(std.mem.indexOf(u8, guard.marker, "closure note") != null);
        try std.testing.expect(std.mem.indexOf(u8, guard.marker, "lane note") != null);
        try std.testing.expect(std.mem.indexOf(u8, guard.marker, "manifest") != null);
        try std.testing.expect(std.mem.indexOf(u8, guard.marker, "fixture") != null);
    }

    try std.testing.expect(std.mem.endsWith(u8, closure_note_path, "phase1-closure.md"));
    try std.testing.expect(std.mem.endsWith(u8, lane_note_path, "phase1-host-helper-lane-sequencing.md"));
    try std.testing.expect(std.mem.endsWith(u8, manifest_path, "phase1_helper_manifest.json"));
    try std.testing.expect(std.mem.endsWith(u8, fixture_path, "phase1_helper_expected.json"));
    try std.testing.expect(std.mem.endsWith(u8, smoke_route, "phase1_host_tools_smoke.zig"));
}
