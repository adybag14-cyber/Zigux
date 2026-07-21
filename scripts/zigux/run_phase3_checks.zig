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

const CHECK_COMMANDS = [_]ScriptCommand{
    .{ .rel_path = "scripts/zigux/check_phase3_dev_t_starter_packet.zig", .args = &.{}, .output_markers = &.{"PHASE3_DEV_T_STARTER_PACKET=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_errptr_xarray_starter_packet.zig", .args = &.{}, .output_markers = &.{"PHASE3_ERRPTR_XARRAY_STARTER_PACKET=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_xarray_slot_starter_packet.zig", .args = &.{}, .output_markers = &.{"PHASE3_XARRAY_SLOT_STARTER_PACKET=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_xarray_slot.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_xarray_slot_dump.zig", "validated zigux/tests/fixtures/phase3_xarray_slot_manifest.json" } },
    .{ .rel_path = "scripts/zigux/check_phase3_idr_slot_starter_packet.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_idr_slot_starter_packet.zig", "validated zigux/tests/phase3_idr_slot_starter_packet_build.zig" } },
    .{ .rel_path = "scripts/zigux/check_phase3_idr_slot.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_idr_slot_dump.zig", "validated zigux/tests/fixtures/phase3_idr_slot/expected.json", "validated zigux/tests/fixtures/phase3_idr_slot_manifest.json" } },
    .{ .rel_path = "scripts/zigux/check_phase3_policy_starter_packet.zig", .args = &.{}, .output_markers = &.{"PHASE3_POLICY_STARTER_PACKET=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_policy_dump.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_policy_dump.zig", "validated zigux/tests/fixtures/phase3_policy_dump_expected.txt" } },
    .{ .rel_path = "scripts/zigux/validate_phase3.zig", .args = &.{}, .output_markers = &.{"PHASE3_VALIDATION=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_abi.zig", .args = &.{}, .output_markers = &.{"PHASE3_ABI_CHECK=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_abi_support_packet.zig", .args = &.{}, .output_markers = &.{"PHASE3_ABI_SUPPORT_PACKET=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_shared_tests_routes.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/build.zig", "validated scripts/zigux/validate_phase3_selftest.zig" } },
    .{ .rel_path = "scripts/zigux/check_phase3_readme_tooling_inventory.zig", .args = &.{}, .output_markers = &.{"validated scripts/zigux/README.md"} },
    .{ .rel_path = "scripts/zigux/check_phase3_wrapper_templates.zig", .args = &.{}, .output_markers = &.{ "validated scripts/zigux/check_phase3_wrapper_templates.zig", "PHASE3_WRAPPER_TEMPLATES_CHECK=pass" } },
    .{ .rel_path = "scripts/zigux/check_phase3_catalog_selftest.zig", .args = &.{}, .output_markers = &.{ "validated scripts/zigux/phase3_catalog.zig", "PHASE3_CATALOG_SELFTEST_CHECK=pass" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_validator_support_surface.zig", .args = &.{}, .output_markers = &.{ "validated Documentation/zigux/phase3-validator-support-surface.md", "validated Documentation/zigux/phase3-shared-reminder-gap.md" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_export_uapi_survey.zig", .args = &.{}, .output_markers = &.{ "validated Documentation/zigux/phase3-export-uapi-boundary-survey.md", "PHASE3_EXPORT_UAPI_SURVEY=pass" } },
    .{ .rel_path = "scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_export_uapi_c_header_smoke.c", "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_abi_header_family_survey.zig", .args = &.{}, .output_markers = &.{ "validated Documentation/zigux/phase3-abi-header-family-survey.md", "PHASE3_ABI_HEADER_FAMILY_SURVEY=pass" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_policy_unsafe_survey.zig", .args = &.{}, .output_markers = &.{ "validated Documentation/zigux/phase3-policy-unsafe-boundary-survey.md", "PHASE3_POLICY_UNSAFE_SURVEY=pass" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_low_level_wrapper_survey.zig", .args = &.{}, .output_markers = &.{ "validated Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md", "PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass" } },
    .{ .rel_path = "scripts/zigux/check_phase3_low_level_wrappers.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_low_level_wrappers.zig", "validated zigux/tests/phase3_low_level_wrappers_build.zig", "validated zigux/tests/build.zig", "validated zigux/Makefile", "validated zigux/helpers/atomic.zig", "validated zigux/helpers/barrier.zig" } },
    .{ .rel_path = "scripts/zigux/validate_phase3_linux_zigux_header_governance.zig", .args = &.{}, .output_markers = &.{"validated Documentation/zigux/phase3-linux-zigux-header-governance.md"} },
    .{ .rel_path = "scripts/zigux/check_phase3_selftest_surface.zig", .args = &.{}, .output_markers = &.{"validated scripts/zigux/README.md"} },
    .{ .rel_path = "scripts/zigux/check_phase3_abi_manifest_replay_routes.zig", .args = &.{}, .output_markers = &.{"PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass"} },
    .{ .rel_path = "scripts/zigux/check_phase3_bitmap_cpumask.zig", .args = &.{}, .output_markers = &.{ "PHASE3_BITMAP_CPUMASK_PACKET=pass", "validated zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json", "validated zigux/tests/phase3_bitmap_cpumask_starter_packet.zig" } },
    .{ .rel_path = "scripts/zigux/check_phase3_list_hlist_starter_packet.zig", .args = &.{}, .output_markers = &.{ "validated zigux/helpers/list_view.zig", "validated zigux/helpers/hlist_view.zig", "validated zigux/tests/phase3_list_hlist_starter_packet.zig", "validated zigux/tests/phase3_list_hlist_starter_packet_build.zig", "validated zigux/tests/fixtures/phase3_list_hlist_manifest.json" } },
    .{ .rel_path = "scripts/zigux/check_phase3_list_hlist.zig", .args = &.{}, .output_markers = &.{ "validated zigux/tests/phase3_list_hlist_dump.zig", "validated zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c", "validated zigux/tests/fixtures/phase3_list_hlist/expected.json", "validated zigux/tests/fixtures/phase3_list_hlist_manifest.json" } },
};

const SELF_TEST_MISSING_CASES = [_]struct { index: usize, message: []const u8 }{
    .{ .index = 0, .message = "expected missing leading script was not reported" },
    .{ .index = 1, .message = "expected errptr-xarray script omission was not reported" },
    .{ .index = 2, .message = "expected xarray-slot starter script omission was not reported" },
    .{ .index = 3, .message = "expected xarray-slot dump script omission was not reported" },
    .{ .index = 4, .message = "expected idr-slot starter script omission was not reported" },
    .{ .index = 5, .message = "expected idr-slot dump script omission was not reported" },
    .{ .index = 6, .message = "expected policy starter script omission was not reported" },
    .{ .index = 7, .message = "expected policy dump script omission was not reported" },
    .{ .index = 8, .message = "expected shared ABI validator omission was not reported" },
    .{ .index = 9, .message = "expected shared ABI checker omission was not reported" },
    .{ .index = 10, .message = "expected shared ABI support-checker omission was not reported" },
    .{ .index = 11, .message = "expected shared-tests-routes script omission was not reported" },
    .{ .index = 12, .message = "expected readme-tooling script omission was not reported" },
    .{ .index = 13, .message = "expected wrapper-template script omission was not reported" },
    .{ .index = 14, .message = "expected catalog-selftest script omission was not reported" },
    .{ .index = 15, .message = "expected validator-support script omission was not reported" },
    .{ .index = 16, .message = "expected export-uapi survey script omission was not reported" },
    .{ .index = 17, .message = "expected export-uapi c-header smoke omission was not reported" },
    .{ .index = 18, .message = "expected abi-header-family survey script omission was not reported" },
    .{ .index = 19, .message = "expected policy-unsafe survey script omission was not reported" },
    .{ .index = 20, .message = "expected low-level-wrapper script omission was not reported" },
    .{ .index = 21, .message = "expected low-level-wrapper compile-route script omission was not reported" },
    .{ .index = 22, .message = "expected linux-zigux header-governance script omission was not reported" },
    .{ .index = 23, .message = "expected selftest-surface script omission was not reported" },
    .{ .index = 24, .message = "expected abi manifest replay-routes script omission was not reported" },
    .{ .index = 25, .message = "expected bitmap-cpumask script omission was not reported" },
    .{ .index = 26, .message = "expected list-hlist starter script omission was not reported" },
    .{ .index = 27, .message = "expected full list-hlist script omission was not reported" },
};

fn missingOutputMarkers(allocator: std.mem.Allocator, stdout: []const u8, markers: []const []const u8) ![]const []const u8 {
    var missing: std.ArrayList([]const u8) = .empty;
    errdefer missing.deinit(allocator);
    for (markers) |marker| {
        if (std.mem.indexOf(u8, stdout, marker) == null) try missing.append(allocator, marker);
    }
    return try missing.toOwnedSlice(allocator);
}

fn validateScriptList(io: Io, allocator: std.mem.Allocator, repo_root: []const u8) ![]const []const u8 {
    var missing: std.ArrayList([]const u8) = .empty;
    for (CHECK_COMMANDS) |command| {
        const path = try guard.joinPath(allocator, repo_root, command.rel_path);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing phase3 check script: {s}", .{command.rel_path});
            try missing.append(allocator, issue);
        }
    }
    return try missing.toOwnedSlice(allocator);
}

fn validateManifestPythonCoverage(io: Io, allocator: std.mem.Allocator, repo_root: []const u8) ![]const []const u8 {
    var issues: std.ArrayList([]const u8) = .empty;

    const loaded = try manifest_routes.loadManifestPythonRoutes(io, allocator, repo_root, MANIFEST_PATH, false, &ORCHESTRATION_ROUTES);
    defer manifest_routes.freeRouteEntries(allocator, loaded.entries);
    defer {
        for (loaded.issues) |issue| allocator.free(issue);
        allocator.free(loaded.issues);
    }

    if (loaded.issues.len != 0) {
        for (loaded.issues) |issue| try issues.append(allocator, try allocator.dupe(u8, issue));
        return try issues.toOwnedSlice(allocator);
    }

    var actual_scripts: std.ArrayList([]const u8) = .empty;
    defer {
        for (actual_scripts.items) |script| allocator.free(script);
        actual_scripts.deinit(allocator);
    }
    for (CHECK_COMMANDS) |command| {
        try actual_scripts.append(allocator, try allocator.dupe(u8, command.rel_path));
    }

    var expected_scripts: std.ArrayList([]const u8) = .empty;
    defer {
        for (expected_scripts.items) |script| allocator.free(script);
        expected_scripts.deinit(allocator);
    }
    for (loaded.entries) |entry| {
        try expected_scripts.append(allocator, try allocator.dupe(u8, entry.script_path));
    }

    try manifest_routes.appendMissingManifestScriptIssues(
        allocator,
        &issues,
        expected_scripts.items,
        actual_scripts.items,
        "manifest python replay route missing from CHECK_COMMANDS:",
    );
    return try issues.toOwnedSlice(allocator);
}

fn buildChildArgv(allocator: std.mem.Allocator, zig_bin: []const u8, repo_root: []const u8, command: ScriptCommand) ![]const []const u8 {
    const script_path = try guard.joinPath(allocator, repo_root, command.rel_path);
    if (command.args.len == 0) {
        const argv = try allocator.alloc([]const u8, 3);
        argv[0] = zig_bin;
        argv[1] = "run";
        argv[2] = script_path;
        return argv;
    }
    const argv = try allocator.alloc([]const u8, 4 + command.args.len);
    argv[0] = zig_bin;
    argv[1] = "run";
    argv[2] = script_path;
    argv[3] = "--";
    for (command.args, 0..) |arg, index| argv[4 + index] = arg;
    return argv;
}

fn printTruncated(io: Io, text: []const u8) !void {
    const limit: usize = 1024;
    if (text.len <= limit) {
        try guard.printLine(io, "{s}", .{text});
        return;
    }
    try guard.printLine(io, "{s}...[truncated {d} bytes]", .{ text[0..limit], text.len });
}

fn runSingleCheck(io: Io, allocator: std.mem.Allocator, repo_root: []const u8, zig_bin: []const u8, command: ScriptCommand, process_cwd: ?[]const u8) !guard.ProcessOutput {
    const argv = try buildChildArgv(allocator, zig_bin, repo_root, command);
    defer {
        allocator.free(argv[2]);
        allocator.free(argv);
    }
    return try guard.runProcessCapture(io, allocator, argv, process_cwd);
}

fn expectCheckFailure(io: Io, allocator: std.mem.Allocator, root: []const u8, zig_bin: []const u8, command_index: usize, markers: []const []const u8, message: []const u8) !u8 {
    try populateRepo(io, allocator, root);
    const command = CHECK_COMMANDS[command_index];
    const target_path = try guard.joinPath(allocator, root, command.rel_path);
    defer allocator.free(target_path);
    try writeSyntheticScript(io, allocator, target_path, markers, null);

    const output = try runSingleCheck(io, allocator, root, zig_bin, command, null);
    defer allocator.free(output.stdout);
    defer allocator.free(output.stderr);

    const marker_issues = try missingOutputMarkers(allocator, output.stdout, command.output_markers);
    defer allocator.free(marker_issues);
    const failed = output.exit_code != 0 or marker_issues.len != 0;
    if (!failed) {
        try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
        try guard.printLine(io, "{s}", .{message});
        return 1;
    }
    return 0;
}

fn runPacket(io: Io, allocator: std.mem.Allocator, repo_root: []const u8, zig_bin: []const u8, process_cwd: ?[]const u8) !u8 {
    const script_issues = try validateScriptList(io, allocator, repo_root);
    defer {
        for (script_issues) |issue| allocator.free(issue);
        allocator.free(script_issues);
    }

    const manifest_issues = try validateManifestPythonCoverage(io, allocator, repo_root);
    defer {
        for (manifest_issues) |issue| allocator.free(issue);
        allocator.free(manifest_issues);
    }

    if (script_issues.len != 0 or manifest_issues.len != 0) {
        try guard.printLine(io, "PHASE3_CHECK_RUNNER=fail", .{});
        for (script_issues) |issue| try guard.printLine(io, "{s}", .{issue});
        for (manifest_issues) |issue| try guard.printLine(io, "{s}", .{issue});
        return 1;
    }

    for (CHECK_COMMANDS) |command| {
        const argv = try buildChildArgv(allocator, zig_bin, repo_root, command);
        defer {
            allocator.free(argv[2]);
            allocator.free(argv);
        }

        const output = try guard.runProcessCapture(io, allocator, argv, process_cwd);
        defer allocator.free(output.stdout);
        defer allocator.free(output.stderr);

        if (output.exit_code != 0) {
            try guard.printLine(io, "PHASE3_CHECK_RUNNER=fail", .{});
            try guard.printLine(io, "phase3 check failed: {s}", .{command.rel_path});
            if (output.stdout.len != 0) try printTruncated(io, std.mem.trimEnd(u8, output.stdout, "\r\n"));
            if (output.stderr.len != 0) try printTruncated(io, std.mem.trimEnd(u8, output.stderr, "\r\n"));
            return 1;
        }

        const marker_issues = try missingOutputMarkers(allocator, output.stdout, command.output_markers);
        defer allocator.free(marker_issues);
        if (marker_issues.len != 0) {
            try guard.printLine(io, "PHASE3_CHECK_RUNNER=fail", .{});
            try guard.printLine(io, "phase3 check produced incomplete success output: {s}", .{command.rel_path});
            for (marker_issues) |marker| try guard.printLine(io, "missing output marker: {s}", .{marker});
            return 1;
        }
    }

    try guard.printLine(io, "PHASE3_CHECK_RUNNER=pass", .{});
    try guard.printLine(io, "PHASE3_CHECK_RUNNER_CASE_COUNT={d}", .{CHECK_COMMANDS.len});
    return 0;
}

fn writeSyntheticScript(io: Io, allocator: std.mem.Allocator, path: []const u8, output_markers: []const []const u8, failure_code: ?u8) !void {
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
    for (output_markers) |marker| {
        const line = try std.fmt.allocPrint(allocator, "    try writer.interface.print(\"{s}\\n\", .{{}});\n", .{marker});
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
        for (CHECK_COMMANDS) |command| {
            try routes.append(allocator, try std.fmt.allocPrint(allocator, "zig run {s}", .{command.rel_path}));
        }
        const extra = [_][]const u8{
            "zig run scripts/zigux/run_phase3_checks.zig",
            "zig run scripts/zigux/validate_phase3_selftest.zig",
            "zig run scripts/zigux/check_phase3_abi.zig -- --self-test",
            "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
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
    for (CHECK_COMMANDS) |command| {
        const path = try guard.joinPath(allocator, root, command.rel_path);
        defer allocator.free(path);
        try writeSyntheticScript(io, allocator, path, command.output_markers, null);
    }
    try writeSyntheticManifest(io, allocator, root, null);
}

fn expectMissingOutputMarker(io: Io, allocator: std.mem.Allocator, root: []const u8, zig_bin: []const u8, command_index: usize, missing_marker_index: usize, message: []const u8) !u8 {
    const command = CHECK_COMMANDS[command_index];
    var kept_markers: [16][]const u8 = undefined;
    var kept_count: usize = 0;
    for (command.output_markers, 0..) |marker, index| {
        if (index == missing_marker_index) continue;
        kept_markers[kept_count] = marker;
        kept_count += 1;
    }
    return expectCheckFailure(io, allocator, root, zig_bin, command_index, kept_markers[0..kept_count], message);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator, zig_bin: []const u8) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "phase3_check_runner");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);

    try populateRepo(io, allocator, root);

    const initial_script_issues = try validateScriptList(io, allocator, root);
    defer {
        for (initial_script_issues) |issue| allocator.free(issue);
        allocator.free(initial_script_issues);
    }
    if (initial_script_issues.len != 0) {
        try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected synthetic phase3 check set to validate", .{});
        return 1;
    }

    const manifest_missing = try validateManifestPythonCoverage(io, allocator, root);
    defer {
        for (manifest_missing) |issue| allocator.free(issue);
        allocator.free(manifest_missing);
    }
    if (manifest_missing.len != 0) {
        try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected synthetic manifest coverage to validate", .{});
        for (manifest_missing) |issue| try guard.printLine(io, "{s}", .{issue});
        return 1;
    }

    for (SELF_TEST_MISSING_CASES) |case_item| {
        try populateRepo(io, allocator, root);
        const missing_path = try guard.joinPath(allocator, root, CHECK_COMMANDS[case_item.index].rel_path);
        defer allocator.free(missing_path);
        guard.deleteFile(io, missing_path) catch {};
        const missing = try validateScriptList(io, allocator, root);
        defer {
            for (missing) |issue| allocator.free(issue);
            allocator.free(missing);
        }
        const expected = try std.fmt.allocPrint(allocator, "missing phase3 check script: {s}", .{CHECK_COMMANDS[case_item.index].rel_path});
        defer allocator.free(expected);
        var found = false;
        for (missing) |issue| {
            if (std.mem.eql(u8, issue, expected)) found = true;
        }
        if (!found) {
            try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
            try guard.printLine(io, "{s}", .{case_item.message});
            return 1;
        }
    }

    try populateRepo(io, allocator, root);
    const manifest_only_route = "zig run scripts/zigux/manifest_only_check.zig";
    try writeSyntheticManifest(io, allocator, root, &.{manifest_only_route});
    const expected_manifest_gap = "manifest python replay route missing from CHECK_COMMANDS: scripts/zigux/manifest_only_check.zig";
    const manifest_gap_issues = try validateManifestPythonCoverage(io, allocator, root);
    defer {
        for (manifest_gap_issues) |issue| allocator.free(issue);
        allocator.free(manifest_gap_issues);
    }
    var found_gap = false;
    for (manifest_gap_issues) |issue| {
        if (std.mem.eql(u8, issue, expected_manifest_gap)) found_gap = true;
    }
    if (!found_gap) {
        try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected manifest-only python replay route omission to be reported", .{});
        return 1;
    }

    try populateRepo(io, allocator, root);
    const manifest_path = try guard.joinPath(allocator, root, MANIFEST_PATH);
    defer allocator.free(manifest_path);
    guard.deleteFile(io, manifest_path) catch {};
    const expected_manifest_missing = try std.fmt.allocPrint(allocator, "missing phase3 manifest: {s}", .{MANIFEST_PATH});
    defer allocator.free(expected_manifest_missing);
    const missing_manifest_issues = try validateManifestPythonCoverage(io, allocator, root);
    defer {
        for (missing_manifest_issues) |issue| allocator.free(issue);
        allocator.free(missing_manifest_issues);
    }
    var found_missing_manifest = false;
    for (missing_manifest_issues) |issue| {
        if (std.mem.eql(u8, issue, expected_manifest_missing)) found_missing_manifest = true;
    }
    if (!found_missing_manifest) {
        try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
        try guard.printLine(io, "expected missing manifest to be reported", .{});
        return 1;
    }

    {
        try populateRepo(io, allocator, root);
        const failing_path = try guard.joinPath(allocator, root, CHECK_COMMANDS[CHECK_COMMANDS.len - 2].rel_path);
        defer allocator.free(failing_path);
        try writeSyntheticScript(io, allocator, failing_path, CHECK_COMMANDS[CHECK_COMMANDS.len - 2].output_markers, 9);
        const output = try runSingleCheck(io, allocator, root, zig_bin, CHECK_COMMANDS[CHECK_COMMANDS.len - 2], null);
        defer allocator.free(output.stdout);
        defer allocator.free(output.stderr);
        if (output.exit_code == 0) {
            try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=fail", .{});
            try guard.printLine(io, "expected failing child validator to fail the runner", .{});
            return 1;
        }
    }

    if ((try expectCheckFailure(io, allocator, root, zig_bin, 3, CHECK_COMMANDS[3].output_markers[0..1], "expected missing xarray-slot dump output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 4, CHECK_COMMANDS[4].output_markers[0..1], "expected missing idr-slot starter build marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 5, CHECK_COMMANDS[5].output_markers[0..2], "expected missing idr-slot dump manifest marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 10, &.{}, "expected missing support-checker output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 15, CHECK_COMMANDS[15].output_markers[0..1], "expected missing validator-support shared-reminder marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 15, CHECK_COMMANDS[15].output_markers[1..2], "expected missing validator-support note marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 7, CHECK_COMMANDS[7].output_markers[0..1], "expected missing policy-dump output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 8, &.{}, "expected missing shared ABI validator pass marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 11, CHECK_COMMANDS[11].output_markers[0..1], "expected missing shared-routes output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 12, &.{}, "expected missing readme-inventory output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 13, CHECK_COMMANDS[13].output_markers[1..2], "expected missing wrapper-template pass marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 17, CHECK_COMMANDS[17].output_markers[1..2], "expected missing export-uapi c-header smoke pass marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 18, CHECK_COMMANDS[18].output_markers[1..2], "expected missing abi-header-family pass marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 19, CHECK_COMMANDS[19].output_markers[1..2], "expected missing policy-unsafe pass marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 20, CHECK_COMMANDS[20].output_markers[0..1], "expected missing low-level-wrapper pass marker to fail the runner")) != 0) return 1;

    const marker_cases = [_]struct { index: usize, marker_index: usize, message: []const u8 }{
        .{ .index = 21, .marker_index = 0, .message = "expected missing low-level-wrapper replay output marker to fail the runner" },
        .{ .index = 21, .marker_index = 1, .message = "expected missing low-level-wrapper focused-build output marker to fail the runner" },
        .{ .index = 21, .marker_index = 2, .message = "expected missing low-level-wrapper shared-build output marker to fail the runner" },
        .{ .index = 21, .marker_index = 3, .message = "expected missing low-level-wrapper make-route output marker to fail the runner" },
        .{ .index = 21, .marker_index = 4, .message = "expected missing low-level-wrapper atomic-helper output marker to fail the runner" },
        .{ .index = 21, .marker_index = 5, .message = "expected missing low-level-wrapper barrier-helper output marker to fail the runner" },
        .{ .index = 25, .marker_index = 0, .message = "expected missing bitmap-cpumask pass marker to fail the runner" },
        .{ .index = 25, .marker_index = 1, .message = "expected missing bitmap-cpumask manifest output marker to fail the runner" },
        .{ .index = 25, .marker_index = 2, .message = "expected missing bitmap-cpumask starter-packet output marker to fail the runner" },
        .{ .index = 26, .marker_index = 0, .message = "expected missing list-hlist list-view output marker to fail the runner" },
        .{ .index = 26, .marker_index = 1, .message = "expected missing list-hlist hlist-view output marker to fail the runner" },
        .{ .index = 26, .marker_index = 2, .message = "expected missing list-hlist starter-packet output marker to fail the runner" },
        .{ .index = 26, .marker_index = 3, .message = "expected missing list-hlist build output marker to fail the runner" },
        .{ .index = 26, .marker_index = 4, .message = "expected missing list-hlist manifest output marker to fail the runner" },
        .{ .index = 27, .marker_index = 0, .message = "expected missing full list-hlist dump output marker to fail the runner" },
        .{ .index = 27, .marker_index = 1, .message = "expected missing full list-hlist c-harness output marker to fail the runner" },
        .{ .index = 27, .marker_index = 2, .message = "expected missing full list-hlist expected-json output marker to fail the runner" },
        .{ .index = 27, .marker_index = 3, .message = "expected missing full list-hlist manifest output marker to fail the runner" },
    };
    for (marker_cases) |case_item| {
        if ((try expectMissingOutputMarker(io, allocator, root, zig_bin, case_item.index, case_item.marker_index, case_item.message)) != 0) {
            return 1;
        }
    }

    if ((try expectCheckFailure(io, allocator, root, zig_bin, 22, &.{}, "expected missing linux-zigux header-governance output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 23, &.{}, "expected missing selftest-surface output marker to fail the runner")) != 0) return 1;
    if ((try expectCheckFailure(io, allocator, root, zig_bin, 24, &.{}, "expected missing abi manifest replay-routes pass marker to fail the runner")) != 0) return 1;

    try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE3_CHECK_RUNNER_SELF_TEST_CASE_COUNT={d}", .{SELF_TEST_MISSING_CASES.len + 40});
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