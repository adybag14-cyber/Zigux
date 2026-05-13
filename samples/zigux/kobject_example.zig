const std = @import("std");

pub const SampleStage = enum {
    cold,
    initialized,
    registered,
    exited,
};

pub const ExitDisposition = enum {
    abandoned_before_registration,
    tore_down_registered_attributes,
};

pub const Descriptor = struct {
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

pub const RenderedValue = struct {
    attr_name: []const u8,
    text: [32]u8,
    len: usize,
};

pub const OwnershipSummary = struct {
    stage: SampleStage,
    active_attr_count: usize,
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
};

pub const ValueSnapshot = struct {
    foo: i32,
    baz: i32,
    bar: i32,
};

pub const AnchorReplay = struct {
    anchor: []const u8,
    directory_name: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    attr_count: usize,
    group_is_named: bool,
    uses_shared_b_handlers: bool,
    attribute_specs: [3]AttributeSpec,
    foo_value: RenderedValue,
    baz_value: RenderedValue,
    bar_value: RenderedValue,
    checked_focus: [5][]const u8,
};

pub const PreRegistrationBoundaryReplay = struct {
    anchor: []const u8,
    stage_before_boundary_checks: SampleStage,
    stage_after_boundary_checks: SampleStage,
    active_attr_count: usize,
    rejected_show: bool,
    rejected_store: bool,
};

pub const InputValidationReplay = struct {
    anchor: []const u8,
    stage_before_validation_checks: SampleStage,
    stage_after_validation_checks: SampleStage,
    baz_store_len: usize,
    bar_store_len: usize,
    baz_value: RenderedValue,
    bar_value: RenderedValue,
    foo_value_after_invalid_integer: RenderedValue,
    rejected_invalid_integer: bool,
    rejected_unknown_store: bool,
    rejected_unknown_show: bool,
};

pub const RegisteredBoundaryReplay = struct {
    anchor: []const u8,
    stage_before_boundary_checks: SampleStage,
    stage_after_boundary_checks: SampleStage,
    active_attr_count: usize,
    init_runs: usize,
    register_runs: usize,
    exit_runs: usize,
    rejected_duplicate_registration: bool,
    rejected_registered_anchor_replay: bool,
    post_rejection_store_len: usize,
    post_rejection_show: RenderedValue,
};

pub const OwnershipReplay = struct {
    anchor: []const u8,
    stage_snapshots: [4]OwnershipSummary,
    replay_readiness: [4]bool,
    initialized_exit: ExitSummary,
    registered_exit: ExitSummary,
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

pub const TeardownReplay = struct {
    anchor: []const u8,
    exit_summary: ExitSummary,
    values_before_exit: ValueSnapshot,
    values_after_exit: ValueSnapshot,
    active_attr_count_after_exit: usize,
    rejected_reinit: bool,
    rejected_reregister: bool,
    rejected_show: bool,
    rejected_store: bool,
    rejected_second_exit: bool,
    rejected_anchor_replay: bool,
};

pub const KobjectExampleSample = struct {
    const Self = @This();

    stage_value: SampleStage = .cold,
    active_attr_count: usize = 0,
    init_runs: usize = 0,
    register_runs: usize = 0,
    exit_runs: usize = 0,
    foo: i32 = 0,
    baz: i32 = 0,
    bar: i32 = 0,

    pub fn descriptor() Descriptor {
        return .{
            .name = "kobject_example",
            .anchor = "samples/kobject/kobject-example.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_value;
    }

    pub fn ownershipSummary(self: *const Self) OwnershipSummary {
        return .{
            .stage = self.stage_value,
            .active_attr_count = self.active_attr_count,
            .init_runs = self.init_runs,
            .register_runs = self.register_runs,
            .exit_runs = self.exit_runs,
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage_value != .cold) return error.InvalidLifecycleTransition;
        self.stage_value = .initialized;
        self.active_attr_count = 0;
        self.foo = 0;
        self.baz = 0;
        self.bar = 0;
        self.init_runs += 1;
    }

    pub fn registerAttributes(self: *Self) !void {
        if (self.stage_value != .initialized) return error.InvalidLifecycleTransition;
        self.stage_value = .registered;
        self.active_attr_count = attributeSpecs().len;
        self.register_runs += 1;
    }

    pub fn showValue(self: *Self, attr_name: []const u8) !RenderedValue {
        if (self.stage_value != .registered) return error.InvalidLifecycleTransition;
        const value = try self.valueFor(attr_name);
        return renderValue(attr_name, value);
    }

    pub fn storeValue(self: *Self, attr_name: []const u8, raw_value: []const u8) !usize {
        if (self.stage_value != .registered) return error.InvalidLifecycleTransition;
        const parsed = try parseInteger(raw_value);
        try self.assignValue(attr_name, parsed);
        return raw_value.len;
    }

    pub fn exit(self: *Self) !ExitSummary {
        return switch (self.stage_value) {
            .initialized => {
                self.stage_value = .exited;
                self.foo = 0;
                self.baz = 0;
                self.bar = 0;
                self.active_attr_count = 0;
                self.exit_runs += 1;
                return .{
                    .disposition = .abandoned_before_registration,
                    .stage_before_exit = .initialized,
                    .stage_after_exit = .exited,
                    .cleared_attr_count = 0,
                    .init_runs = self.init_runs,
                    .register_runs = self.register_runs,
                    .exit_runs = self.exit_runs,
                };
            },
            .registered => {
                self.stage_value = .exited;
                self.foo = 0;
                self.baz = 0;
                self.bar = 0;
                self.active_attr_count = 0;
                self.exit_runs += 1;
                return .{
                    .disposition = .tore_down_registered_attributes,
                    .stage_before_exit = .registered,
                    .stage_after_exit = .exited,
                    .cleared_attr_count = attributeSpecs().len,
                    .init_runs = self.init_runs,
                    .register_runs = self.register_runs,
                    .exit_runs = self.exit_runs,
                };
            },
            else => return error.InvalidLifecycleTransition,
        };
    }

    pub fn runAnchorReplay(self: *Self) !AnchorReplay {
        if (self.stage_value != .initialized) return error.InvalidLifecycleTransition;

        const before = self.stage_value;
        try self.registerAttributes();
        _ = try self.storeValue("foo", "42\n");
        _ = try self.storeValue("baz", "7\n");
        _ = try self.storeValue("bar", "-5\n");

        return .{
            .anchor = descriptor().anchor,
            .directory_name = descriptor().name,
            .stage_before_replay = before,
            .stage_after_replay = self.stage_value,
            .attr_count = self.active_attr_count,
            .group_is_named = false,
            .uses_shared_b_handlers = true,
            .attribute_specs = attributeSpecs(),
            .foo_value = try self.showValue("foo"),
            .baz_value = try self.showValue("baz"),
            .bar_value = try self.showValue("bar"),
            .checked_focus = .{
                "descriptor",
                "registration",
                "shared_b_dispatch",
                "value_roundtrip",
                "lifecycle_boundary",
            },
        };
    }

    pub fn runPreRegistrationBoundaryReplay(self: *Self) !PreRegistrationBoundaryReplay {
        self.requireColdReplayStart();
        try self.init();

        const rejected_show = blk: {
            _ = self.showValue("foo") catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_store = blk: {
            _ = self.storeValue("foo", "1\n") catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };

        return .{
            .anchor = descriptor().anchor,
            .stage_before_boundary_checks = .initialized,
            .stage_after_boundary_checks = self.stage_value,
            .active_attr_count = self.active_attr_count,
            .rejected_show = rejected_show,
            .rejected_store = rejected_store,
        };
    }

    pub fn runInputValidationReplay(self: *Self) !InputValidationReplay {
        self.requireColdReplayStart();
        try self.init();
        try self.registerAttributes();

        const baz_store_len = try self.storeValue("baz", "9\n");
        const bar_store_len = try self.storeValue("bar", "10\n");
        const baz_value = try self.showValue("baz");
        const bar_value = try self.showValue("bar");

        const rejected_invalid_integer = blk: {
            _ = self.storeValue("foo", "abc\n") catch |err| {
                if (err == error.InvalidInteger) break :blk true;
                return err;
            };
            break :blk false;
        };
        const foo_value_after_invalid_integer = try self.showValue("foo");
        const rejected_unknown_store = blk: {
            _ = self.storeValue("qux", "1\n") catch |err| {
                if (err == error.UnknownAttribute) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_unknown_show = blk: {
            _ = self.showValue("qux") catch |err| {
                if (err == error.UnknownAttribute) break :blk true;
                return err;
            };
            break :blk false;
        };

        return .{
            .anchor = descriptor().anchor,
            .stage_before_validation_checks = .registered,
            .stage_after_validation_checks = self.stage_value,
            .baz_store_len = baz_store_len,
            .bar_store_len = bar_store_len,
            .baz_value = baz_value,
            .bar_value = bar_value,
            .foo_value_after_invalid_integer = foo_value_after_invalid_integer,
            .rejected_invalid_integer = rejected_invalid_integer,
            .rejected_unknown_store = rejected_unknown_store,
            .rejected_unknown_show = rejected_unknown_show,
        };
    }

    pub fn runRegisteredBoundaryReplay(self: *Self) !RegisteredBoundaryReplay {
        self.requireColdReplayStart();
        try self.init();
        try self.registerAttributes();

        const rejected_duplicate_registration = blk: {
            self.registerAttributes() catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_registered_anchor_replay = blk: {
            _ = self.runAnchorReplay() catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const post_rejection_store_len = try self.storeValue("foo", "11\n");
        const post_rejection_show = try self.showValue("foo");

        return .{
            .anchor = descriptor().anchor,
            .stage_before_boundary_checks = .registered,
            .stage_after_boundary_checks = self.stage_value,
            .active_attr_count = self.active_attr_count,
            .init_runs = self.init_runs,
            .register_runs = self.register_runs,
            .exit_runs = self.exit_runs,
            .rejected_duplicate_registration = rejected_duplicate_registration,
            .rejected_registered_anchor_replay = rejected_registered_anchor_replay,
            .post_rejection_store_len = post_rejection_store_len,
            .post_rejection_show = post_rejection_show,
        };
    }

    pub fn runOwnershipReplay(self: *Self) !OwnershipReplay {
        self.requireColdReplayStart();

        const cold_snapshot = self.ownershipSummary();
        const cold_ready = replayReady(.cold);

        try self.init();
        const initialized_snapshot = self.ownershipSummary();
        const initialized_ready = replayReady(self.stage_value);

        try self.registerAttributes();
        const registered_snapshot = self.ownershipSummary();
        const registered_ready = replayReady(self.stage_value);

        const registered_exit = try self.exit();
        const exited_snapshot = self.ownershipSummary();
        const exited_ready = replayReady(self.stage_value);

        var initialized_path = Self{};
        try initialized_path.init();
        const initialized_exit = try initialized_path.exit();

        return .{
            .anchor = descriptor().anchor,
            .stage_snapshots = .{ cold_snapshot, initialized_snapshot, registered_snapshot, exited_snapshot },
            .replay_readiness = .{ cold_ready, initialized_ready, registered_ready, exited_ready },
            .initialized_exit = initialized_exit,
            .registered_exit = registered_exit,
        };
    }

    pub fn runTeardownReplay(self: *Self) !TeardownReplay {
        self.requireColdReplayStart();
        try self.init();
        try self.registerAttributes();
        _ = try self.storeValue("foo", "42\n");
        _ = try self.storeValue("baz", "7\n");
        _ = try self.storeValue("bar", "-5\n");

        const values_before_exit = self.valuesSnapshot();
        const exit_summary = try self.exit();
        const values_after_exit = self.valuesSnapshot();

        const rejected_reinit = blk: {
            self.init() catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_reregister = blk: {
            self.registerAttributes() catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_show = blk: {
            _ = self.showValue("foo") catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_store = blk: {
            _ = self.storeValue("foo", "1\n") catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_second_exit = blk: {
            _ = self.exit() catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };
        const rejected_anchor_replay = blk: {
            _ = self.runAnchorReplay() catch |err| {
                if (err == error.InvalidLifecycleTransition) break :blk true;
                return err;
            };
            break :blk false;
        };

        return .{
            .anchor = descriptor().anchor,
            .exit_summary = exit_summary,
            .values_before_exit = values_before_exit,
            .values_after_exit = values_after_exit,
            .active_attr_count_after_exit = self.active_attr_count,
            .rejected_reinit = rejected_reinit,
            .rejected_reregister = rejected_reregister,
            .rejected_show = rejected_show,
            .rejected_store = rejected_store,
            .rejected_second_exit = rejected_second_exit,
            .rejected_anchor_replay = rejected_anchor_replay,
        };
    }

    fn requireColdReplayStart(self: *const Self) void {
        if (self.stage_value != .cold) @panic("replay helpers require a cold sample instance");
    }

    fn valueFor(self: *const Self, attr_name: []const u8) !i32 {
        if (std.mem.eql(u8, attr_name, "foo")) return self.foo;
        return self.sharedBValue(attr_name);
    }

    fn assignValue(self: *Self, attr_name: []const u8, value: i32) !void {
        if (std.mem.eql(u8, attr_name, "foo")) {
            self.foo = value;
            return;
        }
        if (std.mem.eql(u8, attr_name, "baz")) {
            self.baz = value;
            return;
        }
        if (std.mem.eql(u8, attr_name, "bar")) {
            self.bar = value;
            return;
        }
        return error.UnknownAttribute;
    }

    fn sharedBValue(self: *const Self, attr_name: []const u8) !i32 {
        if (std.mem.eql(u8, attr_name, "baz")) return self.baz;
        if (std.mem.eql(u8, attr_name, "bar")) return self.bar;
        return error.UnknownAttribute;
    }

    fn valuesSnapshot(self: *const Self) ValueSnapshot {
        return .{
            .foo = self.foo,
            .baz = self.baz,
            .bar = self.bar,
        };
    }
};

fn attributeSpecs() [3]AttributeSpec {
    return .{
        .{ .name = "foo", .mode = 0o664, .uses_shared_b_handlers = false },
        .{ .name = "baz", .mode = 0o664, .uses_shared_b_handlers = true },
        .{ .name = "bar", .mode = 0o664, .uses_shared_b_handlers = true },
    };
}

fn parseInteger(raw_value: []const u8) !i32 {
    const trimmed = std.mem.trimRight(u8, raw_value, "\r\n");
    if (trimmed.len == 0) return error.InvalidInteger;
    return std.fmt.parseInt(i32, trimmed, 10) catch error.InvalidInteger;
}

fn renderValue(attr_name: []const u8, value: i32) !RenderedValue {
    var buffer: [32]u8 = undefined;
    const rendered = try std.fmt.bufPrint(&buffer, "{d}\n", .{value});
    return .{
        .attr_name = attr_name,
        .text = buffer,
        .len = rendered.len,
    };
}

fn replayReady(stage: SampleStage) bool {
    return stage == .initialized;
}

test "kobject example sample keeps the anchor replay self-check local to the sample file" {
    var sample = KobjectExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", replay.anchor);
    try std.testing.expectEqualStrings("42\n", replay.foo_value.text[0..replay.foo_value.len]);
    try std.testing.expectEqualStrings("7\n", replay.baz_value.text[0..replay.baz_value.len]);
    try std.testing.expectEqualStrings("-5\n", replay.bar_value.text[0..replay.bar_value.len]);
    try std.testing.expectEqual(SampleStage.registered, sample.stage());
}

test "kobject example sample keeps teardown and ownership cues self-checkable" {
    var sample = KobjectExampleSample{};
    const replay = try sample.runTeardownReplay();

    try std.testing.expectEqual(ExitDisposition.tore_down_registered_attributes, replay.exit_summary.disposition);
    try std.testing.expectEqual(@as(i32, 42), replay.values_before_exit.foo);
    try std.testing.expectEqual(@as(i32, 0), replay.values_after_exit.foo);
    try std.testing.expect(replay.rejected_anchor_replay);
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
}
