const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
pub const find_bit = @import("find_bit");
const bitmap = @import("bitmap");
const rbtree = @import("rbtree");
const string = @import("string");

const RbtreeSmokeEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }

    fn cmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
        const wanted: *const i32 = @ptrCast(@alignCast(key));
        const entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", node);
        if (wanted.* < entry.key) return -1;
        if (wanted.* > entry.key) return 1;
        return 0;
    }
};

test "phase1 host-tools smoke imports the live helper modules" {
    try std.testing.expect(@hasDecl(argv_split, "argvSplit"));
    try std.testing.expect(@hasDecl(cmdline, "memparse"));
    try std.testing.expect(@hasDecl(find_bit, "findFirstBit"));
    try std.testing.expect(@hasDecl(bitmap, "setRange"));
    try std.testing.expect(@hasDecl(rbtree, "find"));
    try std.testing.expect(@hasDecl(rbtree, "matchIterator"));
    try std.testing.expect(@hasDecl(string, "strtobool"));
}

test "phase1 host-tools smoke exercises live helper behavior" {
    const parsed = cmdline.memparse("64K tail");
    try std.testing.expectEqual(@as(u64, 64 << 10), parsed.value);
    try std.testing.expectEqualStrings(" tail", parsed.rest);
    try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(",quiet", ""));
    try std.testing.expect(cmdline.parseOptionStr("rootwait,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("rootwait,quiet", "debug"));

    const quoted = cmdline.nextArg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", quoted.param);
    try std.testing.expectEqualStrings("fast path", quoted.value.?);
    try std.testing.expectEqualStrings("tail", quoted.remaining);

    const unterminated = cmdline.nextArg("mode=\"fast boot") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", unterminated.param);
    try std.testing.expectEqualStrings("fast boot", unterminated.value.?);
    try std.testing.expectEqualStrings("", unterminated.remaining);

    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;
    var map = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&map, word_bits - 1, 3);
    try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(word_bits - 1, find_bit.findNextBit(&map, nbits, word_bits - 1));
    try std.testing.expectEqual(word_bits, find_bit.findNextBit(&map, nbits, word_bits));

    var rendered: [32]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&map, nbits, &rendered);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "{d}-{d}", .{ word_bits - 1, word_bits + 1 });
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);

    const sysfs = [_][]const u8{ "disabled", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));

    var tree_entries = [_]RbtreeSmokeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var tree_root = rbtree.Root.init();
    for (&tree_entries) |*entry| {
        rbtree.add(&entry.node, &tree_root, RbtreeSmokeEntry.less);
    }

    const duplicate_key = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);
    var duplicate_serials: [3]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, duplicate_serials[0..duplicate_count]);

    var cached_entries = [_]RbtreeSmokeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var cached_root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.addCached(&cached_entries[0].node, &cached_root, RbtreeSmokeEntry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.addCached(&cached_entries[1].node, &cached_root, RbtreeSmokeEntry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&cached_entries[2].node, &cached_root, RbtreeSmokeEntry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.eraseCached(&cached_entries[1].node, &cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.firstCached(&cached_root));
}
