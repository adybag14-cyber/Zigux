const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn lowercaseInto(dest: []u8, source: []const u8) []u8 {
    for (source, 0..) |byte, idx| {
        dest[idx] = ctype.fastTolower(byte);
    }
    return dest[0..source.len];
}

fn valueAfterEquals(token: []const u8) []const u8 {
    const eq = std.mem.indexOfScalar(u8, token, '=') orelse return "";
    return token[eq + 1 ..];
}

fn parsedArgc(parsed: anytype) usize {
    const Parsed = @TypeOf(parsed);
    return if (@typeInfo(Parsed) == .@"struct" and @hasField(Parsed, "argv"))
        parsed.argc()
    else
        parsed.len;
}

fn parsedArg(parsed: anytype, index: usize) []u8 {
    const Parsed = @TypeOf(parsed);
    return if (@typeInfo(Parsed) == .@"struct" and @hasField(Parsed, "argv"))
        parsed.argv[index]
    else
        parsed[index];
}

fn freeParsedArgv(allocator: std.mem.Allocator, parsed: anytype) void {
    const Ptr = @TypeOf(parsed);
    const Parsed = @typeInfo(Ptr).pointer.child;
    if (@typeInfo(Parsed) == .@"struct" and @hasField(Parsed, "argv")) {
        parsed.deinit();
    } else {
        argv_split.argvFree(allocator, parsed.*);
    }
}

test "ports B casefold option tokens before exact cmdline matching" {
    var parsed = try argv_split.argvSplit(
        std.testing.allocator,
        "QUIET,Debug,TRACE mem=0x20K panic=-2",
    );
    defer freeParsedArgv(std.testing.allocator, &parsed);

    try std.testing.expectEqual(@as(usize, 3), parsedArgc(parsed));

    var lowered_options: [64]u8 = undefined;
    const options = lowercaseInto(lowered_options[0..], parsedArg(parsed, 0));
    try std.testing.expectEqualStrings("quiet,debug,trace", options);
    try std.testing.expect(cmdline.parseOptionStr(options, "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(options, "debug"));
    try std.testing.expect(cmdline.parseOptionStr(options, "trace"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "Debug"));

    const mem = cmdline.memparse(valueAfterEquals(parsedArg(parsed, 1)));
    try std.testing.expectEqual(@as(u64, 0x20 << 10), mem.value);
    try std.testing.expectEqualStrings("", mem.rest);

    const panic = cmdline.memparse(valueAfterEquals(parsedArg(parsed, 2)));
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2))), panic.value);
    try std.testing.expectEqualStrings("", panic.rest);
}

test "ports B count folded option letters and numeric suffix classes" {
    const token = "Debug=0x2K";
    var lower_mask: u32 = 0;
    var hex_mask: u32 = 0;
    var suffix_mask: u32 = 0;

    for (token) |byte| {
        const lowered = ctype.tolower(byte);
        if (ctype.islower(lowered)) {
            lower_mask |= @as(u32, 1) << @intCast(lowered - 'a');
        }
        if (ctype.isxdigit(byte)) {
            hex_mask |= @as(u32, 1) << @intCast(ctype.fastTolower(byte) & 0x0f);
        }
        if (byte == 'K' or byte == 'k') {
            suffix_mask |= @as(u32, 1) << 10;
        }
    }

    try std.testing.expectEqual(@as(u32, 7), hweight.swHweight32(lower_mask));
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight32(hex_mask));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight32(suffix_mask));
}

test "ports B preserve split ownership while normalizing copied tokens" {
    var mutable = [_]u8{ 'M', 'o', 'D', 'e', '=', 'F', 'a', 'S', 't', ' ', 'S', 'i', 'Z', 'e', '=', '0', '7' };
    var parsed = try argv_split.argvSplit(std.testing.allocator, mutable[0..]);
    defer freeParsedArgv(std.testing.allocator, &parsed);

    std.mem.replaceScalar(u8, mutable[0..], 'S', 'x');
    try std.testing.expectEqualStrings("MoDe=FaSt", parsedArg(parsed, 0));
    try std.testing.expectEqualStrings("SiZe=07", parsedArg(parsed, 1));

    var key: [8]u8 = undefined;
    const lowered_key = lowercaseInto(key[0..], parsedArg(parsed, 0)[0..4]);
    try std.testing.expectEqualStrings("mode", lowered_key);

    var value: [8]u8 = undefined;
    const lowered_value = lowercaseInto(value[0..], valueAfterEquals(parsedArg(parsed, 0)));
    try std.testing.expectEqualStrings("fast", lowered_value);

    const size = cmdline.memparse(valueAfterEquals(parsedArg(parsed, 1)));
    try std.testing.expectEqual(@as(u64, 7), size.value);
    try std.testing.expectEqualStrings("", size.rest);
}
