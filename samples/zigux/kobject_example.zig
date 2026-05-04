const std = @import("std");

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    registered,
    exited,
};

pub const SampleFocus = enum {
    bounded_attribute_roundtrip,
    shared_attribute_dispatch,
    ownership_and_lifetime,
    parse_error_visibility,
    static_name_no_uevent_boundary,
    reviewable_non_sysfs_scope,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const RenderedAttribute = struct {
    attr_name: []const u8,
    text: [16]u8,
    len: usize,
};

pub const AttributeMode = u16;

pub const AttributeSpec = struct {
    name: []const u8,
    mode: AttributeMode,
    uses_shared_b_handler: bool,
};

pub const OwnershipSummary = struct {
    stage: SampleStage,
    active_attr_count: usize,
    attributes_are_accessible: bool,
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
    can_run_anchor_replay: bool,
    can_register_attributes: bool,
    can_exit: bool,
};

pub const OwnershipReplay = struct {
    cold: OwnershipSummary,
    initialized: OwnershipSummary,
    registered: OwnershipSummary,
    registered_exit: ExitSummary,
    exited: OwnershipSummary,
};

pub const InitializedExitReplay = struct {
    initialized: OwnershipSummary,
    initialized_exit: ExitSummary,
    exited: OwnershipSummary,
};

pub const PostExitRejectionReplay = struct {
    exit_summary: ExitSummary,
    exited: OwnershipSummary,
    init_rejected: bool,
    register_rejected: bool,
    anchor_replay_rejected: bool,
    initialized_exit_replay_rejected: bool,
    ownership_replay_rejected: bool,
    show_rejected: bool,
    store_rejected: bool,
    exit_rejected: bool,
};

pub const SharedDispatchReplay = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    register_runs_after_replay: usize,
    attributes_are_accessible_after_replay: bool,
    baz_store_len: usize,
    bar_store_len: usize,
    baz_value: RenderedAttribute,
    bar_value: RenderedAttribute,
    invalid_integer_visible: bool,
    unknown_store_visible: bool,
    unknown_show_visible: bool,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    directory_name: []const u8,
    ordered_attr_names: [3][]const u8,
    ordered_attr_modes: [3]AttributeMode,
    ordered_attributes: [3]AttributeSpec,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    attr_count: usize,
    attributes_are_accessible_after_replay: bool,
    register_runs_after_replay: usize,
    group_is_named: bool,
    uses_shared_b_handlers: bool,
    directory_name_is_static: bool,
    emits_uevent: bool,
    supports_dynamic_instances: bool,
    foo_value: RenderedAttribute,
    baz_value: RenderedAttribute,
    bar_value: RenderedAttribute,
    checked_focus: []const SampleFocus,
};

pub const ExitDisposition = enum {
    abandoned_before_registration,
    tore_down_registered_attributes,
};

pub const ExitSummary = struct {
    stage_before_exit: SampleStage,
    stage_after_exit: SampleStage,
    active_attr_count_before_exit: usize,
    active_attr_count_after_exit: usize,
    attributes_were_accessible: bool,
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
    disposition: ExitDisposition,
};

const Attribute = enum {
    foo,
    baz,
    bar,
};

fn sawInvalidLifecycleTransition(result: anytype) !bool {
    if (result) |_| {
        return false;
    } else |err| {
        if (err == error.InvalidLifecycleTransition) return true;
        return err;
    }
}

pub const KobjectExampleSample = struct {
    const Self = @This();

    stage_state: SampleStage = .cold,
    foo: i32 = 0,
    baz: i32 = 0,
    bar: i32 = 0,
    init_runs: usize = 0,
    register_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "kobject_example",
            .anchor = "samples/kobject/kobject-example.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn directoryName() []const u8 {
        return "kobject_example";
    }

    pub fn attributeSpecs() [3]AttributeSpec {
        return .{
            .{ .name = "foo", .mode = 0o664, .uses_shared_b_handler = false },
            .{ .name = "baz", .mode = 0o664, .uses_shared_b_handler = true },
            .{ .name = "bar", .mode = 0o664, .uses_shared_b_handler = true },
        };
    }

    pub fn attrNames() [3][]const u8 {
        const specs = attributeSpecs();
        return .{ specs[0].name, specs[1].name, specs[2].name };
    }

    pub fn attrModes() [3]AttributeMode {
        const specs = attributeSpecs();
        return .{ specs[0].mode, specs[1].mode, specs[2].mode };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn activeAttrCount(self: *const Self) usize {
        return switch (self.stage()) {
            .registered => 3,
            else => 0,
        };
    }

    pub fn attributesAreAccessible(self: *const Self) bool {
        return self.stage() == .registered;
    }

    pub fn ownershipSummary(self: *const Self) OwnershipSummary {
        const current_stage = self.stage();
        return .{
            .stage = current_stage,
            .active_attr_count = self.activeAttrCount(),
            .attributes_are_accessible = self.attributesAreAccessible(),
            .init_runs = self.init_runs,
            .register_runs = self.register_runs,
            .exit_runs = self.exit_runs,
            .can_run_anchor_replay = current_stage == .initialized,
            .can_register_attributes = current_stage == .initialized,
            .can_exit = current_stage == .initialized or current_stage == .registered,
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.foo = 0;
        self.baz = 0;
        self.bar = 0;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn registerAttributes(self: *Self) !void {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.register_runs += 1;
        self.stage_state = .registered;
    }

    fn parseAttrName(name: []const u8) !Attribute {
        if (std.mem.eql(u8, name, "foo")) return .foo;
        if (std.mem.eql(u8, name, "baz")) return .baz;
        if (std.mem.eql(u8, name, "bar")) return .bar;
        return error.UnknownAttribute;
    }

    fn valuePtr(self: *Self, attr: Attribute) *i32 {
        return switch (attr) {
            .foo => &self.foo,
            .baz => &self.baz,
            .bar => &self.bar,
        };
    }

    pub fn storeValue(self: *Self, attr_name: []const u8, input: []const u8) !usize {
        if (self.stage() != .registered) return error.InvalidLifecycleTransition;

        const attr = try parseAttrName(attr_name);
        const trimmed = std.mem.trim(u8, input, " \t\r\n");
        const parsed = std.fmt.parseInt(i32, trimmed, 10) catch return error.InvalidInteger;
        self.valuePtr(attr).* = parsed;
        return input.len;
    }

    pub fn showValue(self: *Self, attr_name: []const u8) !RenderedAttribute {
        if (self.stage() != .registered) return error.InvalidLifecycleTransition;

        const attr = try parseAttrName(attr_name);
        var rendered = RenderedAttribute{
            .attr_name = attr_name,
            .text = undefined,
            .len = 0,
        };
        const value = self.valuePtr(attr).*;
        rendered.len = (try std.fmt.bufPrint(rendered.text[0..], "{d}\n", .{value})).len;
        return rendered;
    }

    pub fn runAnchorReplay(self: *Self) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        try self.registerAttributes();
        _ = try self.storeValue("foo", "42\n");
        _ = try self.storeValue("baz", "7\n");
        _ = try self.storeValue("bar", "-5\n");

        return .{
            .anchor = descriptor().anchor,
            .directory_name = directoryName(),
            .ordered_attr_names = attrNames(),
            .ordered_attr_modes = attrModes(),
            .ordered_attributes = attributeSpecs(),
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .attr_count = self.activeAttrCount(),
            .attributes_are_accessible_after_replay = self.attributesAreAccessible(),
            .register_runs_after_replay = self.register_runs,
            .group_is_named = false,
            .uses_shared_b_handlers = true,
            .directory_name_is_static = true,
            .emits_uevent = false,
            .supports_dynamic_instances = false,
            .foo_value = try self.showValue("foo"),
            .baz_value = try self.showValue("baz"),
            .bar_value = try self.showValue("bar"),
            .checked_focus = &.{
                .bounded_attribute_roundtrip,
                .shared_attribute_dispatch,
                .ownership_and_lifetime,
                .parse_error_visibility,
                .static_name_no_uevent_boundary,
                .reviewable_non_sysfs_scope,
            },
        };
    }

    pub fn runOwnershipReplay(self: *Self) !OwnershipReplay {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        const cold = self.ownershipSummary();
        try self.init();
        const initialized = self.ownershipSummary();
        try self.registerAttributes();
        const registered = self.ownershipSummary();
        const registered_exit = try self.exit();
        const exited = self.ownershipSummary();

        return .{
            .cold = cold,
            .initialized = initialized,
            .registered = registered,
            .registered_exit = registered_exit,
            .exited = exited,
        };
    }

    pub fn runInitializedExitReplay(self: *Self) !InitializedExitReplay {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.init();
        const initialized = self.ownershipSummary();
        const initialized_exit = try self.exit();
        const exited = self.ownershipSummary();

        return .{
            .initialized = initialized,
            .initialized_exit = initialized_exit,
            .exited = exited,
        };
    }

    pub fn runPostExitRejectionReplay(self: *Self) !PostExitRejectionReplay {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.init();
        try self.registerAttributes();
        const exit_summary = try self.exit();
        const exited = self.ownershipSummary();

        return .{
            .exit_summary = exit_summary,
            .exited = exited,
            .init_rejected = try sawInvalidLifecycleTransition(self.init()),
            .register_rejected = try sawInvalidLifecycleTransition(self.registerAttributes()),
            .anchor_replay_rejected = try sawInvalidLifecycleTransition(self.runAnchorReplay()),
            .initialized_exit_replay_rejected = try sawInvalidLifecycleTransition(self.runInitializedExitReplay()),
            .ownership_replay_rejected = try sawInvalidLifecycleTransition(self.runOwnershipReplay()),
            .show_rejected = try sawInvalidLifecycleTransition(self.showValue("foo")),
            .store_rejected = try sawInvalidLifecycleTransition(self.storeValue("foo", "1\n")),
            .exit_rejected = try sawInvalidLifecycleTransition(self.exit()),
        };
    }

    pub fn runSharedDispatchReplay(self: *Self) !SharedDispatchReplay {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        const stage_before_replay = self.stage();
        try self.init();
        try self.registerAttributes();
        const baz_store_len = try self.storeValue("baz", "9\n");
        const bar_store_len = try self.storeValue("bar", "10\n");
        const baz_value = try self.showValue("baz");
        const bar_value = try self.showValue("bar");

        var invalid_integer_visible = false;
        if (self.storeValue("foo", "abc\n")) |_| {
            return error.ExpectedInvalidInteger;
        } else |err| switch (err) {
            error.InvalidInteger => invalid_integer_visible = true,
            else => return err,
        }

        var unknown_store_visible = false;
        if (self.storeValue("qux", "1\n")) |_| {
            return error.ExpectedUnknownAttribute;
        } else |err| switch (err) {
            error.UnknownAttribute => unknown_store_visible = true,
            else => return err,
        }

        var unknown_show_visible = false;
        if (self.showValue("qux")) |_| {
            return error.ExpectedUnknownAttribute;
        } else |err| switch (err) {
            error.UnknownAttribute => unknown_show_visible = true,
            else => return err,
        }

        return .{
            .stage_before_replay = stage_before_replay,
            .stage_after_replay = self.stage(),
            .register_runs_after_replay = self.register_runs,
            .attributes_are_accessible_after_replay = self.attributesAreAccessible(),
            .baz_store_len = baz_store_len,
            .bar_store_len = bar_store_len,
            .baz_value = baz_value,
            .bar_value = bar_value,
            .invalid_integer_visible = invalid_integer_visible,
            .unknown_store_visible = unknown_store_visible,
            .unknown_show_visible = unknown_show_visible,
        };
    }

    pub fn exit(self: *Self) !ExitSummary {
        const stage_before_exit = self.stage();
        const active_attr_count_before_exit = self.activeAttrCount();
        const attributes_were_accessible = self.attributesAreAccessible();
        const disposition = switch (stage_before_exit) {
            .initialized => ExitDisposition.abandoned_before_registration,
            .registered => ExitDisposition.tore_down_registered_attributes,
            else => return error.InvalidLifecycleTransition,
        };

        self.foo = 0;
        self.baz = 0;
        self.bar = 0;
        self.exit_runs += 1;
        self.stage_state = .exited;

        return .{
            .stage_before_exit = stage_before_exit,
            .stage_after_exit = self.stage(),
            .active_attr_count_before_exit = active_attr_count_before_exit,
            .active_attr_count_after_exit = self.activeAttrCount(),
            .attributes_were_accessible = attributes_were_accessible,
            .init_runs = self.init_runs,
            .register_runs = self.register_runs,
            .exit_runs = self.exit_runs,
            .disposition = disposition,
        };
    }
};

test "kobject sample replay keeps the descriptor and anchor reviewable and non-runtime" {
    const descriptor = KobjectExampleSample.descriptor();
    var sample = KobjectExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();
    const expected_focus = [_]SampleFocus{
        .bounded_attribute_roundtrip,
        .shared_attribute_dispatch,
        .ownership_and_lifetime,
        .parse_error_visibility,
        .static_name_no_uevent_boundary,
        .reviewable_non_sysfs_scope,
    };

    try std.testing.expectEqualStrings("kobject_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqualStrings("kobject_example", replay.directory_name);
    try std.testing.expectEqualStrings("foo", replay.ordered_attr_names[0]);
    try std.testing.expectEqualStrings("baz", replay.ordered_attr_names[1]);
    try std.testing.expectEqualStrings("bar", replay.ordered_attr_names[2]);
    try std.testing.expectEqual(@as(AttributeMode, 0o664), replay.ordered_attr_modes[0]);
    try std.testing.expectEqual(@as(AttributeMode, 0o664), replay.ordered_attr_modes[1]);
    try std.testing.expectEqual(@as(AttributeMode, 0o664), replay.ordered_attr_modes[2]);
    try std.testing.expectEqualStrings("foo", replay.ordered_attributes[0].name);
    try std.testing.expectEqualStrings("baz", replay.ordered_attributes[1].name);
    try std.testing.expectEqualStrings("bar", replay.ordered_attributes[2].name);
    try std.testing.expectEqual(@as(AttributeMode, 0o664), replay.ordered_attributes[0].mode);
    try std.testing.expectEqual(@as(AttributeMode, 0o664), replay.ordered_attributes[1].mode);
    try std.testing.expectEqual(@as(AttributeMode, 0o664), replay.ordered_attributes[2].mode);
    try std.testing.expect(!replay.ordered_attributes[0].uses_shared_b_handler);
    try std.testing.expect(replay.ordered_attributes[1].uses_shared_b_handler);
    try std.testing.expect(replay.ordered_attributes[2].uses_shared_b_handler);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.registered, replay.stage_after_replay);
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
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, replay.checked_focus);
}

test "kobject sample keeps shared dispatch and parse failures explicit through a sample-owned replay" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runSharedDispatchReplay();

    try std.testing.expectEqual(SampleStage.cold, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.registered, replay.stage_after_replay);
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
}

test "kobject sample keeps the pre-registration ownership boundary explicit" {
    var sample = KobjectExampleSample{};

    try std.testing.expectEqual(SampleStage.cold, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.activeAttrCount());
    try std.testing.expect(!sample.attributesAreAccessible());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.storeValue("foo", "1\n"));

    try sample.init();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.activeAttrCount());
    try std.testing.expect(!sample.attributesAreAccessible());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.storeValue("foo", "1\n"));
}

test "kobject sample makes ownership snapshots reviewable through a sample-owned replay" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runOwnershipReplay();

    try std.testing.expectEqual(SampleStage.cold, replay.cold.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.active_attr_count);
    try std.testing.expect(!replay.cold.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.cold.exit_runs);
    try std.testing.expect(!replay.cold.can_run_anchor_replay);
    try std.testing.expect(!replay.cold.can_register_attributes);
    try std.testing.expect(!replay.cold.can_exit);

    try std.testing.expectEqual(SampleStage.initialized, replay.initialized.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized.active_attr_count);
    try std.testing.expect(!replay.initialized.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized.exit_runs);
    try std.testing.expect(replay.initialized.can_run_anchor_replay);
    try std.testing.expect(replay.initialized.can_register_attributes);
    try std.testing.expect(replay.initialized.can_exit);

    try std.testing.expectEqual(SampleStage.registered, replay.registered.stage);
    try std.testing.expectEqual(@as(usize, 3), replay.registered.active_attr_count);
    try std.testing.expect(replay.registered.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.registered.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered.register_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.registered.exit_runs);
    try std.testing.expect(!replay.registered.can_run_anchor_replay);
    try std.testing.expect(!replay.registered.can_register_attributes);
    try std.testing.expect(replay.registered.can_exit);

    try std.testing.expectEqual(SampleStage.registered, replay.registered_exit.stage_before_exit);
    try std.testing.expectEqual(SampleStage.exited, replay.registered_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.registered_exit.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), replay.registered_exit.active_attr_count_after_exit);
    try std.testing.expect(replay.registered_exit.attributes_were_accessible);
    try std.testing.expectEqual(ExitDisposition.tore_down_registered_attributes, replay.registered_exit.disposition);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.registered_exit.exit_runs);

    try std.testing.expectEqual(SampleStage.exited, replay.exited.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.exited.active_attr_count);
    try std.testing.expect(!replay.exited.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exited.exit_runs);
    try std.testing.expect(!replay.exited.can_run_anchor_replay);
    try std.testing.expect(!replay.exited.can_register_attributes);
    try std.testing.expect(!replay.exited.can_exit);
}

test "kobject sample teardown keeps ownership boundaries explicit" {
    var initialized_sample = KobjectExampleSample{};
    const initialized_replay = try initialized_sample.runInitializedExitReplay();
    const initialized_exit = initialized_replay.initialized_exit;

    try std.testing.expectEqual(SampleStage.initialized, initialized_replay.initialized.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_replay.initialized.active_attr_count);
    try std.testing.expect(!initialized_replay.initialized.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), initialized_replay.initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_replay.initialized.register_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_replay.initialized.exit_runs);
    try std.testing.expect(initialized_replay.initialized.can_run_anchor_replay);
    try std.testing.expect(initialized_replay.initialized.can_register_attributes);
    try std.testing.expect(initialized_replay.initialized.can_exit);

    try std.testing.expectEqual(SampleStage.initialized, initialized_exit.stage_before_exit);
    try std.testing.expectEqual(SampleStage.exited, initialized_exit.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.active_attr_count_after_exit);
    try std.testing.expect(!initialized_exit.attributes_were_accessible);
    try std.testing.expectEqual(ExitDisposition.abandoned_before_registration, initialized_exit.disposition);
    try std.testing.expectEqual(@as(usize, 1), initialized_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_exit.exit_runs);

    try std.testing.expectEqual(SampleStage.exited, initialized_replay.exited.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_replay.exited.active_attr_count);
    try std.testing.expect(!initialized_replay.exited.attributes_are_accessible);
    try std.testing.expectEqual(@as(usize, 1), initialized_replay.exited.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_replay.exited.register_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_replay.exited.exit_runs);
    try std.testing.expect(!initialized_replay.exited.can_run_anchor_replay);
    try std.testing.expect(!initialized_replay.exited.can_register_attributes);
    try std.testing.expect(!initialized_replay.exited.can_exit);
    try std.testing.expectEqual(@as(i32, 0), initialized_sample.foo);
    try std.testing.expectEqual(@as(i32, 0), initialized_sample.baz);
    try std.testing.expectEqual(@as(i32, 0), initialized_sample.bar);
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.registerAttributes());
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.runInitializedExitReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.storeValue("foo", "1\n"));
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_sample.exit());
}

test "kobject sample keeps post-exit rejections reviewable through a sample-owned replay" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runPostExitRejectionReplay();

    try std.testing.expectEqual(SampleStage.registered, replay.exit_summary.stage_before_exit);
    try std.testing.expectEqual(SampleStage.exited, replay.exit_summary.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.exit_summary.active_attr_count_before_exit);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_summary.active_attr_count_after_exit);
    try std.testing.expect(replay.exit_summary.attributes_were_accessible);
    try std.testing.expectEqual(ExitDisposition.tore_down_registered_attributes, replay.exit_summary.disposition);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_summary.exit_runs);

    try std.testing.expectEqual(SampleStage.exited, replay.exited.stage);
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
    try std.testing.expectEqual(@as(i32, 0), sample.foo);
    try std.testing.expectEqual(@as(i32, 0), sample.baz);
    try std.testing.expectEqual(@as(i32, 0), sample.bar);
}
