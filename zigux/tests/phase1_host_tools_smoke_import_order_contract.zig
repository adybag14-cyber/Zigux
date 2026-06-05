const std = @import("std");
const contract_options = @import("contract_options");

const smoke_text = contract_options.smoke_text;

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, needle).?);
    return index;
}

fn requireOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireOnce(haystack, before);
    const after_index = try requireOnce(haystack, after);
    try std.testing.expect(before_index < after_index);
}

test "smoke source keeps the Phase 1 helper import roster closed and ordered" {
    const imports = [_][]const u8{
        "const argv_split = @import(\"argv_split\");",
        "const cmdline = @import(\"cmdline\");",
        "pub const find_bit = @import(\"find_bit\");",
        "const bitmap = @import(\"bitmap\");",
        "const ctype = @import(\"ctype\");",
        "const hweight = @import(\"hweight\");",
        "const list_sort = @import(\"list_sort\");",
        "const rbtree = @import(\"rbtree\");",
        "const string = @import(\"string\");",
        "const slab = @import(\"slab\");",
        "const str_error_r = @import(\"str_error_r\");",
        "const vsprintf = @import(\"vsprintf\");",
        "const zalloc = @import(\"zalloc\");",
        "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");",
    };

    var previous_index: ?usize = null;
    for (imports) |marker| {
        const index = try requireOnce(smoke_text, marker);
        if (previous_index) |previous| {
            try std.testing.expect(previous < index);
        }
        previous_index = index;
    }
}

test "smoke source keeps helper imports above local smoke scaffolding" {
    try requireOrdered(
        smoke_text,
        "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");",
        "comptime {\n    _ = phase1_find_bit_fixture_guard;\n}",
    );
    try requireOrdered(
        smoke_text,
        "comptime {\n    _ = phase1_find_bit_fixture_guard;\n}",
        "const ListSortSmokeEntry = struct {",
    );
    try requireOrdered(
        smoke_text,
        "const ListSortSmokeEntry = struct {",
        "const RbtreeSmokeEntry = struct {",
    );
    try requireOrdered(
        smoke_text,
        "const RbtreeSmokeEntry = struct {",
        "test \"phase1 host-tools smoke imports the live helper modules\"",
    );
}

test "smoke source keeps declaration assertions aligned with the import roster" {
    const declarations = [_][]const u8{
        "try std.testing.expect(@hasDecl(argv_split, \"argvSplit\"));",
        "try std.testing.expect(@hasDecl(cmdline, \"memparse\"));",
        "try std.testing.expect(@hasDecl(find_bit, \"findFirstBit\"));",
        "try std.testing.expect(@hasDecl(bitmap, \"setRange\"));",
        "try std.testing.expect(@hasDecl(ctype, \"isalpha\"));",
        "try std.testing.expect(@hasDecl(hweight, \"swHweight64\"));",
        "try std.testing.expect(@hasDecl(list_sort, \"listSort\"));",
        "try std.testing.expect(@hasDecl(rbtree, \"find\"));",
        "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));",
        "try std.testing.expect(@hasDecl(string, \"strtobool\"));",
        "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));",
        "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));",
        "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));",
        "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));",
    };

    var previous_index: ?usize = null;
    for (declarations) |marker| {
        const index = try requireOnce(smoke_text, marker);
        if (previous_index) |previous| {
            try std.testing.expect(previous < index);
        }
        previous_index = index;
    }
}

test "smoke source rejects stale direct helper paths and private find_bit imports" {
    try requireMissing(smoke_text, "@import(\"../../tools/lib/");
    try requireMissing(smoke_text, "\nconst find_bit = @import(\"find_bit\");");
    try requireMissing(smoke_text, "const phase1_find_bit_fixture_guard = @import(\"../fixtures/");
    try requireMissing(smoke_text, "@import(\"phase1_helper_manifest");
    try requireMissing(smoke_text, "root_module.addImport(");
}
