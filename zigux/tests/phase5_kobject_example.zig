const std = @import("std");
const sample = @import("kobject_example_sample");

test "phase 5 kobject sample keeps shared attribute dispatch and parse failures explicit through a sample-owned replay" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runInputValidationReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_before_validation_checks);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_validation_checks);
    try std.testing.expectEqual(@as(usize, 2), replay.baz_store_len);
    try std.testing.expectEqual(@as(usize, 3), replay.bar_store_len);
    try std.testing.expectEqualStrings("9\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("10\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expectEqualStrings("0\n", replay.foo_value_after_invalid_integer.text[0..replay.foo_value_after_invalid_integer.len]);
    try std.testing.expect(replay.rejected_invalid_integer);
    try std.testing.expect(replay.rejected_unknown_store);
    try std.testing.expect(replay.rejected_unknown_show);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
}

test "phase 5 kobject sample still exposes direct parse failures on the public sample surface" {
    var module = sample.KobjectExampleSample{};
    try module.init();
    try module.registerAttributes();

    try std.testing.expectEqual(@as(usize, 2), try module.storeValue("baz", "9\n"));
    try std.testing.expectEqual(@as(usize, 3), try module.storeValue("bar", "10\n"));
    try std.testing.expectEqualStrings("9\n", (try module.showValue("baz")).text[0..2]);
    try std.testing.expectEqualStrings("10\n", (try module.showValue("bar")).text[0..3]);
    try std.testing.expectError(error.InvalidInteger, module.storeValue("foo", "abc\n"));
    try std.testing.expectError(error.UnknownAttribute, module.storeValue("qux", "1\n"));
    try std.testing.expectError(error.UnknownAttribute, module.showValue("qux"));
}
