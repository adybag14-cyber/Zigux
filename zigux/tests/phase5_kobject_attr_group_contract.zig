const std = @import("std");
const companion = @import("kobject_attr_group_contract");

test "phase 5 kobject attr-group companion keeps the anchor-local contract reviewable through a focused test surface" {
    const contract = companion.referencePattern();

    try std.testing.expectEqualStrings("samples/kobject/kobject-example.c", contract.anchor);
    try std.testing.expectEqualStrings("kobject_example", contract.directory);
    try std.testing.expectEqual(@as(usize, 4), contract.attr_slots_including_null_terminator);
    try std.testing.expect(!contract.group_is_named);
    try std.testing.expect(contract.all_modes_match_reference);
    try std.testing.expect(contract.all_modes_disallow_world_write);
    try std.testing.expect(contract.shared_b_handler_pair_consistent);
}

test "phase 5 kobject attr-group companion keeps the foo/baz/bar ownership-facing shape explicit" {
    const contract = companion.referencePattern();
    const expected_names = [_][]const u8{ "foo", "baz", "bar" };
    const expected_shared_handlers = [_]bool{ false, true, true };

    inline for (expected_names, expected_shared_handlers, 0..) |name, uses_shared_handlers, idx| {
        try std.testing.expectEqualStrings(name, contract.attribute_specs[idx].name);
        try std.testing.expectEqual(@as(u16, 0o664), contract.attribute_specs[idx].mode);
        try std.testing.expectEqual(uses_shared_handlers, contract.attribute_specs[idx].uses_shared_b_handlers);
    }
}
