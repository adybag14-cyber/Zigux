const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
const manifest_routes = @import("phase3_manifest_routes.zig");

const MANIFEST_PATH = "zigux/tests/fixtures/phase3_abi_manifest.json";

const ORCHESTRATION_ROUTES = [_][]const u8{
    "scripts/zigux/run_phase3_checks.zig",
    "scripts/zigux/validate_phase3_selftest.zig",
};

const ScriptCommand = struct {
    rel_path: []const u8,
    args: []const []const u8,
    output_markers: []const []const u8,
};

const SELFTEST_COMMANDS = [_]ScriptCommand{
    .{ .rel_path = "scripts/zigux/check_phase3_dev_t_starter_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass", "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_errptr_xarray_starter_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass", "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_xarray_slot_starter_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass", "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_xarray_slot.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_XARRAY_SLOT_SELF_TEST=pass", "PHASE3_XARRAY_SLOT_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_idr_slot_starter_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass", "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_idr_slot.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_IDR_SLOT_SELF_TEST=pass", "PHASE3_IDR_SLOT_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_policy_starter_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass", "PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_policy_dump.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_POLICY_DUMP_SELF_TEST=pass", "PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_VALIDATION_SELF_TEST=pass", "PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_abi.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_ABI_CHECK_SELF_TEST=pass", "PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_abi_support_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass", "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_abi_manifest_replay_routes.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass", "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_shared_tests_routes.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass", "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_readme_tooling_inventory.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass", "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_wrapper_templates.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass", "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_catalog_selftest.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass", "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/run_phase3_checks.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_CHECK_RUNNER_SELF_TEST=pass", "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_validator_support_surface.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST=pass", "PHASE3_VALIDATOR_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_export_uapi_survey.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass", "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass", "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_abi_header_family_survey.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass", "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_policy_unsafe_survey.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass", "PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_low_level_wrapper_survey.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass", "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_low_level_wrappers.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST=pass", "PHASE3_LOW_LEVEL_WRAPPERS_SELF_TEST_CASES=" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_linux_zigux_header_governance.zig", .args = &.{"--self-test"}, .output_markers = &.{"PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_wrapper_templates.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_WRAPPER_SELF_TEST=pass", "PHASE3_WRAPPER_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_selftest_surface.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_SELFTEST_SURFACE_SELF_TEST=pass", "PHASE3_SELFTEST_SURFACE_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_bitmap_cpumask.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass", "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_list_hlist_starter_packet.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass", "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT=" } },
    .{ .rel_path = "scripts/zigux/check_phase3_list_hlist.zig", .args = &.{"--self-test"}, .output_markers = &.{ "PHASE3_LIST_HLIST_SELF_TEST=pass", "PHASE3_LIST_HLIST_SELF_TEST_CASES=" } },
};

fn printTruncated(io: Io, text: []const u8) !void {
    const limit: usize = 1024;
    if (text.len <= limit) {
        try guard.printLine(io, "{s}", .{text});
        return;
    }
    try guard.printLine(io, "{s}...[truncated {d} bytes]", .{ text[0..limit], text.len });
}

fn hasOutputMarker(stdout: []const u8, marker: []const u8) bool {
    if (std.mem.endsWith(u8, marker, "=")) {
        var iter = std.mem.splitScalar(u8, stdout, '\n');
        while (iter.next()) |line| {
            if (std.mem.startsWith(u8, line, marker)) return true;
        }
        return false;
    }
    return std.mem.indexOf(u8, stdout, marker) != null;
}

fn missingOutputMarkers(allocator: std.mem.Allocator, stdout: []const u8, markers: []const []const u8) ![]const []const u8 {
    var missing: std.ArrayList([]const u8) = .empty;
    errdefer missing.deinit(allocator);
    for (markers) |marker| {
        if (!hasOutputMarker(stdout, marker)) try missing.append(allocator, marker);
    }
    return try missing.toOwnedSlice(allocator);
}

fn validateScriptList(io: Io, allocator: std.mem.Allocator, repo_root: []const u8) ![]const []const u8 {
    var missing: std.ArrayList([]const u8) = .empty;
    for (SELFTEST_COMMANDS) |command| {
        const path = try guard.joinPath(allocator, repo_root, command.rel_path);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing selftest script: {s}", .{command.rel_path});
            try missing.append(allocator, issue);
        }
    }
    return try missing.toOwnedSlice(allocator);
}

fn commandToRouteEntry(allocator: std.mem.Allocator, command: ScriptCommand) !manifest_routes.RouteEntry {
    return .{
        .script_path = try allocator.dupe(u8, command.rel_path),
        .args = try dupArgs(allocator, command.args),
    };
}

fn dupArgs(allocator: std.mem.Allocator, args: []const []const u8) ![]const []const u8 {
    const owned = try allocator.alloc([]const u8, args.len);
    for (args, 0..) |arg, index| owned[index] = try allocator.dupe(u8, arg);
    return owned;
}

fn validateManifestSelftestCoverage(io: Io, allocator: std.mem.Allocator, repo_root: []const u8) ![]const []const u8 {
    var issues: std.ArrayList([]const u8) = .empty;

    const loaded = try manifest_routes.loadManifestPythonRoutes(io, allocator, repo_root, MANIFEST_PATH, true, &ORCHESTRATION_ROUTES);
    defer manifest_routes.freeRouteEntries(allocator, loaded.entries);
    defer {
        for (loaded.issues) |issue| allocator.free(issue);
        allocator.free(loaded.issues);
    }

    if (loaded.issues.len != 0) {
        for (loaded.issues) |issue| try issues.append(allocator, try allocator.dupe(u8, issue));
        return try issues.toOwnedSlice(allocator);
    }

    var actual: std.ArrayList(manifest_routes.RouteEntry) = .empty;
    defer {
        for (actual.items) |entry| manifest_routes.freeRouteEntry(allocator, entry);
        actual.deinit(allocator);
    }
    for (SELFTEST_COMMANDS) |command| {
        try actual.append(allocator, try commandToRouteEntry(allocator, command));
    }

    try manifest_routes.appendMissingManifestRouteIssues(
        allocator,
        &issues,
        loaded.entries,
        actual.items,
        "manifest self-test replay route missing from SELFTEST_COMMANDS:",
    );
    return try issues.toOwnedSlice(allocator);
}

fn buildChildArgv(allocator: std.mem.Allocator, zig_bin: []const u8, repo_root: []const u8, command: ScriptCommand) ![]const []const u8 {
    const script_path = try guard.joinPath(allocator, repo_root, command.rel_path);
    const argv = try allocator.alloc([]const u8, 4 + command.args.len);
    argv[0] = zig_bin;
    argv[1] = "run";
    argv[2] = script_path;
    argv[3] = "--";
    for (command.args, 0..) |arg, index| argv[4 + index] = arg;
    return argv;
}

fn runPacket(io: Io, allocator: std.mem.Allocator, repo_root: []const u8, zig_bin: []const u8, process_cwd: ?[]const u8) !u8 {
    const script_issues = try validateScriptList(io, allocator, repo_root);
    defer {
        for (script_issues) |issue| allocator.free(issue);
        allocator.free(script_issues);
    }

    const manifest_issues = try validateManifestSelftestCoverage(io, allocator, repo_root);
    defer {
        for (manifest_issues) |issue| allocator.free(issue);
        allocator.free(manifest_issues);
    }

    if (script_issues.len != 0 or manifest_issues.len != 0) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST=fail", .{});
        for (script_issues) |issue| try guard.printLine(io, "{s}", .{issue});
        for (manifest_issues) |issue| try guard.printLine(io, "{s}", .{issue});
        return 1;
    }

    for (SELFTEST_COMMANDS) |command| {
        const argv = try buildChildArgv(allocator, zig_bin, repo_root, command);
        defer {
            allocator.free(argv[2]);
            allocator.free(argv);
        }

        const output = try guard.runProcessCapture(io, allocator, argv, process_cwd);
        defer allocator.free(output.stdout);
        defer allocator.free(output.stderr);

        if (output.exit_code != 0) {
            try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST=fail", .{});
            var printable = try std.fmt.allocPrint(allocator, "self-test failed: {s}", .{command.rel_path});
            defer allocator.free(printable);
            for (command.args) |arg| {
                const next = try std.fmt.allocPrint(allocator, "{s} {s}", .{ printable, arg });
                allocator.free(printable);
                printable = next;
            }
            try guard.printLine(io, "{s}", .{printable});
            if (output.stdout.len != 0) try printTruncated(io, std.mem.trimEnd(u8, output.stdout, "\r\n"));
            if (output.stderr.len != 0) try printTruncated(io, std.mem.trimEnd(u8, output.stderr, "\r\n"));
            return 1;
        }

        const marker_issues = try missingOutputMarkers(allocator, output.stdout, command.output_markers);
        defer allocator.free(marker_issues);
        if (marker_issues.len != 0) {
            try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST=fail", .{});
            for (marker_issues) |marker| {
                try guard.printLine(io, "missing selftest output marker for {s}: {s}", .{ command.rel_path, marker });
            }
            return 1;
        }
    }

    try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST=pass", .{});
    return 0;
}

fn writeSyntheticScript(
    io: Io,
    allocator: std.mem.Allocator,
    path: []const u8,
    markers: []const []const u8,
    drop_index: ?usize,
    failure_code: ?u8,
) !void {
    var lines: std.ArrayList(u8) = .empty;
    defer lines.deinit(allocator);
    try lines.appendSlice(allocator,
        \\const std = @import("std");
        \\const Io = std.Io;
        \\pub fn main(init: std.process.Init) !void {
        \\    const io = init.io;
        \\    var buffer: [1024]u8 = undefined;
        \\    var writer = Io.File.stdout().writer(io, &buffer);
        \\
    );
    for (markers, 0..) |marker, index| {
        if (drop_index) |wanted| if (wanted == index) continue;
        const line = if (std.mem.endsWith(u8, marker, "="))
            try std.fmt.allocPrint(allocator, "    try writer.interface.print(\"{s}1\\n\", .{{}});\n", .{marker})
        else
            try std.fmt.allocPrint(allocator, "    try writer.interface.print(\"{s}\\n\", .{{}});\n", .{marker});
        defer allocator.free(line);
        try lines.appendSlice(allocator, line);
    }
    if (failure_code) |code| {
        try lines.appendSlice(allocator,
            \\    var err_buffer: [1024]u8 = undefined;
            \\    var err_writer = Io.File.stderr().writer(io, &err_buffer);
            \\    try err_writer.interface.print("synthetic stderr detail\n", .{});
            \\    try err_writer.interface.flush();
            \\
        );
        const exit_line = try std.fmt.allocPrint(allocator, "    std.process.exit({d});\n", .{code});
        defer allocator.free(exit_line);
        try lines.appendSlice(allocator, exit_line);
    } else {
        try lines.appendSlice(allocator, "    try writer.interface.flush();\n");
    }
    try lines.appendSlice(allocator, "}\n");
    try guard.writeUtf8File(io, path, lines.items);
}

fn writeSyntheticManifest(io: Io, allocator: std.mem.Allocator, root: []const u8, replay_routes: ?[]const []const u8) !void {
    const manifest_path = try guard.joinPath(allocator, root, MANIFEST_PATH);
    defer allocator.free(manifest_path);

    var routes: std.ArrayList([]const u8) = .empty;
    defer {
        for (routes.items) |route| allocator.free(route);
        routes.deinit(allocator);
    }

    if (replay_routes) |provided| {
        for (provided) |route| try routes.append(allocator, try allocator.dupe(u8, route));
    } else {
        for (SELFTEST_COMMANDS) |command| {
            var route = try std.fmt.allocPrint(allocator, "zig run {s}", .{command.rel_path});
            for (command.args) |arg| {
                const next = try std.fmt.allocPrint(allocator, "{s} {s}", .{ route, arg });
                allocator.free(route);
                route = next;
            }
            try routes.append(allocator, route);
        }
        const extra = [_][]const u8{
            "zig run scripts/zigux/run_phase3_checks.zig",
            "zig run scripts/zigux/validate_phase3_selftest.zig",
            "zig run scripts/zigux/check_phase3_abi.zig",
            "zig build phase3-test --build-file zigux/tests/build.zig",
        };
        for (extra) |route| try routes.append(allocator, try allocator.dupe(u8, route));
    }

    var json_lines: std.ArrayList(u8) = .empty;
    defer json_lines.deinit(allocator);
    try json_lines.appendSlice(allocator, "{\n  \"replay_routes\": [\n");
    for (routes.items, 0..) |route, index| {
        const suffix = if (index + 1 == routes.items.len) "\n" else ",\n";
        const line = try std.fmt.allocPrint(allocator, "    \"{s}\"{s}", .{ route, suffix });
        defer allocator.free(line);
        try json_lines.appendSlice(allocator, line);
    }
    try json_lines.appendSlice(allocator, "  ]\n}\n");
    try guard.writeUtf8File(io, manifest_path, json_lines.items);
}

fn populateRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    var marker_map: std.StringHashMap(std.ArrayList([]const u8)) = .init(allocator);
    defer {
        var it = marker_map.iterator();
        while (it.next()) |entry| {
            for (entry.value_ptr.items) |marker| allocator.free(marker);
            entry.value_ptr.deinit(allocator);
            allocator.free(entry.key_ptr.*);
        }
        marker_map.deinit();
    }

    for (SELFTEST_COMMANDS) |command| {
        const gop = try marker_map.getOrPut(command.rel_path);
        if (!gop.found_existing) {
            gop.value_ptr.* = .empty;
            gop.key_ptr.* = try allocator.dupe(u8, command.rel_path);
        }
        for (command.output_markers) |marker| {
            try gop.value_ptr.append(allocator, try allocator.dupe(u8, marker));
        }
    }

    var it = marker_map.iterator();
    while (it.next()) |entry| {
        const path = try guard.joinPath(allocator, root, entry.key_ptr.*);
        defer allocator.free(path);
        try writeSyntheticScript(io, allocator, path, entry.value_ptr.items, null, null);
    }

    try writeSyntheticManifest(io, allocator, root, null);
}

fn commandIndex(script_name: []const u8) !usize {
    for (SELFTEST_COMMANDS, 0..) |command, index| {
        if (std.mem.eql(u8, std.fs.path.basename(command.rel_path), script_name)) return index;
    }
    return error.MissingCommand;
}

fn expectMissingScript(io: Io, allocator: std.mem.Allocator, root: []const u8, zig_bin: []const u8, script_name: []const u8) !bool {
    try populateRepo(io, allocator, root);
    const index = try commandIndex(script_name);
    const missing_path = try guard.joinPath(allocator, root, SELFTEST_COMMANDS[index].rel_path);
    defer allocator.free(missing_path);
    guard.deleteFile(io, missing_path) catch {};
    const expected = try std.fmt.allocPrint(allocator, "missing selftest script: {s}", .{SELFTEST_COMMANDS[index].rel_path});
    defer allocator.free(expected);
    const issues = try validateScriptList(io, allocator, root);
    defer {
        for (issues) |issue| allocator.free(issue);
        allocator.free(issues);
    }
    for (issues) |issue| {
        if (std.mem.eql(u8, issue, expected)) return true;
    }
    _ = zig_bin;
    return false;
}

fn expectMissingMarker(io: Io, allocator: std.mem.Allocator, root: []const u8, zig_bin: []const u8, script_name: []const u8, marker_index: usize) !bool {
    try populateRepo(io, allocator, root);
    const index = try commandIndex(script_name);
    const command = SELFTEST_COMMANDS[index];
    const path = try guard.joinPath(allocator, root, command.rel_path);
    defer allocator.free(path);
    try writeSyntheticScript(io, allocator, path, command.output_markers, marker_index, null);

    const argv = try buildChildArgv(allocator, zig_bin, root, command);
    defer {
        allocator.free(argv[2]);
        allocator.free(argv);
    }

    const output = try guard.runProcessCapture(io, allocator, argv, null);
    defer allocator.free(output.stdout);
    defer allocator.free(output.stderr);
    if (output.exit_code != 0) return true;
    const marker_issues = try missingOutputMarkers(allocator, output.stdout, command.output_markers);
    defer allocator.free(marker_issues);
    return marker_issues.len != 0;
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator, zig_bin: []const u8) !u8 {
    var case_count: usize = 0;
    var tmp = try guard.TempWorkspace.init(io, allocator, "phase3_validate_selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);

    try populateRepo(io, allocator, root);

    case_count += 1;
    const initial_script_issues = try validateScriptList(io, allocator, root);
    defer {
        for (initial_script_issues) |issue| allocator.free(issue);
        allocator.free(initial_script_issues);
    }
    if (initial_script_issues.len != 0) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected synthetic self-test script set to validate", .{});
        return 1;
    }

    case_count += 1;
    const manifest_missing = try validateManifestSelftestCoverage(io, allocator, root);
    defer {
        for (manifest_missing) |issue| allocator.free(issue);
        allocator.free(manifest_missing);
    }
    if (manifest_missing.len != 0) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected synthetic self-test manifest coverage to validate", .{});
        for (manifest_missing) |issue| try guard.printLine(io, "{s}", .{issue});
        return 1;
    }

    case_count += 1;
    if ((try runPacket(io, allocator, root, zig_bin, null)) != 0) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected synthetic self-test packet to pass", .{});
        return 1;
    }

    for (SELFTEST_COMMANDS) |command| {
        case_count += 1;
        const script_name = std.fs.path.basename(command.rel_path);
        if (!(try expectMissingScript(io, allocator, root, zig_bin, script_name))) {
            try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
            try guard.printLine(io, "expected missing script to be reported: {s}", .{command.rel_path});
            return 1;
        }
    }

    case_count += 1;
    try populateRepo(io, allocator, root);
    const manifest_only_route = "zig run scripts/zigux/manifest_only_selftest.zig -- --self-test";
    try writeSyntheticManifest(io, allocator, root, &.{manifest_only_route});
    const expected_manifest_gap = "manifest self-test replay route missing from SELFTEST_COMMANDS: scripts/zigux/manifest_only_selftest.zig --self-test";
    const manifest_gap_issues = try validateManifestSelftestCoverage(io, allocator, root);
    defer {
        for (manifest_gap_issues) |issue| allocator.free(issue);
        allocator.free(manifest_gap_issues);
    }
    var found_gap = false;
    for (manifest_gap_issues) |issue| {
        if (std.mem.eql(u8, issue, expected_manifest_gap)) found_gap = true;
    }
    if (!found_gap) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected manifest-only self-test replay route omission to be reported", .{});
        return 1;
    }

    case_count += 1;
    try populateRepo(io, allocator, root);
    const manifest_path = try guard.joinPath(allocator, root, MANIFEST_PATH);
    defer allocator.free(manifest_path);
    guard.deleteFile(io, manifest_path) catch {};
    const expected_manifest_missing = try std.fmt.allocPrint(allocator, "missing phase3 manifest: {s}", .{MANIFEST_PATH});
    defer allocator.free(expected_manifest_missing);
    const missing_manifest_issues = try validateManifestSelftestCoverage(io, allocator, root);
    defer {
        for (missing_manifest_issues) |issue| allocator.free(issue);
        allocator.free(missing_manifest_issues);
    }
    var found_missing_manifest = false;
    for (missing_manifest_issues) |issue| {
        if (std.mem.eql(u8, issue, expected_manifest_missing)) found_missing_manifest = true;
    }
    if (!found_missing_manifest) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected missing manifest to be reported", .{});
        return 1;
    }

    case_count += 1;
    try populateRepo(io, allocator, root);
    const failing_index = try commandIndex("check_phase3_low_level_wrappers.zig");
    const failing_command = SELFTEST_COMMANDS[failing_index];
    const failing_path = try guard.joinPath(allocator, root, failing_command.rel_path);
    defer allocator.free(failing_path);
    try writeSyntheticScript(io, allocator, failing_path, failing_command.output_markers, null, 7);
    if ((try runPacket(io, allocator, root, zig_bin, null)) != 1) {
        try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected failing child self-test to fail the packet", .{});
        return 1;
    }

    try populateRepo(io, allocator, root);

    const marker_cases = [_]struct { script_name: []const u8, marker_index: usize }{
        .{ .script_name = "run_phase3_checks.zig", .marker_index = 0 },
        .{ .script_name = "validate_phase3.zig", .marker_index = 1 },
        .{ .script_name = "check_phase3_idr_slot_starter_packet.zig", .marker_index = 0 },
        .{ .script_name = "check_phase3_idr_slot_starter_packet.zig", .marker_index = 1 },
        .{ .script_name = "check_phase3_idr_slot.zig", .marker_index = 0 },
        .{ .script_name = "check_phase3_idr_slot.zig", .marker_index = 1 },
        .{ .script_name = "check_phase3_list_hlist.zig", .marker_index = 0 },
        .{ .script_name = "check_phase3_list_hlist.zig", .marker_index = 1 },
    };
    for (marker_cases) |case_item| {
        case_count += 1;
        if (!(try expectMissingMarker(io, allocator, root, zig_bin, case_item.script_name, case_item.marker_index))) {
            try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=fail", .{});
            try guard.printLine(io, "expected missing self-test output marker to fail the packet: {s} marker {d}", .{ case_item.script_name, case_item.marker_index });
            return 1;
        }
    }

    try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE3_VALIDATE_SELFTEST_SELF_TEST_CASE_COUNT={d}", .{case_count});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var repo_root: ?[]const u8 = null;
    var zig_bin: ?[]const u8 = null;

    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            repo_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            zig_bin = args[index];
            continue;
        }
        std.process.exit(2);
    }

    const root = repo_root orelse try guard.repoRootFromScript(allocator);
    defer if (repo_root == null) allocator.free(root);

    const environment_zig = init.environ_map.get("ZIG");
    const zig = zig_bin orelse environment_zig orelse try guard.findZigExecutable(io, allocator, root, null);
    defer if (zig_bin == null and environment_zig == null) allocator.free(zig);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator, zig));
    }

    std.process.exit(try runPacket(io, allocator, root, zig, root));
}