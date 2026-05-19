const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
pub const find_bit = @import("find_bit");
const bitmap = @import("bitmap");
const ctype = @import("ctype");
const hweight = @import("hweight");
const list_sort = @import("list_sort");
const rbtree = @import("rbtree");
const string = @import("string");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
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
    try std.testing.expect(@hasDecl(string, "strtobool"));
    try std.testing.expect(@hasDecl(string, "matchString"));
    try std.testing.expect(@hasDecl(string, "strnchr"));
    try std.testing.expect(@hasDecl(string, "strnchrNul"));
    try std.testing.expect(@hasDecl(slab, "kmallocBytes"));
    try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));
    try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));
    try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));
}

test "phase1 host-tools smoke exercises live helper behavior" {
    var split = try argv_split.argv_split(std.testing.allocator, "  zigux   host\ttools  ");
    defer argv_split.argv_free(&split);
    try std.testing.expectEqual(@as(usize, 3), split.argc());
    try std.testing.expectEqualStrings("zigux", split.argv[0]);
    try std.testing.expectEqualStrings("host", split.argv[1]);
    try std.testing.expectEqualStrings("tools", split.argv[2]);

    const parsed = cmdline.memparse("64K tail");
    try std.testing.expectEqual(@as(u64, 64 << 10), parsed.value);
    try std.testing.expectEqualStrings(" tail", parsed.rest);

    const signed = cmdline.memparse("-2K tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), signed.value);
    try std.testing.expectEqualStrings(" tail", signed.rest);

    const saturated = cmdline.memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), saturated.value);
    try std.testing.expectEqualStrings("", saturated.rest);

    try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(",quiet", ""));
    try std.testing.expect(cmdline.parseOptionStr("rootwait,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("rootwait,quiet", "debug"));

    const keyed = cmdline.nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("console", keyed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", keyed.value.?);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", keyed.remaining);

    const quoted_pair = cmdline.nextArg(keyed.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", quoted_pair.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", quoted_pair.value.?);
    try std.testing.expectEqualStrings("panic=-1", quoted_pair.remaining);

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

    slab.kmalloc_nr_allocated = 0;
    const allocated = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (allocated) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    slab.kfree(allocated);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var error_buffer: [32]u8 = undefined;
    try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, &error_buffer));
    var tiny_error_buffer: [8]u8 = undefined;
    try std.testing.expectEqualStrings("INTERNA", str_error_r.strErrorR(4096, &tiny_error_buffer));

    var render_buffer: [16]u8 = undefined;
    const rendered_len = vsprintf.scnprintf(&render_buffer, "{s}:{d}", .{ "zigux", 9 });
    try std.testing.expectEqual(@as(usize, 7), rendered_len);
    try std.testing.expectEqualStrings("zigux:9", render_buffer[0..rendered_len]);

    var padded_render: [12]u8 = undefined;
    const padded_len = vsprintf.scnprintfPad(&padded_render, 10, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 9), padded_len);
    try std.testing.expectEqualStrings("id=7      ", padded_render[0..10]);

    const allocator = std.testing.allocator;
    var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &zero_bytes);
    for (zero_bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    const ZeroValue = struct {
        count: u32,
        enabled: bool,
    };
    var zero_value: ?*ZeroValue = try zalloc.zallocValue(allocator, ZeroValue);
    defer zalloc.zfreeValue(allocator, ZeroValue, &zero_value);
    try std.testing.expectEqual(@as(u32, 0), zero_value.?.count);
    try std.testing.expectEqual(false, zero_value.?.enabled);

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
    const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "{d}-{d}", .{ word_bits - 1, word_bits + 1 });
    try std.testing.expectEqualStrings(expected_text, rendered[0..bitmap_rendered_len]);

    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);

    const sysfs = [_][]const u8{ "disabled", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));

    const lookup = [_][]const u8{ "disabled", "manual", "manual", "auto" };
    const lookup_cstr = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&lookup, "manual"));
    try std.testing.expectEqual(@as(?usize, 3), string.match_string(&lookup, &lookup_cstr));

    const counted = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&counted, counted.len, 'b'));

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

test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {
    var src = [_]find_bit.Word{~@as(find_bit.Word, 0)};

    var direct_copy = [_]find_bit.Word{0x1357};
    var alias_copy = [_]find_bit.Word{0x1357};
    bitmap.copy(direct_copy[0..0], src[0..0], 0);
    bitmap.bitmap_copy(alias_copy[0..0], src[0..0], 0);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_copy, &alias_copy);

    var direct_clear = [_]find_bit.Word{0x2468};
    var alias_clear = [_]find_bit.Word{0x2468};
    bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0);
    bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_clear, &alias_clear);

    var direct_extend = [_]find_bit.Word{0xaaaa};
    var alias_extend = [_]find_bit.Word{0xaaaa};
    bitmap.copyAndExtend(direct_extend[0..0], src[0..0], 0, 0);
    bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_extend, &alias_extend);

    const empty_map = [_]find_bit.Word{0};
    var direct_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    var alias_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const direct_len = bitmap.scnprintf(&empty_map, 8, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualSlices(u8, &direct_buffer, &alias_buffer);
}
