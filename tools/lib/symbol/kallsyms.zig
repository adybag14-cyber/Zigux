const std = @import("std");

pub const KSYM_NAME_LEN: usize = 512;

pub const elf_stb_local: u8 = 0;
pub const elf_stb_global: u8 = 1;
pub const elf_stb_weak: u8 = 2;

pub const elf_stt_object: u8 = 1;
pub const elf_stt_func: u8 = 2;

pub const ParsedSymbol = struct {
    name: []const u8,
    symbol_type: u8,
    start: u64,
};

pub const ParseLineError = error{
    SymbolNameTooLong,
};

pub fn kallsyms2ElfBinding(symbol_type: u8) u8 {
    if (symbol_type == 'W') {
        return elf_stb_weak;
    }

    return if (std.ascii.isUpper(symbol_type)) elf_stb_global else elf_stb_local;
}

pub fn kallsyms2ElfType(symbol_type: u8) u8 {
    return switch (std.ascii.toLower(symbol_type)) {
        't', 'w' => elf_stt_func,
        else => elf_stt_object,
    };
}

pub fn isFunction(symbol_type: u8) bool {
    return switch (std.ascii.toUpper(symbol_type)) {
        'T', 'W' => true,
        else => false,
    };
}

fn trimTrailingCarriageReturn(line: []const u8) []const u8 {
    if (line.len != 0 and line[line.len - 1] == '\r') {
        return line[0 .. line.len - 1];
    }

    return line;
}

pub fn parseLine(line: []const u8) ParseLineError!?ParsedSymbol {
    const trimmed = trimTrailingCarriageReturn(line);
    if (trimmed.len == 0) {
        return null;
    }

    const first_space = std.mem.indexOfScalar(u8, trimmed, ' ') orelse return null;
    if (first_space == 0 or first_space + 2 >= trimmed.len) {
        return null;
    }

    const symbol_type = trimmed[first_space + 1];
    if (symbol_type == ' ' or trimmed[first_space + 2] != ' ') {
        return null;
    }

    const start = std.fmt.parseUnsigned(u64, trimmed[0..first_space], 16) catch return null;
    const name = trimmed[first_space + 3 ..];
    if (name.len > KSYM_NAME_LEN) {
        return error.SymbolNameTooLong;
    }

    return .{
        .name = name,
        .symbol_type = symbol_type,
        .start = start,
    };
}

pub fn forEachParsedLine(
    contents: []const u8,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    var lines = std.mem.splitScalar(u8, contents, '\n');
    while (lines.next()) |line| {
        const parsed = try parseLine(line) orelse continue;
        try process_symbol(context, parsed);
    }
}

fn processParsedLine(
    line: []const u8,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    const parsed = try parseLine(line) orelse return;
    try process_symbol(context, parsed);
}

fn processParsedChunk(
    pending: *std.ArrayList(u8),
    allocator: std.mem.Allocator,
    chunk: []const u8,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    var line_start: usize = 0;
    while (std.mem.indexOfScalarPos(u8, chunk, line_start, '\n')) |newline_index| {
        try pending.appendSlice(allocator, chunk[line_start..newline_index]);
        try processParsedLine(pending.items, context, process_symbol);
        pending.clearRetainingCapacity();
        line_start = newline_index + 1;
    }

    try pending.appendSlice(allocator, chunk[line_start..]);
}

pub fn forEachParsedChunked(
    allocator: std.mem.Allocator,
    reader_context: anytype,
    comptime next_chunk: fn (@TypeOf(reader_context)) anyerror!?[]const u8,
    process_context: anytype,
    comptime process_symbol: fn (@TypeOf(process_context), ParsedSymbol) anyerror!void,
) !void {
    var pending = std.ArrayList(u8).empty;
    defer pending.deinit(allocator);

    while (try next_chunk(reader_context)) |chunk| {
        try processParsedChunk(&pending, allocator, chunk, process_context, process_symbol);
    }

    if (pending.items.len != 0) {
        try processParsedLine(pending.items, process_context, process_symbol);
    }
}

pub fn forEachParsedReader(
    allocator: std.mem.Allocator,
    reader: anytype,
    scratch_buffer: []u8,
    process_context: anytype,
    comptime process_symbol: fn (@TypeOf(process_context), ParsedSymbol) anyerror!void,
) !void {
    if (scratch_buffer.len == 0) {
        return error.EmptyScratchBuffer;
    }

    var pending = std.ArrayList(u8).empty;
    defer pending.deinit(allocator);

    while (true) {
        const read_len = try reader.read(scratch_buffer);
        if (read_len == 0) {
            break;
        }

        try processParsedChunk(
            &pending,
            allocator,
            scratch_buffer[0..read_len],
            process_context,
            process_symbol,
        );
    }

    if (pending.items.len != 0) {
        try processParsedLine(pending.items, process_context, process_symbol);
    }
}

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

test "binding, type, and function helpers preserve the C-style symbol rules" {
    try std.testing.expectEqual(elf_stb_weak, kallsyms2ElfBinding('W'));
    try std.testing.expectEqual(elf_stb_global, kallsyms2ElfBinding('T'));
    try std.testing.expectEqual(elf_stb_local, kallsyms2ElfBinding('t'));

    try std.testing.expectEqual(elf_stt_func, kallsyms2ElfType('T'));
    try std.testing.expectEqual(elf_stt_func, kallsyms2ElfType('w'));
    try std.testing.expectEqual(elf_stt_object, kallsyms2ElfType('D'));

    try std.testing.expect(isFunction('T'));
    try std.testing.expect(isFunction('w'));
    try std.testing.expect(!isFunction('B'));
}

test "parseLine keeps valid kallsyms records and skips malformed ones" {
    const parsed = (try parseLine("ffffffff81000000 T startup_64")) orelse unreachable;
    try std.testing.expectEqual(@as(u64, 0xffffffff81000000), parsed.start);
    try std.testing.expectEqual(@as(u8, 'T'), parsed.symbol_type);
    try std.testing.expectEqualStrings("startup_64", parsed.name);

    try std.testing.expectEqual(@as(?ParsedSymbol, null), try parseLine(""));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), try parseLine("not-hex T broken"));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), try parseLine("ffffffff81000000 TT broken"));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), try parseLine("ffffffff81000000"));
}

test "forEachParsedLine processes valid lines in order and propagates parse and callback errors" {
    const Fixture = struct {
        fn collect(list: *std.ArrayList(ParsedSymbol), symbol: ParsedSymbol) !void {
            try list.append(std.testing.allocator, symbol);
        }

        fn failOnWeakSymbol(list: *std.ArrayList(ParsedSymbol), symbol: ParsedSymbol) anyerror!void {
            if (symbol.symbol_type == 'W') {
                return error.StopOnWeakSymbol;
            }

            try list.append(std.testing.allocator, symbol);
        }
    };

    var parsed = std.ArrayList(ParsedSymbol).empty;
    defer parsed.deinit(std.testing.allocator);

    try forEachParsedLine(
        "ffffffff81000000 T startup_64\n" ++
            "invalid line\n" ++
            "ffffffff81000100 d cpu_debug_store\n",
        &parsed,
        Fixture.collect,
    );

    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
    try std.testing.expectEqual(@as(u8, 'd'), parsed.items[1].symbol_type);
    try std.testing.expectEqualStrings("cpu_debug_store", parsed.items[1].name);

    const too_long_name = "a" ** (KSYM_NAME_LEN + 1);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_line);

    try std.testing.expectError(error.SymbolNameTooLong, forEachParsedLine(
        oversized_line,
        &parsed,
        Fixture.collect,
    ));

    parsed.clearRetainingCapacity();
    try std.testing.expectError(error.StopOnWeakSymbol, forEachParsedLine(
        "ffffffff81000000 T startup_64\n" ++
            "fffffff81000200 W weak_handler\n" ++
            "ffffffff81000300 t ignored_after_callback_error\n",
        &parsed,
        Fixture.failOnWeakSymbol,
    ));
    try std.testing.expectEqual(@as(usize, 1), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
}

test "forEachParsedChunked preserves line parsing across chunk boundaries" {
    const OwnedParsedSymbol = struct {
        name: []u8,
        symbol_type: u8,
        start: u64,

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            allocator.free(self.name);
            self.* = undefined;
        }
    };

    const Fixture = struct {
        fn collect(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try list.append(std.testing.allocator, .{
                .name = try std.testing.allocator.dupe(u8, symbol.name),
                .symbol_type = symbol.symbol_type,
                .start = symbol.start,
            });
        }
    };

    var state = ChunkFixtureState{
        .chunks = &.{
            "ffffffff81000000 T start",
            "up_64\nbad",
            " line\nffffffff81000100 d data_symbol",
        },
    };

    var parsed = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (parsed.items) |*symbol| {
            symbol.deinit(std.testing.allocator);
        }
        parsed.deinit(std.testing.allocator);
    }

    try forEachParsedChunked(
        std.testing.allocator,
        &state,
        nextFixtureChunk,
        &parsed,
        Fixture.collect,
    );

    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
    try std.testing.expectEqualStrings("data_symbol", parsed.items[1].name);
    try std.testing.expectEqual(@as(u8, 'd'), parsed.items[1].symbol_type);
}

test "forEachParsedChunked propagates oversized-symbol errors from buffered lines" {
    const OwnedParsedSymbol = struct {
        name: []u8,
        symbol_type: u8,
        start: u64,

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            allocator.free(self.name);
            self.* = undefined;
        }
    };

    const Fixture = struct {
        fn collect(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try list.append(std.testing.allocator, .{
                .name = try std.testing.allocator.dupe(u8, symbol.name),
                .symbol_type = symbol.symbol_type,
                .start = symbol.start,
            });
        }
    };

    const too_long_name = "a" ** (kallsyms.KSYM_NAME_LEN + 1);
    const first_chunk = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name[0..20}},
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