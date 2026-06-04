const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "genksyms bridge escapes newline and tab bytes in rendered JSON data" {
    const rendered_args = [_][]const u8{
        "-d",
        "line\narg",
        "--",
        "tab\targ",
    };
    const reference_files = [_][]const u8{
        "refs\nfirst.symref",
        "refs\tsecond.symref",
    };
    const request = genksyms.Request{
        .raw_args = &rendered_args,
        .rendered_args = &rendered_args,
        .debug_level = 1,
        .warnings = false,
        .dump_defs = false,
        .preserve = false,
        .reference_files = &reference_files,
        .dump_types_file = "types\nand\ttabs.symtypes",
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    const rendered = output.written();

    try testing.expect(std.mem.indexOfScalar(u8, rendered, '\n') == rendered.len - 1);
    try testing.expect(std.mem.indexOfScalar(u8, rendered[0 .. rendered.len - 1], '\n') == null);
    try testing.expect(std.mem.indexOfScalar(u8, rendered, '\t') == null);
    try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "line\\narg"));
    try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "tab\\targ"));
    try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "refs\\nfirst.symref"));
    try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "refs\\tsecond.symref"));
    try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "types\\nand\\ttabs.symtypes"));

    var parsed = try std.json.parseFromSlice(std.json.Value, testing.allocator, rendered, .{});
    defer parsed.deinit();

    const root = parsed.value.object;
    const argv = root.get("argv").?.array.items;
    try testing.expectEqualStrings("line\narg", argv[2].string);
    try testing.expectEqualStrings("tab\targ", argv[4].string);

    const options = root.get("options").?.object;
    const refs = options.get("reference_files").?.array.items;
    try testing.expectEqualStrings("refs\nfirst.symref", refs[0].string);
    try testing.expectEqualStrings("refs\tsecond.symref", refs[1].string);
    try testing.expectEqualStrings("types\nand\ttabs.symtypes", options.get("dump_types_file").?.string);
}
