const std = @import("std");

const SourceFile = struct {
    contents: []u8,
};

const import_markers = [_][]const u8{
    "pub const find_bit = @import(\"find_bit\");",
    "const bitmap = @import(\"bitmap\");",
    "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");",
    "_ = phase1_find_bit_fixture_guard;",
};

const declaration_markers = [_][]const u8{
    "@hasDecl(find_bit, \"findFirstBit\")",
    "@hasDecl(bitmap, \"setRange\")",
};

const base_behavior_markers = [_][]const u8{
    "const word_bits = find_bit.bits_per_long;",
    "bitmap.setRange(&map, word_bits - 1, 3);",
    "find_bit.findFirstBit(&map, nbits)",
    "find_bit.findNextBit(&map, nbits, word_bits - 1)",
    "find_bit.findNextBit(&map, nbits, word_bits)",
    "find_bit.findLastBit(&map, nbits)",
    "find_bit.findFirstZeroBit(&tail_zero_map, nbits)",
    "find_bit.findNextZeroBit(&tail_zero_map, nbits, word_bits)",
    "find_bit.findFirstAndBit(&tail_and_lhs, &tail_and_rhs, nbits)",
    "find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, word_bits + 4)",
};

const tail_behavior_markers = [_][]const u8{
    "const tail_clamped_set = [_]find_bit.Word",
    "try std.testing.expectEqual(word_bits + 3, find_bit.findFirstBit(&tail_clamped_set, nbits));",
    "try std.testing.expectEqual(nbits, find_bit.findNextBit(&tail_clamped_set, nbits, word_bits + 4));",
    "try std.testing.expectEqual(word_bits + 3, find_bit.findLastBit(&tail_clamped_set, nbits));",
    "bitmap.lastWordMask(nbits) | (@as(find_bit.Word, 1) << 7)",
};

const andnot_clump_markers = [_][]const u8{
    "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned",
    "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)",
    "find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 2)",
    "find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4)",
    "find_bit.findFirstClump8(&clump, &clump_map, nbits)",
    "find_bit.find_first_clump8(&clump, &clump_map, nbits)",
    "find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long)",
    "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)",
};

fn readSource(path: []const u8, limit: usize) !SourceFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            std.testing.allocator,
            .limited(limit),
        ),
    };
}

fn unloadSource(source: SourceFile) void {
    std.testing.allocator.free(source.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.TestUnexpectedResult;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.TestUnexpectedResult;
    try std.testing.expect(before_index < after_index);
}

test "phase1 host-tools smoke keeps find_bit import and behavior anchors" {
    const smoke = try readSource("zigux/tests/phase1_host_tools_smoke.zig", 256 * 1024);
    defer unloadSource(smoke);

    inline for (import_markers) |marker| {
        try expectContains(smoke.contents, marker);
    }
    inline for (declaration_markers) |marker| {
        try expectContains(smoke.contents, marker);
    }
    inline for (base_behavior_markers) |marker| {
        try expectContains(smoke.contents, marker);
    }
    inline for (tail_behavior_markers) |marker| {
        try expectContains(smoke.contents, marker);
    }
    inline for (andnot_clump_markers) |marker| {
        try expectContains(smoke.contents, marker);
    }

    try expectOrdered(
        smoke.contents,
        "const word_bits = find_bit.bits_per_long;",
        "bitmap.setRange(&map, word_bits - 1, 3);",
    );
    try expectOrdered(
        smoke.contents,
        "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)",
        "find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4)",
    );
    try expectOrdered(
        smoke.contents,
        "find_bit.findFirstClump8(&clump, &clump_map, nbits)",
        "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)",
    );
}

test "phase1 host-tools build root keeps find_bit wired into smoke and bitmap" {
    const build_root = try readSource("zigux/tests/build.zig", 512 * 1024);
    defer unloadSource(build_root);

    const required_build_markers = [_][]const u8{
        "fn addPhase1HostToolsSmoke(",
        ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")",
        "const find_bit_module = b.createModule(.{",
        ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\")",
        "const bitmap_module = b.createModule(.{",
        ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\")",
        "bitmap_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"bitmap\", bitmap_module);",
        ".name = \"phase1-host-tools-smoke\"",
        "const phase1_step = b.step(",
        "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    };
    inline for (required_build_markers) |marker| {
        try expectContains(build_root.contents, marker);
    }

    try expectOrdered(
        build_root.contents,
        "bitmap_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"find_bit\", find_bit_module);",
    );
    try expectOrdered(
        build_root.contents,
        "root_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"bitmap\", bitmap_module);",
    );
}
