const std = @import("std");
const contract_options = @import("contract_options");

const smoke_text = contract_options.smoke_text;
const build_text = contract_options.build_text;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, needle).?);
}

test "smoke harness keeps argv_split imported through the shared build root" {
    try requireOnce(smoke_text, "const argv_split = @import(\"argv_split\");");
    try requireOnce(build_text, "const argv_split_module = b.createModule(.{");
    try requireOnce(build_text, ".root_source_file = b.path(\"../../tools/lib/argv_split.zig\"),");
    try requireOnce(build_text, "root_module.addImport(\"argv_split\", argv_split_module);");
    try requireOnce(build_text, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),");
    try requireOnce(build_text, ".name = \"phase1-host-tools-smoke\",");
}

test "smoke harness keeps argv_split public alias and token anchors" {
    try requireContains(smoke_text, "try std.testing.expect(@hasDecl(argv_split, \"argvSplit\"));");
    try requireContains(smoke_text, "var split = try argv_split.argv_split(std.testing.allocator, \"  zigux   host\\ttools  \");");
    try requireContains(smoke_text, "defer argv_split.argv_free(&split);");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, 3), split.argc());");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"zigux\", split.argv[0]);");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"host\", split.argv[1]);");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"tools\", split.argv[2]);");
}

test "smoke harness keeps argv_split ahead of downstream helper behavior" {
    const split_index = std.mem.indexOf(u8, smoke_text, "var split = try argv_split.argv_split") orelse return error.MarkerMissing;
    const memparse_index = std.mem.indexOf(u8, smoke_text, "const parsed = cmdline.memparse") orelse return error.MarkerMissing;
    const ctype_index = std.mem.indexOf(u8, smoke_text, "try std.testing.expectEqual(@as(u8, 0x41), ctype.mask('A'));") orelse return error.MarkerMissing;
    try std.testing.expect(split_index < memparse_index);
    try std.testing.expect(memparse_index < ctype_index);
}

test "argv smoke contract rejects stale helper and ownership spellings" {
    try requireMissing(build_text, "root_module.addImport(\"argv\", argv_split_module);");
    try requireMissing(build_text, ".root_source_file = b.path(\"../../lib/argv_split.zig\"),");
    try requireMissing(smoke_text, "argv_split.argvSplit(std.testing.allocator, \"  zigux   host\\ttools  \")");
    try requireMissing(smoke_text, "defer split.deinit();");
    try requireMissing(smoke_text, "try std.testing.expectEqual(@as(usize, 2), split.argc());");
}
