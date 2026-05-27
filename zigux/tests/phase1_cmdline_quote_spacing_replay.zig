const std = @import("std");
const cmdline = @import("cmdline");

test "nextArg preserves quoted bare parameters and empty values across repeated spacing" {
    const input = "   \"flag with space\"   key=\"\"   bare   tail=\" spaced value \"";

    const first = cmdline.nextArg(input) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("flag with space", first.param);
    try std.testing.expect(first.value == null);
    try std.testing.expectEqualStrings("key=\"\"   bare   tail=\" spaced value \"", first.remaining);

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("key", second.param);
    try std.testing.expectEqualStrings("", second.value.?);
    try std.testing.expectEqualStrings("bare   tail=\" spaced value \"", second.remaining);

    const third = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("bare", third.param);
    try std.testing.expect(third.value == null);
    try std.testing.expectEqualStrings("tail=\" spaced value \"", third.remaining);

    const fourth = cmdline.nextArg(third.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("tail", fourth.param);
    try std.testing.expectEqualStrings(" spaced value ", fourth.value.?);
    try std.testing.expectEqualStrings("", fourth.remaining);
}

test "nextArg keeps fully quoted bare tokens distinct from quoted key value tokens" {
    const bare = cmdline.nextArg("   \"single token\"  rest") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("single token", bare.param);
    try std.testing.expect(bare.value == null);
    try std.testing.expectEqualStrings("rest", bare.remaining);

    const keyed = cmdline.nextArg("   \"mode=fast path\"   rest") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", keyed.param);
    try std.testing.expectEqualStrings("fast path", keyed.value.?);
    try std.testing.expectEqualStrings("rest", keyed.remaining);
}
