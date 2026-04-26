const std = @import("std");
const kallsyms = @import("kallsyms");

const ChunkFixtureState = struct {
    chunks: []const []const u8,
    index: usize = 0,
};

const SliceReader = struct {
    bytes: []const u8,
    index: usize = 0,

    pub fn read(self: *SliceReader, buffer: []u8) !usize {
        const remaining = self.bytes.len - self.index;
        if (remaining == 0) {
            return 0;
        }

        const read_len = @min(buffer.len, remaining);
        @memcpy(buffer[0..read_len], self.bytes[self.index .. self.index + read_len]);
        self.index += read_len;
        return read_len;
    }
};

fn nextFixtureChunk(state: *ChunkFixtureState) anyerror!?[]const u8 {
    if (state.index >= state.chunks.len) {
        return null;
    }

    const chunk = state.chunks[state.index];
    state.index += 1;
    return chunk;
}

test "phase 8 kallsyms module imports cleanly" {
    _ = kallsyms;
}

test "phase 8 kallsyms starter slice covers symbol helpers and injected record parsing" {
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

    try std.testing.expectError(
        error.SymbolNameTooLong,
        kallsyms.forEachParsedLine(oversized_line, &symbols, Collector.append),
    );
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
        nextFixtureChunk,
        &symbols,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 'w'), symbols.items[1].symbol_type);

    const too_long_name = "a" ** (kallsyms.KSYM_NAME_LEN + 1);
    const first_chunk = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name[0..20]},
    );
    defer std.testing.allocator.free(first_chunk);
    const second_chunk = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}\n",
        .{too_long_name[20..]},
    );
    defer std.testing.allocator.free(second_chunk);

    var error_state = ChunkFixtureState{
        .chunks = &.{ first_chunk, second_chunk },
    };

    try std.testing.expectError(
        error.SymbolNameTooLong,
        kallsyms.forEachParsedChunked(
            std.testing.allocator,
            &error_state,
            nextFixtureChunk,
            &symbols,
            Collector.append,
        ),
    );
}

test "phase 8 kallsyms reader adapter reuses the chunk parser with short reads" {
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

    var stream = SliceReader{
        .bytes = "ffffffff81000000 T startup_64\r\ninvalid\nffffffff81000300 w weak_tail",
    };
    var scratch_buffer: [11]u8 = undefined;

    var symbols = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (symbols.items) |*symbol| {
            symbol.deinit(std.testing.allocator);
        }
        symbols.deinit(std.testing.allocator);
    }

    try kallsyms.forEachParsedReader(
        std.testing.allocator,
        &stream,
        &scratch_buffer,
        &symbols,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 'w'), symbols.items[1].symbol_type);

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
            &symbols,
            Collector.append,
        ),
    );
}