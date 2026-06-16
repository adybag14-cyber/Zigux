// Ported from check-phase1-host-tools-smoke.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_HOST_TOOLS_SMOKE_SELF_TEST=pass";

const BUILD_REL = "zigux/tests/build.zig";

const EXPECTED_BUILD_LINES = [_][]const u8{
    "fn addPhase1HostToolsSmoke(",
    ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/argv_split.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/cmdline.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/ctype.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/hweight.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/list_sort.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/rbtree.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/string.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/slab.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/str_error_r.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/vsprintf.zig\"),",
    ".root_source_file = b.path(\"../../tools/lib/zalloc.zig\"),",
    "bitmap_module.addImport(\"find_bit\", find_bit_module);",
    "root_module.addImport(\"argv_split\", argv_split_module);",
    "root_module.addImport(\"cmdline\", cmdline_module);",
    "root_module.addImport(\"find_bit\", find_bit_module);",
    "root_module.addImport(\"bitmap\", bitmap_module);",
    "root_module.addImport(\"ctype\", ctype_module);",
    "root_module.addImport(\"hweight\", hweight_module);",
    "root_module.addImport(\"list_sort\", list_sort_module);",
    "root_module.addImport(\"rbtree\", rbtree_module);",
    "root_module.addImport(\"string\", string_module);",
    "root_module.addImport(\"slab\", slab_module);",
    "root_module.addImport(\"str_error_r\", str_error_r_module);",
    "root_module.addImport(\"vsprintf\", vsprintf_module);",
    "root_module.addImport(\"zalloc\", zalloc_module);",
    ".name = \"phase1-host-tools-smoke\",",
    "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);",
    "const phase1_step = b.step(",
    "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\",",
    "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    "test_step.dependOn(&phase1_host_tools_smoke.step);",
};

const EXPECTED_SMOKE_LINES = [_][]const u8{
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
    "fn returnedSerial(node: ?*rbtree.Node) i32 {",
    "test \"phase1 host-tools smoke imports the live helper modules\" {",
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
    "test \"phase1 host-tools smoke exercises live helper behavior\" {",
    "var split = try argv_split.argv_split(std.testing.allocator, \"  zigux   host\ttools  \");",
    "const parsed = cmdline.memparse(\"64K tail\");",
    "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,quiet\", \"quiet\"));",
    "try std.testing.expect(ctype.isalpha('Q'));",
    "try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));",
    "const allocated = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;",
    "try std.testing.expectEqualStrings(\"Permission denied\", str_error_r.strErrorR(13, &error_buffer));",
    "const rendered_len = vsprintf.scnprintf(&render_buffer, \"{s}:{d}\", .{ \"zigux\", 9 });",
    "var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);",
    "list_sort.listSort(null, &list_head, list_cmp);",
    "bitmap.setRange(&map, word_bits - 1, 3);",
    "try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&map, nbits));",
    "const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);",
    "try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, \"auto\"));",
    "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);",
    "var cached_leftmost_entries = [_]RbtreeSmokeEntry{",
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "cached_leftmost_return_serials[0] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[0].node, &cached_leftmost_root, RbtreeSmokeEntry.less));",
    "cached_leftmost_return_serials[1] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[1].node, &cached_leftmost_root, RbtreeSmokeEntry.less));",
    "cached_leftmost_return_serials[2] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[2].node, &cached_leftmost_root, RbtreeSmokeEntry.less));",
    "cached_leftmost_return_serials[3] = returnedSerial(rbtree.addCached(&cached_leftmost_entries[3].node, &cached_leftmost_root, RbtreeSmokeEntry.less));",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "try std.testing.expectEqual(@as(?*rbtree.Node, &cached_leftmost_entries[2].node), rbtree.firstCached(&cached_leftmost_root));",
    "try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.addCached(&cached_entries[1].node, &cached_root, RbtreeSmokeEntry.less));",
    "try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.eraseCached(&cached_entries[1].node, &cached_root));",
};

const SMOKE_REL = "zigux/tests/phase1_host_tools_smoke.zig";

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    {
        const relative_path = "zigux/tests/build.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "zigux/tests/build.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_BUILD_LINES) |marker| {
            const count = guard.countOccurrences(text, marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:actual_count={d}:{s}", .{ relative_path, count, marker });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_SMOKE_LINES) |marker| {
            const count = guard.countOccurrences(text, marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:actual_count={d}:{s}", .{ relative_path, count, marker });
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    {
        const relative_path = "zigux/tests/build.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_BUILD_LINES) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_SMOKE_LINES) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_EXPECTED_BUILD_MARKER_COUNT={d}", .{@as(usize, EXPECTED_BUILD_LINES.len)});
    try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_EXPECTED_SMOKE_MARKER_COUNT={d}", .{@as(usize, EXPECTED_SMOKE_LINES.len)});
    std.process.exit(0);
}
