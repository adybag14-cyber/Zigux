const std = @import("std");

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const validator_path = "scripts/zigux/validate-phase1-closure.py";

const DocsOnlyMarker = struct {
    name: []const u8,
    validator_key: []const u8,
    description_fragment: []const u8,
};

const docs_only_markers = [_]DocsOnlyMarker{
    .{
        .name = "PHASE1_BITMAP_PARTIAL_XOR_REVIEW",
        .validator_key = "bitmap_partial_xor_review",
        .description_fragment = "partial_xor_nbits and partial_xor_masked_values stay owned by the shared Phase 1 parity fixture",
    },
    .{
        .name = "PHASE1_BITMAP_COMPLEMENT_TAIL_REVIEW",
        .validator_key = "bitmap_complement_tail_review",
        .description_fragment = "helper-local complement-tail masking stays explicit through the direct bitmap tests",
    },
    .{
        .name = "PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW",
        .validator_key = "find_bit_linux_alias_tail_review",
        .description_fragment = "helper-local Linux-style find_next_or_bit tail and past-end alias proof",
    },
};

const validator_owned_neighbors = [_][]const u8{
    "PHASE1_BITMAP_UNIT_REVIEW",
    "PHASE1_BITMAP_EMPTY_UNIT_REVIEW",
    "PHASE1_FIND_BIT_REVIEW_GUARD",
    "bitmap_unit_review",
    "bitmap_empty_unit_review",
    "find_bit_review_guard",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |relative| {
        count += 1;
        index += relative + needle.len;
    }
    return count;
}

test "docs-only Phase 1 review markers stay present in the closure note" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, closure_note_path);
    defer allocator.free(closure_note);

    for (docs_only_markers) |marker| {
        try std.testing.expectEqual(@as(usize, 1), countNeedle(closure_note, marker.name));
        try std.testing.expect(std.mem.indexOf(u8, closure_note, marker.description_fragment) != null);
    }
}

test "closure validator does not promote docs-only review markers into the hard roster" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, validator_path);
    defer allocator.free(validator);

    for (docs_only_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, validator, marker.name) == null);
        try std.testing.expect(std.mem.indexOf(u8, validator, marker.validator_key) == null);
    }
}

test "neighboring validator-owned closure markers remain explicit" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, validator_path);
    defer allocator.free(validator);

    for (validator_owned_neighbors) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, validator, needle) != null);
    }
}
