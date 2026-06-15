const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

const exclamation: u8 = '!';

fn splitLen(result: anytype) usize {
    return switch (@typeInfo(@TypeOf(result))) {
        .pointer => result.len,
        .@"struct" => result.argc(),
        else => @compileError("unsupported argvSplit result shape"),
    };
}

fn splitArg(result: anytype, index: usize) []const u8 {
    return switch (@typeInfo(@TypeOf(result))) {
        .pointer => result[index],
        .@"struct" => result.argv[index],
        else => @compileError("unsupported argvSplit result shape"),
    };
}

fn splitArgMut(result: anytype, index: usize) []u8 {
    return switch (@typeInfo(@TypeOf(result))) {
        .pointer => result[index],
        .@"struct" => result.argv[index],
        else => @compileError("unsupported argvSplit result shape"),
    };
}

fn freeSplit(allocator: std.mem.Allocator, result: anytype) void {
    const Result = @typeInfo(@TypeOf(result)).pointer.child;
    switch (@typeInfo(Result)) {
        .pointer => argv_split.argvFree(allocator, result.*),
        .@"struct" => result.deinit(),
        else => @compileError("unsupported argvSplit result shape"),
    }
}

fn hweight8Count(value: u32) u32 {
    if (@hasDecl(hweight, "hweight8")) {
        return hweight.hweight8(value);
    }
    return hweight.swHweight8(value);
}

fn hweight16Count(value: u32) u32 {
    if (@hasDecl(hweight, "hweight16")) {
        return hweight.hweight16(value);
    }
    return hweight.swHweight16(value);
}

fn hweight32Count(value: u32) u32 {
    if (@hasDecl(hweight, "hweight32")) {
        return hweight.hweight32(value);
    }
    return hweight.swHweight32(value);
}

fn hweight64Count(value: u64) u64 {
    if (@hasDecl(hweight, "hweight64")) {
        return hweight.hweight64(value);
    }
    return hweight.swHweight64(value);
}

test "argv split preserves exclamation packet tokens" {
    var args = try argv_split.argvSplit(
        std.testing.allocator,
        " root=!/disk exclamation!bridge key=value!more plain ",
    );
    defer freeSplit(std.testing.allocator, &args);

    try std.testing.expectEqual(@as(usize, 4), splitLen(args));
    try std.testing.expectEqualStrings("root=!/disk", splitArg(args, 0));
    try std.testing.expectEqualStrings("exclamation!bridge", splitArg(args, 1));
    try std.testing.expectEqualStrings("key=value!more", splitArg(args, 2));
    try std.testing.expectEqualStrings("plain", splitArg(args, 3));
}

test "argv split exclamation tokens are duplicated and writable" {
    var args = try argv_split.argvSplit(std.testing.allocator, "alpha!beta gamma");
    defer freeSplit(std.testing.allocator, &args);

    const first = splitArgMut(args, 0);
    first[0] = 'A';

    try std.testing.expectEqualStrings("Alpha!beta", first);
    try std.testing.expectEqualStrings("gamma", splitArg(args, 1));
}

test "cmdline memparse leaves exclamation tail exact" {
    const hex = cmdline.memparse("0x21!mask");
    try std.testing.expectEqual(@as(u64, 0x21), hex.value);
    try std.testing.expectEqualStrings("!mask", hex.rest);

    const scaled = cmdline.memparse("33K!boot");
    try std.testing.expectEqual(@as(u64, 33 << 10), scaled.value);
    try std.testing.expectEqualStrings("!boot", scaled.rest);
}

test "cmdline option list treats exclamation as option data" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug!trace,nohlt", "debug!trace"));
    try std.testing.expect(cmdline.parse_option_str("quiet,exclamation!bridge,nohlt", "exclamation!bridge"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug!trace,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug!trace,nohlt", "trace"));
}

test "cmdline nextArg keeps exclamation within tokens when present" {
    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.nextArg("debug!trace root=!/disk") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("debug!trace", first.param);
        try std.testing.expect(first.value == null);
        try std.testing.expectEqualStrings("root=!/disk", first.remaining);

        const second = cmdline.next_arg(first.remaining) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", second.param);
        try std.testing.expectEqualStrings("!/disk", second.value.?);
        try std.testing.expectEqualStrings("", second.remaining);
    }
}

test "ctype classifies exclamation as punctuation graph print data" {
    try std.testing.expectEqual(ctype._P, ctype.mask(exclamation));
    try std.testing.expect(ctype.ispunct(exclamation));
    try std.testing.expect(ctype.isgraph(exclamation));
    try std.testing.expect(ctype.isprint(exclamation));
    try std.testing.expect(!ctype.isspace(exclamation));
    try std.testing.expect(!ctype.isalnum(exclamation));
    try std.testing.expectEqual(exclamation, ctype.tolower(exclamation));
    try std.testing.expectEqual(exclamation, ctype.toupper(exclamation));
    try std.testing.expectEqual(exclamation, ctype.fastTolower(exclamation));
}

test "hweight counts exclamation byte lanes consistently" {
    try std.testing.expectEqual(@as(u32, 2), hweight8Count(exclamation));
    try std.testing.expectEqual(@as(u32, 4), hweight16Count(0x2121));
    try std.testing.expectEqual(@as(u32, 8), hweight32Count(0x2121_2121));
    try std.testing.expectEqual(@as(u64, 16), hweight64Count(0x2121_2121_2121_2121));
}

test "exclamation bridge keeps mask tail visible across helpers" {
    var args = try argv_split.argvSplit(std.testing.allocator, "mask=0x21!flags tail");
    defer freeSplit(std.testing.allocator, &args);

    const mask_arg = splitArg(args, 0);
    const equals_index = std.mem.indexOfScalar(u8, mask_arg, '=') orelse return error.TestUnexpectedResult;
    const parsed = cmdline.memparse(mask_arg[equals_index + 1 ..]);

    try std.testing.expectEqual(@as(u64, 0x21), parsed.value);
    try std.testing.expectEqualStrings("!flags", parsed.rest);
    try std.testing.expect(ctype.ispunct(parsed.rest[0]));
    try std.testing.expectEqual(@as(u32, 2), hweight8Count(parsed.rest[0]));
}
