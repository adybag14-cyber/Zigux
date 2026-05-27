const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves version side effect before too many long reference files" {
    const args = [_][]const u8{
        "--version",
        "--reference",
        "01.symref",
        "--reference",
        "02.symref",
        "--reference",
        "03.symref",
        "--reference",
        "04.symref",
        "--reference",
        "05.symref",
        "--reference",
        "06.symref",
        "--reference",
        "07.symref",
        "--reference",
        "08.symref",
        "--reference",
        "09.symref",
        "--reference",
        "10.symref",
        "--reference",
        "11.symref",
        "--reference",
        "12.symref",
        "--reference",
        "13.symref",
        "--reference",
        "14.symref",
        "--reference",
        "15.symref",
        "--reference",
        "16.symref",
        "--reference",
        "17.symref",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try std.testing.expectEqual(@as(usize, 1), failure.version_count);
            try std.testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper replay preserves abbreviated version side effect before too many short reference files" {
    const args = [_][]const u8{
        "--ver",
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
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try std.testing.expectEqual(@as(usize, 1), failure.version_count);
            try std.testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedFailure,
    }
}
