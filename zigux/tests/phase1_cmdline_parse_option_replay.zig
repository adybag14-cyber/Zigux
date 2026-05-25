const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 parseOptionStr replay keeps exact token boundaries" {
    try std.testing.expect(cmdline.parseOptionStr("alpha,beta,gamma", "alpha"));
    try std.testing.expect(cmdline.parseOptionStr("alpha,beta,gamma", "gamma"));
    try std.testing.expect(cmdline.parseOptionStr("alpha,beta\x00gamma", "beta"));

    try std.testing.expect(!cmdline.parseOptionStr("alpha,beta,gamma", "alp"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,beta,gamma", "bet"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,beta,gamma", "gamma,delta"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,beta=1,gamma", "beta"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,beta\x00gamma", "gamma"));
    try std.testing.expect(cmdline.parse_option_str("alpha,beta,gamma", "beta"));
}

test "phase1 parseOptionStr replay limits empty matches to comma-bounded gaps" {
    try std.testing.expect(cmdline.parseOptionStr(",alpha", ""));
    try std.testing.expect(cmdline.parseOptionStr("alpha,,beta", ""));
    try std.testing.expect(cmdline.parseOptionStr("alpha,,,beta", ""));

    try std.testing.expect(!cmdline.parseOptionStr("alpha,\x00beta", ""));
    try std.testing.expect(!cmdline.parseOptionStr("\x00,alpha", ""));
    try std.testing.expect(!cmdline.parseOptionStr("alpha", ""));
    try std.testing.expect(!cmdline.parse_option_str("alpha,\x00beta", ""));
}