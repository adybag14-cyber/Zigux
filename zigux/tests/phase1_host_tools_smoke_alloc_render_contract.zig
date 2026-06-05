const std = @import("std");
const config = @import("contract_config");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase1 smoke imports allocation error and render helpers" {
    const smoke = @embedFile(config.smoke_path);

    try expectContains(smoke, "const slab = @import(\"slab\");");
    try expectContains(smoke, "const str_error_r = @import(\"str_error_r\");");
    try expectContains(smoke, "const vsprintf = @import(\"vsprintf\");");
    try expectContains(smoke, "const zalloc = @import(\"zalloc\");");
    try expectContains(smoke, "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));");
    try expectContains(smoke, "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));");
    try expectContains(smoke, "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));");
    try expectContains(smoke, "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));");
    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(string, \"strnchrNul\"));", "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));");
    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));", "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));");
    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));", "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));");
    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));", "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));");
}

test "phase1 smoke keeps allocation error and render behavior anchors" {
    const smoke = @embedFile(config.smoke_path);

    try expectContains(smoke, "slab.kmalloc_nr_allocated = 0;");
    try expectContains(smoke, "slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO)");
    try expectContains(smoke, "try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);");
    try expectContains(smoke, "slab.kfree(allocated);");
    try expectContains(smoke, "try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"Permission denied\", str_error_r.strErrorR(13, &error_buffer));");
    try expectContains(smoke, "str_error_r.strErrorR(4096, &unknown_error_buffer)");
    try expectContains(smoke, "\"INTERNAL ERROR: strerror_r(4096, [buf], 64)=22\"");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"INTERNA\", str_error_r.strErrorR(4096, &tiny_error_buffer));");
    try expectContains(smoke, "const rendered_len = vsprintf.scnprintf(&render_buffer, \"{s}:{d}\", .{ \"zigux\", 9 });");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"zigux:9\", render_buffer[0..rendered_len]);");
    try expectContains(smoke, "const padded_len = vsprintf.scnprintfPad(&padded_render, 10, \"id={d}\", .{7});");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"id=7      \", padded_render[0..10]);");
    try expectContains(smoke, "var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);");
    try expectContains(smoke, "defer zalloc.zfreeBytes(allocator, &zero_bytes);");
    try expectContains(smoke, "var zero_value: ?*ZeroValue = try zalloc.zallocValue(allocator, ZeroValue);");
    try expectContains(smoke, "defer zalloc.zfreeValue(allocator, ZeroValue, &zero_value);");
    try expectContains(smoke, "try std.testing.expectEqual(false, zero_value.?.enabled);");
    try expectOrdered(smoke, "slab.kmalloc_nr_allocated = 0;", "var error_buffer: [32]u8 = undefined;");
    try expectOrdered(smoke, "var error_buffer: [32]u8 = undefined;", "var render_buffer: [16]u8 = undefined;");
    try expectOrdered(smoke, "var render_buffer: [16]u8 = undefined;", "var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);");
}

test "phase1 shared build root wires allocation error and render helpers" {
    const tests_build = @embedFile(config.tests_build_path);

    try expectContains(tests_build, "const slab_module = b.createModule(.{");
    try expectContains(tests_build, ".root_source_file = b.path(\"../../tools/lib/slab.zig\"),");
    try expectContains(tests_build, "const str_error_r_module = b.createModule(.{");
    try expectContains(tests_build, ".root_source_file = b.path(\"../../tools/lib/str_error_r.zig\"),");
    try expectContains(tests_build, "const vsprintf_module = b.createModule(.{");
    try expectContains(tests_build, ".root_source_file = b.path(\"../../tools/lib/vsprintf.zig\"),");
    try expectContains(tests_build, "const zalloc_module = b.createModule(.{");
    try expectContains(tests_build, ".root_source_file = b.path(\"../../tools/lib/zalloc.zig\"),");
    try expectContains(tests_build, "root_module.addImport(\"slab\", slab_module);");
    try expectContains(tests_build, "root_module.addImport(\"str_error_r\", str_error_r_module);");
    try expectContains(tests_build, "root_module.addImport(\"vsprintf\", vsprintf_module);");
    try expectContains(tests_build, "root_module.addImport(\"zalloc\", zalloc_module);");
    try expectContains(tests_build, "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\",");
    try expectContains(tests_build, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectAbsent(tests_build, "alloc_render_contract");
    try expectOrdered(tests_build, "root_module.addImport(\"string\", string_module);", "root_module.addImport(\"slab\", slab_module);");
    try expectOrdered(tests_build, "root_module.addImport(\"slab\", slab_module);", "root_module.addImport(\"str_error_r\", str_error_r_module);");
    try expectOrdered(tests_build, "root_module.addImport(\"str_error_r\", str_error_r_module);", "root_module.addImport(\"vsprintf\", vsprintf_module);");
    try expectOrdered(tests_build, "root_module.addImport(\"vsprintf\", vsprintf_module);", "root_module.addImport(\"zalloc\", zalloc_module);");
}
