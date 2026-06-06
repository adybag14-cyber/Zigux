const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectRenderedContains(request: genksyms.Request, expected: []const u8) !void {
    for (request.rendered_args) |arg| {
        if (std.mem.eql(u8, expected, arg)) return;
    }
    return error.ExpectedRenderedArgument;
}

fn expectNoReferenceNamed(request: genksyms.Request, forbidden: []const u8) !void {
    for (request.reference_files) |reference| {
        try testing.expect(!std.mem.eql(u8, forbidden, reference));
    }
}

test "terminator keeps invalid long and short options after delayed positionals as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--warnings",
        "leftover.c",
        "-d",
        "--",
        "--unknown",
        "-x",
        "-Vx",
        "rightover.h",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try expectRenderedContains(request, "--");
                try expectRenderedContains(request, "leftover.c");
                try expectRenderedContains(request, "--unknown");
                try expectRenderedContains(request, "-x");
                try expectRenderedContains(request, "-Vx");
                try expectRenderedContains(request, "rightover.h");
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "terminator keeps ambiguous long option spellings after delayed positionals as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "leftover.c",
        "--reference",
        "base.symref",
        "--",
        "--d",
        "--du=tail",
        "--dump-t=tail.types",
        "--ref=tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("base.symref", request.reference_files[0]);
                try testing.expect(request.dump_types_file == null);
                try expectNoReferenceNamed(request, "tail.symref");
                try expectRenderedContains(request, "leftover.c");
                try expectRenderedContains(request, "--");
                try expectRenderedContains(request, "--d");
                try expectRenderedContains(request, "--du=tail");
                try expectRenderedContains(request, "--dump-t=tail.types");
                try expectRenderedContains(request, "--ref=tail.symref");
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "terminator bridge renders invalid ambiguous lookalikes after positionals as argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-Vd",
        "leftover.c",
        "--",
        "--unknown",
        "--d",
        "-x",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"--unknown\""));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"--d\""));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"-x\""));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"debug_level\":1"));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"reference_files\":[]"));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"dump_types_file\":null"));
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
