const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRenderedContains(rendered_args: []const []const u8, needle: []const u8) !void {
    for (rendered_args) |arg| {
        if (std.mem.eql(u8, arg, needle)) return;
    }
    return error.ExpectedRenderedArg;
}

fn terminatorIndex(rendered_args: []const []const u8) !usize {
    for (rendered_args, 0..) |arg, index| {
        if (std.mem.eql(u8, arg, "--")) return index;
    }
    return error.ExpectedTerminatorArg;
}

fn expectTerminatorTail(rendered_args: []const []const u8, expected_tail: []const []const u8) !void {
    const index = try terminatorIndex(rendered_args);
    try testing.expect(rendered_args.len >= expected_tail.len);
    const tail_start = rendered_args.len - expected_tail.len;
    try testing.expect(tail_start > index);
    for (expected_tail, rendered_args[tail_start..]) |expected, actual| {
        try testing.expectEqualStrings(expected, actual);
    }
}

test "genksyms terminator keeps mixed short clusters after positionals as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-d",
        "leftover.c",
        "--",
        "-Vd",
        "-qDp",
        "-rpost.symref",
        "-Tpost.symtypes",
        "-xV",
        "-h",
    };
    const expected_tail = [_][]const u8{
        "-Vd",
        "-qDp",
        "-rpost.symref",
        "-Tpost.symtypes",
        "-xV",
        "-h",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try expectRenderedContains(request.rendered_args, "leftover.c");
                try expectTerminatorTail(request.rendered_args, &expected_tail);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms terminator short clusters do not override pre-terminator request state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--warnings",
        "leftover.c",
        "--",
        "-qDpV",
        "-dDwp",
        "-rpost.symref",
        "-Tpost.symtypes",
    };
    const expected_tail = [_][]const u8{
        "-qDpV",
        "-dDwp",
        "-rpost.symref",
        "-Tpost.symtypes",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try expectRenderedContains(request.rendered_args, "--version");
                try expectRenderedContains(request.rendered_args, "--warnings");
                try expectRenderedContains(request.rendered_args, "leftover.c");
                try expectTerminatorTail(request.rendered_args, &expected_tail);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge renders post-terminator short clusters without request mutation" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--dump",
        "carrier.c",
        "--",
        "-qDpV",
        "-rpost.symref",
        "-Tpost.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.dump_defs);
                try testing.expect(!request.warnings);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, request);
                const rendered = output.written();

                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"--\""));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"-qDpV\""));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"-rpost.symref\""));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"-Tpost.symtypes\""));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"debug_level\":0"));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"warnings\":false"));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"dump_defs\":true"));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"preserve\":false"));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"reference_files\":[]"));
                try testing.expect(std.mem.containsAtLeast(u8, rendered, 1, "\"dump_types_file\":null"));
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
