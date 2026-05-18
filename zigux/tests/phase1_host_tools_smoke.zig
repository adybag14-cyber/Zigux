const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
pub const find_bit = @import("find_bit");
const bitmap = @import("bitmap");
const ctype = @import("ctype");
const hweight = @import("hweight");
const list_sort = @import("list_sort");
const rbtree = @import("rbtree");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const string = @import("string");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const ListSortSmokeEntry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

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
    try std.testing.expect(@hasDecl(ctype, "isalpha"));
    try std.testing.expect(@hasDecl(hweight, "swHweight64"));
    try std.testing.expect(@hasDecl(list_sort, "listSort"));
    try std.testing.expect(@hasDecl(rbtree, "find"));
    try std.testing.expect(@hasDecl(rbtree, "matchIterator"));
    try std.testing.expect(@hasDecl(slab, "kmallocBytes"));
    try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));
    try std.testing.expect(@hasDecl(string, "strtobool"));
    try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));
    try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));
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

    try std.testing.expect(ctype.isalpha('Q'));
    try std.testing.expect(ctype.isdigit('7'));
    try std.testing.expectEqual(@as(u8, 'm'), ctype.fastTolower('M'));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper('z'));

    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));
    try std.testing.expectEqual(@popCount(@as(usize, 0xf0f0)), hweight.hweightLong(0xf0f0));

    var list_head: list_sort.ListHead = .{};
    list_head.init();
    var list_entries = [_]ListSortSmokeEntry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    const list_cmp = struct {
        fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const ListSortSmokeEntry = @fieldParentPtr("node", a);
            const rhs: *const ListSortSmokeEntry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;
    for (&list_entries) |*entry| {
        list_sort.listAddTail(&entry.node, &list_head);
    }
    list_sort.listSort(null, &list_head, list_cmp);

    var sorted_keys: [5]i32 = undefined;
    var sorted_ordinals: [5]usize = undefined;
    var sorted_count: usize = 0;
    var sorted_node = list_head.next;
    while (sorted_node != &list_head) : (sorted_node = sorted_node.?.next) {
        const entry: *const ListSortSmokeEntry = @fieldParentPtr("node", sorted_node.?);
        sorted_keys[sorted_count] = entry.key;
        sorted_ordinals[sorted_count] = entry.ordinal;
        sorted_count += 1;
    }
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, sorted_keys[0..sorted_count]);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, sorted_ordinals[0..sorted_count]);

    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;
    var map = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&map, word_bits - 1, 3);
    try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(word_bits - 1, find_bit.findNextBit(&map, nbits, word_bits - 1));
    try std.testing.expectEqual(word_bits, find_bit.findNextBit(&map, nbits, word_bits));
    try std.testing.expectEqual(word_bits + 1, find_bit.findLastBit(&map, nbits));

    const empty_last_map = [_]find_bit.Word{ 0, 0 };
    try std.testing.expectEqual(nbits, find_bit.findLastBit(&empty_last_map, nbits));

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

    var strerror_buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings("No such file or directory", str_error_r.strErrorR(2, &strerror_buffer));
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 64)=22", str_error_r.strErrorR(4096, &strerror_buffer));
    var strerror_empty: [0]u8 = undefined;
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(2, &strerror_empty));
    var strerror_tiny = [_]u8{0xaa};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(4096, &strerror_tiny));
    try std.testing.expectEqual(@as(u8, 0), strerror_tiny[0]);

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    const slab_plain = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_plain) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    slab.kfree(slab_plain);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.slabIsAvailable());

    var vsprintf_buffer: [16]u8 = undefined;
    const scnprintf_len = vsprintf.scnprintf(&vsprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqualStrings("zigux:7", vsprintf_buffer[0..scnprintf_len]);

    var vsprintf_pad_buffer: [9]u8 = undefined;
    const scnprintf_pad_len = vsprintf.scnprintfPad(&vsprintf_pad_buffer, vsprintf_pad_buffer.len - 1, "id={d}", .{7});
    try std.testing.expect(scnprintf_pad_len <= vsprintf_pad_buffer.len - 1);
    try std.testing.expectEqualStrings("id=7    ", vsprintf_pad_buffer[0 .. vsprintf_pad_buffer.len - 1]);
    var vsprintf_zero = [_]u8{ 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(&vsprintf_zero, 0, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), vsprintf_zero[0]);

    const allocator = std.testing.allocator;
    var zalloc_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &zalloc_bytes);
    for (zalloc_bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    zalloc.zfreeBytes(allocator, &zalloc_bytes);
    try std.testing.expect(zalloc_bytes == null);

    var zalloc_zero: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &zalloc_zero);
    try std.testing.expect(zalloc_zero != null);
    try std.testing.expectEqual(@as(usize, 0), zalloc_zero.?.len);
    zalloc.zfreeBytes(allocator, &zalloc_zero);
    try std.testing.expect(zalloc_zero == null);
    zalloc.zfreeBytes(allocator, &zalloc_zero);
    try std.testing.expect(zalloc_zero == null);

    const ZallocValue = struct {
        a: u32,
        b: bool,
    };
    var zalloc_value: ?*ZallocValue = try zalloc.zallocValue(allocator, ZallocValue);
    defer zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expectEqual(@as(u32, 0), zalloc_value.?.a);
    try std.testing.expectEqual(false, zalloc_value.?.b);
    zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expect(zalloc_value == null);
    zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expect(zalloc_value == null);
}

test "phase1 host-tools smoke checks additional lane10 helper edges" {
    var truncated_message = [_]u8{0xaa} ** 4;
    try std.testing.expectEqualStrings("Suc", str_error_r.strErrorR(0, &truncated_message));
    try std.testing.expectEqual(@as(u8, 0), truncated_message[3]);
    var single_char_message = [_]u8{0xaa};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(0, &single_char_message));
    try std.testing.expectEqual(@as(u8, 0), single_char_message[0]);

    slab.kmalloc_nr_allocated = 0;
    const slab_array = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_array) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(3, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var empty_vsprintf: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(&empty_vsprintf, "{s}", .{"zigux"}));
    var single_byte_vsprintf = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&single_byte_vsprintf, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), single_byte_vsprintf[0]);

    const allocator = std.testing.allocator;
    var optional_bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &optional_bytes);
    try std.testing.expect(optional_bytes == null);
    const EmptyValue = struct {
        flag: bool,
    };
    var optional_value: ?*EmptyValue = null;
    zalloc.zfreeValue(allocator, EmptyValue, &optional_value);
    try std.testing.expect(optional_value == null);
}
