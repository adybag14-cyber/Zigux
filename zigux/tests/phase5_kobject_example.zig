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
    const initialized = module.ownershipSummary();
    try std.testing.expect(initialized.can_run_anchor_replay);
    const replay = try module.runAnchorReplay();
    const registered = module.ownershipSummary();
    const expected_focus = [_]sample.SampleFocus{
        .bounded_attribute_roundtrip,
        .shared_attribute_dispatch,
        .ownership_and_lifetime,
        .parse_error_visibility,
        .static_name_no_uevent_boundary,
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
    try std.testing.expectEqualStrings("foo", replay.ordered_attributes[0].name);
    try std.testing.expectEqualStrings("baz", replay.ordered_attributes[1].name);
    try std.testing.expectEqualStrings("bar", replay.ordered_attributes[2].name);
    try std.testing.expectEqual(@as(sample.AttributeMode, 0o664), replay.ordered_attributes[0].mode);
    try std.testing.expectEqual(@as(sample.AttributeMode, 0o664), replay.ordered_attributes[1].mode);
    try std.testing.expectEqual(@as(sample.AttributeMode, 0o664), replay.ordered_attributes[2].mode);
    try std.testing.expect(!replay.ordered_attributes[0].uses_shared_b_handler);
    try std.testing.expect(replay.ordered_attributes[1].uses_shared_b_handler);
    try std.testing.expect(replay.ordered_attributes[2].uses_shared_b_handler);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 3), replay.attr_count);
    try std.testing.expect(replay.attributes_are_accessible_after_replay);
    try std.testing.expectEqual(@as(usize, 1), replay.register_runs_after_replay);
    try std.testing.expect(!replay.group_is_named);
    try std.testing.expect(replay.uses_shared_b_handlers);
    try std.testing.expect(replay.directory_name_is_static);
    try std.testing.expect(!replay.emits_uevent);
    try std.testing.expect(!replay.supports_dynamic_instances);
    try std.testing.expectEqualStrings("foo", replay.foo_value.attr_name);
    try std.testing.expectEqualStrings("baz", replay.baz_value.attr_name);
    try std.testing.expectEqualStrings("bar", replay.bar_value.attr_name);
    try std.testing.expectEqualStrings("42\n", replay.foo_value.text[0..replay.foo_value.len]);
    try std.testing.expectEqualStrings("7\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("-5\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expectEqualSlices(sample.SampleFocus, &expected_focus, replay.checked_focus);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
    try std.testing.expect(!registered.can_run_anchor_replay);
    try std.testing.expect(!registered.can_register_attributes);
    try std.testing.expect(registered.can_exit);
}

test "phase 5 kobject sample keeps shared attribute dispatch and parse failures explicit" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runSharedDispatchReplay();

    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 1), replay.register_runs_after_replay);
    try std.testing.expect(replay.attributes_are_accessible_after_replay);
    try std.testing.expectEqual(@as(usize, 2), replay.baz_store_len);
    try std.testing.expectEqual(@as(usize, 3), replay.bar_store_len);
    try std.testing.expectEqualStrings("baz", replay.baz_value.attr_name);
    try std.testing.expectEqualStrings("bar", replay.bar_value.attr_name);
    try std.testing.expectEqualStrings("9\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("10\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expect(replay.invalid_integer_visible);
    try std.testing.expect(replay.unknown_store_visible);
    try std.testing.expect(replay.unknown_show_visible);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
}

test "phase 5 kobject sample makes ownership and lifetime boundaries explicit" {
    var module = sample.KobjectExampleSample{};

    const cold = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expect(!cold.can_run_anchor_replay);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));

    try module.init();
    const initialized = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expect(initialized.can_run_anchor_replay);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    var abandonment = sample.KobjectExampleSample{};
    const abandonment_replay = try abandonment.runInitializedExitReplay();
    const initialized_exit = abandonment_replay.initialized_exit;

    try std.testing.expectEqual(sample.SampleStage.initialized, abandonment_replay.initialized.stage);
    try std.testing.expectEqual(@as(usize, 0), abandonment_replay.initialized.active_attr_count);
    try std.testing.expect(!abandonment_replay.initialized.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), abandonment_replay.initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), abandonment_replay.initialized.register_runs);
    try std.testing.expectEqual(@as(usize, 0), abandonment_replay.initialized.exit_runs);
    try std.testing.expect(abandonment_replay.initialized.can_run_anchor_replay);
    try std.testing.expect(abandonment_replay.initialized.can_register_attributes);
    try std.testing.expect(abandonment_replay.initialized.can_exit);

    try std.testing.expectEqual(sample.SampleStage.initialized, initialized_exit.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, initialized_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.active_attr_count_after_exit);
    try std.testing.expect(!initialized_exit.attributes_were_accessible);
    try std.testing.expectEqual(sample.ExitDisposition.abandoned_before_registration, initialized_exit.disposition);
    try std.testing.expectEqual(@as(usize, 1), initialized_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_exit.exit_runs);

    try std.testing.expectEqual(sample.SampleStage.exited, abandonment_replay.exited.stage);
    try std.testing.expectEqual(@as(usize, 0), abandonment_replay.exited.active_attr_count);
    try std.testing.expect(!abandonment_replay.exited.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), abandonment_replay.exited.init_runs);
    try std.testing.expectEqual(@as(usize, 0), abandonment_replay.exited.register_runs);
    try std.testing.expectEqual(@as(usize, 1), abandonment_replay.exited.exit_runs);
    try std.testing.expect(!abandonment_replay.exited.can_run_anchor_replay);
    try std.testing.expect(!abandonment_replay.exited.can_register_attributes);
    try std.testing.expect(!abandonment_replay.exited.can_exit);
    try std.testing.expectEqual(@as(i32, 0), abandonment.foo);
    try std.testing.expectEqual(@as(i32, 0), abandonment.baz);
    try std.testing.expectEqual(@as(i32, 0), abandonment.bar);
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.runInitializedExitReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, abandonment.exit());
}

test "phase 5 kobject sample records sample-owned lifecycle replay explicitly" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runOwnershipReplay();

    try std.testing.expectEqual(sample.SampleStage.cold, replay.cold.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.active_attr_count);
    try std.testing.expect(!replay.cold.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.exit_runs);
    try std.testing.expect(!replay.cold.can_run_anchor_replay);
    try std.testing.expect(!replay.cold.can_register_attributes);
    try std.testing.expect(!replay.cold.can_exit);

    try std.testing.expectEqual(sample.SampleStage.initialized, replay.initialized.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized.active_attr_count);
    try std.testing.expect(!replay.initialized.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized.exit_runs);
    try std.testing.expect(replay.initialized.can_run_anchor_replay);
    try std.testing.expect(replay.initialized.can_register_attributes);
    try std.testing.expect(replay.initialized.can_exit);

    try std.testing.expectEqual(sample.SampleStage.registered, replay.registered.stage);
    try std.testing.expectEqual(@as(usize, 3), replay.registered.active_attr_count);
    try std.testing.expect(replay.registered.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.registered.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.registered.exit_runs);
    try std.testing.expect(!replay.registered.can_run_anchor_replay);
    try std.testing.expect(!replay.registered.can_register_attributes);
    try std.testing.expect(replay.registered.can_exit);

    try std.testing.expectEqual(sample.SampleStage.registered, replay.registered_exit.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.registered_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.registered_exit.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), replay.registered_exit.active_attr_count_after_exit);
    try std.testing.expect(replay.registered_exit.attributes_were_accessible);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, replay.registered_exit.disposition);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.exit_runs);

    try std.testing.expectEqual(sample.SampleStage.exited, replay.exited.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.exited.active_attr_count);
    try std.testing.expect(!replay.exited.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.exit_runs);
    try std.testing.expect(!replay.exited.can_run_anchor_replay);
    try std.testing.expect(!replay.exited.can_register_attributes);
    try std.testing.expect(!replay.exited.can_exit);

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
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "phase 5 kobject sample keeps post-exit rejections reviewable through a sample-owned replay" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runPostExitRejectionReplay();

    try std.testing.expectEqual(sample.SampleStage.registered, replay.exit_summary.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.exit_summary.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.exit_summary.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_summary.active_attr_count_after_exit);
    try std.testing.expect(replay.exit_summary.attributes_were_accessible);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, replay.exit_summary.disposition);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.exit_runs);

    try std.testing.expectEqual(sample.SampleStage.exited, replay.exited.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.exited.active_attr_count);
    try std.testing.expect(!replay.exited.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.exit_runs);
    try std.testing.expect(!replay.exited.can_run_anchor_replay);
    try std.testing.expect(!replay.exited.can_register_attributes);
    try std.testing.expect(!replay.exited.can_exit);
    try std.testing.expect(replay.init_rejected);
    try std.testing.expect(replay.register_rejected);
    try std.testing.expect(replay.anchor_replay_rejected);
    try std.testing.expect(replay.initialized_exit_replay_rejected);
    try std.testing.expect(replay.ownership_replay_rejected);
    try std.testing.expect(replay.show_rejected);
    try std.testing.expect(replay.store_rejected);
    try std.testing.expect(replay.exit_rejected);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expect(!module.attributesAreAccessible());
    try std.testing.expectEqual(@as(usize, 0), module.activeAttrCount());
    try std.testing.expectEqual(@as(i32, 0), module.foo);
    try std.testing.expectEqual(@as(i32, 0), module.baz);
    try std.testing.expectEqual(@as(i32, 0), module.bar);
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.register_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
}
