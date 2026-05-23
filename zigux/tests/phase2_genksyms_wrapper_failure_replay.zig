const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves mixed version counts before ambiguous long failures" {
    const args = [_][]const u8{
        "--version",
        "--ver",
        "--d",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try std.testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try std.testing.expectEqualStrings("--d", option),
                else => return error.ExpectedAmbiguousLongOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper replay preserves mixed version counts before invalid long failures" {
    const args = [_][]const u8{
        "--ver",
        "-V",
        "--unknown",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try std.testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try std.testing.expectEqualStrings("--unknown", option),
                else => return error.ExpectedInvalidLongOptionFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper replay preserves mixed version counts before missing short arguments" {
    const args = [_][]const u8{
        "-V",
        "--version",
        "-T",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try std.testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try std.testing.expectEqualStrings("T", option),
                else => return error.ExpectedMissingShortArgumentFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "phase2 genksyms wrapper replay preserves mixed version counts before too many reference files" {
    const args = [_][]const u8{
        "--version",
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
            try std.testing.expectEqual(@as(usize, 2), failure.version_count);
            try std.testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedFailure,
    }
}
