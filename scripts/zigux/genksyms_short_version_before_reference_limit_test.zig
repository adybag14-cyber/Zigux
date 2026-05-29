const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "short version side effects survive reference limit failure" {
    const args = [_][]const u8{
        "-VV",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            try testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedReferenceLimitFailure,
    }
}

test "short version and reference inline cluster keeps version count before limit" {
    const args = [_][]const u8{
        "-Vr01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
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
