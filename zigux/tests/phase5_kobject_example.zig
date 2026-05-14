const std = @import("std");
const sample = @import("kobject_example_sample");

test "phase 5 kobject sample keeps the descriptor contract explicit through the focused test surface too" {
    const descriptor = sample.KobjectExampleSample.descriptor();

    try std.testing.expectEqualStrings("kobject_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 kobject sample keeps the anchor replay explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqualStrings("kobject_example", replay.directory_name);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 3), replay.attr_count);
    try std.testing.expect(!replay.group_is_named);
    try std.testing.expect(replay.uses_shared_b_handlers);
    try std.testing.expectEqualStrings("foo", replay.attribute_specs[0].name);
    try std.testing.expectEqualStrings("baz", replay.attribute_specs[1].name);
    try std.testing.expectEqualStrings("bar", replay.attribute_specs[2].name);
    try std.testing.expectEqual(@as(u16, 0o664), replay.attribute_specs[0].mode);
    try std.testing.expect(replay.attribute_specs[1].uses_shared_b_handlers);
    try std.testing.expect(replay.attribute_specs[2].uses_shared_b_handlers);
    try std.testing.expectEqualStrings("42\n", replay.foo_value.text[0..replay.foo_value.len]);
    try std.testing.expectEqualStrings("7\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("-5\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expectEqual(@as(usize, 5), replay.checked_focus.len);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
}

test "phase 5 kobject sample keeps the pre-registration boundary explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runPreRegistrationBoundaryReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_boundary_checks);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_boundary_checks);
    try std.testing.expectEqual(@as(usize, 0), replay.active_attr_count);
    try std.testing.expect(replay.rejected_show);
    try std.testing.expect(replay.rejected_store);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
}

test "phase 5 kobject sample keeps the sample-owned single-init boundary replay explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runSingleInitBoundaryReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_second_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_second_init);
    try std.testing.expectEqual(@as(usize, 0), replay.active_attr_count);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_runs);
    try std.testing.expect(replay.rejected_second_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());

    const summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.initialized, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.active_attr_count);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.register_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
}

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

test "phase 5 kobject sample keeps the already-registered boundary explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runRegisteredBoundaryReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_before_boundary_checks);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.stage_after_boundary_checks);
    try std.testing.expectEqual(@as(usize, 3), replay.active_attr_count);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_runs);
    try std.testing.expect(replay.rejected_duplicate_registration);
    try std.testing.expect(replay.rejected_registered_anchor_replay);
    try std.testing.expectEqual(@as(usize, 3), replay.post_rejection_store_len);
    try std.testing.expectEqualStrings("foo", replay.post_rejection_show.attr_name);
    try std.testing.expectEqualStrings("11\n", replay.post_rejection_show.text[0..replay.post_rejection_show.len]);
    try std.testing.expectEqual(sample.SampleStage.registered, module.stage());
}

test "phase 5 kobject sample initialized-only exit abandonment stays explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    try module.init();

    const exit_summary = try module.exit();
    try std.testing.expectEqual(sample.ExitDisposition.abandoned_before_registration, exit_summary.disposition);
    try std.testing.expectEqual(sample.SampleStage.initialized, exit_summary.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, exit_summary.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 0), exit_summary.cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 1), exit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), exit_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 1), exit_summary.exit_runs);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());

    const summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.exited, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.active_attr_count);
}

test "phase 5 kobject sample ownership replay stays explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
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
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[1].init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[2].init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[2].register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].exit_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].exit_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[2].exit_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].exit_runs);
    try std.testing.expectEqual(false, replay.replay_readiness[0]);
    try std.testing.expectEqual(true, replay.replay_readiness[1]);
    try std.testing.expectEqual(false, replay.replay_readiness[2]);
    try std.testing.expectEqual(false, replay.replay_readiness[3]);
    try std.testing.expectEqual(sample.ExitDisposition.abandoned_before_registration, replay.initialized_exit.disposition);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.initialized_exit.stage_before_exit);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized_exit.cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 1), replay.initialized_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.initialized_exit.exit_runs);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, replay.registered_exit.disposition);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.registered_exit.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.registered_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.registered_exit.cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.exit_runs);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
}

test "phase 5 kobject sample registered teardown replay stays explicit through the focused test surface too" {
    var module = sample.KobjectExampleSample{};
    const replay = try module.runTeardownReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(sample.ExitDisposition.tore_down_registered_attributes, replay.exit_summary.disposition);
    try std.testing.expectEqual(sample.SampleStage.registered, replay.exit_summary.stage_before_exit);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.exit_summary.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.exit_summary.cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.exit_runs);
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
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
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
