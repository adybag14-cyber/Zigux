const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.ExpectedRequestCommand,
    };
}

test "double dash tail preserves option-looking tokens as rendered data" {
    const args = [_][]const u8{
        "--reference=base.symref",
        "-T",
        "types.before",
        "--",
        "--reference=tail.symref",
        "--dump-types=tail.types",
        "-d",
        "symbol-after-terminator",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("base.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.before", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "terminator tail survives bridge json escaping without mutating request state" {
    const args = [_][]const u8{
        "-w",
        "--",
        "--quiet",
        "tail\nline",
        "--dump-types=after.symtypes",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(?[]const u8, null), request.dump_types_file);

    var out: std.Io.Writer.Allocating = .init(testing.allocator);
    defer out.deinit();
    try genksyms.renderGenksymsBridge(&out.writer, request);

    const rendered = out.written();
    try testing.expect(std.mem.indexOf(u8, rendered, "\"--quiet\"") != null);
    try testing.expect(std.mem.indexOf(u8, rendered, "\"tail\\nline\"") != null);
    try testing.expect(std.mem.indexOf(u8, rendered, "\"--dump-types=after.symtypes\"") != null);
    try testing.expect(std.mem.indexOf(u8, rendered, "\"dump_types_file\":null") != null);
    try testing.expect(std.mem.indexOfScalar(u8, rendered, '\n').? == rendered.len - 1);
    try testing.expect(std.mem.indexOf(u8, rendered[0 .. rendered.len - 1], "\n") == null);
}
