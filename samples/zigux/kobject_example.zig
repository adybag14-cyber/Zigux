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

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .registered => {},
            else => return error.InvalidLifecycleTransition,
        }

        self.foo = 0;
        self.baz = 0;
        self.bar = 0;
        self.exit_runs += 1;
        self.stage_state = .exited;
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
