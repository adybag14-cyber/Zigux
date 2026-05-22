const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 kobject attr-group survey keeps the companion contract markers explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const companion = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/kobject_example_attr_group_contract.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(companion);

    const required_markers = [_][]const u8{
        "pub const linux_anchor = \"samples/kobject/kobject-example.c\";",
        "pub const directory_name = \"kobject_example\";",
        ".{ .name = \"foo\", .mode = 0o664, .uses_shared_b_handlers = false }",
        ".{ .name = \"baz\", .mode = 0o664, .uses_shared_b_handlers = true }",
        ".{ .name = \"bar\", .mode = 0o664, .uses_shared_b_handlers = true }",
        ".attr_slots_including_null_terminator = specs.len + 1",
        ".group_is_named = false",
        ".all_modes_disallow_world_write = modesDisallowWorldWrite(specs)",
        ".shared_b_handler_pair_consistent = sharedBHandlerPairConsistent(specs)",
    };
    for (required_markers) |marker| {
        try expectContains(companion, marker);
    }
}

test "phase 5 kobject attr-group survey keeps the focused external replay aligned with the companion contract" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const replay = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_kobject_attr_group_contract.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(replay);

    const required_markers = [_][]const u8{
        "const companion = @import(\"kobject_attr_group_contract\");",
        "phase 5 kobject attr-group companion keeps the anchor-local contract reviewable through a focused test surface",
        "phase 5 kobject attr-group companion keeps the foo/baz/bar ownership-facing shape explicit",
        "contract.attr_slots_including_null_terminator",
        "contract.all_modes_match_reference",
        "contract.all_modes_disallow_world_write",
        "contract.shared_b_handler_pair_consistent",
        "const expected_names = [_][]const u8{ \"foo\", \"baz\", \"bar\" };",
        "const expected_shared_handlers = [_]bool{ false, true, true };",
    };
    for (required_markers) |marker| {
        try expectContains(replay, marker);
    }
}

test "phase 5 kobject attr-group survey keeps the shared phase5 build route aware of the focused replay" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    const required_markers = [_][]const u8{
        "../../samples/zigux/kobject_example_attr_group_contract.zig",
        "phase5_kobject_attr_group_contract.zig",
        "\"kobject_attr_group_contract\"",
        "\"phase5-kobject-attr-group-contract-tests\"",
        "test_step.dependOn(&run_phase5_kobject_attr_group_contract_tests.step);",
    };
    for (required_markers) |marker| {
        try expectContains(build_file, marker);
    }
}
