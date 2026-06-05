const std = @import("std");

const Check = struct {
    label: []const u8,
    needle: []const u8,
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(text: []const u8, check: Check) !void {
    errdefer std.debug.print("missing marker: {s}\n{s}\n", .{ check.label, check.needle });
    try std.testing.expect(std.mem.indexOf(u8, text, check.needle) != null);
}

fn expectContainsAll(text: []const u8, checks: []const Check) !void {
    for (checks) |check| {
        try expectContains(text, check);
    }
}

test "shared reminder checker owns the current Lane 15 packet roster" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, "scripts/zigux/check-phase1-shared-reminder-packet.py");
    defer allocator.free(checker);

    try expectContainsAll(checker, &.{
        .{ .label = "guard purpose", .needle = "Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow." },
        .{ .label = "closure note required", .needle = "\"Documentation/zigux/phase1-closure.md\"," },
        .{ .label = "lane sequencing required", .needle = "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\"," },
        .{ .label = "shared reminder self required", .needle = "\"scripts/zigux/check-phase1-shared-reminder-packet.py\"," },
        .{ .label = "closure validator required", .needle = "\"scripts/zigux/validate-phase1-closure.py\"," },
        .{ .label = "tests root required", .needle = "\"zigux/tests/build.zig\"," },
        .{ .label = "phase1 smoke required", .needle = "\"zigux/tests/phase1_host_tools_smoke.zig\"," },
        .{ .label = "workflow required", .needle = "\".github/workflows/zigux-bootstrap.yml\"," },
        .{ .label = "marker table", .needle = "MARKERS = {" },
        .{ .label = "workflow line exactness", .needle = "collect_stripped_line_markers(text, relative_path, markers)" },
        .{ .label = "pass output", .needle = "PHASE1_SHARED_REMINDER_PACKET=pass" },
        .{ .label = "self-test output", .needle = "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass" },
    });
}

test "closure note and docs root name the shared reminder checker as current proof" {
    const allocator = std.testing.allocator;
    const closure = try readFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure);
    const docs_root = try readFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    const tests_readme = try readFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    try expectContainsAll(closure, &.{
        .{ .label = "current reminder packet marker", .needle = "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md" },
        .{ .label = "shared reminder checker in closure", .needle = "scripts/zigux/check-phase1-shared-reminder-packet.py" },
        .{ .label = "current master makefile posture", .needle = "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`" },
        .{ .label = "shared tests route", .needle = "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`" },
    });

    try expectContainsAll(docs_root, &.{
        .{ .label = "docs root shared reminder", .needle = "- `scripts/zigux/check-phase1-shared-reminder-packet.py`" },
        .{ .label = "docs root current packet wording", .needle = "the current Phase 1 reminder packet explicit from the docs root" },
    });

    try expectContainsAll(tests_readme, &.{
        .{ .label = "tests root current packet", .needle = "current direct-readback Phase 1 reminder packet:" },
        .{ .label = "tests root shared reminder", .needle = "- `scripts/zigux/check-phase1-shared-reminder-packet.py`" },
        .{ .label = "tests root smoke route", .needle = "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`" },
    });
}

test "shared tests root and smoke replay keep every Phase 1 helper family imported" {
    const allocator = std.testing.allocator;
    const build_root = try readFile(allocator, "zigux/tests/build.zig");
    defer allocator.free(build_root);
    const smoke = try readFile(allocator, "zigux/tests/phase1_host_tools_smoke.zig");
    defer allocator.free(smoke);

    try expectContainsAll(build_root, &.{
        .{ .label = "smoke root", .needle = "fn addPhase1HostToolsSmoke(" },
        .{ .label = "slab module", .needle = "const slab_module = b.createModule(.{" },
        .{ .label = "str_error_r module", .needle = "const str_error_r_module = b.createModule(.{" },
        .{ .label = "vsprintf module", .needle = "const vsprintf_module = b.createModule(.{" },
        .{ .label = "zalloc module", .needle = "const zalloc_module = b.createModule(.{" },
        .{ .label = "smoke step", .needle = ".name = \"phase1-host-tools-smoke\"," },
    });

    try expectContainsAll(smoke, &.{
        .{ .label = "argv import", .needle = "const argv_split = @import(\"argv_split\");" },
        .{ .label = "slab import", .needle = "const slab = @import(\"slab\");" },
        .{ .label = "str_error_r import", .needle = "const str_error_r = @import(\"str_error_r\");" },
        .{ .label = "vsprintf import", .needle = "const vsprintf = @import(\"vsprintf\");" },
        .{ .label = "zalloc import", .needle = "const zalloc = @import(\"zalloc\");" },
        .{ .label = "bitmap witness", .needle = "try std.testing.expect(@hasDecl(bitmap, \"setRange\"));" },
        .{ .label = "slab witness", .needle = "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));" },
        .{ .label = "vsprintf witness", .needle = "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));" },
        .{ .label = "zalloc witness", .needle = "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));" },
    });
}

test "workflow keeps shared reminder validation before closure validation" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const shared_self = std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test") orelse return error.MissingSharedReminderSelfTest;
    const shared_check = std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n") orelse return error.MissingSharedReminderCheck;
    const closure_self = std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/validate-phase1-closure.py --self-test") orelse return error.MissingClosureSelfTest;
    const closure_check = std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/validate-phase1-closure.py\n") orelse return error.MissingClosureCheck;

    try std.testing.expect(shared_self < shared_check);
    try std.testing.expect(shared_check < closure_self);
    try std.testing.expect(closure_self < closure_check);
}
