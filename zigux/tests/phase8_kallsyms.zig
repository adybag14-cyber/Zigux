const std = @import("std");
const kallsyms = @import("kallsyms");
const phase8_kallsyms_slice = @import("phase8_kallsyms_options").phase8_kallsyms_slice;

test "phase 8 kallsyms module imports cleanly" {
    _ = kallsyms;
}

test "phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit" {
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "PHASE8_SLICE=kallsyms-parse-wrapper-parked"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "helper-first expansion"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "output-stable tooling behavior"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "one direct `kallsymsParse()` wrapper"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "oversized symbol names now truncate to `KSYM_NAME_LEN`"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "weak-object `V` and `v` classes still follow the current C header contract"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_kallsyms_slice, 1, "make -C zigux phase8-help-kallsyms-test"));
}

test "phase 8 kallsyms direct parser truncates oversized names" {
    const parsed = kallsyms.parseLine("ffffffff81000100 t secondary_startup_64") orelse unreachable;
    try std.testing.expectEqual(@as(u64, 0xffffffff81000100), parsed.start);
    try std.testing.expectEqualStrings("secondary_startup_64", parsed.name);

    const too_long_name = "a" ** (kallsyms.KSYM_NAME_LEN + 1);
    const oversized_line = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name});
    defer std.testing.allocator.free(oversized_line);

    const truncated = kallsyms.parseLine(oversized_line) orelse unreachable;
    try std.testing.expectEqual(@as(usize, kallsyms.KSYM_NAME_LEN), truncated.name.len);
    try std.testing.expectEqualStrings(too_long_name[0..kallsyms.KSYM_NAME_LEN], truncated.name);
}

test "phase 8 kallsyms keeps weak object classes on the current header-backed path" {
    try std.testing.expectEqual(kallsyms.elf_stb_global, kallsyms.kallsyms2ElfBinding('V'));
    try std.testing.expectEqual(kallsyms.elf_stb_local, kallsyms.kallsyms2ElfBinding('v'));
    try std.testing.expectEqual(kallsyms.elf_stt_object, kallsyms.kallsyms2ElfType('V'));
    try std.testing.expectEqual(kallsyms.elf_stt_object, kallsyms.kallsyms2ElfType('v'));
    try std.testing.expect(!kallsyms.isFunction('V'));
    try std.testing.expect(!kallsyms.isFunction('v'));
}

test "phase 8 kallsyms chunked parser also truncates oversized names" {
    const ChunkFixtureState = struct {
        chunks: []const []const u8,
        index: usize = 0,
    };

    const ChunkFixture = struct {
        fn next(state: *ChunkFixtureState) anyerror!?[]const u8 {
            if (state.index >= state.chunks.len) return null;
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
        for (symbols.items) |*symbol| symbol.deinit(std.testing.allocator);
        symbols.deinit(std.testing.allocator);
    }

    try kallsyms.forEachParsedChunked(std.testing.allocator, &state, ChunkFixture.next, &symbols, Collector.append);
    try std.testing.expectEqual(@as(usize, 2), symbols.items.len);
    try std.testing.expectEqualStrings("startup_64\r", symbols.items[0].name);
    try std.testing.expectEqualStrings("weak_tail", symbols.items[1].name);

    for (symbols.items) |*symbol| symbol.deinit(std.testing.allocator);
    symbols.clearRetainingCapacity();

    const too_long_name = "a" ** (kallsyms.KSYM_NAME_LEN + 21);
    const first_chunk = try std.fmt.allocPrint(std.testing.allocator, "1 T {s}", .{too_long_name[0..40]});
    defer std.testing.allocator.free(first_chunk);
    const second_chunk = try std.fmt.allocPrint(std.testing.allocator, "{s}\n", .{too_long_name[40..]});
    defer std.testing.allocator.free(second_chunk);
    var oversized_state = ChunkFixtureState{ .chunks = &.{ first_chunk, second_chunk } };
    try kallsyms.forEachParsedChunked(std.testing.allocator, &oversized_state, ChunkFixture.next, &symbols, Collector.append);
    try std.testing.expectEqual(@as(usize, 1), symbols.items.len);
    try std.testing.expectEqualStrings(too_long_name[0..kallsyms.KSYM_NAME_LEN], symbols.items[0].name);
}

test "phase 8 kallsyms segmented reader bubbles callback failures unchanged" {
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

    const ErroringState = struct {
        seen: usize = 0,
    };

    const ErroringCollector = struct {
        fn collect(state: *ErroringState, symbol: kallsyms.ParsedSymbol) !void {
            state.seen += 1;
            if (std.mem.eql(u8, symbol.name, "weak_handler")) {
                return error.DownstreamParserConsumerFailed;
            }
        }
    };

    const contents =
        "ffffffff81000000 T startup_64\n" ++
        "ffffffff81000200 W weak_handler\n";
    var reader = SliceReader{ .bytes = contents };
    var scratch_buffer: [9]u8 = undefined;
    var state = ErroringState{};

    try std.testing.expectError(
        error.DownstreamParserConsumerFailed,
        kallsyms.forEachParsedReader(
            std.testing.allocator,
            &reader,
            &scratch_buffer,
            &state,
            ErroringCollector.collect,
        ),
    );
    try std.testing.expectEqual(@as(usize, 2), state.seen);
}

test "phase 8 kallsyms wrappers preserve the parked callback contract" {
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
        std.testing.io,
        temp_dir.dir,
        "kallsyms.map",
        &callback_state,
        CallbackState.collect,
    );
    try std.testing.expectEqual(@as(i32, 23), result);
    try std.testing.expectEqual(@as(usize, 2), callback_state.names.items.len);
    try std.testing.expectEqualStrings("startup_64", callback_state.names.items[0]);
    try std.testing.expectEqualStrings("weak_handler", callback_state.names.items[1]);
}
