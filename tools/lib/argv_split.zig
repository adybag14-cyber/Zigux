const std = @import("std");

pub const ArgvSplitResult = struct {
    allocator: std.mem.Allocator,
    argv: [][]u8,

    pub fn argc(self: ArgvSplitResult) usize {
        return self.argv.len;
    }

    pub fn deinit(self: *ArgvSplitResult) void {
        for (self.argv) |arg| {
            self.allocator.free(arg);
        }
        self.allocator.free(self.argv);
        self.* = .{
            .allocator = self.allocator,
            .argv = &.{},
        };
    }
};

fn skipSpaces(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and text[idx] != 0 and std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn skipArg(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and text[idx] != 0 and !std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn countArgc(text: []const u8) usize {
    var idx: usize = 0;
    var count: usize = 0;

    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx >= text.len or text[idx] == 0) {
            break;
        }
        count += 1;
        idx = skipArg(text, idx);
    }

    return count;
}

fn freeAllocatedArgs(allocator: std.mem.Allocator, argv: [][]u8, count: usize) void {
    for (argv[0..count]) |arg| {
        allocator.free(arg);
    }
}

pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitResult {
    const snapshot = try allocator.dupe(u8, text);
    defer allocator.free(snapshot);

    const argc = countArgc(snapshot);
    var argv = try allocator.alloc([]u8, argc);
    errdefer allocator.free(argv);

    var idx: usize = 0;
    var arg_idx: usize = 0;
    errdefer freeAllocatedArgs(allocator, argv, arg_idx);

    while (idx < snapshot.len) {
        idx = skipSpaces(snapshot, idx);
        if (idx >= snapshot.len or snapshot[idx] == 0) {
            break;
        }

        const end = skipArg(snapshot, idx);
        argv[arg_idx] = try allocator.dupe(u8, snapshot[idx..end]);
        arg_idx += 1;
        idx = end;
    }

    return .{
        .allocator = allocator,
        .argv = argv,
    };
}

pub fn argvFree(result: *ArgvSplitResult) void {
    result.deinit();
}

pub const argv_split = argvSplit;
pub const argv_free = argvFree;

test "argvSplit matches the phase 1 committed fixture shape" {
    var result = try argvSplit(std.testing.allocator, "alpha beta gamma");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqual(@as(usize, 3), result.argv.len);
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
}

test "argvSplit collapses repeated whitespace and blank inputs to zero arguments" {
    var blank = try argvSplit(std.testing.allocator, "");
    defer blank.deinit();
    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);

    var spaced = try argvSplit(std.testing.allocator, " \t alpha \n  beta   gamma  ");
    defer spaced.deinit();
    try std.testing.expectEqual(@as(usize, 3), spaced.argc());
    try std.testing.expectEqualStrings("alpha", spaced.argv[0]);
    try std.testing.expectEqualStrings("beta", spaced.argv[1]);
    try std.testing.expectEqualStrings("gamma", spaced.argv[2]);

    var only_spaces = try argv_split(std.testing.allocator, " \n\t ");
    defer argv_free(&only_spaces);
    try std.testing.expectEqual(@as(usize, 0), only_spaces.argc());
}

test "argvSplit treats ascii control whitespace as separators and quotes literally" {
    var result = try argvSplit(std.testing.allocator, "\ralpha\x0bbeta\x0cgamma\r\n\"delta epsilon\" zeta");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 6), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
    try std.testing.expectEqualStrings("\"delta", result.argv[3]);
    try std.testing.expectEqualStrings("epsilon\"", result.argv[4]);
    try std.testing.expectEqualStrings("zeta", result.argv[5]);
}

test "argvSplit duplicates argument storage before the source buffer changes" {
    var source = [_]u8{ 'o', 'n', 'e', ' ', 't', 'w', 'o' };
    var result = try argvSplit(std.testing.allocator, &source);
    defer result.deinit();

    source[0] = 'X';
    source[4] = 'Y';

    try std.testing.expectEqualStrings("one", result.argv[0]);
    try std.testing.expectEqualStrings("two", result.argv[1]);
}

test "argvSplit stops at the first embedded NUL byte" {
    const source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a', 0, 'g', 'a', 'm', 'm', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}

test "argvSplit treats a NUL after leading whitespace as end of input" {
    const source = [_]u8{ ' ', '\t', 0, 'a', 'l', 'p', 'h', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}

test "argvSplit treats a NUL reached while skipping separator whitespace as end of input" {
    const source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', '\t', 0, 'b', 'e', 't', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqual(@as(usize, 1), result.argv.len);
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
}

test "argvSplit truncates the current token at an embedded NUL" {
    const source = [_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'b', 'e', 't', 'a', ' ', 'g', 'a', 'm', 'm', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqual(@as(usize, 1), result.argv.len);
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
}

test "countArgc ignores hidden suffix arguments beyond the first embedded NUL" {
    const leading_nul = [_]u8{ ' ', '\t', 0, 'a', 'l', 'p', 'h', 'a' };
    const separator_nul = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', '\t', 0, 'b', 'e', 't', 'a' };
    const token_nul = [_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'b', 'e', 't', 'a', ' ', 'g', 'a', 'm', 'm', 'a' };

    try std.testing.expectEqual(@as(usize, 0), countArgc(leading_nul[0..]));
    try std.testing.expectEqual(@as(usize, 1), countArgc(separator_nul[0..]));
    try std.testing.expectEqual(@as(usize, 1), countArgc(token_nul[0..]));
}

test "argvSplit keeps countArgc aligned with every representative embedded-NUL placement" {
    const source = [_]u8{ ' ', 'a', 'l', 'p', 'h', 'a', ' ', '\t', 'b', 'e', 't', 'a', '\n', 'g', 'a', 'm', 'm', 'a' };
    const expected_argc = [_]usize{ 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3 };

    for (0..source.len) |nul_index| {
        var probe = source;
        probe[nul_index] = 0;

        var result = try argvSplit(std.testing.allocator, probe[0..]);
        defer result.deinit();

        try std.testing.expectEqual(expected_argc[nul_index], countArgc(probe[0..]));
        try std.testing.expectEqual(expected_argc[nul_index], result.argc());
        try std.testing.expectEqual(expected_argc[nul_index], result.argv.len);
    }
}

fn argvSplitAllocationProbe(allocator: std.mem.Allocator, text: []const u8) !void {
    var result = try argvSplit(allocator, text);
    defer result.deinit();
}

test "argvSplit frees earlier arguments when a later allocation fails" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        argvSplitAllocationProbe,
        .{"alpha beta gamma delta"},
    );
}

test "argvSplit cleanup resets state and tolerates repeat deinit calls" {
    var result = try argvSplit(std.testing.allocator, "alpha beta");

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    result.deinit();
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    argv_free(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}

test "argvSplit cleanup keeps empty and NUL-truncated empty results inert" {
    var blank = try argvSplit(std.testing.allocator, "");
    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    blank.deinit();
    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);
    argv_free(&blank);
    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);

    const source = [_]u8{ ' ', '\t', 0, 'a', 'l', 'p', 'h', 'a' };
    var nul_terminated = try argv_split(std.testing.allocator, source[0..]);
    try std.testing.expectEqual(@as(usize, 0), nul_terminated.argc());
    nul_terminated.deinit();
    try std.testing.expectEqual(@as(usize, 0), nul_terminated.argc());
    try std.testing.expectEqual(@as(usize, 0), nul_terminated.argv.len);
    argv_free(&nul_terminated);
    try std.testing.expectEqual(@as(usize, 0), nul_terminated.argc());
    try std.testing.expectEqual(@as(usize, 0), nul_terminated.argv.len);
}

const MutatingAllocator = struct {
    backing_allocator: std.mem.Allocator,
    source: []u8,
    trigger_alloc_index: usize,
    alloc_index: usize = 0,
    mutated: bool = false,

    fn allocator(self: *MutatingAllocator) std.mem.Allocator {
        return .{
            .ptr = self,
            .vtable = &.{
                .alloc = alloc,
                .resize = resize,
                .remap = remap,
                .free = free,
            },
        };
    }

    fn mutateSource(self: *MutatingAllocator) void {
        if (self.mutated or self.source.len < 16) {
            return;
        }

        @memcpy(self.source[6..10], "zeta");
        @memcpy(self.source[11..16], "omega");
        self.mutated = true;
    }

    fn alloc(ctx: *anyopaque, len: usize, alignment: std.mem.Alignment, ret_addr: usize) ?[*]u8 {
        const self: *MutatingAllocator = @ptrCast(@alignCast(ctx));
        if (self.alloc_index == self.trigger_alloc_index) {
            self.mutateSource();
        }
        const memory = self.backing_allocator.rawAlloc(len, alignment, ret_addr) orelse return null;
        self.alloc_index += 1;
        return memory;
    }

    fn resize(ctx: *anyopaque, memory: []u8, alignment: std.mem.Alignment, new_len: usize, ret_addr: usize) bool {
        const self: *MutatingAllocator = @ptrCast(@alignCast(ctx));
        return self.backing_allocator.rawResize(memory, alignment, new_len, ret_addr);
    }

    fn remap(ctx: *anyopaque, memory: []u8, alignment: std.mem.Alignment, new_len: usize, ret_addr: usize) ?[*]u8 {
        const self: *MutatingAllocator = @ptrCast(@alignCast(ctx));
        return self.backing_allocator.rawRemap(memory, alignment, new_len, ret_addr);
    }

    fn free(ctx: *anyopaque, memory: []u8, alignment: std.mem.Alignment, ret_addr: usize) void {
        const self: *MutatingAllocator = @ptrCast(@alignCast(ctx));
        self.backing_allocator.rawFree(memory, alignment, ret_addr);
    }
};

test "argvSplit snapshots the source before later argument allocations can observe mutation" {
    var source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a', ' ', 'g', 'a', 'm', 'm', 'a' };
    var allocator_state = MutatingAllocator{
        .backing_allocator = std.testing.allocator,
        .source = source[0..],
        .trigger_alloc_index = 2,
    };

    var result = try argvSplit(allocator_state.allocator(), source[0..]);
    defer result.deinit();

    try std.testing.expect(allocator_state.mutated);
    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
    try std.testing.expectEqualStrings("zeta", source[6..10]);
    try std.testing.expectEqualStrings("omega", source[11..16]);
}
