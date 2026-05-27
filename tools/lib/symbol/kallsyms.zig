const std = @import("std");

pub const KSYM_NAME_LEN: usize = 512;
pub const default_reader_chunk_len: usize = 4096;
pub const elf_stb_local: u8 = 0;
pub const elf_stb_global: u8 = 1;
pub const elf_stb_weak: u8 = 2;
pub const elf_stt_object: u8 = 1;
pub const elf_stt_func: u8 = 2;

const max_buffered_line_len: usize = 64 + 3 + KSYM_NAME_LEN;

pub const ParsedSymbol = struct {
    name: []const u8,
    symbol_type: u8,
    start: u64,
};

pub const ProcessSymbolFn = *const fn (?*anyopaque, [:0]const u8, u8, u64) i32;

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

fn normalizeName(name: []const u8) []const u8 {
    var end = name.len;
    while (end != 0 and name[end - 1] == '\r') : (end -= 1) {}
    const trimmed = name[0..end];
    return if (trimmed.len > KSYM_NAME_LEN) trimmed[0..KSYM_NAME_LEN] else trimmed;
}

pub fn parseLine(line: []const u8) ?ParsedSymbol {
    if (line.len == 0) return null;

    const first_space = std.mem.indexOfScalar(u8, line, ' ') orelse return null;
    if (first_space == 0 or first_space + 2 >= line.len) return null;

    const symbol_type = line[first_space + 1];
    if (symbol_type == ' ' or line[first_space + 2] != ' ') return null;

    const start = std.fmt.parseUnsigned(u64, line[0..first_space], 16) catch return null;
    return .{
        .name = normalizeName(line[first_space + 3 ..]),
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

const LineBufferState = struct {
    dropping_tail: bool = false,
};

fn appendBoundedLineBytes(
    pending: *std.ArrayList(u8),
    allocator: std.mem.Allocator,
    line_state: *LineBufferState,
    bytes: []const u8,
) !void {
    if (line_state.dropping_tail or bytes.len == 0) return;

    const remaining = max_buffered_line_len -| pending.items.len;
    if (remaining == 0) {
        line_state.dropping_tail = true;
        return;
    }

    const kept = @min(remaining, bytes.len);
    try pending.appendSlice(allocator, bytes[0..kept]);
    if (kept != bytes.len) {
        line_state.dropping_tail = true;
    }
}

fn processParsedChunk(
    pending: *std.ArrayList(u8),
    allocator: std.mem.Allocator,
    line_state: *LineBufferState,
    chunk: []const u8,
    context: anytype,
    comptime process_symbol: fn (@TypeOf(context), ParsedSymbol) anyerror!void,
) !void {
    var line_start: usize = 0;
    while (std.mem.indexOfScalarPos(u8, chunk, line_start, '\n')) |newline_index| {
        try appendBoundedLineBytes(pending, allocator, line_state, chunk[line_start..newline_index]);
        try processParsedLine(pending.items, context, process_symbol);
        pending.clearRetainingCapacity();
        line_state.dropping_tail = false;
        line_start = newline_index + 1;
    }

    try appendBoundedLineBytes(pending, allocator, line_state, chunk[line_start..]);
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

    var line_state = LineBufferState{};
    while (try next_chunk(reader_context)) |chunk| {
        try processParsedChunk(&pending, allocator, &line_state, chunk, process_context, process_symbol);
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

    var line_state = LineBufferState{};
    while (true) {
        const bytes_read = try reader.read(scratch_buffer);
        if (bytes_read == 0) break;
        try processParsedChunk(
            &pending,
            allocator,
            &line_state,
            scratch_buffer[0..bytes_read],
            process_context,
            process_symbol,
        );
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

const CallbackState = struct {
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
    result: i32 = 0,

    fn process(self: *@This(), symbol: ParsedSymbol) anyerror!void {
        // Keep callback output bounded and NUL-terminated even when the input line was oversized.
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

    const parsed = parseLine("ffffffff81000000 T startup_64") orelse unreachable;
    try std.testing.expectEqual(@as(u64, 0xffffffff81000000), parsed.start);
    try std.testing.expectEqualStrings("startup_64", parsed.name);
    const crlf_parsed = parseLine("ffffffff81000000 T startup_64\r") orelse unreachable;
    try std.testing.expectEqualStrings("startup_64", crlf_parsed.name);
    try std.testing.expectEqual(@as(?ParsedSymbol, null), parseLine(""));
    try std.testing.expectEqual(@as(?ParsedSymbol, null), parseLine("not-hex T broken"));
}

test "weak object symbol classes keep the current C helper classification" {
    try std.testing.expectEqual(elf_stb_global, kallsyms2ElfBinding('V'));
    try std.testing.expectEqual(elf_stb_local, kallsyms2ElfBinding('v'));
    try std.testing.expectEqual(elf_stt_object, kallsyms2ElfType('V'));
    try std.testing.expectEqual(elf_stt_object, kallsyms2ElfType('v'));
    try std.testing.expect(!isFunction('V'));
    try std.testing.expect(!isFunction('v'));

    const parsed = parseLine("ffffffff81000200 V weak_object") orelse unreachable;
    try std.testing.expectEqual(@as(u8, 'V'), parsed.symbol_type);
    try std.testing.expectEqualStrings("weak_object", parsed.name);
}

test "parseLine truncates oversized names without keeping a parser-local error surface" {
    const too_long_name = "a" ** (KSYM_NAME_LEN + 9);
    const oversized_line = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name});
    defer std.testing.allocator.free(oversized_line);

    const parsed = parseLine(oversized_line) orelse unreachable;
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), parsed.name.len);
    try std.testing.expectEqualStrings(too_long_name[0..KSYM_NAME_LEN], parsed.name);
}

test "callback file parsing keeps oversized symbol names bounded and NUL-terminated" {
    const CallbackStateForOversizedName = struct {
        names: std.ArrayList([]u8),
        symbol_types: std.ArrayList(u8),
        starts: std.ArrayList(u64),
        saw_terminator: bool = false,

        fn init() @This() {
            return .{
                .names = std.ArrayList([]u8).empty,
                .symbol_types = std.ArrayList(u8).empty,
                .starts = std.ArrayList(u64).empty,
            };
        }

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            for (self.names.items) |name| allocator.free(name);
            self.names.deinit(allocator);
            self.symbol_types.deinit(allocator);
            self.starts.deinit(allocator);
            self.* = undefined;
        }

        fn collect(context: ?*anyopaque, name: [:0]const u8, symbol_type: u8, start: u64) i32 {
            const self: *@This() = @ptrCast(@alignCast(context.?));
            self.saw_terminator = name[name.len] == 0;
            self.names.append(std.testing.allocator, std.testing.allocator.dupe(u8, name) catch return -99) catch return -98;
            self.symbol_types.append(std.testing.allocator, symbol_type) catch return -97;
            self.starts.append(std.testing.allocator, start) catch return -96;
            return 0;
        }
    };

    const too_long_name = "a" ** (KSYM_NAME_LEN + 73);
    const contents = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}\r\n2 t done\r\n",
        .{too_long_name},
    );
    defer std.testing.allocator.free(contents);

    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;

    {
        const file = try temp_dir.dir.createFile(io, "kallsyms.map", .{ .read = true });
        defer file.close(io);
        var writer_buffer: [256]u8 = undefined;
        var writer: std.Io.File.Writer = .init(file, io, &writer_buffer);
        try writer.interface.writeAll(contents);
        try writer.interface.flush();
    }

    var callback_state = CallbackStateForOversizedName.init();
    defer callback_state.deinit(std.testing.allocator);

    var scratch_buffer: [17]u8 = undefined;
    const file = try temp_dir.dir.openFile(io, "kallsyms.map", .{});
    defer file.close(io);
    const result = try kallsymsParseFile(
        std.testing.allocator,
        io,
        file,
        &scratch_buffer,
        &callback_state,
        CallbackStateForOversizedName.collect,
    );

    try std.testing.expectEqual(@as(i32, 0), result);
    try std.testing.expect(callback_state.saw_terminator);
    try std.testing.expectEqual(@as(usize, 2), callback_state.names.items.len);
    try std.testing.expectEqual(@as(usize, KSYM_NAME_LEN), callback_state.names.items[0].len);
    try std.testing.expectEqualStrings(too_long_name[0..KSYM_NAME_LEN], callback_state.names.items[0]);
    try std.testing.expectEqualStrings("done", callback_state.names.items[1]);
    try std.testing.expectEqual(@as(u8, 'T'), callback_state.symbol_types.items[0]);
    try std.testing.expectEqual(@as(u64, 1), callback_state.starts.items[0]);
    try std.testing.expectEqual(@as(u64, 2), callback_state.starts.items[1]);
}

test "chunked parsing preserves split records and truncates oversized names" {
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
            "ffffffff81000000 T st",
            "artup_64\r\ninvalid",
            "\nffffffff81000300 w weak_tail",
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
    try std.testing.expectEqualStrings("weak_tail", parsed.items[1].name);

    for (parsed.items) |*symbol| symbol.deinit(std.testing.allocator);
    parsed.clearRetainingCapacity();

    const too_long_name = "a" ** (KSYM_NAME_LEN + 21);
    const first_chunk = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name[0..40]});
    defer std.testing.allocator.free(first_chunk);
    const second_chunk = try std.fmt.allocPrint(std.testing.allocator, "{s}\n", .{too_long_name[40..]});
    defer std.testing.allocator.free(second_chunk);

    var oversized_state = ChunkFixtureState{ .chunks = &.{ first_chunk, second_chunk } };
    try forEachParsedChunked(
        std.testing.allocator,
        &oversized_state,
        nextFixtureChunk,
        &parsed,
        Collector.append,
    );
    try std.testing.expectEqual(@as(usize, 1), parsed.items.len);
    try std.testing.expectEqualStrings(too_long_name[0..KSYM_NAME_LEN], parsed.items[0].name);
}

test "chunked parsing bounds oversized line buffering to the current helper window" {
    const OwnedParsedSymbol = struct {
        name: []u8,
        symbol_type: u8,
        start: u64,

        fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
            allocator.free(self.name);
            self.* = undefined;
        }
    };

    var backing_buffer: [2048]u8 = undefined;
    var fixed_buffer = std.heap.FixedBufferAllocator.init(&backing_buffer);
    const allocator = fixed_buffer.allocator();

    const Collector = struct {
        list: *std.ArrayList(OwnedParsedSymbol),
        allocator: std.mem.Allocator,

        fn append(self: *@This(), symbol: ParsedSymbol) !void {
            try self.list.append(self.allocator, .{
                .name = try self.allocator.dupe(u8, symbol.name),
                .symbol_type = symbol.symbol_type,
                .start = symbol.start,
            });
        }
    };

    const too_long_name = "a" ** (KSYM_NAME_LEN + 2048);
    const first_chunk = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name[0..100]});
    defer std.testing.allocator.free(first_chunk);
    const second_chunk = try std.fmt.allocPrint(std.testing.allocator, "{s}\n2 t done\n", .{too_long_name[100..]});
    defer std.testing.allocator.free(second_chunk);

    var state = ChunkFixtureState{ .chunks = &.{ first_chunk, second_chunk } };
    var parsed = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (parsed.items) |*symbol| symbol.deinit(allocator);
        parsed.deinit(allocator);
    }

    var collector = Collector{ .list = &parsed, .allocator = allocator };
    try forEachParsedChunked(allocator, &state, nextFixtureChunk, &collector, Collector.append);
    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqualStrings(too_long_name[0..KSYM_NAME_LEN], parsed.items[0].name);
    try std.testing.expectEqualStrings("done", parsed.items[1].name);
}

test "reader, path, and callback wrappers normalize carriage returns before newline" {
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

    const contents =
        "ffffffff81000000 T startup_64\r\n" ++
        "ffffffff81000200 W weak_handler\r\n";

    var reader = SliceReader{ .bytes = contents };
    var scratch_buffer: [8]u8 = undefined;
    var parsed = std.ArrayList(OwnedParsedSymbol).empty;
    defer {
        for (parsed.items) |*symbol| symbol.deinit(std.testing.allocator);
        parsed.deinit(std.testing.allocator);
    }

    try forEachParsedReader(std.testing.allocator, &reader, &scratch_buffer, &parsed, Collector.append);
    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
    try std.testing.expectEqualStrings("weak_handler", parsed.items[1].name);

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

    for (parsed.items) |*symbol| symbol.deinit(std.testing.allocator);
    parsed.clearRetainingCapacity();
    try forEachParsedPath(
        std.testing.allocator,
        io,
        temp_dir.dir,
        "kallsyms.map",
        &scratch_buffer,
        &parsed,
        Collector.append,
    );
    try std.testing.expectEqual(@as(usize, 2), parsed.items.len);
    try std.testing.expectEqualStrings("startup_64", parsed.items[0].name);
    try std.testing.expectEqualStrings("weak_handler", parsed.items[1].name);

    const CallbackStateForTest = struct {
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
            for (self.names.items) |name| allocator.free(name);
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
            if (symbol_type == 'W') return 23;
            return 0;
        }
    };

    var callback_state = CallbackStateForTest.init();
    defer callback_state.deinit(std.testing.allocator);
    const result = try kallsymsParse(
        std.testing.allocator,
        io,
        temp_dir.dir,
        "kallsyms.map",
        &callback_state,
        CallbackStateForTest.collect,
    );
    try std.testing.expectEqual(@as(i32, 23), result);
    try std.testing.expectEqual(@as(usize, 2), callback_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", callback_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", callback_state.names.items[1]);
}
