const std = @import("std");
const contract_options = @import("contract_options");

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{first});
        return error.MissingMarker;
    };
    const second_index = std.mem.indexOf(u8, haystack, second) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{second});
        return error.MissingMarker;
    };
    try std.testing.expect(first_index < second_index);
}

test "phase1 smoke source keeps allocator and render helper imports" {
    const smoke = try readFile(contract_options.smoke_path);
    defer std.testing.allocator.free(smoke);

    try expectContains(smoke, "const slab = @import(\"slab\");");
    try expectContains(smoke, "const str_error_r = @import(\"str_error_r\");");
    try expectContains(smoke, "const vsprintf = @import(\"vsprintf\");");
    try expectContains(smoke, "const zalloc = @import(\"zalloc\");");

    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));", "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));");
    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));", "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));");
    try expectOrdered(smoke, "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));", "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));");
}

test "phase1 smoke source keeps allocator error render behavior aligned" {
    const smoke = try readFile(contract_options.smoke_path);
    defer std.testing.allocator.free(smoke);

    try expectContains(smoke, "slab.kmalloc_nr_allocated = 0;");
    try expectContains(smoke, "slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO)");
    try expectContains(smoke, "try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);");
    try expectContains(smoke, "try std.testing.expectEqual(@as(u8, 0), byte);");
    try expectContains(smoke, "slab.kfree(allocated);");
    try expectContains(smoke, "try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);");

    try expectContains(smoke, "try std.testing.expectEqualStrings(\"Permission denied\", str_error_r.strErrorR(13, &error_buffer));");
    try expectContains(smoke, "INTERNAL ERROR: strerror_r(4096, [buf], 64)=22");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"INTERNA\", str_error_r.strErrorR(4096, &tiny_error_buffer));");

    try expectContains(smoke, "const rendered_len = vsprintf.scnprintf(&render_buffer, \"{s}:{d}\", .{ \"zigux\", 9 });");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"zigux:9\", render_buffer[0..rendered_len]);");
    try expectContains(smoke, "const padded_len = vsprintf.scnprintfPad(&padded_render, 10, \"id={d}\", .{7});");
    try expectContains(smoke, "try std.testing.expectEqualStrings(\"id=7      \", padded_render[0..10]);");

    try expectContains(smoke, "var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);");
    try expectContains(smoke, "defer zalloc.zfreeBytes(allocator, &zero_bytes);");
    try expectContains(smoke, "var zero_value: ?*ZeroValue = try zalloc.zallocValue(allocator, ZeroValue);");
    try expectContains(smoke, "defer zalloc.zfreeValue(allocator, ZeroValue, &zero_value);");
    try expectContains(smoke, "try std.testing.expectEqual(@as(u32, 0), zero_value.?.count);");
    try expectContains(smoke, "try std.testing.expectEqual(false, zero_value.?.enabled);");

    try expectOrdered(smoke, "slab.kmalloc_nr_allocated = 0;", "try std.testing.expectEqualStrings(\"Permission denied\", str_error_r.strErrorR(13, &error_buffer));");
    try expectOrdered(smoke, "try std.testing.expectEqualStrings(\"INTERNA\", str_error_r.strErrorR(4096, &tiny_error_buffer));", "const rendered_len = vsprintf.scnprintf(&render_buffer");
    try expectOrdered(smoke, "const padded_len = vsprintf.scnprintfPad(&padded_render", "var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);");
}

test "phase1 tests build keeps allocator error render modules wired into smoke route" {
    const build_file = try readFile(contract_options.tests_build_path);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, "const slab_module = b.createModule(.{");
    try expectContains(build_file, ".root_source_file = b.path(\"../../tools/lib/slab.zig\"),");
    try expectContains(build_file, "const str_error_r_module = b.createModule(.{");
    try expectContains(build_file, ".root_source_file = b.path(\"../../tools/lib/str_error_r.zig\"),");
    try expectContains(build_file, "const vsprintf_module = b.createModule(.{");
    try expectContains(build_file, ".root_source_file = b.path(\"../../tools/lib/vsprintf.zig\"),");
    try expectContains(build_file, "const zalloc_module = b.createModule(.{");
    try expectContains(build_file, ".root_source_file = b.path(\"../../tools/lib/zalloc.zig\"),");

    try expectContains(build_file, "root_module.addImport(\"slab\", slab_module);");
    try expectContains(build_file, "root_module.addImport(\"str_error_r\", str_error_r_module);");
    try expectContains(build_file, "root_module.addImport(\"vsprintf\", vsprintf_module);");
    try expectContains(build_file, "root_module.addImport(\"zalloc\", zalloc_module);");

    try expectContains(build_file, "\"phase1-host-tools-smoke\"");
    try expectContains(build_file, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains(build_file, "smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains(build_file, "test_step.dependOn(&phase1_host_tools_smoke.step);");
}
