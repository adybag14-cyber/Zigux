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

test "smoke harness keeps ctype and hweight imported through the shared build root" {
    try requireOnce(smoke_text, "const ctype = @import(\"ctype\");");
    try requireOnce(smoke_text, "const hweight = @import(\"hweight\");");
    try requireOnce(build_text, "const ctype_module = b.createModule(.{");
    try requireOnce(build_text, ".root_source_file = b.path(\"../../tools/lib/ctype.zig\"),");
    try requireOnce(build_text, "const hweight_module = b.createModule(.{");
    try requireOnce(build_text, ".root_source_file = b.path(\"../../tools/lib/hweight.zig\"),");
    try requireOnce(build_text, "root_module.addImport(\"ctype\", ctype_module);");
    try requireOnce(build_text, "root_module.addImport(\"hweight\", hweight_module);");
    try requireOnce(build_text, ".name = \"phase1-host-tools-smoke\",");
}

test "smoke harness keeps ctype declaration and behavior anchors" {
    try requireContains(smoke_text, "try std.testing.expect(@hasDecl(ctype, \"isalpha\"));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 0x41), ctype.mask('A'));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 0x42), ctype.mask('a'));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 0xa0), ctype.mask(' '));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.isalnum('A'));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.isalpha('Q'));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.isdigit('7'));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.isspace('\\t'));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.isxdigit('f'));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.ispunct('!'));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower('A'));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 'm'), ctype.fastTolower('M'));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper('z'));");
    try requireContains(smoke_text, "try std.testing.expect(ctype.isodigit('7'));");
    try requireContains(smoke_text, "try std.testing.expect(!ctype.isodigit('8'));");
}

test "smoke harness keeps hweight declaration and width anchors" {
    try requireContains(smoke_text, "try std.testing.expect(@hasDecl(hweight, \"swHweight64\"));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0xf0));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0xf0f0));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xf0f0_f0f0));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@popCount(@as(usize, 0xf0f0)), hweight.hweightLong(0xf0f0));");
}

test "smoke harness keeps ctype before hweight and before allocation smoke" {
    const ctype_index = std.mem.indexOf(u8, smoke_text, "try std.testing.expectEqual(@as(u8, 0x41), ctype.mask('A'));") orelse return error.MarkerMissing;
    const hweight_index = std.mem.indexOf(u8, smoke_text, "try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0xf0));") orelse return error.MarkerMissing;
    const slab_index = std.mem.indexOf(u8, smoke_text, "slab.kmalloc_nr_allocated = 0;") orelse return error.MarkerMissing;
    try std.testing.expect(ctype_index < hweight_index);
    try std.testing.expect(hweight_index < slab_index);
}

test "ctype and hweight smoke contract rejects stale helper and ownership spellings" {
    try requireMissing(build_text, "root_module.addImport(\"ctype\", cmdline_module);");
    try requireMissing(build_text, "root_module.addImport(\"hweight\", bitmap_module);");
    try requireMissing(build_text, ".root_source_file = b.path(\"../../lib/ctype.zig\"),");
    try requireMissing(build_text, ".root_source_file = b.path(\"../../lib/hweight.zig\"),");
    try requireMissing(smoke_text, "ctype.isalpha('a')");
    try requireMissing(smoke_text, "hweight.swHweight64(0xffff)");
    try requireMissing(smoke_text, "try std.testing.expectEqual(@as(u32, 32), hweight.swHweight64");
}
