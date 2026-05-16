const std = @import("std");
const sample = @import("kobject_example_sample");

test "phase 5 kobject sample keeps the registration ownership replay explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runRegistrationOwnershipReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_before_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_register);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_register);
    try std.testing.expectEqual(@as(usize, 0), replay.active_attr_count_before_register);
    try std.testing.expectEqual(@as(usize, 3), replay.active_attr_count_after_register);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_runs);
    try std.testing.expect(replay.rejected_registration_before_init);
    try std.testing.expect(replay.rejected_duplicate_registration);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
}
