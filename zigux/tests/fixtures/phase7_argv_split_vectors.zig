const std = @import("std");

pub const ArgvSplitVector = struct {
    name: []const u8,
    input: []const u8,
    expected_argc: usize,
    expected_tokens: []const []const u8,
    expect_empty_storage_view: bool = false,
    expect_first_nul_truncation: bool = false,
};

pub const whitespace_tokens = [_][]const u8{
    "alpha",
    "beta",
    "gamma",
};

pub const blank_tokens = [_][]const u8{};

pub const first_nul_tokens = [_][]const u8{
    "alpha",
    "beta",
};

pub const quoted_tokens = [_][]const u8{
    "alpha",
    "\"beta",
    "gamma\"",
    "delta",
};

pub const phase7_argv_split_vectors = [_]ArgvSplitVector{
    .{
        .name = "copied_storage_whitespace_packet",
        .input = " alpha  beta\tgamma\n",
        .expected_argc = 3,
        .expected_tokens = whitespace_tokens[0..],
    },
    .{
        .name = "blank_input_reuses_empty_packet",
        .input = " \t\n",
        .expected_argc = 0,
        .expected_tokens = blank_tokens[0..],
        .expect_empty_storage_view = true,
    },
    .{
        .name = "whitespace_before_first_nul_reuses_empty_packet",
        .input = " \t\n\x00ignored tail",
        .expected_argc = 0,
        .expected_tokens = blank_tokens[0..],
        .expect_empty_storage_view = true,
    },
    .{
        .name = "first_nul_truncation_keeps_tail_outside_packet",
        .input = "alpha beta\x00ignored tail",
        .expected_argc = 2,
        .expected_tokens = first_nul_tokens[0..],
        .expect_first_nul_truncation = true,
    },
    .{
        .name = "quoted_tokens_stay_whitespace_split",
        .input = "alpha \"beta gamma\" delta",
        .expected_argc = 4,
        .expected_tokens = quoted_tokens[0..],
    },
};

test "phase 7 argv split fixture vectors stay reviewable" {
    try std.testing.expectEqual(@as(usize, 5), phase7_argv_split_vectors.len);
    try std.testing.expectEqualStrings("copied_storage_whitespace_packet", phase7_argv_split_vectors[0].name);
    try std.testing.expectEqualStrings("blank_input_reuses_empty_packet", phase7_argv_split_vectors[1].name);
    try std.testing.expectEqualStrings("whitespace_before_first_nul_reuses_empty_packet", phase7_argv_split_vectors[2].name);
    try std.testing.expectEqualStrings("first_nul_truncation_keeps_tail_outside_packet", phase7_argv_split_vectors[3].name);
    try std.testing.expectEqualStrings("quoted_tokens_stay_whitespace_split", phase7_argv_split_vectors[4].name);
    try std.testing.expect(phase7_argv_split_vectors[1].expect_empty_storage_view);
    try std.testing.expect(phase7_argv_split_vectors[2].expect_empty_storage_view);
    try std.testing.expect(phase7_argv_split_vectors[3].expect_first_nul_truncation);
    try std.testing.expectEqualStrings("gamma", phase7_argv_split_vectors[0].expected_tokens[2]);
    try std.testing.expectEqual(@as(usize, 0), phase7_argv_split_vectors[2].expected_tokens.len);
    try std.testing.expectEqualStrings("beta", phase7_argv_split_vectors[3].expected_tokens[1]);
    try std.testing.expectEqualStrings("\"beta", phase7_argv_split_vectors[4].expected_tokens[1]);
}
