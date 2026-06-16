// Ported from check-phase1-host-tools-smoke-alignment.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_SELF_TEST=pass";

const EXPECTED_BUILD_HELPER_LINES = [_][]const u8{
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
};

const EXPECTED_BUILD_MARKERS = [_][]const u8{
    "fn addPhase1HostToolsSmoke(",
    ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),",
    "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);",
    "\"phase1-host-tools-smoke\",",
    "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\",",
    "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    "test_step.dependOn(&phase1_host_tools_smoke.step);",
};

const EXPECTED_CLOSURE_MARKERS = [_][]const u8{
    "The current shared tests-root closure route is narrow on purpose:",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "That route keeps a minimal shared import-and-wire smoke check alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.",
};

const EXPECTED_HELPERS = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const EXPECTED_SMOKE_BEHAVIOR_MARKERS = [_][]const u8{
    "const parsed = cmdline.memparse(\"64K tail\");",
    "const signed = cmdline.memparse(\"-2K tail\");",
    "const saturated = cmdline.memparse(\"+9223372036854775808\");",
    "const rendered_len = vsprintf.scnprintf(&render_buffer, \"{s}:{d}\", .{ \"zigux\", 9 });",
    "const padded_len = vsprintf.scnprintfPad(&padded_render, 10, \"id={d}\", .{7});",
    "var tree_root = rbtree.Root.init();",
    "var cached_root = rbtree.RootCached.init();",
    "bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0);",
    "bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);",
    "const sysfs = [_][]const u8{ \"disabled\", \"auto\\n\", \"manual\" };",
};

const EXPECTED_SMOKE_DECL_CHECKS = [_][]const u8{
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

const EXPECTED_SMOKE_IMPORTS = [_][]const u8{
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
};

const EXPECTED_SMOKE_TEST_ANCHORS = [_][]const u8{
    "test \"phase1 host-tools smoke imports the live helper modules\" {",
    "test \"phase1 host-tools smoke exercises live helper behavior\" {",
    "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\" {",
};

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const PHASE1_SMOKE_REL = "zigux/tests/phase1_host_tools_smoke.zig";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase1-closure.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
};

const TESTS_BUILD_REL = "zigux/tests/build.zig";

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
        const relative_path = "Documentation/zigux/phase1-closure.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
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
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        const parsed = try guard.parseJsonValue(allocator, text);
        defer parsed.deinit();
    }

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        for (EXPECTED_CLOSURE_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        for (EXPECTED_BUILD_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        for (EXPECTED_BUILD_HELPER_LINES) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        for (EXPECTED_SMOKE_BEHAVIOR_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
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
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_CLOSURE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_BUILD_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_BUILD_HELPER_LINES) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_SMOKE_BEHAVIOR_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "zigux/tests/build.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    std.process.exit(0);
}
