const std = @import("std");

pub const KSYM_NAME_LEN: usize = 512;
pub const default_reader_chunk_len: usize = 4096;

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

pub const ParseLineError = error{
    SymbolNameTooLong,
};

pub fn kallsyms2ElfBinding(symbol_type: u8) u8 {
    if (symbol_type == 'W') return elf_stb_weak;
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

fn validateNameLen(name: []const u8) ParseLineError![]const u8 {
    if (name.len > KSYM_NAME_LEN) {
        return error.SymbolNameTooLong;
    }
    return name;
}

pub fn parseLine(line: []const u8) ParseLineError!?ParsedSymbol {
    const trimmed = trimTrailingCarriageReturn(line);
    if (trimmed.len == 0) return null;

    const first_space = std.mem.indexOfScalar(u8, trimmed, ' ') orelse return null;
    if (first_space == 0 or first_space + 2 >= trimmed.len) return null;

    const symbol_type = trimmed[first_space + 1];
    if (symbol_type == ' ' or trimmed[first_space + 2] != ' ') return null;

    const start = std.fmt.parseUnsigned(u64, trimmed[0..first_space], 16) catch return null;
    const name = try validateNameLen(trimmed[first_space + 3 ..]);

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
    if (scratch_buffer.len == 0) return error.EmptyScratchBuffer;

    var pending = std.ArrayList(u8).empty;
    defer pending.deinit(allocator);

    while (true) {
        const bytes_read = try reader.read(scratch_buffer);
        if (bytes_read == 0) break;
        try processParsedChunk(&pending, allocator, scratch_buffer[0..bytes_read], process_context, process_symbol);
    }

    if (pending.items.len != 0) {
        try processParsedLine(pending.items, process_context, process_symbol);
    }
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

const CallbackState = struct {
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

pub fn kallsymsParseFile(
    allocator: std.mem.Allocator,
    io: std.Io,
    file: std.Io.File,
    scratch_buffer: []u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    var callback_state = CallbackState{
        .context = context,
        .process_symbol = process_symbol,
    };

    forEachParsedFile(
        allocator,
        io,
        file,
        scratch_buffer,
        &callback_state,
        CallbackState.process,
    ) catch |err| switch (err) {
        error.StopParsing => return callback_state.result,
        else => return err,
    };

    return callback_state.result;
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

pub fn kallsymsParse(
    allocator: std.mem.Allocator,
    io: std.Io,
    dir: std.Io.Dir,
    sub_path: []const u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    const file = try dir.openFile(io, sub_path, .{});
    defer file.close(io);

    var scratch_buffer: [default_reader_chunk_len]u8 = undefined;
    return kallsymsParseFile(allocator, io, file, &scratch_buffer, context, process_symbol);
}

const ChunkFixtureState = struct {
    chunks: []const []const u8,
    index: usize = 0,
};

fn nextFixtureChunk(state: *ChunkFixtureState) anyerror!?[]const u8 {
    if (state.index >= state.chunks.len) return null;
    const chunk = state.chunks[state.index];
    state.index += 1;
    return chunk;
}

test "kallsyms helpers preserve classification and malformed-line behavior" {
    try std.testing.expectEqual(elf_stb_weak, kallsyms2ElfBinding('W'));
    try std.testing.expectEqual(elf_stt_func, kallsyms2ElfType('w'));
    try std.testing.expect(isFunction('T'));
    try std.testing.expect(!isFunction('B'));

    const parsed = (try parseLine("ffffffff81000000 T startup_64")) orelse unreachable;
    try std.testing.expectEqual(@as(u64, 0xffffffff81000000), parsed.start);
    try std.testing.expectEqualStrings("startup_64", parsed.name);

    try std.testing.expectEqual(@as(?ParsedSymbol, null), try parseLine(""));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), try parseLine("not-hex T broken"));
}

test "parseLine rejects oversized names instead of truncating them" {
    const too_long_name = "a" ** (KSYM_NAME_LEN + 9);
    const oversized_line = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name});
    defer std.testing.allocator.free(oversized_line);

    try std.testing.expectError(error.SymbolNameTooLong, parseLine(oversized_line));
}

test "chunked parsing preserves split records and fails closed on oversized names" {
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
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
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
        for (parsed.items) |*symbol| symbol.deinit(std.testing.allocator);
        parsed.deinit(std.testing.allocator);
    }

    try forEachParsedChunked(std.testing.allocator, &state, nextFixtureChunk, &parsed, Collector.append);
    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
    try std.testing.expectEqualStrings("data_symbol", parsed.items[1].name);

    for (parsed.items) |*symbol| symbol.deinit(std.testing.allocator);
    parsed.clearRetainingCapacity();

    const too_long_name = "a" ** (KSYM_NAME_LEN + 21);
    const first_chunk = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name[0..40]});
    defer std.testing.allocator.free(first_chunk);
    const second_chunk = try std.fmt.allocPrint(std.testing.allocator, "{s}\n", .{too_long_name[40..]});
    defer std.testing.allocator.free(second_chunk);

    var oversized_state = ChunkFixtureState{
        .chunks = &.{ first_chunk, second_chunk },
    };

    try std.testing.expectError(
        error.SymbolNameTooLong,
        forEachParsedChunked(std.testing.allocator, &oversized_state, nextFixtureChunk, &parsed, Collector.append),
    );
    try std.testing.expectEqual(@as(usize, 0), parsed.items.len);
}

test "reader, path, and callback wrappers preserve the parked parser contract" {
    const SliceReader = struct {
        bytes: []const u8,
        index: usize = 0,

        pub fn read(self: *@This(), dest: []u8) !usize {
            if (self.index >= self.bytes.len) return 0;
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
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: ParsedSymbol) !void {
            try list.append(std.testing.allocator, .{
                .name = try std.testing.allocator.dupe(u8, symbol.name),
                .symbol_type = symbol.symbol_type,
                .start = symbol.start,
            });
        }
    };

    const CallbackFixture = struct {
        names: std.ArrayList([]u8),

        fn init() @This() {
            return .{ .names = std.ArrayList([]u8).empty };
        }

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            for (self.names.items) |name| allocator.free(name);
            self.names.deinit(allocator);
            self.* = undefined;
        }

        fn collect(context: ?*anyopaque, name: [:0]const u8, _: u8, _: u64) i32 {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            if (std.mem.eql(u8, name, "weak_tail")) return 23;
            return 0;
        }
    };

    const contents =
        "ffffffff81000000 T startup_64\r\n" ++
        "bad line\n" ++
        "ffffffff81000400 w weak_tail\n";

    var stream = SliceReader{ .bytes = contents };
    var scratch_buffer: [11]u8 = undefined;
    var from_reader = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (from_reader.items) |*symbol| symbol.deinit(std.testing.allocator);
        from_reader.deinit(std.testing.allocator);
    }

    try forEachParsedReader(std.testing.allocator, &stream, &scratch_buffer, &from_reader, Collector.append);
    try std.testing.expectEqual(@as(usize, 2), from_reader.items.len);

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
        for (from_path.items) |*symbol| symbol.deinit(std.testing.allocator);
        from_path.deinit(std.testing.allocator);
    }
    try forEachParsedPath(std.testing.allocator, io, temp_dir.dir, "kallsyms.map", &scratch_buffer, &from_path, Collector.append);
    try std.testing.expectEqual(@as(usize, 2), from_path.items.len);

    const file = try temp_dir.dir.openFile(io, "kallsyms.map", .{});
    defer file.close(io);

    var callback_state = CallbackFixture.init();
    defer callback_state.deinit(std.testing.allocator);
    const result = try kallsymsParseFile(
        std.testing.allocator,
        io,
        file,
        &scratch_buffer,
        &callback_state,
        CallbackFixture.collect,
    );
    try std.testing.expectEqual(@as(i32, 23), result);
    try std.testing.expectEqual(@as(usize, 2), callback_state.names.items.len);
}