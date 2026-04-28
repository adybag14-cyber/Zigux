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
    const expected_focus = [_]sample.SampleFocus{
        .bounded_attribute_roundtrip,
        .shared_attribute_dispatch,
        .ownership_and_lifetime,
        .parse_error_visibility,
        .reviewable_non_sysfs_scope,
    };

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqualStrings("kobject_example", replay.directory_name);
    try std.testing.expectEqualStrings("foo", replay.ordered_attr_names[0]);
    try std.testing.expectEqualStrings("baz", replay.ordered_attr_names[1]);
    try std.testing.expectEqualStrings("bar", replay.ordered_attr_names[2]);
    try std.testing.expectEqual(@as(sample.AttributeMode, 0o664), replay.ordered_attr_modes[0]);
    try std.testing.expectEqual(@as(sample.AttributeMode, 0o664), replay.ordered_attr_modes[1]);
    try std.testing.expectEqual(@as(sample.AttributeMode, 0o664), replay.ordered_attr_modes[2]);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 3), replay.attr_count);
    try std.testing.expect(!replay.group_is_named);
    try std.testing.expect(replay.uses_shared_b_handlers);
    try std.testing.expectEqualStrings("foo", replay.foo_value.attr_name);
    try std.testing.expectEqualStrings("baz", replay.baz_value.attr_name);
    try std.testing.expectEqualStrings("bar", replay.bar_value.attr_name);
    try std.testing.expectEqualStrings("42\n", replay.foo_value.text[0..replay.foo_value.len]);
    try std.testing.expectEqualStrings("7\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("-5\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expectEqualSlices(sample.SampleFocus, &expected_focus, replay.checked_focus);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
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

test "phase 5 kobject sample makes ownership and lifetime boundaries explicit" {
    var module = sample.KobjectExampleSample{};

    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));

    try module.init();
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    const initialized_exit = try module.exit();
    try std.testing.expectEqual(sample.SampleStage.initialized, initialized_exit.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, initialized_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.active_attr_count_after_exit);
    try std.testing.expect(!initialized_exit.attributes_were_accessible);
    try std.testing.expectEqual(sample.ExitDisposition.abandoned_before_registration, initialized_exit.disposition);
    try std.testing.expectEqual(@as(usize, 1), initialized_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_exit.exit_runs);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expectEqual(@as(i32, 0), module.foo);
    try std.testing.expectEqual(@as(i32, 0), module.baz);
    try std.testing.expectEqual(@as(i32, 0), module.bar);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "phase 5 kobject sample records registered teardown ownership explicitly" {
    var module = sample.KobjectExampleSample{};

    try module.init();
    try module.registerAttributes();
    try std.testing.expect(module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 3), module.activeAttrCount());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerAttributes());

    const registered_exit = try module.exit();
    try std.testing.expectEqual(sample.SampleStage.registered, registered_exit.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, registered_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), registered_exit.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), registered_exit.active_attr_count_after_exit);
    try std.testing.expect(registered_exit.attributes_were_accessible);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, registered_exit.disposition);
    try std.testing.expectEqual(@as(usize, 1), registered_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), registered_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), registered_exit.exit_runs);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expectEqual(@as(i32, 0), module.foo);
    try std.testing.expectEqual(@as(i32, 0), module.baz);
    try std.testing.expectEqual(@as(i32, 0), module.bar);
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.register_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}
