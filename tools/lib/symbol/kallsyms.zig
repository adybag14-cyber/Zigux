const std = @import("std");

pub const KSYM_NAME_LEN: usize = 512;
pub const default_reader_chunk_len: usize = 4096;
pub const max_buffered_line_len: usize = 32 + 3 + KSYM_NAME_LEN;

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

pub const ProcessSymbolFn = *const fn (?*anyopaque, [:0]const u8, u8, u64) i32;

const ProcessSymbolCallbackState = struct {
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
    result: i32 = 0,

    fn process(self: *@This(), symbol: ParsedSymbol) anyerror!void {
        var name_buffer: [KSYM_NAME_LEN + 1:0]u8 = undefined;
        @memcpy(name_buffer[0..symbol.name.len], symbol.name);
        name_buffer[symbol.name.len] = 0;

        const callback_result = self.process_symbol(
            self.context,
            name_buffer[0..symbol.name.len :0],
            symbol.symbol_type,
            symbol.start,
        );
        if (callback_result != 0) {
            self.result = callback_result;
            return error.StopParsing;
        }
    }
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

pub fn parseLine(line: []const u8) ?ParsedSymbol {
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
    const name = trimmed[first_space + 3 .. @min(trimmed.len, first_space + 3 + KSYM_NAME_LEN)];

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
        const parsed = parseLine(line) orelse continue;
        try process_symbol(context, parsed);
    }
}

fn processParsedLine(
    line: []const u8,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    const parsed = parseLine(line) orelse return;
    try process_symbol(context, parsed);
}

const PendingParsedLine = struct {
    bytes: [max_buffered_line_len]u8 = undefined,
    len: usize = 0,
    discarding_tail: bool = false,

    fn deinit(self: *@This()) void {
        self.* = undefined;
    }

    fn appendBounded(self: *@This(), byte: u8) void {
        if (self.discarding_tail) {
            return;
        }
        if (self.len >= self.bytes.len) {
            self.discarding_tail = true;
            return;
        }
        self.bytes[self.len] = byte;
        self.len += 1;
    }

    fn items(self: *const @This()) []const u8 {
        return self.bytes[0..self.len];
    }

    fn finish(
        self: *@This(),
        context: anytype,
        comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
    ) !void {
        try processParsedLine(self.items(), context, process_symbol);
        self.len = 0;
        self.discarding_tail = false;
    }
};

fn finishPendingAtEof(
    pending: *PendingParsedLine,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    if (pending.len == 0) {
        return;
    }

    try pending.finish(context, process_symbol);
}

fn processParsedChunk(
    pending: *PendingParsedLine,
    chunk: []const u8,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    for (chunk) |byte| {
        if (byte == '\n') {
            try pending.finish(context, process_symbol);
            continue;
        }
        pending.appendBounded(byte);
    }
}

pub fn forEachParsedChunked(
    allocator: std.mem.Allocator,
    reader_context: anytype,
    comptime next_chunk: fn (@TypeOf(reader_context)) anyerror!?[]const u8,
    process_context: anytype,
    comptime process_symbol: fn (@TypeOf(process_context), ParsedSymbol) anyerror!void,
) !void {
    _ = allocator;
    var pending = PendingParsedLine{};
    defer pending.deinit();

    while (try next_chunk(reader_context)) |chunk| {
        try processParsedChunk(&pending, chunk, process_context, process_symbol);
    }

    try finishPendingAtEof(&pending, process_context, process_symbol);
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

    _ = allocator;
    var pending = PendingParsedLine{};
    defer pending.deinit();

    while (true) {
        const bytes_read = try reader.read(scratch_buffer);
        if (bytes_read == 0) {
            break;
        }

        try processParsedChunk(&pending, scratch_buffer[0..bytes_read], process_context, process_symbol);
    }

    try finishPendingAtEof(&pending, process_context, process_symbol);
}

pub fn forEachParsedFile(
    allocator: std.mem.Allocator,
    io: std.Io,
    file: std.Io.File,
    scratch_buffer: []u8,
    process_context: anytype,
    comptime process_symbol: fn (@TypeOf(process_context), ParsedSymbol) anyerror!void,
) !void {
    const ReaderAdapter = struct {
        reader: *std.Io.File.Reader,

        pub fn read(self: *@This(), dest: []u8) !usize {
            return self.reader.interface.readSliceShort(dest);
        }
    };

    var reader_buffer: [default_reader_chunk_len]u8 = undefined;
    var file_reader = file.reader(io, &reader_buffer);
    var adapter = ReaderAdapter{ .reader = &file_reader };
    try forEachParsedReader(allocator, &adapter, scratch_buffer, process_context, process_symbol);
}

pub fn forEachParsedPath(
    allocator: std.mem.Allocator,
    io: std.Io,
    dir: std.Io.Dir,
    sub_path: []const u8,
    scratch_buffer: []u8,
    process_context: anytype,
    comptime process_symbol: fn (@TypeOf(process_context), ParsedSymbol) anyerror!void,
) !void {
    const file = try dir.openFile(io, sub_path, .{});
    defer file.close(io);

    try forEachParsedFile(allocator, io, file, scratch_buffer, process_context, process_symbol);
}

pub fn kallsymsParseContents(
    contents: []const u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    var callback_state = ProcessSymbolCallbackState{
        .context = context,
        .process_symbol = process_symbol,
    };

    forEachParsedLine(contents, &callback_state, ProcessSymbolCallbackState.process) catch |err| switch (err) {
        error.StopParsing => return callback_state.result,
        else => return err,
    };

    return callback_state.result;
}

pub fn kallsymsParseChunked(
    allocator: std.mem.Allocator,
    reader_context: anytype,
    comptime next_chunk: fn (@TypeOf(reader_context)) anyerror!?[]const u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    var callback_state = ProcessSymbolCallbackState{
        .context = context,
        .process_symbol = process_symbol,
    };

    forEachParsedChunked(
        allocator,
        reader_context,
        next_chunk,
        &callback_state,
        ProcessSymbolCallbackState.process,
    ) catch |err| switch (err) {
        error.StopParsing => return callback_state.result,
        else => return err,
    };

    return callback_state.result;
}

pub fn kallsymsParseReader(
    allocator: std.mem.Allocator,
    reader: anytype,
    scratch_buffer: []u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    var callback_state = ProcessSymbolCallbackState{
        .context = context,
        .process_symbol = process_symbol,
    };

    forEachParsedReader(
        allocator,
        reader,
        scratch_buffer,
        &callback_state,
        ProcessSymbolCallbackState.process,
    ) catch |err| switch (err) {
        error.StopParsing => return callback_state.result,
        else => return err,
    };

    return callback_state.result;
}

pub fn kallsymsParseInDir(
    allocator: std.mem.Allocator,
    io: std.Io,
    dir: std.Io.Dir,
    sub_path: []const u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    var scratch_buffer: [default_reader_chunk_len]u8 = undefined;
    var callback_state = ProcessSymbolCallbackState{
        .context = context,
        .process_symbol = process_symbol,
    };

    forEachParsedPath(
        allocator,
        io,
        dir,
        sub_path,
        &scratch_buffer,
        &callback_state,
        ProcessSymbolCallbackState.process,
    ) catch |err| switch (err) {
        error.StopParsing => return callback_state.result,
        else => return err,
    };

    return callback_state.result;
}

pub fn kallsymsParse(
    allocator: std.mem.Allocator,
    io: std.Io,
    filename: []const u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    return kallsymsParseInDir(
        allocator,
        io,
        std.Io.Dir.cwd(),
        filename,
        context,
        process_symbol,
    ) catch return -1;
}

const ChunkFixtureState = struct {
    chunks: []const []const u8,
    index: usize = 0,
};

fn nextFixtureChunk(state: *ChunkFixtureState) anyerror!?[]const u8 {
    if (state.index >= state.chunks.len) {
        return null;
    }

    const chunk = state.chunks[state.index];
    state.index += 1;
    return chunk;
}

const OwnedParsedSymbol = struct {
    name: []u8,
    symbol_type: u8,
    start: u64,

    fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
        allocator.free(self.name);
        self.* = undefined;
    }
};

fn appendOwnedParsedSymbol(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
    try list.append(std.testing.allocator, .{
        .name = try std.testing.allocator.dupe(u8, symbol.name),
        .symbol_type = symbol.symbol_type,
        .start = symbol.start,
    });
}

fn deinitOwnedParsedSymbols(list: *std.ArrayList(OwnedParsedSymbol)) void {
    for (list.items) |*symbol| {
        symbol.deinit(std.testing.allocator);
    }
    list.deinit(std.testing.allocator);
}

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
    const parsed = parseLine("ffffffff81000000 T startup_64") orelse unreachable;
    try std.testing.expectEqual(@as(u64, 0xffffffff81000000), parsed.start);
    try std.testing.expectEqual(@as(u8, 'T'), parsed.symbol_type);
    try std.testing.expectEqualStrings("startup_64", parsed.name);

    try std.testing.expectEqual(@as(?ParsedSymbol, null), parseLine(""));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), parseLine("not-hex T broken"));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), parseLine("ffffffff81000000 TT broken"));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), parseLine("ffffffff81000000"));

    const too_long_name = "a" ** (KSYM_NAME_LEN + 9);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_line);

    const truncated = parseLine(oversized_line) orelse unreachable;
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), truncated.name.len);
    try std.testing.expect(std.mem.allEqual(u8, truncated.name, 'a'));
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

    const too_long_name = "a" ** (KSYM_NAME_LEN + 7);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_line);

    parsed.clearRetainingCapacity();
    try forEachParsedLine(
        oversized_line,
        &parsed,
        Fixture.collect,
    );
    try std.testing.expectEqual(@as(usize, 1), parsed.items.len);
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), parsed.items[0].name.len);
    try std.testing.expect(std.mem.allEqual(u8, parsed.items[0].name, 'a'));

    parsed.clearRetainingCapacity();
    try std.testing.expectError(error.StopOnWeakSymbol, forEachParsedLine(
        "ffffffff81000000 T startup_64\n" ++
            "ffffffff81000200 W weak_handler\n" ++
            "ffffffff81000300 t ignored_after_callback_error\n",
        &parsed,
        Fixture.failOnWeakSymbol,
    ));
    try std.testing.expectEqual(@as(usize, 1), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
}

test "forEachParsedChunked preserves line parsing across chunk boundaries" {
    const Fixture = struct {
        fn collect(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try appendOwnedParsedSymbol(list, symbol);
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
    defer deinitOwnedParsedSymbols(&parsed);

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

    const too_long_name = "a" ** (KSYM_NAME_LEN + 17);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_line);

    const split_index = 9 + (KSYM_NAME_LEN / 2);
    var oversized_state = ChunkFixtureState{
        .chunks = &[_][]const u8{
            oversized_line[0..split_index],
            oversized_line[split_index..],
        },
    };

    var oversized = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&oversized);

    try forEachParsedChunked(
        std.testing.allocator,
        &oversized_state,
        nextFixtureChunk,
        &oversized,
        Fixture.collect,
    );

    try std.testing.expectEqual(@as(usize, 1), oversized.items.len);
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), oversized.items[0].name.len);
    try std.testing.expect(std.mem.allEqual(u8, oversized.items[0].name, 'a'));
}

test "forEachParsedChunked discards oversized line tails once the bounded callback surface is full" {
    const Fixture = struct {
        fn collect(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try appendOwnedParsedSymbol(list, symbol);
        }
    };

    const oversized_name = "a" ** (KSYM_NAME_LEN + 400);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{oversized_name},
    );
    defer std.testing.allocator.free(oversized_line);

    const next_line = "ffffffff81000400 t next_symbol\n";
    const split_index = max_buffered_line_len + 27;
    var state = ChunkFixtureState{
        .chunks = &[_][]const u8{
            oversized_line[0..split_index],
            oversized_line[split_index..],
            "\n",
            next_line,
        },
    };

    var parsed = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&parsed);

    try forEachParsedChunked(
        std.testing.allocator,
        &state,
        nextFixtureChunk,
        &parsed,
        Fixture.collect,
    );

    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), parsed.items[0].name.len);
    try std.testing.expect(std.mem.allEqual(u8, parsed.items[0].name, 'a'));
    try std.testing.expectEqualStrings("next_symbol", parsed.items[1].name);
    try std.testing.expectEqual(@as(u8, 't'), parsed.items[1].symbol_type);
}

test "chunked and reader entrypoints keep the final unterminated line at EOF" {
    const Fixture = struct {
        fn collect(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try appendOwnedParsedSymbol(list, symbol);
        }
    };

    var chunked_state = ChunkFixtureState{
        .chunks = &.{
            "ffffffff81000000 T startup_",
            "64\nffffffff81000400 w weak_tail",
        },
    };
    var chunked_symbols = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&chunked_symbols);

    try forEachParsedChunked(
        std.testing.allocator,
        &chunked_state,
        nextFixtureChunk,
        &chunked_symbols,
        Fixture.collect,
    );

    try std.testing.expectEqual(@as(usize, 2), chunked_symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", chunked_symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", chunked_symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 'w'), chunked_symbols.items[1].symbol_type);

    var reader = SliceReader{
        .bytes = "ffffffff81000000 T startup_64\nffffffff81000400 w weak_tail",
    };
    var scratch_buffer: [9]u8 = undefined;
    var reader_symbols = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&reader_symbols);

    try forEachParsedReader(
        std.testing.allocator,
        &reader,
        &scratch_buffer,
        &reader_symbols,
        Fixture.collect,
    );

    try std.testing.expectEqual(@as(usize, 2), reader_symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", reader_symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", reader_symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 'w'), reader_symbols.items[1].symbol_type);
}

test "forEachParsedReader and path reuse the same malformed-line skipping semantics" {
    const Fixture = struct {
        fn collect(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try appendOwnedParsedSymbol(list, symbol);
        }
    };

    const contents =
        "ffffffff81000000 T startup_64\r\n" ++
        "bad line\n" ++
        "ffffffff81000400 w weak_tail\n";

    var stream = SliceReader{ .bytes = contents };
    var scratch_buffer: [11]u8 = undefined;
    var from_reader = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&from_reader);

    try forEachParsedReader(
        std.testing.allocator,
        &stream,
        &scratch_buffer,
        &from_reader,
        Fixture.collect,
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
    defer deinitOwnedParsedSymbols(&from_path);

    try forEachParsedPath(
        std.testing.allocator,
        io,
        temp_dir.dir,
        "kallsyms.map",
        &scratch_buffer,
        &from_path,
        Fixture.collect,
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
        forEachParsedReader(
            std.testing.allocator,
            &empty_stream,
            &empty_scratch_buffer,
            &from_path,
            Fixture.collect,
        ),
    );
}

test "kallsymsParse wrappers preserve the C-shaped callback contract and bounded names" {
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

        fn collectWithoutStop(context: ?*anyopaque, name: [:0]const u8, symbol_type: u8, start: u64) i32 {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            self.symbol_types.append(std.testing.allocator, symbol_type) catch return -97;
            self.starts.append(std.testing.allocator, start) catch return -96;
            return 0;
        }
    };

    const contents =
        "ffffffff81000000 T startup_64\n" ++
        "garbage\n" ++
        "ffffffff81000200 W weak_handler\n" ++
        "ffffffff81000300 t ignored_after_stop\n";

    var contents_state = CallbackState.init();
    defer contents_state.deinit(std.testing.allocator);

    const contents_result = try kallsymsParseContents(
        contents,
        &contents_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 23), contents_result);
    try std.testing.expectEqual(@as(usize, 2), contents_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", contents_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", contents_state.names.items[1]);
    try std.testing.expectEqual(@as(u8, 'W'), contents_state.symbol_types.items[1]);
    try std.testing.expectEqual(@as(u64, 0xffffffff81000200), contents_state.starts.items[1]);

    var chunked_state = ChunkFixtureState{
        .chunks = &.{
            "ffffffff81000000 T start",
            "up_64\ngarbage\nffff",
            "ffff81000200 W weak_handler\nffffffff81000300 t ignored_after_stop\n",
        },
    };
    var chunked_callback_state = CallbackState.init();
    defer chunked_callback_state.deinit(std.testing.allocator);

    const chunked_result = try kallsymsParseChunked(
        std.testing.allocator,
        &chunked_state,
        nextFixtureChunk,
        &chunked_callback_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 23), chunked_result);
    try std.testing.expectEqual(@as(usize, 2), chunked_callback_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", chunked_callback_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", chunked_callback_state.names.items[1]);
    try std.testing.expectEqual(@as(u8, 'W'), chunked_callback_state.symbol_types.items[1]);
    try std.testing.expectEqual(@as(u64, 0xffffffff81000200), chunked_callback_state.starts.items[1]);

    var reader_state = CallbackState.init();
    defer reader_state.deinit(std.testing.allocator);

    var reader = SliceReader{ .bytes = contents };
    var reader_scratch_buffer: [13]u8 = undefined;
    const reader_result = try kallsymsParseReader(
        std.testing.allocator,
        &reader,
        &reader_scratch_buffer,
        &reader_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 23), reader_result);
    try std.testing.expectEqual(@as(usize, 2), reader_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", reader_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", reader_state.names.items[1]);
    try std.testing.expectEqual(@as(u8, 'W'), reader_state.symbol_types.items[1]);
    try std.testing.expectEqual(@as(u64, 0xffffffff81000200), reader_state.starts.items[1]);

    var empty_reader = SliceReader{ .bytes = contents };
    var empty_reader_scratch_buffer: [0]u8 = .{};
    var empty_reader_state = CallbackState.init();
    defer empty_reader_state.deinit(std.testing.allocator);

    try std.testing.expectError(
        error.EmptyScratchBuffer,
        kallsymsParseReader(
            std.testing.allocator,
            &empty_reader,
            &empty_reader_scratch_buffer,
            &empty_reader_state,
            CallbackState.collectWithoutStop,
        ),
    );

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

    var callback_state = CallbackState.init();
    defer callback_state.deinit(std.testing.allocator);

    const result = try kallsymsParseInDir(
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

    const filename = try std.fs.path.join(
        std.testing.allocator,
        &.{ ".zig-cache", "tmp", temp_dir.sub_path[0..], "kallsyms.map" },
    );
    defer std.testing.allocator.free(filename);

    var filename_state = CallbackState.init();
    defer filename_state.deinit(std.testing.allocator);

    const filename_result = try kallsymsParse(
        std.testing.allocator,
        io,
        filename,
        &filename_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 23), filename_result);
    try std.testing.expectEqual(@as(usize, 2), filename_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", filename_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", filename_state.names.items[1]);
    try std.testing.expectEqual(@as(u8, 'W'), filename_state.symbol_types.items[1]);
    try std.testing.expectEqual(@as(u64, 0xffffffff81000200), filename_state.starts.items[1]);

    var missing_state = CallbackState.init();
    defer missing_state.deinit(std.testing.allocator);

    const missing_result = try kallsymsParse(
        std.testing.allocator,
        io,
        "missing-kallsyms.map",
        &missing_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, -1), missing_result);
    try std.testing.expectEqual(@as(usize, 0), missing_state.names.items.len);

    const too_long_name = "b" ** (KSYM_NAME_LEN + 21);
    const oversized_contents = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}\n",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_contents);

    var oversized_contents_state = CallbackState.init();
    defer oversized_contents_state.deinit(std.testing.allocator);

    const oversized_contents_result = try kallsymsParseContents(
        oversized_contents,
        &oversized_contents_state,
        CallbackState.collectWithoutStop,
    );

    try std.testing.expectEqual(@as(i32, 0), oversized_contents_result);
    try std.testing.expectEqual(@as(usize, 1), oversized_contents_state.names.items.len);
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), oversized_contents_state.names.items[0].len);
    try std.testing.expect(std.mem.allEqual(u8, oversized_contents_state.names.items[0], 'b'));
    try std.testing.expectEqual(@as(u8, 'T'), oversized_contents_state.symbol_types.items[0]);
    try std.testing.expectEqual(@as(u64, 1), oversized_contents_state.starts.items[0]);

    {
        const file = try temp_dir.dir.createFile(io, "oversized-kallsyms.map", .{ .read = true, .truncate = true });
        defer file.close(io);
        var writer_buffer: [640]u8 = undefined;
        var writer: std.Io.File.Writer = .init(file, io, &writer_buffer);
        try writer.interface.writeAll(oversized_contents);
        try writer.interface.flush();
    }

    const oversized_filename = try std.fs.path.join(
        std.testing.allocator,
        &.{ ".zig-cache", "tmp", temp_dir.sub_path[0..], "oversized-kallsyms.map" },
    );
    defer std.testing.allocator.free(oversized_filename);

    var oversized_state = CallbackState.init();
    defer oversized_state.deinit(std.testing.allocator);

    const oversized_result = try kallsymsParse(
        std.testing.allocator,
        io,
        oversized_filename,
        &oversized_state,
        CallbackState.collectWithoutStop,
    );

    try std.testing.expectEqual(@as(i32, 0), oversized_result);
    try std.testing.expectEqual(@as(usize, 1), oversized_state.names.items.len);
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), oversized_state.names.items[0].len);
    try std.testing.expect(std.mem.allEqual(u8, oversized_state.names.items[0], 'b'));
    try std.testing.expectEqual(@as(u8, 'T'), oversized_state.symbol_types.items[0]);
    try std.testing.expectEqual(@as(u64, 1), oversized_state.starts.items[0]);
}

test "kallsymsParseReader keeps the final unterminated callback record at EOF" {
    const CallbackState = struct {
        names: std.ArrayList([]u8),

        fn init() @This() {
            return .{
                .names = std.ArrayList([]u8).empty,
            };
        }

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            for (self.names.items) |name| {
                allocator.free(name);
            }
            self.names.deinit(allocator);
            self.* = undefined;
        }

        fn collect(context: ?*anyopaque, name: [:0]const u8, symbol_type: u8, start: u64) i32 {
            _ = symbol_type;
            _ = start;
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            return 0;
        }
    };

    var state = CallbackState.init();
    defer state.deinit(std.testing.allocator);

    var reader = SliceReader{
        .bytes = "ffffffff81000000 T startup_64\nffffffff81000400 w weak_tail",
    };
    var scratch_buffer: [12]u8 = undefined;

    const result = try kallsymsParseReader(
        std.testing.allocator,
        &reader,
        &scratch_buffer,
        &state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 0), result);
    try std.testing.expectEqual(@as(usize, 2), state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", state.names.items[0]);
    try std.testing.expectEqualStrings("weak_tail", state.names.items[1]);
}

test "kallsymsParseInDir and kallsymsParse keep the final unterminated callback record with owned scratch" {
    const CallbackState = struct {
        names: std.ArrayList([]u8),

        fn init() @This() {
            return .{
                .names = std.ArrayList([]u8).empty,
            };
        }

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            for (self.names.items) |name| {
                allocator.free(name);
            }
            self.names.deinit(allocator);
            self.* = undefined;
        }

        fn collect(context: ?*anyopaque, name: [:0]const u8, symbol_type: u8, start: u64) i32 {
            _ = symbol_type;
            _ = start;
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            return 0;
        }
    };

    const contents =
        "ffffffff81000000 T startup_64\n" ++
        "ffffffff81000400 w weak_tail";

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;

    {
        const file = try temp_dir.dir.createFile(io, "kallsyms-eof.map", .{ .read = true });
        defer file.close(io);
        var writer_buffer: [128]u8 = undefined;
        var writer: std.Io.File.Writer = .init(file, io, &writer_buffer);
        try writer.interface.writeAll(contents);
        try writer.interface.flush();
    }

    var in_dir_state = CallbackState.init();
    defer in_dir_state.deinit(std.testing.allocator);

    const in_dir_result = try kallsymsParseInDir(
        std.testing.allocator,
        io,
        temp_dir.dir,
        "kallsyms-eof.map",
        &in_dir_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 0), in_dir_result);
    try std.testing.expectEqual(@as(usize, 2), in_dir_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", in_dir_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_tail", in_dir_state.names.items[1]);

    const filename = try std.fs.path.join(
        std.testing.allocator,
        &.{ ".zig-cache", "tmp", temp_dir.sub_path[0..], "kallsyms-eof.map" },
    );
    defer std.testing.allocator.free(filename);

    var filename_state = CallbackState.init();
    defer filename_state.deinit(std.testing.allocator);

    const filename_result = try kallsymsParse(
        std.testing.allocator,
        io,
        filename,
        &filename_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, 0), filename_result);
    try std.testing.expectEqual(@as(usize, 2), filename_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", filename_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_tail", filename_state.names.items[1]);
}
