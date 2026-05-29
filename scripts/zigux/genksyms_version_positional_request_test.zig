const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.ExpectedRequestCommand,
    };
}

test "pure version flags become request when positional input is present" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "module_input.c",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
    try testing.expectEqualStrings("-VV", request.rendered_args[0]);
    try testing.expectEqualStrings("module_input.c", request.rendered_args[1]);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
}

test "positional input before long version keeps the invocation in request mode" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "module_input.c",
        "--version",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("module_input.c", request.rendered_args[1]);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
}

test "positional input does not hide later parsed request options after version" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--ver",
        "-d",
        "-r",
        "symbols.symref",
        "rightover.h",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("symbols.symref", request.reference_files[0]);
    try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
    try testing.expectEqualStrings("--ver", request.rendered_args[0]);
    try testing.expectEqualStrings("-d", request.rendered_args[1]);
    try testing.expectEqualStrings("-r", request.rendered_args[2]);
    try testing.expectEqualStrings("symbols.symref", request.rendered_args[3]);
    try testing.expectEqualStrings("leftover.c", request.rendered_args[4]);
    try testing.expectEqualStrings("rightover.h", request.rendered_args[5]);
}
