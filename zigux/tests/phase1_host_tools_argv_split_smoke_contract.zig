const std = @import("std");
const smoke_options = @import("smoke_options");

const smoke_text = smoke_options.smoke_text;
const build_root_text = smoke_options.build_root_text;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, marker).?);
    return index;
}

test "smoke harness keeps argv_split imported and freed through the public aliases" {
    try requireContains(smoke_text, "const argv_split = @import(\"argv_split\");");
    try requireContains(smoke_text, "try std.testing.expect(@hasDecl(argv_split, \"argvSplit\"));");
    try requireContains(smoke_text, "var split = try argv_split.argv_split(std.testing.allocator, \"  zigux   host\\ttools  \");");
    try requireContains(smoke_text, "defer argv_split.argv_free(&split);");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, 3), split.argc());");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"zigux\", split.argv[0]);");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"host\", split.argv[1]);");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"tools\", split.argv[2]);");
}

test "argv_split smoke slice stays in the first live helper behavior block" {
    const behavior_header = try markerIndex(
        smoke_text,
        "test \"phase1 host-tools smoke exercises live helper behavior\" {",
    );
    const split_call = try markerIndex(
        smoke_text,
        "var split = try argv_split.argv_split(std.testing.allocator, \"  zigux   host\\ttools  \");",
    );
    const first_cmdline = try markerIndex(smoke_text, "const parsed = cmdline.memparse(\"64K tail\");");
    const first_ctype = try markerIndex(smoke_text, "try std.testing.expectEqual(@as(u8, 0x41), ctype.mask('A'));");

    try std.testing.expect(behavior_header < split_call);
    try std.testing.expect(split_call < first_cmdline);
    try std.testing.expect(first_cmdline < first_ctype);
}

test "shared build root wires argv_split directly into the Phase 1 smoke route" {
    const factory = try markerIndex(build_root_text, "fn addPhase1HostToolsSmoke(");
    const module_decl = try markerIndex(build_root_text, "const argv_split_module = b.createModule(.{");
    const source_path = try markerIndex(
        build_root_text,
        ".root_source_file = b.path(\"../../tools/lib/argv_split.zig\"),",
    );
    const import_decl = try markerIndex(
        build_root_text,
        "root_module.addImport(\"argv_split\", argv_split_module);",
    );
    const route = try markerIndex(
        build_root_text,
        "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\",",
    );

    try std.testing.expect(factory < module_decl);
    try std.testing.expect(module_decl < source_path);
    try std.testing.expect(source_path < import_decl);
    try std.testing.expect(import_decl < route);
    try requireMissing(build_root_text, "phase1-host-tools-smoke-argv-split-only");
}
