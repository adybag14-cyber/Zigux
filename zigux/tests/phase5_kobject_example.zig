const std = @import("std");
const sample = @import("kobject_example_sample");

test "phase 5 kobject sample stays in the reference-sample lane" {
    const descriptor = sample.KobjectExampleSample.descriptor();

    try std.testing.expectEqualStrings("kobject_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 kobject sample replays bounded attribute registration and roundtrips" {
    var module = sample.KobjectExampleSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqualStrings("kobject_example", replay.directory_name);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 3), replay.attr_count);
    try std.testing.expect(!replay.group_is_named);
    try std.testing.expect(replay.uses_shared_b_handlers);
    try std.testing.expectEqualStrings("foo", replay.foo_value.attr_name);
    try std.testing.expectEqualStrings("42\n", replay.foo_value.text[0..replay.foo_value.len]);
    try std.testing.expectEqualStrings("7\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("-5\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expectEqual(@as(usize, 5), replay.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.bounded_attribute_roundtrip, replay.checked_focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.shared_attribute_dispatch, replay.checked_focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.ownership_and_lifetime, replay.checked_focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.parse_error_visibility, replay.checked_focus[3]);
    try std.testing.expectEqual(sample.SampleFocus.reviewable_non_sysfs_scope, replay.checked_focus[4]);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
}

test "phase 5 kobject sample keeps the ordered attribute group shape explicit" {
    const specs = sample.KobjectExampleSample.attributeSpecs();
    try std.testing.expectEqual(@as(usize, 3), specs.len);
    try std.testing.expectEqualStrings("foo", specs[0].name);
    try std.testing.expectEqualStrings("baz", specs[1].name);
    try std.testing.expectEqualStrings("bar", specs[2].name);
    try std.testing.expectEqual(@as(u16, 0o664), specs[0].mode);
    try std.testing.expectEqual(@as(u16, 0o664), specs[1].mode);
    try std.testing.expectEqual(@as(u16, 0o664), specs[2].mode);
    try std.testing.expect(!specs[0].uses_shared_b_handlers);
    try std.testing.expect(specs[1].uses_shared_b_handlers);
    try std.testing.expect(specs[2].uses_shared_b_handlers);

    var module = sample.KobjectExampleSample{};
    try module.init();
    const replay = try module.runAnchorReplay();
    try std.testing.expectEqualStrings("foo", replay.attribute_specs[0].name);
    try std.testing.expectEqualStrings("baz", replay.attribute_specs[1].name);
    try std.testing.expectEqualStrings("bar", replay.attribute_specs[2].name);
}

test "phase 5 kobject sample keeps shared attribute dispatch and parse failures explicit" {
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

test "phase 5 kobject sample makes ownership summaries and lifecycle replays explicit" {
    var module = sample.KobjectExampleSample{};

    const summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.cold, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.active_attr_count);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));

    const replay = try module.runOwnershipReplay();
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_snapshots[0].stage);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_snapshots[1].stage);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_snapshots[2].stage);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.stage_snapshots[3].stage);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].active_attr_count);
    try std.testing.expectEqual(@as(usize, 3), replay.stage_snapshots[2].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[3].active_attr_count);
    try std.testing.expectEqual(false, replay.replay_readiness[0]);
    try std.testing.expectEqual(true, replay.replay_readiness[1]);
    try std.testing.expectEqual(false, replay.replay_readiness[2]);
    try std.testing.expectEqual(false, replay.replay_readiness[3]);
    try std.testing.expectEqual(sample.ExitDisposition.abandoned_before_registration, replay.initialized_exit.disposition);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, replay.registered_exit.disposition);
    try std.testing.expectEqual(sample.SampleStage.exited, module.ownershipSummary().stage);
    try std.testing.expectEqual(@as(usize, 0), module.ownershipSummary().active_attr_count);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
}

test "phase 5 kobject sample keeps registered teardown boundary reviewable through a sample-owned replay" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runTeardownReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, replay.exit_summary.disposition);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.exit_summary.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.exit_summary.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.exit_summary.cleared_attr_count);
    try std.testing.expectEqual(@as(i32, 42), replay.values_before_exit.foo);
    try std.testing.expectEqual(@as(i32, 7), replay.values_before_exit.baz);
    try std.testing.expectEqual(@as(i32, -5), replay.values_before_exit.bar);
    try std.testing.expectEqual(@as(i32, 0), replay.values_after_exit.foo);
    try std.testing.expectEqual(@as(i32, 0), replay.values_after_exit.baz);
    try std.testing.expectEqual(@as(i32, 0), replay.values_after_exit.bar);
    try std.testing.expectEqual(@as(usize, 0), replay.active_attr_count_after_exit);
    try std.testing.expect(replay.rejected_reinit);
    try std.testing.expect(replay.rejected_reregister);
    try std.testing.expect(replay.rejected_show);
    try std.testing.expect(replay.rejected_store);
    try std.testing.expect(replay.rejected_second_exit);
    try std.testing.expect(replay.rejected_anchor_replay);
    try std.testing.expectEqual(sample.SampleStage.exited, module.ownershipSummary().stage);
    try std.testing.expectEqual(@as(usize, 0), module.ownershipSummary().active_attr_count);
}
