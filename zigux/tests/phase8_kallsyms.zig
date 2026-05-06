const std = @import("std");
const kallsyms = @import("kallsyms");

const phase8_kallsyms_slice = @import("phase8_kallsyms_options").phase8_kallsyms_slice;

test "phase 8 kallsyms module imports cleanly" {
    _ = kallsyms;
}

test "phase 8 kallsyms slice note keeps helper-first output-stable tooling posture explicit" {
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "PHASE8_SLICE=kallsyms-parse-wrapper-parked"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "helper-first expansion"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "output-stable tooling behavior"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "zig test tools/lib/symbol/kallsyms.zig"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "one direct `kallsymsParse()` wrapper"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "oversized symbol names truncate to `KSYM_NAME_LEN`"));
}

test "phase 8 kallsyms parked slice covers symbol helpers and injected record parsing" {
    try std.testing.expectEqual(kallsyms.elf_stb_weak, kallsyms.kallsyms2ElfBinding('W'));
    try std.testing.expectEqual(kallsyms.elf_stb_global, kallsyms.kallsyms2ElfBinding('T'));
    try std.testing.expectEqual(kallsyms.elf_stb_local, kallsyms.kallsyms2ElfBinding('t'));
    try std.testing.expectEqual(kallsyms.elf_stt_func, kallsyms.kallsyms2ElfType('w'));
    try std.testing.expectEqual(kallsyms.elf_stt_object, kallsyms.kallsyms2ElfType('B'));
    try std.testing.expect(kallsyms.isFunction('W'));
    try std.testing.expect(!kallsyms.isFunction('n'));

    const parsed = (try kallsyms.parseLine("ffffffff81000100 t secondary_startup_64")) orelse unreachable;
    try std.testing.expectEqual(@as(u64, 0xffffffff81000100), parsed.start);
    try std.testing.expectEqual(@as(u8, 't'), parsed.symbol_type);
    try std.testing.expectEqualStrings("secondary_startup_64", parsed.name);

    const Collector = struct {
        fn append(list: *std.ArrayList(kallsyms.ParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
            try list.append(std.testing.allocator, symbol);
        }
    };

    var symbols = std.ArrayList(kallsyms.ParsedSymbol).empty;
    defer symbols.deinit(std.testing.allocator);

    try kallsyms.forEachParsedLine(
        "ffffffff81000000 T startup_64\n" ++
            "garbage\n" ++
            "ffffffff81000200 W weak_handler\n",
        &symbols,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_handler", symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 'W'), symbols.items[1].symbol_type);

    const too_long_name = "a" ** (kallsyms.KSYM_NAME_LEN + 1);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_line);

    const oversized = (try kallsyms.parseLine(oversized_line)) orelse unreachable;
    try std.testing.expectEqual(@as(usize, kallsyms.KSYM_NAME_LEN), oversized.name.len);
    try std.testing.expectEqualStrings(too_long_name[0..kallsyms.KSYM_NAME_LEN], oversized.name);
}

test "phase 8 kallsyms injected parser preserves callback failures" {
    const Collector = struct {
        fn stopOnWeakSymbol(list: *std.ArrayList(kallsyms.ParsedSymbol), symbol: kallsyms.ParsedSymbol) anyerror!void {
            if (symbol.symbol_type == 'W') {
                return error.StopOnWeakSymbol;
            }

            try list.append(std.testing.allocator, symbol);
        }
    };

    var symbols = std.ArrayList(kallsyms.ParsedSymbol).empty;
    defer symbols.deinit(std.testing.allocator);

    try std.testing.expectError(
        error.StopOnWeakSymbol,
        kallsyms.forEachParsedLine(
            "ffffffff81000000 T startup_64\n" ++
                "ffffffff81000200 W weak_handler\n" ++
                "ffffffff81000300 t ignored_after_callback_error\n",
            &symbols,
            Collector.stopOnWeakSymbol,
        ),
    );
    try std.testing.expectEqual(@as(usize, 1), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", symbols.items[0].name);
}

test "phase 8 kallsyms chunked reader slice keeps parser behavior across split input" {
    const ChunkFixtureState = struct {
        chunks: []const []const u8,
        index: usize = 0,
    };

    const ChunkFixture = struct {
        fn next(state: *ChunkFixtureState) anyerror!?[]const u8 {
            if (state.index >= state.chunks.len) {
                return null;
            }

            const chunk = state.chunks[state.index];
            state.index += 1;
            return chunk;
        }
    };

    const OwnedParsedSymbol = struct {
        name: []u8,
        symbol_type: u8,
        start: u64,

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            allocator.free(self.name);
            self.* = undefined;
        }
    };

    const Collector = struct {
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
            try list.append(std.testing.allocator, .{
                .name = try std.testing.allocator.dupe(u8, symbol.name),
                .symbol_type = symbol.symbol_type,
                .start = symbol.start,
            });
        }
    };

    var state = ChunkFixtureState{
        .chunks = &.{
            "ffffffff81000000 T st",
            "artup_64\r\ninvalid",
            "\nffffffff81000300 w weak_tail",
        },
    };

    var symbols = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (symbols.items) |*symbol| {
            symbol.deinit(std.testing.allocator);
        }
        symbols.deinit(std.testing.allocator);
    }

    try kallsyms.forEachParsedChunked(
        std.testing.allocator,
        &state,
        ChunkFixture.next,
        &symbols,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 'w'), symbols.items[1].symbol_type);
}

test "phase 8 kallsyms thin reader and path adapters preserve the shipped parser contract" {
    const SliceReader = struct {
        bytes: []const u8,
        index: usize = 0,

        pub fn read(self: *@This(), dest: []u8) !usize {
            if (self.index >= self.bytes.len) {
                return 0;
            }

            const amt = @min(dest.len, self.bytes.len - self.index);
            @memcpy(dest[0..amt], self.bytes[self.index .. self.index + amt]);
            self.index += amt;
            return amt;
        }
    };

    const OwnedParsedSymbol = struct {
        name: []u8,
        symbol_type: u8,
        start: u64,

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            allocator.free(self.name);
            self.* = undefined;
        }
    };

    const Collector = struct {
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
            try list.append(std.testing.allocator, .{
                .name = try std.testing.allocator.dupe(u8, symbol.name),
                .symbol_type = symbol.symbol_type,
                .start = symbol.start,
            });
        }
    };

    const contents =
        "ffffffff81000000 T startup_64\r\n" ++
        "bad line\n" ++
        "ffffffff81000400 w weak_tail";

    var stream = SliceReader{ .bytes = contents };
    var scratch_buffer: [11]u8 = undefined;
    var from_reader = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (from_reader.items) |*symbol| {
            symbol.deinit(std.testing.allocator);
        }
        from_reader.deinit(std.testing.allocator);
    }

    try kallsyms.forEachParsedReader(
        std.testing.allocator,
        &stream,
        &scratch_buffer,
        &from_reader,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), from_reader.items.len);
    try std.testing.expectEqualStrings("startup_64", from_reader.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", from_reader.items[1].name);

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;

    {
        const file = try temp_dir.dir.createFile(io, "kallsyms.map", .{ .read = true });
        defer file.close(io);
        var writer_buffer: [128]u8 = undefined;
        var writer: std.Io.File.Writer = .init(file, io, &writer_buffer);
        try writer.interface.writeAll(contents);
        try writer.interface.flush();
    }

    var from_path = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (from_path.items) |*symbol| {
            symbol.deinit(std.testing.allocator);
        }
        from_path.deinit(std.testing.allocator);
    }

    try kallsyms.forEachParsedPath(
        std.testing.allocator,
        io,
        temp_dir.dir,
        "kallsyms.map",
        &scratch_buffer,
        &from_path,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), from_path.items.len);
    try std.testing.expectEqualStrings("startup_64", from_path.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", from_path.items[1].name);
    try std.testing.expectEqual(@as(u8, 'w'), from_path.items[1].symbol_type);

    var empty_stream = SliceReader{
        .bytes = "ffffffff81000000 T startup_64\n",
    };
    var empty_scratch_buffer: [0]u8 = .{};

    try std.testing.expectError(
        error.EmptyScratchBuffer,
        kallsyms.forEachParsedReader(
            std.testing.allocator,
            &empty_stream,
            &empty_scratch_buffer,
            &from_path,
            Collector.append,
        ),
    );
}

test "phase 8 kallsyms file wrapper keeps the direct callback contract on an already-open file" {
    const CallbackState = struct {
        names: std.ArrayList([]u8),
        symbol_types: std.ArrayList(u8),
        starts: std.ArrayList(u64),

        fn init() @This() {
            return .{
                .names = std.ArrayList([]u8).empty,
                .symbol_types = std.ArrayList(u8).empty,
                .starts = std.ArrayList(u64).empty,
            };
        }

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            for (self.names.items) |name| {
                allocator.free(name);
            }
            self.names.deinit(allocator);
            self.symbol_types.deinit(allocator);
            self.starts.deinit(allocator);
            self.* = undefined;
        }

        fn collect(context: ?*anyopaque, name: [:0]const u8, symbol_type: u8, start: u64) i32 {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            self.symbol_types.append(std.testing.allocator, symbol_type) catch return -97;
            self.starts.append(std.testing.allocator, start) catch return -96;
            if (symbol_type == 'W') {
                return 29;
            }
            return 0;
        }
    };

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;

    {
        const file = try temp_dir.dir.createFile(io, "kallsyms.map", .{ .read = true });
        defer file.close(io);
        var writer_buffer: [128]u8 = undefined;
        var writer: std.Io.File.Writer = .init(file, io, &writer_buffer);
        try writer.interface.writeAll(
            "ffffffff81000000 T startup_64\n" ++
                "bad line\n" ++
                "ffffffff81000200 W weak_handler\n" ++
                "ffffffff81000300 t ignored_after_stop\n",
        );
        try writer.interface.flush();
    }

    const file = try temp_dir.dir.openFile(io, "kallsyms.map", .{});
    defer file.close(io);

    var scratch_buffer: [19]u8 = undefined;
    var callback_state = CallbackState.init();
    defer callback_state.deinit(std.testing.allocator);

    const result = try kallsyms.kallsymsParseFile(
        std.testing.allocator,
        io,
        file,
        &scratch_buffer,
        &callback_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 29), result);
    try std.testing.expectEqual(@as(usize, 2), callback_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", callback_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", callback_state.names.items[1]);
}

test "phase 8 kallsyms direct wrapper preserves the C-shaped callback contract" {
    const CallbackState = struct {
        names: std.ArrayList([]u8),
        symbol_types: std.ArrayList(u8),
        starts: std.ArrayList(u64),

        fn init() @This() {
            return .{
                .names = std.ArrayList([]u8).empty,
                .symbol_types = std.ArrayList(u8).empty,
                .starts = std.ArrayList(u64).empty,
            };
        }

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            for (self.names.items) |name| {
                allocator.free(name);
            }
            self.names.deinit(allocator);
            self.symbol_types.deinit(allocator);
            self.starts.deinit(allocator);
            self.* = undefined;
        }

        fn collect(context: ?*anyopaque, name: [:0]const u8, symbol_type: u8, start: u64) i32 {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            self.symbol_types.append(std.testing.allocator, symbol_type) catch return -97;
            self.starts.append(std.testing.allocator, start) catch return -96;
            if (symbol_type == 'W') {
                return 23;
            }
            return 0;
        }
    };

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;

    {
        const file = try temp_dir.dir.createFile(io, "kallsyms.map", .{ .read = true });
        defer file.close(io);
        var writer_buffer: [128]u8 = undefined;
        var writer: std.Io.File.Writer = .init(file, io, &writer_buffer);
        try writer.interface.writeAll(
            "ffffffff81000000 T startup_64\n" ++
                "garbage\n" ++
                "ffffffff81000200 W weak_handler\n" ++
                "ffffffff81000300 t ignored_after_stop\n",
        );
        try writer.interface.flush();
    }

    var callback_state = CallbackState.init();
    defer callback_state.deinit(std.testing.allocator);

    const result = try kallsyms.kallsymsParse(
        std.testing.allocator,
        io,
        temp_dir.dir,
        "kallsyms.map",
        &callback_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 23), result);
    try std.testing.expectEqual(@as(usize, 2), callback_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", callback_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", callback_state.names.items[1]);
    try std.testing.expectEqual(@as(u8, 'W'), callback_state.symbol_types.items[1]);
    try std.testing.expectEqual(@as(u64, 0xffffffff81000200), callback_state.starts.items[1]);
}
