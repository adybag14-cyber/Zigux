// Ported from check-phase1-helper-replay-presence.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_HELPER_REPLAY_PRESENCE_SELF_TEST=pass";

const BUILD_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "root_source", .marker = ".root_source_file = b.path(\"phase1_helpers.zig\")," },
    .{ .label = "find_bit_module", .marker = ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\")," },
    .{ .label = "bitmap_module", .marker = ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\")," },
    .{ .label = "rbtree_module", .marker = ".root_source_file = b.path(\"../../tools/lib/rbtree.zig\")," },
    .{ .label = "string_module", .marker = ".root_source_file = b.path(\"../../tools/lib/string.zig\")," },
    .{ .label = "find_bit_import", .marker = "root_module.addImport(\"find_bit\", find_bit_module);" },
    .{ .label = "bitmap_import", .marker = "root_module.addImport(\"bitmap\", bitmap_module);" },
    .{ .label = "rbtree_import", .marker = "root_module.addImport(\"rbtree\", rbtree_module);" },
    .{ .label = "string_import", .marker = "root_module.addImport(\"string\", string_module);" },
    .{ .label = "step_name", .marker = ".name = \"phase1-helpers\"," },
    .{ .label = "step_route", .marker = "\"Run the focused Phase 1 helper replay anchor from zigux/tests\"," },
};
const HELPER_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "bitmap_import", .marker = "const bitmap = @import(\"bitmap\");" },
    .{ .label = "find_bit_import", .marker = "const find_bit = @import(\"find_bit\");" },
    .{ .label = "rbtree_import", .marker = "const rbtree = @import(\"rbtree\");" },
    .{ .label = "string_import", .marker = "const string = @import(\"string\");" },
    .{ .label = "fixture_embed", .marker = "const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");" },
    .{ .label = "replay_test", .marker = "test \"phase 1 helper ports match committed parity fixture\" {" },
    .{ .label = "find_bit_replay", .marker = "try std.testing.expectEqual(fixture.find_bit.tail_clamped_last, find_bit.findLastBit(&tail_clamped_bits, tail_nbits));" },
    .{ .label = "bitmap_replay", .marker = "try std.testing.expectEqualSlices(u64, fixture.bitmap.partial_xor_masked_values, &[_]u64{" },
    .{ .label = "string_replay", .marker = "try std.testing.expectEqualSlices(u8, fixture.string.replace_char_cstr_bytes, &replace_char_cstr_bytes);" },
    .{ .label = "rbtree_replay", .marker = "try std.testing.expectEqualSlices(i32, fixture.rbtree.cached_leftmost_return_serials, &cached_leftmost_return_serials);" },
};
const SMOKE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_bit_decl", .marker = "try std.testing.expect(@hasDecl(find_bit, \"findFirstBit\"));" },
    .{ .label = "bitmap_decl", .marker = "try std.testing.expect(@hasDecl(bitmap, \"setRange\"));" },
    .{ .label = "rbtree_decl", .marker = "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));" },
    .{ .label = "string_decl", .marker = "try std.testing.expect(@hasDecl(string, \"strnchrNul\"));" },
    .{ .label = "smoke_test", .marker = "test \"phase1 host-tools smoke exercises live helper behavior\" {" },
};

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    if (failures.items.len > 0) return failures;

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_GUARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}


pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_HELPER_REPLAY_PRESENCE_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

