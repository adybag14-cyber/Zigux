const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms bridge keeps abbreviated long flag side effects in request mode" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--deb",
        "--warn",
        "--qui",
        "--pres",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge keeps exact dump distinct from abbreviated dump-types" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--dump",
        "--dump-t=types.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge keeps abbreviated long reference argument ordering" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ref=first.symref",
        "--refer",
        "second.symref",
        "input.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.reference_files.len);
                try testing.expectEqualStrings("first.symref", request.reference_files[0]);
                try testing.expectEqualStrings("second.symref", request.reference_files[1]);
                try testing.expectEqualSlices([]const u8, &.{
                    "--ref=first.symref",
                    "--refer",
                    "second.symref",
                    "input.c",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
