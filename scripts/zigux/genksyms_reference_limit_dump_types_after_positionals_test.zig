const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "reference limit ignores interleaved dump-types after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "pre.c",
        "--version",
        "--dump-types",
        "early.types",
        "-r",
        "01.symref",
        "-Tinline-a.types",
        "--reference=02.symref",
        "--dump-types=middle.types",
        "-r03.symref",
        "--reference",
        "04.symref",
        "-T",
        "late.types",
        "-r05.symref",
        "-r06.symref",
        "-r07.symref",
        "-r08.symref",
        "-r09.symref",
        "-r10.symref",
        "-r11.symref",
        "-r12.symref",
        "-r13.symref",
        "-r14.symref",
        "-r15.symref",
        "-r16.symref",
        "--dump-types=final.types",
        "post.h",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "--dump-types",
        "early.types",
        "-r",
        "01.symref",
        "-Tinline-a.types",
        "--reference=02.symref",
        "--dump-types=middle.types",
        "-r03.symref",
        "--reference",
        "04.symref",
        "-T",
        "late.types",
        "-r05.symref",
        "-r06.symref",
        "-r07.symref",
        "-r08.symref",
        "-r09.symref",
        "-r10.symref",
        "-r11.symref",
        "-r12.symref",
        "-r13.symref",
        "-r14.symref",
        "-r15.symref",
        "-r16.symref",
        "--dump-types=final.types",
        "pre.c",
        "post.h",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 16), request.reference_files.len);
                try testing.expectEqualStrings("01.symref", request.reference_files[0]);
                try testing.expectEqualStrings("02.symref", request.reference_files[1]);
                try testing.expectEqualStrings("16.symref", request.reference_files[15]);
                try testing.expectEqualStrings("final.types", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"dump_types_file\":\"final.types\""));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"reference_files\":[\"01.symref\",\"02.symref\""));
                try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"post.h\"]"));
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "seventeenth reference fails even when dump-types was overwritten after positionals" {
    const args = [_][]const u8{
        "pre.c",
        "-V",
        "--dump-types",
        "first.types",
        "-r01.symref",
        "-Tsecond.types",
        "-r02.symref",
        "-r03.symref",
        "-r04.symref",
        "-r05.symref",
        "-r06.symref",
        "-r07.symref",
        "-r08.symref",
        "-r09.symref",
        "-r10.symref",
        "-r11.symref",
        "-r12.symref",
        "-r13.symref",
        "-r14.symref",
        "-r15.symref",
        "-r16.symref",
        "-T",
        "last-before-fail.types",
        "--reference=17.symref",
        "--dump-types",
        "unreached.types",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            try testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedReferenceLimitFailure,
    }
}
