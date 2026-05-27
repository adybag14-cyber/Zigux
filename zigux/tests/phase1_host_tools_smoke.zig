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

fn returnedSerial(node: ?*rbtree.Node) i32 {
    const current = node orelse return -1;
    const entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", current);
    return @as(i32, @intCast(entry.serial));
}

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
    try std.testing.expect(@hasDecl(string, "strlcat"));
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

    const hexadecimal = cmdline.memparse("0x20M");
    try std.testing.expectEqual(@as(u64, 0x20 << 20), hexadecimal.value);
    try std.testing.expectEqualStrings("", hexadecimal.rest);

    const octal = cmdline.memparse("010K");
    try std.testing.expectEqual(@as(u64, 8 << 10), octal.value);
    try std.testing.expectEqualStrings("", octal.rest);

    const invalid = cmdline.memparse("xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("xyz", invalid.rest);

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

    try std.testing.expectEqual(@as(u8, 0x41), ctype.mask('A'));
    try std.testing.expectEqual(@as(u8, 0x42), ctype.mask('a'));
    try std.testing.expectEqual(@as(u8, 0xa0), ctype.mask(' '));
    try std.testing.expect(ctype.isalnum('A'));
    try std.testing.expect(ctype.isalpha('Q'));
    try std.testing.expect(ctype.isdigit('7'));
    try std.testing.expect(ctype.isspace('\t'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(ctype.ispunct('!'));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower('A'));
    try std.testing.expectEqual(@as(u8, 'm'), ctype.fastTolower('M'));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper('z'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));

    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0xf0));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0xf0f0));
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
    var unknown_error_buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(4096, [buf], 64)=22",
        str_error_r.strErrorR(4096, &unknown_error_buffer),
    );
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

    var bool_head: list_sort.ListHead = .{};
    bool_head.init();
    var bool_entries = [_]ListSortSmokeEntry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    const bool_cmp = struct {
        fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const ListSortSmokeEntry = @fieldParentPtr("node", a);
            const rhs: *const ListSortSmokeEntry = @fieldParentPtr("node", b);
            return @intFromBool(lhs.key > rhs.key);
        }
    }.less;
    for (&bool_entries) |*entry| {
        list_sort.listAddTail(&entry.node, &bool_head);
    }
    list_sort.listSort(null, &bool_head, bool_cmp);

    sorted_count = 0;
    sorted_node = bool_head.next;
    while (sorted_node != &bool_head) : (sorted_node = sorted_node.?.next) {
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

    const tail_clamped_set = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 7),
    };
    try std.testing.expectEqual(word_bits + 3, find_bit.findFirstBit(&tail_clamped_set, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&tail_clamped_set, nbits, word_bits + 4));
    try std.testing.expectEqual(word_bits + 3, find_bit.findLastBit(&tail_clamped_set, nbits));

    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        bitmap.lastWordMask(nbits) | (@as(find_bit.Word, 1) << 7),
    };
    try std.testing.expectEqual(nbits, find_bit.findFirstZeroBit(&tail_zero_map, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&tail_zero_map, nbits, word_bits));

    const tail_and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 8),
    };
    const tail_and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(word_bits + 3, find_bit.findFirstAndBit(&tail_and_lhs, &tail_and_rhs, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, word_bits + 4));

    var rendered: [32]u8 = undefined;
    const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "{d}-{d}", .{ word_bits - 1, word_bits + 1 });
    try std.testing.expectEqualStrings(expected_text, rendered[0..bitmap_rendered_len]);

    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);

    var appended = [_]u8{ 'h', 'i', 0, 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 5), string.strlcat(appended[0..], "all"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 'a', 'l', 'l', 0 }, appended[0..]);

    var truncated_append = [_]u8{ 'a', 'b', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated_append[0..], "cdef"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, truncated_append[0..]);

    const sysfs = [_][]const u8{ "disabled", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));
    try std.testing.expect(string.sysfs_streq("auto\n", "auto"));

    const lookup = [_][]const u8{ "disabled", "manual", "manual", "auto" };
    const lookup_cstr = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&lookup, "manual"));
    try std.testing.expectEqual(@as(?usize, 3), string.match_string(&lookup, &lookup_cstr));

    const counted = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&counted, counted.len, 'b'));
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));

    const terminator_clamped = [_]u8{ 'a', 0, 'b', 'c' };
    try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&terminator_clamped, 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&terminator_clamped, 'z'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrNul("abcz", 'c'));
    try std.testing.expectEqual(@as(usize, 2), string.strchrnul("abcz", 'c'));

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
    const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;
    const found_duplicate_entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", found_duplicate);
    try std.testing.expectEqual(@as(i32, 10), found_duplicate_entry.key);

    const missing_key = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing_key, &tree_root, RbtreeSmokeEntry.cmp) == null);

    const first_duplicate = rbtree.findFirst(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;
    const first_duplicate_entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", first_duplicate);
    try std.testing.expectEqual(@as(usize, 0), first_duplicate_entry.serial);

    const second_duplicate = rbtree.nextMatch(&duplicate_key, first_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;
    const second_duplicate_entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", second_duplicate);
    try std.testing.expectEqual(@as(usize, 2), second_duplicate_entry.serial);

    const third_duplicate = rbtree.nextMatch(&duplicate_key, second_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;
    const third_duplicate_entry: *const RbtreeSmokeEntry = @fieldParentPtr("node", third_duplicate);
    try std.testing.expectEqual(@as(usize, 4), third_duplicate_entry.serial);
    try std.testing.expect(rbtree.nextMatch(&duplicate_key, third_duplicate, RbtreeSmokeEntry.cmp) == null);

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

    var cached_leftmost_entries = [_]RbtreeSmokeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 12, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 5, .serial = 3 },
    };
    var cached_leftmost_root = rbtree.RootCached.init();
    var cached_leftmost_return_serials: [4]i32 = undefined;
    cached_leftmost_return_serials[0] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[0].node, &cached_leftmost_root, RbtreeSmokeEntry.less));
    cached_leftmost_return_serials[1] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[1].node, &cached_leftmost_root, RbtreeSmokeEntry.less));
    cached_leftmost_return_serials[2] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[2].node, &cached_leftmost_root, RbtreeSmokeEntry.less));
    cached_leftmost_return_serials[3] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[3].node, &cached_leftmost_root, RbtreeSmokeEntry.less));
    try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_leftmost_entries[2].node), rbtree.firstCached(&cached_leftmost_root));

    var cached_entries = [_]RbtreeSmokeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var cached_replacement = RbtreeSmokeEntry{ .key = 10, .serial = 4 };
    var cached_root = rbtree.RootCached.init();
    var cached_root_transition_serials: [4]i32 = undefined;
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.addCached(&cached_entries[0].node, &cached_root, RbtreeSmokeEntry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.addCached(&cached_entries[1].node, &cached_root, RbtreeSmokeEntry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&cached_entries[2].node, &cached_root, RbtreeSmokeEntry.less));
    cached_root_transition_serials[0] = returnedSerial(rbtree.eraseCached(&cached_entries[1].node, &cached_root));
    cached_root_transition_serials[1] = returnedSerial(rbtree.firstCached(&cached_root));
    rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root);
    cached_root_transition_serials[2] = returnedSerial(rbtree.firstCached(&cached_root));
    rbtree.eraseInitCached(&cached_replacement.node, &cached_root);
    cached_root_transition_serials[3] = returnedSerial(rbtree.firstCached(&cached_root));
    try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[2].node), rbtree.firstCached(&cached_root));
    try std.testing.expect(rbtree.emptyNode(&cached_replacement.node));
}

test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    const tail_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4));

    const clump_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6) };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &clump_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_first_clump8(&clump, &clump_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
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
