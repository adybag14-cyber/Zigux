const std = @import("std");
const kallsyms = @import("kallsyms");

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
        \\ffffffff81000000 T startup_64
        \\garbage
        \\ffffffff81000200 W weak_handler
        \
    ,
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
