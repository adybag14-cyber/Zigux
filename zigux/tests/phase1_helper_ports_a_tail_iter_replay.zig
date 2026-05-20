const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn wordMask(bits: []const usize) Word {
    var value: Word = 0;
    for (bits) |bit| {
        value |= @as(Word, 1) << @intCast(bit);
    }
    return value;
}

const Entry = struct {
    key: i32,
    node: rbtree.Node = .{},

    fn init(key: i32) Entry {
        return .{ .key = key };
    }
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_key = entryFromNode(lhs).key;
    const rhs_key = entryFromNode(rhs).key;
    return if (lhs_key < rhs_key) -1 else if (lhs_key > rhs_key) 1 else 0;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    const node_key = entryFromNode(node).key;
    return if (key.* < node_key) -1 else if (key.* > node_key) 1 else 0;
}

test "helper ports A replay keeps copied tails and last-bit scans aligned" {
    const copied_bits = bits_per_long + 5;
    const total_bits = bits_per_long * 2 + 3;

    var src = [_]Word{
        ~@as(Word, 0),
        ~@as(Word, 0),
    };
    var dst = [_]Word{
        ~@as(Word, 0),
        ~@as(Word, 0),
        ~@as(Word, 0),
    };

    bitmap.copyAndExtend(dst[0..], src[0..], copied_bits, total_bits);

    try std.testing.expectEqual(~@as(Word, 0), dst[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(copied_bits), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
    try std.testing.expectEqual(copied_bits - 1, find_bit.findLastBit(dst[0..], total_bits));
    try std.testing.expectEqual(copied_bits, find_bit.findFirstZeroBit(dst[0..], total_bits));
}

test "helper ports A replay ignores masked tails across subset and and-not scans" {
    const nbits = bits_per_long + 3;

    var lhs = [_]Word{
        wordMask(&.{ 1, 5 }),
        wordMask(&.{ 0, 2 }) | ~bitmap.lastWordMask(nbits),
    };
    var rhs = [_]Word{
        wordMask(&.{ 1, 3, 5 }),
        wordMask(&.{ 0, 2 }),
    };
    var diff = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    try std.testing.expect(bitmap.subset(lhs[0..], rhs[0..], nbits));
    try std.testing.expect(bitmap.intersects(lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndBit(lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextAndBit(lhs[0..], rhs[0..], nbits, bits_per_long));
    try std.testing.expect(!bitmap.andNotBits(diff[0..], lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(lhs[0..], rhs[0..], nbits, 0));
    try std.testing.expectEqual(@as(Word, 0), diff[0]);
    try std.testing.expectEqual(@as(Word, 0), diff[1]);
}

test "helper ports A replay keeps string parsing pinned to visible C-string bytes" {
    const parsed = string.memparse("+2Ktail");
    try std.testing.expectEqual(@as(u64, 2 << 10), parsed.value);
    try std.testing.expectEqualStrings("tail", parsed.rest);

    try std.testing.expectEqual(true, try string.strtobool("On"));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));

    const prefix = [_]u8{ 'p', 'r', 'e', 0, 'x' };
    const value = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'y' };
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&value, &prefix));

    const suffixed = [_]u8{ 'n', 'a', 'm', 'e', '.', 't', 'x', 't', 0, '.', 'b', 'a', 'k' };
    try std.testing.expect(string.strEndsWith(&suffixed, ".txt"));

    const cstr = [_]u8{ 'k', 'e', 'y', 0, '=', '1' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("read", 3, 'e'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, '='));
}

test "helper ports A replay keeps cached replacement and duplicate walks aligned" {
    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        Entry.init(2),
        Entry.init(1),
        Entry.init(2),
        Entry.init(3),
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root).?);

    var replacement = Entry.init(1);
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);

    const duplicate_key: i32 = 2;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    try std.testing.expectEqual(&entries[0].node, iter.next().?);
    try std.testing.expectEqual(&entries[2].node, iter.next().?);
    try std.testing.expect(iter.next() == null);

    var duplicate_candidate = Entry.init(2);
    rbtree.clearNode(&duplicate_candidate.node);
    const existing = rbtree.findAddCached(&duplicate_candidate.node, &root, cmpNode).?;
    try std.testing.expectEqual(@as(i32, 2), entryFromNode(existing).key);
    try std.testing.expect(rbtree.emptyNode(&duplicate_candidate.node));

    const missing_key: i32 = 7;
    var missing_iter = rbtree.matchIterator(&missing_key, &root.root, cmpKey);
    try std.testing.expect(missing_iter.next() == null);
}
