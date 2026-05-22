const std = @import("std");

pub const linux_anchor = "samples/kobject/kobject-example.c";
pub const directory_name = "kobject_example";

pub const AttributeSpec = struct {
    name: []const u8,
    mode: u16,
    uses_shared_b_handlers: bool,
};

pub const AttributeGroupContract = struct {
    anchor: []const u8,
    directory: []const u8,
    attribute_specs: [3]AttributeSpec,
    ordered_attr_names: [3][]const u8,
    attr_slots_including_null_terminator: usize,
    group_is_named: bool,
    all_modes_match_reference: bool,
    all_modes_disallow_world_write: bool,
    shared_b_handler_pair_consistent: bool,
    shared_b_handler_names: [2][]const u8,
    dedicated_handler_name: []const u8,
};

pub fn referencePattern() AttributeGroupContract {
    const specs = [_]AttributeSpec{
        .{ .name = "foo", .mode = 0o664, .uses_shared_b_handlers = false },
        .{ .name = "baz", .mode = 0o664, .uses_shared_b_handlers = true },
        .{ .name = "bar", .mode = 0o664, .uses_shared_b_handlers = true },
    };

    return .{
        .anchor = linux_anchor,
        .directory = directory_name,
        .attribute_specs = specs,
        .ordered_attr_names = attrNames(specs),
        .attr_slots_including_null_terminator = specs.len + 1,
        .group_is_named = false,
        .all_modes_match_reference = modesMatchReference(specs),
        .all_modes_disallow_world_write = modesDisallowWorldWrite(specs),
        .shared_b_handler_pair_consistent = sharedBHandlerPairConsistent(specs),
        .shared_b_handler_names = .{ "baz", "bar" },
        .dedicated_handler_name = "foo",
    };
}

fn attrNames(specs: [3]AttributeSpec) [3][]const u8 {
    return .{ specs[0].name, specs[1].name, specs[2].name };
}

fn modesMatchReference(specs: [3]AttributeSpec) bool {
    inline for (specs) |spec| {
        if (spec.mode != 0o664) return false;
    }
    return true;
}

fn modesDisallowWorldWrite(specs: [3]AttributeSpec) bool {
    inline for (specs) |spec| {
        if ((spec.mode & 0o002) != 0) return false;
    }
    return true;
}

fn sharedBHandlerPairConsistent(specs: [3]AttributeSpec) bool {
    return !specs[0].uses_shared_b_handlers and
        specs[1].uses_shared_b_handlers and
        specs[2].uses_shared_b_handlers;
}

test "kobject companion keeps the Linux attribute mode and unnamed-group contract explicit" {
    const contract = referencePattern();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", contract.anchor);
    try std.testing.expectEqualStrings("kobject_example", contract.directory);
    try std.testing.expectEqual(@as(usize, 4), contract.attr_slots_including_null_terminator);
    try std.testing.expect(!contract.group_is_named);
    try std.testing.expect(contract.all_modes_match_reference);
    try std.testing.expect(contract.all_modes_disallow_world_write);
    try std.testing.expect(contract.shared_b_handler_pair_consistent);
    try std.testing.expectEqualStrings("foo", contract.attribute_specs[0].name);
    try std.testing.expectEqualStrings("baz", contract.attribute_specs[1].name);
    try std.testing.expectEqualStrings("bar", contract.attribute_specs[2].name);
    try std.testing.expectEqualStrings("foo", contract.ordered_attr_names[0]);
    try std.testing.expectEqualStrings("baz", contract.ordered_attr_names[1]);
    try std.testing.expectEqualStrings("bar", contract.ordered_attr_names[2]);
}

test "kobject companion keeps the shared baz and bar handler pair separate from foo" {
    const contract = referencePattern();

    try std.testing.expectEqual(@as(u16, 0o664), contract.attribute_specs[0].mode);
    try std.testing.expectEqual(@as(u16, 0o664), contract.attribute_specs[1].mode);
    try std.testing.expectEqual(@as(u16, 0o664), contract.attribute_specs[2].mode);
    try std.testing.expect(!contract.attribute_specs[0].uses_shared_b_handlers);
    try std.testing.expect(contract.attribute_specs[1].uses_shared_b_handlers);
    try std.testing.expect(contract.attribute_specs[2].uses_shared_b_handlers);
    try std.testing.expectEqualStrings("foo", contract.dedicated_handler_name);
    try std.testing.expectEqualStrings("baz", contract.shared_b_handler_names[0]);
    try std.testing.expectEqualStrings("bar", contract.shared_b_handler_names[1]);
}
