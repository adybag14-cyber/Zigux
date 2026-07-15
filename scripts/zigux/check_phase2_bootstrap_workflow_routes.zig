const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const TOOLCHAIN_POLICY_REL = "scripts/zigux/zig-toolchain-policy.json";
const BOOTSTRAP_NOTES_REL = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";
const WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml";
const MAKEFILE_REL = "zigux/Makefile";
const AGGREGATE_ROUTE = "phase2";
const EXPECTED_SELF_TEST_CASE_COUNT = 24;

const CURRENT_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn noteMarkers(allocator: std.mem.Allocator, routes: []const []const u8) ![]const []const u8 {
    var markers: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (markers.items) |marker| allocator.free(marker);
        markers.deinit(allocator);
    }
    for (routes) |_| {}
    for (routes) |route| {
        try markers.append(allocator, try std.fmt.allocPrint(allocator, "`make -C zigux {s}`", .{route}));
    }
    try markers.append(allocator, try std.fmt.allocPrint(allocator, "`make -C zigux {s}`", .{AGGREGATE_ROUTE}));
    return markers.toOwnedSlice(allocator);
}

fn workflowLines(allocator: std.mem.Allocator, routes: []const []const u8) ![]const []const u8 {
    var lines: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (lines.items) |line| allocator.free(line);
        lines.deinit(allocator);
    }
    for (routes) |route| {
        try lines.append(allocator, try std.fmt.allocPrint(allocator, "run: make -C zigux {s}", .{route}));
    }
    try lines.append(allocator, try std.fmt.allocPrint(allocator, "run: make -C zigux {s}", .{AGGREGATE_ROUTE}));
    return lines.toOwnedSlice(allocator);
}

fn makefileRuleLines(allocator: std.mem.Allocator, routes: []const []const u8) ![]const []const u8 {
    var lines: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (lines.items) |line| allocator.free(line);
        lines.deinit(allocator);
    }
    for (routes) |route| {
        const line = if (std.mem.eql(u8, route, "phase2-kconfig") or std.mem.eql(u8, route, "phase2-genksyms") or std.mem.eql(u8, route, "phase2-fixdep"))
            try std.fmt.allocPrint(allocator, "{s}: phase2-toolchain", .{route})
        else if (std.mem.eql(u8, route, "phase2-validate"))
            try std.fmt.allocPrint(allocator, "{s}: {s} {s} {s} {s} {s} {s}", .{ route, routes[0], routes[1], routes[2], routes[3], routes[4], routes[5] })
        else
            try std.fmt.allocPrint(allocator, "{s}:", .{route});
        try lines.append(allocator, line);
    }
    try lines.append(allocator, try std.fmt.allocPrint(allocator, "{s}: {s}", .{ AGGREGATE_ROUTE, routes[routes.len - 1] }));
    return lines.toOwnedSlice(allocator);
}

const PHONY_ROUTE_TOKENS = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    AGGREGATE_ROUTE,
};

fn loadRequiredRoutes(io: Io, allocator: std.mem.Allocator, root: []const u8) ![]const []const u8 {
    const policy_path = try guard.joinPath(allocator, root, TOOLCHAIN_POLICY_REL);
    defer allocator.free(policy_path);
    const policy_text = try guard.readUtf8File(io, allocator, policy_path);
    defer allocator.free(policy_text);
    const parsed = guard.parseJsonValue(allocator, policy_text) catch return error.InvalidPolicy;
    defer parsed.deinit();
    const object = switch (parsed.value) {
        .object => |value| value,
        else => return error.InvalidPolicy,
    };
    const upgrade_policy = object.get("upgrade_policy") orelse return error.InvalidPolicy;
    const upgrade_object = switch (upgrade_policy) {
        .object => |value| value,
        else => return error.InvalidPolicy,
    };
    const routes_value = upgrade_object.get("required_make_routes") orelse return error.InvalidPolicy;
    const routes_array = switch (routes_value) {
        .array => |items| items,
        else => return error.InvalidPolicy,
    };
    if (routes_array.items.len == 0) return error.InvalidPolicy;
    var routes: std.ArrayList([]const u8) = .empty;
    errdefer routes.deinit(allocator);
    var seen = std.StringHashMap(void).init(allocator);
    defer seen.deinit();
    for (routes_array.items) |item| {
        const route = switch (item) {
            .string => |route_text| route_text,
            else => return error.InvalidPolicy,
        };
        if (route.len == 0 or std.mem.trim(u8, route, " \t").len == 0) return error.InvalidPolicy;
        const normalized = std.mem.trim(u8, route, " \t");
        if (seen.contains(normalized)) return error.InvalidPolicy;
        try seen.put(normalized, {});
        try routes.append(allocator, try allocator.dupe(u8, normalized));
    }
    return routes.toOwnedSlice(allocator);
}

fn phonyLine(text: []const u8) ?[]const u8 {
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |line| {
        if (std.mem.startsWith(u8, line, ".PHONY:")) return line;
    }
    return null;
}

fn collectFailures(io: Io, allocator: std.mem.Allocator, root: []const u8) ![]const []const u8 {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |failure| allocator.free(failure);
        failures.deinit(allocator);
    }

    for (&[_][]const u8{ TOOLCHAIN_POLICY_REL, BOOTSTRAP_NOTES_REL, WORKFLOW_REL, MAKEFILE_REL }) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{rel});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures.toOwnedSlice(allocator);

    const routes = loadRequiredRoutes(io, allocator, root) catch |err| switch (err) {
        error.InvalidPolicy => {
            const issue = try std.fmt.allocPrint(allocator, "invalid_policy:invalid required_make_routes in {s}", .{TOOLCHAIN_POLICY_REL});
            try failures.append(allocator, issue);
            return failures.toOwnedSlice(allocator);
        },
        else => |e| return e,
    };
    defer {
        for (routes) |route| allocator.free(route);
        allocator.free(routes);
    }

    const note_path = try guard.joinPath(allocator, root, BOOTSTRAP_NOTES_REL);
    defer allocator.free(note_path);
    const workflow_path = try guard.joinPath(allocator, root, WORKFLOW_REL);
    defer allocator.free(workflow_path);
    const makefile_path = try guard.joinPath(allocator, root, MAKEFILE_REL);
    defer allocator.free(makefile_path);
    const note_text = try guard.readUtf8File(io, allocator, note_path);
    defer allocator.free(note_text);
    const workflow_text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow_text);
    const makefile_text = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(makefile_text);

    const markers = try noteMarkers(allocator, routes);
    defer {
        for (markers) |marker| allocator.free(marker);
        allocator.free(markers);
    }
    for (markers) |marker| {
        if (std.mem.indexOf(u8, note_text, marker) == null) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:missing:{s}", .{ BOOTSTRAP_NOTES_REL, marker });
            try failures.append(allocator, issue);
        }
    }

    const wf_lines = try workflowLines(allocator, routes);
    defer {
        for (wf_lines) |line| allocator.free(line);
        allocator.free(wf_lines);
    }
    for (wf_lines) |line| try guard.appendExactTrimmedLineOnceIssue(allocator, &failures, workflow_text, WORKFLOW_REL, line);

    const mk_lines = try makefileRuleLines(allocator, routes);
    defer {
        for (mk_lines) |line| allocator.free(line);
        allocator.free(mk_lines);
    }
    for (mk_lines) |line| try guard.appendExactTrimmedLineOnceIssue(allocator, &failures, makefile_text, MAKEFILE_REL, line);

    const phony = phonyLine(makefile_text) orelse "";
    for (PHONY_ROUTE_TOKENS) |token| {
        if (std.mem.indexOf(u8, phony, token) == null) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:phony:missing:{s}", .{ MAKEFILE_REL, token });
            try failures.append(allocator, issue);
        }
    }

    return failures.toOwnedSlice(allocator);
}

fn buildPolicy(routes: []const []const u8, allocator: std.mem.Allocator) ![]u8 {
    var route_values = try allocator.alloc(std.json.Value, routes.len);
    defer allocator.free(route_values);
    for (routes, 0..) |route, index| route_values[index] = .{ .string = route };
    const payload = std.json.Value{ .object = .{} };
    _ = payload;
    var out = std.ArrayList(u8).empty;
    defer out.deinit(allocator);
    try out.appendSlice(allocator,
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.877+a3ae499dc",
        \\  "minimum_version": "0.17.0-dev.877+a3ae499dc",
        \\  "archive_sha256": {"x86_64-linux": "
    );
    for (0..64) |_| try out.append(allocator, '3');
    try out.appendSlice(allocator,
        \\"},
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": [
    );
    var aw: std.Io.Writer.Allocating = .init(allocator);
    for (routes, 0..) |route, index| {
        try aw.writer.print("      \"{s}\"{s}\n", .{ route, if (index + 1 == routes.len) "" else "," });
    }
    const routes_json = try aw.toOwnedSlice();
    defer allocator.free(routes_json);
    try out.appendSlice(allocator, routes_json);
    try out.appendSlice(allocator,
        \\    ]
        \\  }
        \\}
        \\
    );
    return out.toOwnedSlice(allocator);
}

fn buildSampleRoot(io: Io, allocator: std.mem.Allocator, root: []const u8, routes: []const []const u8) !void {
    const markers = try noteMarkers(allocator, routes);
    defer {
        for (markers) |marker| allocator.free(marker);
        allocator.free(markers);
    }
    const wf_lines = try workflowLines(allocator, routes);
    defer {
        for (wf_lines) |line| allocator.free(line);
        allocator.free(wf_lines);
    }
    const mk_rules = try makefileRuleLines(allocator, routes);
    defer {
        for (mk_rules) |line| allocator.free(line);
        allocator.free(mk_rules);
    }

    const policy_text = try buildPolicy(routes, allocator);
    defer allocator.free(policy_text);
    const policy_path = try guard.joinPath(allocator, root, TOOLCHAIN_POLICY_REL);
    defer allocator.free(policy_path);
    try guard.writeUtf8File(io, policy_path, policy_text);

    var note = std.ArrayList(u8).empty;
    defer note.deinit(allocator);
    try note.appendSlice(allocator, "# Phase 2 Toolchain Bootstrap Notes\n\n## Current direct packet\n\nThe rematerialized make-wrapper packet is directly readable on current `master` through ");
    for (markers[0 .. markers.len - 1], 0..) |marker, index| {
        if (index != 0) try note.appendSlice(allocator, ", ");
        try note.appendSlice(allocator, marker);
    }
    var note_aw: std.Io.Writer.Allocating = .init(allocator);
    try note_aw.writer.print(", and {s}, so keep those routes in the present packet instead of the repo-reality-gap list.\n\n", .{markers[markers.len - 1]});
    try note.appendSlice(allocator, try note_aw.toOwnedSlice());
    const note_path = try guard.joinPath(allocator, root, BOOTSTRAP_NOTES_REL);
    defer allocator.free(note_path);
    try guard.writeUtf8File(io, note_path, note.items);

    var workflow_aw: std.Io.Writer.Allocating = .init(allocator);
    try workflow_aw.writer.writeAll("name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n");
    for (wf_lines) |line| {
        try workflow_aw.writer.writeAll("      - name: route\n");
        try workflow_aw.writer.print("        {s}\n", .{line});
    }
    try workflow_aw.writer.writeByte('\n');
    const workflow_path = try guard.joinPath(allocator, root, WORKFLOW_REL);
    defer allocator.free(workflow_path);
    try guard.writeUtf8File(io, workflow_path, try workflow_aw.toOwnedSlice());

    var makefile_aw: std.Io.Writer.Allocating = .init(allocator);
    try makefile_aw.writer.writeAll(".PHONY: ");
    for (routes, 0..) |route, index| {
        if (index != 0) try makefile_aw.writer.writeByte(' ');
        try makefile_aw.writer.writeAll(route);
    }
    try makefile_aw.writer.print(" {s}\n\n", .{AGGREGATE_ROUTE});
    for (routes, mk_rules[0 .. mk_rules.len - 1]) |route, rule| {
        try makefile_aw.writer.print("{s}\n\t@echo {s}\n\n", .{ rule, route });
    }
    try makefile_aw.writer.print("{s}\n\t@echo {s}\n\n", .{ mk_rules[mk_rules.len - 1], AGGREGATE_ROUTE });
    const makefile_path = try guard.joinPath(allocator, root, MAKEFILE_REL);
    defer allocator.free(makefile_path);
    try guard.writeUtf8File(io, makefile_path, try makefile_aw.toOwnedSlice());
}

fn removeFirst(allocator: std.mem.Allocator, text: []const u8, needle: []const u8) ![]u8 {
    const index = std.mem.indexOf(u8, text, needle) orelse return error.MissingNeedle;
    var out = try allocator.alloc(u8, text.len - needle.len);
    @memcpy(out[0..index], text[0..index]);
    @memcpy(out[index..out.len], text[index + needle.len ..]);
    return out;
}

fn anyContainsSubstring(failures: []const []const u8, needle: []const u8) bool {
    for (failures) |failure| {
        if (std.mem.indexOf(u8, failure, needle) != null) return true;
    }
    return false;
}

fn anyStartsWith(failures: []const []const u8, prefix: []const u8) bool {
    for (failures) |failure| {
        if (std.mem.startsWith(u8, failure, prefix)) return true;
    }
    return false;
}

fn pickIndex(len: usize, preferred: usize) usize {
    return @min(preferred, len - 1);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var checks: usize = 0;
    var tmp = try guard.TempWorkspace.init(io, allocator, "p2_bootstrap_workflow_routes");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    const routes = CURRENT_ROUTES[0..];

    try buildSampleRoot(io, allocator, root, routes);
    const ok_failures = try collectFailures(io, allocator, root);
    defer {
        for (ok_failures) |failure| allocator.free(failure);
        allocator.free(ok_failures);
    }
    try guard.expectSelfTest(ok_failures.len == 0);
    checks += 1;

    const markers = try noteMarkers(allocator, routes);
    defer {
        for (markers) |marker| allocator.free(marker);
        allocator.free(markers);
    }
    const route_workflow_lines = try workflowLines(allocator, routes);
    defer {
        for (route_workflow_lines) |line| allocator.free(line);
        allocator.free(route_workflow_lines);
    }
    const rule_lines = try makefileRuleLines(allocator, routes);
    defer {
        for (rule_lines) |line| allocator.free(line);
        allocator.free(rule_lines);
    }

    const note_path = try guard.joinPath(allocator, root, BOOTSTRAP_NOTES_REL);
    defer allocator.free(note_path);
    const workflow_path = try guard.joinPath(allocator, root, WORKFLOW_REL);
    defer allocator.free(workflow_path);
    const makefile_path = try guard.joinPath(allocator, root, MAKEFILE_REL);
    defer allocator.free(makefile_path);
    const policy_path = try guard.joinPath(allocator, root, TOOLCHAIN_POLICY_REL);
    defer allocator.free(policy_path);

    try buildSampleRoot(io, allocator, root, routes);
    const note_text = try guard.readUtf8File(io, allocator, note_path);
    defer allocator.free(note_text);
    const broken_note = try removeFirst(allocator, note_text, markers[1]);
    defer allocator.free(broken_note);
    try guard.writeUtf8File(io, note_path, broken_note);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), markers[1]));
    checks += 1;

    for (&[_][]const u8{ route_workflow_lines[0], route_workflow_lines[route_workflow_lines.len - 1] }) |workflow_line| {
        try buildSampleRoot(io, allocator, root, routes);
        const workflow_text = try guard.readUtf8File(io, allocator, workflow_path);
        defer allocator.free(workflow_text);
        const broken = try removeFirst(allocator, workflow_text, workflow_line);
        defer allocator.free(broken);
        try guard.writeUtf8File(io, workflow_path, broken);
        try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), workflow_line));
        checks += 1;
    }

    try buildSampleRoot(io, allocator, root, routes);
    const workflow_text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow_text);
    const dup = try std.fmt.allocPrint(allocator, "{s}      - name: duplicate-route\n        {s}\n", .{ workflow_text, route_workflow_lines[2] });
    defer allocator.free(dup);
    try guard.writeUtf8File(io, workflow_path, dup);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), route_workflow_lines[2]));
    checks += 1;

    for (&[_][]const u8{ rule_lines[0], rule_lines[rule_lines.len - 1] }) |makefile_line| {
        try buildSampleRoot(io, allocator, root, routes);
        const makefile_text = try guard.readUtf8File(io, allocator, makefile_path);
        defer allocator.free(makefile_text);
        const broken = try removeFirst(allocator, makefile_text, makefile_line);
        defer allocator.free(broken);
        try guard.writeUtf8File(io, makefile_path, broken);
        try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), makefile_line));
        checks += 1;
    }

    try buildSampleRoot(io, allocator, root, routes);
    const makefile_text = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(makefile_text);
    const phony_needle = try std.fmt.allocPrint(allocator, ".PHONY: {s} {s} {s} {s} {s} {s} {s} {s}", .{ routes[0], routes[1], routes[2], routes[3], routes[4], routes[5], routes[6], AGGREGATE_ROUTE });
    defer allocator.free(phony_needle);
    const phony_replacement = try std.fmt.allocPrint(allocator, ".PHONY: {s} {s} {s} {s} {s} {s} {s} {s}", .{ routes[0], routes[1], routes[2], routes[3], routes[5], routes[6], AGGREGATE_ROUTE, "extra" });
    defer allocator.free(phony_replacement);
    const broken_makefile = try std.mem.replaceOwned(u8, allocator, makefile_text, phony_needle, phony_replacement);
    defer allocator.free(broken_makefile);
    try guard.writeUtf8File(io, makefile_path, broken_makefile);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), "phony"));
    checks += 1;

    for (&[_][]const u8{ TOOLCHAIN_POLICY_REL, BOOTSTRAP_NOTES_REL, WORKFLOW_REL, MAKEFILE_REL }) |rel| {
        try buildSampleRoot(io, allocator, root, routes);
        const path = try guard.joinPath(allocator, root, rel);
        try guard.deleteFile(io, path);
        allocator.free(path);
        const failures = try collectFailures(io, allocator, root);
        defer {
            for (failures) |failure| allocator.free(failure);
            allocator.free(failures);
        }
        const expected = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{rel});
        defer allocator.free(expected);
        var found = false;
        for (failures) |failure| {
            if (std.mem.eql(u8, failure, expected)) found = true;
        }
        try guard.expectSelfTest(found);
        checks += 1;
    }

    for (&[_]usize{ 0, pickIndex(markers.len, 3), markers.len - 1 }) |marker_index| {
        try buildSampleRoot(io, allocator, root, routes);
        const text = try guard.readUtf8File(io, allocator, note_path);
        defer allocator.free(text);
        const broken = try removeFirst(allocator, text, markers[marker_index]);
        defer allocator.free(broken);
        try guard.writeUtf8File(io, note_path, broken);
        try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), markers[marker_index]));
        checks += 1;
    }

    for (&[_]usize{ pickIndex(route_workflow_lines.len, 1), pickIndex(route_workflow_lines.len, 4), route_workflow_lines.len - 1 }) |line_index| {
        try buildSampleRoot(io, allocator, root, routes);
        const text = try guard.readUtf8File(io, allocator, workflow_path);
        defer allocator.free(text);
        const broken = try removeFirst(allocator, text, route_workflow_lines[line_index]);
        defer allocator.free(broken);
        try guard.writeUtf8File(io, workflow_path, broken);
        try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), route_workflow_lines[line_index]));
        checks += 1;
    }

    try buildSampleRoot(io, allocator, root, routes);
    const mk_text = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(mk_text);
    const broken_mk = try removeFirst(allocator, mk_text, rule_lines[3]);
    defer allocator.free(broken_mk);
    try guard.writeUtf8File(io, makefile_path, broken_mk);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), rule_lines[3]));
    checks += 1;

    try buildSampleRoot(io, allocator, root, routes);
    const mk_text2 = try guard.readUtf8File(io, allocator, makefile_path);
    defer allocator.free(mk_text2);
    const broken_mk2 = try removeFirst(allocator, mk_text2, "phase2-cross");
    defer allocator.free(broken_mk2);
    try guard.writeUtf8File(io, makefile_path, broken_mk2);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), "phase2-cross"));
    checks += 1;

    try buildSampleRoot(io, allocator, root, routes);
    const note_text2 = try guard.readUtf8File(io, allocator, note_path);
    defer allocator.free(note_text2);
    const broken_note2 = try std.mem.replaceOwned(u8, allocator, note_text2, "phase2-tools", "phase2-tools-drift");
    defer allocator.free(broken_note2);
    try guard.writeUtf8File(io, note_path, broken_note2);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), "phase2-tools"));
    checks += 1;

    try buildSampleRoot(io, allocator, root, routes);
    try guard.writeUtf8File(io, policy_path, "{not-json}\n");
    try guard.expectSelfTest(anyStartsWith(try collectFailures(io, allocator, root), "invalid_policy:invalid required_make_routes"));
    checks += 1;

    try buildSampleRoot(io, allocator, root, routes);
    const empty_policy = try buildPolicy(&[_][]const u8{}, allocator);
    defer allocator.free(empty_policy);
    try guard.writeUtf8File(io, policy_path, empty_policy);
    try guard.expectSelfTest(anyContainsSubstring(try collectFailures(io, allocator, root), "invalid required_make_routes"));
    checks += 1;

    try buildSampleRoot(io, allocator, root, routes);
    var expanded = std.ArrayList([]const u8).empty;
    defer expanded.deinit(allocator);
    try expanded.appendSlice(allocator, routes);
    try expanded.append(allocator, "phase2-future");
    const expanded_policy = try buildPolicy(expanded.items, allocator);
    defer allocator.free(expanded_policy);
    try guard.writeUtf8File(io, policy_path, expanded_policy);
    const expanded_failures = try collectFailures(io, allocator, root);
    defer {
        for (expanded_failures) |failure| allocator.free(failure);
        allocator.free(expanded_failures);
    }
    try guard.expectSelfTest(anyContainsSubstring(expanded_failures, "phase2-future"));
    try guard.expectSelfTest(anyContainsSubstring(expanded_failures, "`make -C zigux phase2-future`"));
    try guard.expectSelfTest(anyContainsSubstring(expanded_failures, "run: make -C zigux phase2-future"));
    try guard.expectSelfTest(anyContainsSubstring(expanded_failures, "phase2-future:"));
    checks += 1;

    try guard.expectSelfTest(checks == EXPECTED_SELF_TEST_CASE_COUNT);
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST_CASE_COUNT={d}", .{checks});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var write_sample_root: ?[]const u8 = null;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--write-sample-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            write_sample_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (write_sample_root) |sample_root| {
        try buildSampleRoot(io, allocator, sample_root, CURRENT_ROUTES[0..]);
        return;
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    const failures = try collectFailures(io, allocator, root);
    defer {
        for (failures) |failure| allocator.free(failure);
        allocator.free(failures);
    }
    if (failures.len != 0) {
        for (failures) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }
    const routes = try loadRequiredRoutes(io, allocator, root);
    defer {
        for (routes) |route| allocator.free(route);
        allocator.free(routes);
    }
    const wf_lines = try workflowLines(allocator, routes);
    defer {
        for (wf_lines) |line| allocator.free(line);
        allocator.free(wf_lines);
    }
    const mk_lines = try makefileRuleLines(allocator, routes);
    defer {
        for (mk_lines) |line| allocator.free(line);
        allocator.free(mk_lines);
    }
    const policy_path = try guard.joinPath(allocator, root, TOOLCHAIN_POLICY_REL);
    defer allocator.free(policy_path);
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass", .{});
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_POLICY_PATH={s}", .{policy_path});
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_REQUIRED_ROUTE_COUNT={d}", .{routes.len});
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_WORKFLOW_LINE_COUNT={d}", .{wf_lines.len});
    try guard.printLine(io, "PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_MAKEFILE_LINE_COUNT={d}", .{mk_lines.len});
}
