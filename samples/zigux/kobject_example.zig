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
    reviewable_non_sysfs_scope,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const AttributeSpec = struct {
    name: []const u8,
    mode: u16,
    uses_shared_b_handlers: bool,
};

pub const RenderedAttribute = struct {
    attr_name: []const u8,
    text: [16]u8,
    len: usize,
};

pub const OwnershipSummary = struct {
    stage: SampleStage,
    active_attr_count: usize,
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
};

pub const ExitDisposition = enum {
    abandoned_before_registration,
    tore_down_registered_attributes,
};

pub const ExitSummary = struct {
    disposition: ExitDisposition,
    stage_before_exit: SampleStage,
    stage_after_exit: SampleStage,
    cleared_attr_count: usize,
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
};

pub const OwnershipReplaySummary = struct {
    anchor: []const u8,
    stage_snapshots: [4]OwnershipSummary,
    replay_readiness: [4]bool,
    initialized_exit: ExitSummary,
    registered_exit: ExitSummary,
};

pub const RegisteredBoundarySummary = struct {
    anchor: []const u8,
    stage_before_boundary_checks: SampleStage,
    stage_after_boundary_checks: SampleStage,
    active_attr_count: usize,
    rejected_duplicate_registration: bool,
    rejected_registered_anchor_replay: bool,
};

pub const AttributeValues = struct {
    foo: i32,
    baz: i32,
    bar: i32,
};

pub const TeardownReplaySummary = struct {
    anchor: []const u8,
    exit_summary: ExitSummary,
    values_before_exit: AttributeValues,
    values_after_exit: AttributeValues,
    active_attr_count_after_exit: usize,
    rejected_reinit: bool,
    rejected_reregister: bool,
    rejected_show: bool,
    rejected_store: bool,
    rejected_second_exit: bool,
    rejected_anchor_replay: bool,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    directory_name: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    attr_count: usize,
    group_is_named: bool,
    uses_shared_b_handlers: bool,
    attribute_specs: [3]AttributeSpec,
    foo_value: RenderedAttribute,
    baz_value: RenderedAttribute,
    bar_value: RenderedAttribute,
    checked_focus: []const SampleFocus,
};

const Attribute = enum {
    foo,
    baz,
    bar,
};

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
            .{ .name = "foo", .mode = 0o664, .uses_shared_b_handlers = false },
            .{ .name = "baz", .mode = 0o664, .uses_shared_b_handlers = true },
            .{ .name = "bar", .mode = 0o664, .uses_shared_b_handlers = true },
        };
    }

    pub fn attrNames() [3][]const u8 {
        const specs = attributeSpecs();
        return .{ specs[0].name, specs[1].name, specs[2].name };
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

    pub fn ownershipSummary(self: *const Self) OwnershipSummary {
        return .{
            .stage = self.stage(),
            .active_attr_count = self.activeAttrCount(),
            .init_runs = self.init_runs,
            .register_runs = self.register_runs,
            .exit_runs = self.exit_runs,
        };
    }

    fn valueSnapshot(self: *const Self) AttributeValues {
        return .{
            .foo = self.foo,
            .baz = self.baz,
            .bar = self.bar,
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

    fn rejectedLifecycleTransition(result: anytype) bool {
        if (result) |_| {
            return false;
        } else |err| {
            return err == error.InvalidLifecycleTransition;
        }
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

    pub fn runOwnershipReplay(self: *Self) !OwnershipReplaySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        const cold_summary = self.ownershipSummary();
        try self.init();
        const initialized_summary = self.ownershipSummary();

        var initialized_exit_sample = KobjectExampleSample{};
        try initialized_exit_sample.init();
        const initialized_exit = try initialized_exit_sample.exit();

        try self.registerAttributes();
        const registered_summary = self.ownershipSummary();
        const registered_exit = try self.exit();
        const exited_summary = self.ownershipSummary();

        return .{
            .anchor = descriptor().anchor,
            .stage_snapshots = .{ cold_summary, initialized_summary, registered_summary, exited_summary },
            .replay_readiness = .{ false, true, false, false },
            .initialized_exit = initialized_exit,
            .registered_exit = registered_exit,
        };
    }

    pub fn runRegisteredBoundaryReplay(self: *Self) !RegisteredBoundarySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.init();
        try self.registerAttributes();
        const stage_before_checks = self.stage();
        const rejected_duplicate_registration = rejectedLifecycleTransition(self.registerAttributes());
        const rejected_registered_anchor_replay = rejectedLifecycleTransition(self.runAnchorReplay());

        return .{
            .anchor = descriptor().anchor,
            .stage_before_boundary_checks = stage_before_checks,
            .stage_after_boundary_checks = self.stage(),
            .active_attr_count = self.activeAttrCount(),
            .rejected_duplicate_registration = rejected_duplicate_registration,
            .rejected_registered_anchor_replay = rejected_registered_anchor_replay,
        };
    }

    pub fn runTeardownReplay(self: *Self) !TeardownReplaySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.init();
        try self.registerAttributes();
        _ = try self.storeValue("foo", "42\n");
        _ = try self.storeValue("baz", "7\n");
        _ = try self.storeValue("bar", "-5\n");

        const values_before_exit = self.valueSnapshot();
        const exit_summary = try self.exit();

        return .{
            .anchor = descriptor().anchor,
            .exit_summary = exit_summary,
            .values_before_exit = values_before_exit,
            .values_after_exit = self.valueSnapshot(),
            .active_attr_count_after_exit = self.activeAttrCount(),
            .rejected_reinit = rejectedLifecycleTransition(self.init()),
            .rejected_reregister = rejectedLifecycleTransition(self.registerAttributes()),
            .rejected_show = rejectedLifecycleTransition(self.showValue("foo")),
            .rejected_store = rejectedLifecycleTransition(self.storeValue("foo", "1\n")),
            .rejected_second_exit = rejectedLifecycleTransition(self.exit()),
            .rejected_anchor_replay = rejectedLifecycleTransition(self.runAnchorReplay()),
        };
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
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .attr_count = self.activeAttrCount(),
            .group_is_named = false,
            .uses_shared_b_handlers = true,
            .attribute_specs = attributeSpecs(),
            .foo_value = try self.showValue("foo"),
            .baz_value = try self.showValue("baz"),
            .bar_value = try self.showValue("bar"),
            .checked_focus = &.{
                .bounded_attribute_roundtrip,
                .shared_attribute_dispatch,
                .ownership_and_lifetime,
                .parse_error_visibility,
                .reviewable_non_sysfs_scope,
            },
        };
    }

    pub fn exit(self: *Self) !ExitSummary {
        const previous_stage = self.stage();
        const disposition = switch (previous_stage) {
            .initialized => ExitDisposition.abandoned_before_registration,
            .registered => ExitDisposition.tore_down_registered_attributes,
            else => return error.InvalidLifecycleTransition,
        };
        const cleared_attr_count = self.activeAttrCount();

        self.foo = 0;
        self.baz = 0;
        self.bar = 0;
        self.exit_runs += 1;
        self.stage_state = .exited;

        return .{
            .disposition = disposition,
            .stage_before_exit = previous_stage,
            .stage_after_exit = self.stage(),
            .cleared_attr_count = cleared_attr_count,
            .init_runs = self.init_runs,
            .register_runs = self.register_runs,
            .exit_runs = self.exit_runs,
        };
    }
};

test "kobject sample replay keeps the anchor reviewable and non-runtime" {
    var sample = KobjectExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqualStrings("kobject_example", replay.directory_name);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.registered, replay.stage_after_replay);
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
}

test "kobject sample keeps attributes inaccessible until registration" {
    var sample = KobjectExampleSample{};

    try sample.init();
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.activeAttrCount());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.showValue("foo"));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.storeValue("foo", "1\n"));

    try sample.registerAttributes();
    try std.testing.expectEqual(@as(usize, 3), sample.activeAttrCount());
    _ = try sample.storeValue("foo", "1\n");
    const rendered = try sample.showValue("foo");
    try std.testing.expectEqualStrings("1\n", rendered.text[0..rendered.len]);
}

test "kobject sample keeps shared attribute dispatch and parse failures explicit" {
    var sample = KobjectExampleSample{};
    try sample.init();
    try sample.registerAttributes();

    try std.testing.expectEqual(@as(usize, 2), try sample.storeValue("baz", "9\n"));
    try std.testing.expectEqual(@as(usize, 3), try sample.storeValue("bar", "10\n"));
    try std.testing.expectEqualStrings("9\n", (try sample.showValue("baz")).text[0..2]);
    try std.testing.expectEqualStrings("10\n", (try sample.showValue("bar")).text[0..3]);
    try std.testing.expectError(error.InvalidInteger, sample.storeValue("foo", "abc\n"));
    try std.testing.expectError(error.UnknownAttribute, sample.storeValue("qux", "1\n"));
    try std.testing.expectError(error.UnknownAttribute, sample.showValue("qux"));
}

test "kobject sample ownership summary tracks lifecycle snapshots" {
    var sample = KobjectExampleSample{};

    var summary = sample.ownershipSummary();
    try std.testing.expectEqual(SampleStage.cold, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.active_attr_count);

    try sample.init();
    summary = sample.ownershipSummary();
    try std.testing.expectEqual(SampleStage.initialized, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.active_attr_count);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.register_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);

    try sample.registerAttributes();
    summary = sample.ownershipSummary();
    try std.testing.expectEqual(SampleStage.registered, summary.stage);
    try std.testing.expectEqual(@as(usize, 3), summary.active_attr_count);
    try std.testing.expectEqual(@as(usize, 1), summary.register_runs);
}

test "kobject sample ownership replay keeps lifecycle and exit cues reviewable" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runOwnershipReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(SampleStage.cold, replay.stage_snapshots[0].stage);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_snapshots[1].stage);
    try std.testing.expectEqual(SampleStage.registered, replay.stage_snapshots[2].stage);
    try std.testing.expectEqual(SampleStage.exited, replay.stage_snapshots[3].stage);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].active_attr_count);
    try std.testing.expectEqual(@as(usize, 3), replay.stage_snapshots[2].active_attr_count);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[3].active_attr_count);
    try std.testing.expectEqual(false, replay.replay_readiness[0]);
    try std.testing.expectEqual(true, replay.replay_readiness[1]);
    try std.testing.expectEqual(false, replay.replay_readiness[2]);
    try std.testing.expectEqual(false, replay.replay_readiness[3]);
    try std.testing.expectEqual(ExitDisposition.abandoned_before_registration, replay.initialized_exit.disposition);
    try std.testing.expectEqual(SampleStage.initialized, replay.initialized_exit.stage_before_exit);
    try std.testing.expectEqual(@as(usize, 0), replay.initialized_exit.register_runs);
    try std.testing.expectEqual(ExitDisposition.tore_down_registered_attributes, replay.registered_exit.disposition);
    try std.testing.expectEqual(SampleStage.registered, replay.registered_exit.stage_before_exit);
    try std.testing.expectEqual(@as(usize, 3), replay.registered_exit.cleared_attr_count);
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
}

test "kobject sample keeps already-registered lifecycle boundaries explicit" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runRegisteredBoundaryReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(SampleStage.registered, replay.stage_before_boundary_checks);
    try std.testing.expectEqual(SampleStage.registered, replay.stage_after_boundary_checks);
    try std.testing.expectEqual(@as(usize, 3), replay.active_attr_count);
    try std.testing.expect(replay.rejected_duplicate_registration);
    try std.testing.expect(replay.rejected_registered_anchor_replay);
    try std.testing.expectEqual(SampleStage.registered, sample.stage());
}

test "kobject sample initialized-only exit records abandonment" {
    var sample = KobjectExampleSample{};
    try sample.init();

    const exit_summary = try sample.exit();
    try std.testing.expectEqual(ExitDisposition.abandoned_before_registration, exit_summary.disposition);
    try std.testing.expectEqual(SampleStage.initialized, exit_summary.stage_before_exit);
    try std.testing.expectEqual(SampleStage.exited, exit_summary.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 0), exit_summary.cleared_attr_count);
    try std.testing.expectEqual(@as(usize, 1), exit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), exit_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 1), exit_summary.exit_runs);
    try std.testing.expectEqual(SampleStage.exited, sample.ownershipSummary().stage);
    try std.testing.expectEqual(@as(usize, 0), sample.ownershipSummary().active_attr_count);
}

test "kobject sample registered teardown replay keeps reset and rejection cues reviewable" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runTeardownReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqual(ExitDisposition.tore_down_registered_attributes, replay.exit_summary.disposition);
    try std.testing.expectEqual(SampleStage.registered, replay.exit_summary.stage_before_exit);
    try std.testing.expectEqual(SampleStage.exited, replay.exit_summary.stage_after_exit);
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
}
