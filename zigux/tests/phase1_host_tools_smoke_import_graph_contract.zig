const std = @import("std");
const options = @import("phase1_host_tools_smoke_import_graph_options");

const helper_imports = [_][]const u8{
    "argv_split",
    "cmdline",
    "find_bit",
    "bitmap",
    "ctype",
    "hweight",
    "list_sort",
    "rbtree",
    "string",
    "slab",
    "str_error_r",
    "vsprintf",
    "zalloc",
};

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) == null);
}

fn countOccurrences(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, text, start, needle)) |found| {
        count += 1;
        start = found + needle.len;
    }
    return count;
}

fn sliceBetween(text: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, text, start_marker) orelse return error.MissingStartMarker;
    const after_start = start + start_marker.len;
    const relative_end = std.mem.indexOf(u8, text[after_start..], end_marker) orelse return error.MissingEndMarker;
    return text[start .. after_start + relative_end];
}

test "shared build root wires the phase1 host-tools smoke helper graph" {
    const build_zig = options.tests_build_zig;

    try requireContains(build_zig, "fn addPhase1HostToolsSmoke(");
    try requireContains(build_zig, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try requireContains(build_zig, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try requireContains(build_zig, "string_module.addImport(\"cmdline\", cmdline_module);");
    try requireContains(build_zig, "b.step(\n        \"phase1-host-tools-smoke\"");
    try requireContains(build_zig, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try requireAbsent(build_zig, "phase1_step.dependOn(&phase3");

    inline for (helper_imports) |name| {
        const module_decl = "const " ++ name ++ "_module = b.createModule(.{";
        const root_import = "root_module.addImport(\"" ++ name ++ "\", " ++ name ++ "_module);";
        try requireContains(build_zig, module_decl);
        try requireContains(build_zig, root_import);
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(build_zig, root_import));
    }
}

test "phase1 smoke source imports and declaration-checks every helper family" {
    const smoke_zig = options.phase1_smoke_zig;

    inline for (helper_imports) |name| {
        try requireContains(smoke_zig, "@import(\"" ++ name ++ "\")");
    }

    const decl_checks = [_][]const u8{
        "@hasDecl(argv_split, \"argvSplit\")",
        "@hasDecl(cmdline, \"memparse\")",
        "@hasDecl(find_bit, \"findFirstBit\")",
        "@hasDecl(bitmap, \"setRange\")",
        "@hasDecl(ctype, \"isalpha\")",
        "@hasDecl(hweight, \"swHweight64\")",
        "@hasDecl(list_sort, \"listSort\")",
        "@hasDecl(rbtree, \"find\")",
        "@hasDecl(string, \"strtobool\")",
        "@hasDecl(slab, \"kmallocBytes\")",
        "@hasDecl(str_error_r, \"strErrorR\")",
        "@hasDecl(vsprintf, \"scnprintf\")",
        "@hasDecl(zalloc, \"zallocBytes\")",
    };

    inline for (decl_checks) |marker| {
        try requireContains(smoke_zig, marker);
    }
}

test "helper graph stays rooted in phase1 host helpers only" {
    const build_zig = options.tests_build_zig;
    const smoke_zig = options.phase1_smoke_zig;
    const phase1_smoke_build = try sliceBetween(
        build_zig,
        "fn addPhase1HostToolsSmoke(",
        "\nfn addPhase1StringDirectAnchor(",
    );

    try requireAbsent(phase1_smoke_build, "root_module.addImport(\"abi_bindings\"");
    try requireAbsent(phase1_smoke_build, "root_module.addImport(\"export_shim\"");
    try requireAbsent(smoke_zig, "@import(\"abi_bindings\")");
    try requireAbsent(smoke_zig, "@import(\"export_shim\")");
}
