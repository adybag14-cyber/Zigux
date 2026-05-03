const std = @import("std");
const kallsyms = @import("kallsyms");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
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

fn appendOwnedParsedSymbol(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
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

test "phase 8 kallsyms module imports cleanly" {
    _ = kallsyms;
}

test "phase 8 kallsyms chunked reader slice keeps parser behavior across split input" {
    const Collector = struct {
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
            try appendOwnedParsedSymbol(list, symbol);
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
    defer deinitOwnedParsedSymbols(&symbols);

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
}

test "phase 8 kallsyms chunked reader slice preserves callback failures across split input" {
    const Collector = struct {
        fn stopOnWeakSymbol(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) anyerror!void {
            if (symbol.symbol_type == 'W') {
                return error.StopOnWeakSymbol;
            }

            try appendOwnedParsedSymbol(list, symbol);
        }
    };

    var state = ChunkFixtureState{
        .chunks = &.{
            "ffffffff81000000 T start",
            "up_64\nffffffff81000200 W weak",
            "_handler\nffffffff81000300 t ignored_after_callback_error\n",
        },
    };

    var symbols = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&symbols);

    try std.testing.expectError(
        error.StopOnWeakSymbol,
        kallsyms.forEachParsedChunked(
            std.testing.allocator,
            &state,
            nextFixtureChunk,
            &symbols,
            Collector.stopOnWeakSymbol,
        ),
    );

    try std.testing.expectEqual(@as(usize, 1), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64", symbols.items[0].name);
    try std.testing.expectEqual(@as(u8, 'T'), symbols.items[0].symbol_type);
}

test "phase 8 kallsyms chunked reader slice discards oversized tails once the bounded callback surface is full" {
    const Collector = struct {
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
            try appendOwnedParsedSymbol(list, symbol);
        }
    };

    const oversized_name = "a" ** (kallsyms.KSYM_NAME_LEN + 400);
    const oversized_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}",
        .{oversized_name},
    );
    defer std.testing.allocator.free(oversized_line);

    const next_line = "ffffffff81000400 t next_symbol\n";
    const split_index = kallsyms.max_buffered_line_len + 27;
    var state = ChunkFixtureState{
        .chunks = &[_][]const u8{
            oversized_line[0..split_index],
            oversized_line[split_index..],
            "\n",
            next_line,
        },
    };

    var symbols = std.ArrayList(OwnedParsedSymbol).empty;
    defer deinitOwnedParsedSymbols(&symbols);

    try kallsyms.forEachParsedChunked(
        std.testing.allocator,
        &state,
        nextFixtureChunk,
        &symbols,
        Collector.append,
    );

    try std.testing.expectEqual(@as(usize, 2), symbols.items.len);
    try std.testing.expectEqual(@as(usize, kallsyms.KSYM_NAME_LEN), symbols.items[0].name.len);
    try std.testing.expect(std.mem.allEqual(u8, symbols.items[0].name, 'a'));
    try std.testing.expectEqualStrings("next_symbol", symbols.items[1].name);
    try std.testing.expectEqual(@as(u8, 't'), symbols.items[1].symbol_type);
}

test "phase 8 kallsyms thin reader and path adapters preserve the shipped parser contract" {
    const Collector = struct {
        fn append(list: *std.ArrayList(OwnedParsedSymbol), symbol: kallsyms.ParsedSymbol) !void {
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
    defer deinitOwnedParsedSymbols(&from_path);

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

test "phase 8 kallsyms direct wrappers preserve the C-shaped callback contract across contents, reader, and path entrypoints" {
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

    const contents_result = try kallsyms.kallsymsParseContents(
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

    var reader = SliceReader{ .bytes = contents };
    var reader_scratch_buffer: [13]u8 = undefined;
    var reader_state = CallbackState.init();
    defer reader_state.deinit(std.testing.allocator);

    const reader_result = try kallsyms.kallsymsParseReader(
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
        kallsyms.kallsymsParseReader(
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

    const result = try kallsyms.kallsymsParseInDir(
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

    const filename_result = try kallsyms.kallsymsParse(
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

    const missing_result = try kallsyms.kallsymsParse(
        std.testing.allocator,
        io,
        "missing-kallsyms.map",
        &missing_state,
        CallbackState.collect,
    );

    try std.testing.expectEqual(@as(i32, -1), missing_result);
    try std.testing.expectEqual(@as(usize, 0), missing_state.names.items.len);

    const too_long_name = "b" ** (kallsyms.KSYM_NAME_LEN + 21);
    const oversized_contents = try std.fmt.allocPrint(
        std.testing.allocator,
        "1 T {s}\n",
        .{too_long_name},
    );
    defer std.testing.allocator.free(oversized_contents);

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

    const oversized_result = try kallsyms.kallsymsParse(
        std.testing.allocator,
        io,
        oversized_filename,
        &oversized_state,
        CallbackState.collectWithoutStop,
    );

    try std.testing.expectEqual(@as(i32, 0), oversized_result);
    try std.testing.expectEqual(@as(usize, 1), oversized_state.names.items.len);
    try std.testing.expectEqual(@as(usize, kallsyms.KSYM_NAME_LEN), oversized_state.names.items[0].len);
    try std.testing.expect(std.mem.allEqual(u8, oversized_state.names.items[0], 'b'));
    try std.testing.expectEqual(@as(u8, 'T'), oversized_state.symbol_types.items[0]);
    try std.testing.expectEqual(@as(u64, 1), oversized_state.starts.items[0]);
}

test "phase 8 kallsyms docs keep the parked parser boundary explicit" {
    const slice_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-kallsyms-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "PHASE8_STATUS=parked");
    try expectContains(slice_note, "PHASE8_SLICE=kallsyms-parse-wrapper-parked");
    try expectContains(slice_note, "legacy validator alias: `PHASE8_SLICE=kallsyms-parse-wrapper-starter`");
    try expectContains(slice_note, "tools/lib/symbol/kallsyms.zig");
    try expectContains(slice_note, "zigux/tests/phase8_kallsyms.zig");
    try expectContains(slice_note, "zigux/tests/phase8_kallsyms_only_build.zig");
    try expectContains(slice_note, "zigux/tests/phase8_help_kallsyms_only_build.zig");
    try expectContains(slice_note, "serious repo-hosted tooling");
    try expectContains(slice_note, "helper-local `tools/lib/symbol/kallsyms.zig` tests own");
    try expectContains(slice_note, "focused `zigux/tests/phase8_kallsyms.zig` replay");
    try expectContains(slice_note, "chunked overlong-line handling");
    try expectContains(slice_note, "stops buffering after the bounded callback surface is full");
    try expectContains(slice_note, "kallsymsParseContents()");
    try expectContains(slice_note, "kallsymsParseReader()");
    try expectContains(slice_note, "kallsymsParse()");
    try expectContains(slice_note, "kallsymsParseInDir()");
    try expectContains(slice_note, "make -C zigux phase8-kallsyms-test");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all");
    try expectContains(slice_note, "does not yet claim:");
    try expectContains(slice_note, "api/io.h");
}

test "phase 8 kallsyms review checklist keeps the parked parser packet reviewable" {
    const review_checklist = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "parked Phase 8 `kallsyms` parser packet");
    try expectContains(review_checklist, "Documentation/zigux/phase8-kallsyms-slice.md");
    try expectContains(review_checklist, "zigux/tests/phase8_kallsyms.zig");
    try expectContains(review_checklist, "chunked discard-after-boundary handling");
    try expectContains(review_checklist, "`kallsyms__parse()`");
    try expectContains(review_checklist, "`api/io.h`");
}

test "phase 8 kallsyms shared help-plus-symbol shard stays reviewable" {
    const shared_build = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(shared_build);

    try expectContains(shared_build, "../../tools/lib/subcmd/help.zig");
    try expectContains(shared_build, "../../tools/lib/symbol/kallsyms.zig");
    try expectContains(shared_build, "phase8_help.zig");
    try expectContains(shared_build, "phase8_kallsyms.zig");
    try expectContains(shared_build, "phase8-help-tests");
    try expectContains(shared_build, "phase8-kallsyms-tests");
    try expectContains(shared_build, "Run focused Phase 8 help and kallsyms tests");
}

test "phase 8 kallsyms evidence still matches the live C helper anchors" {
    const kallsyms_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/symbol/kallsyms.c",
        16 * 1024,
    );
    defer std.testing.allocator.free(kallsyms_c);

    try expectContains(kallsyms_c, "u8 kallsyms2elf_type(char type)");
    try expectContains(kallsyms_c, "bool kallsyms__is_function(char symbol_type)");
    try expectContains(kallsyms_c, "static void read_to_eol(struct io *io)");
    try expectContains(kallsyms_c, "int kallsyms__parse(const char *filename, void *arg,");
    try expectContains(kallsyms_c, "io.fd = open(filename, O_RDONLY, 0);");
    try expectContains(kallsyms_c, "if (io__get_hex(&io, &start) != ' ')");
    try expectContains(kallsyms_c, "char symbol_name[KSYM_NAME_LEN + 1];");
    try expectContains(kallsyms_c, "err = process_symbol(arg, symbol_name, symbol_type, start);");
    try expectContains(kallsyms_c, "close(io.fd);");
}
