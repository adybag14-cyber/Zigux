const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const BRIDGE_REL = "scripts/zigux/kconfig/confdata_bridge.zig";
const CASES_REL = "zigux/tests/fixtures/kconfig_bridge/cases.json";
const MANIFEST_REL = "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json";
const SURVEY_REL = "Documentation/zigux/phase2-confdata-bridge-survey.md";

const EXPECTED_SELF_TEST_CASE_COUNT = 4;

const Issue = struct {
    code: []const u8,
    value: []const u8,
};

fn countTestAnchors(bridge_text: []const u8) ![]const []const u8 {
    var anchors: std.ArrayList([]const u8) = .empty;
    var iter = std.mem.splitScalar(u8, bridge_text, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (!std.mem.startsWith(u8, line, "test \"")) continue;
        const end_quote = std.mem.indexOf(u8, line[6 .. line.len], "\"") orelse continue;
        if (end_quote == 0) continue;
        const anchor = line[6 .. 6 + end_quote];
        if (!std.mem.endsWith(u8, line[6 + end_quote + 1 ..], "{")) continue;
        try anchors.append(std.heap.page_allocator, anchor);
    }
    if (anchors.items.len == 0) return error.MissingAnchors;
    return anchors.toOwnedSlice(std.heap.page_allocator);
}

fn loadConfdataCases(payload: std.json.Value) ![]const std.json.ObjectMap {
    const object = switch (payload) {
        .object => |value| value,
        else => return error.InvalidCases,
    };
    const raw_cases = object.get("confdata_cases") orelse return error.InvalidCases;
    const array = switch (raw_cases) {
        .array => |items| items,
        else => return error.InvalidCases,
    };
    const out = try std.heap.page_allocator.alloc(std.json.ObjectMap, array.items.len);
    for (array.items, 0..) |item, index| {
        out[index] = switch (item) {
            .object => |case_object| case_object,
            else => return error.InvalidCases,
        };
    }
    return out;
}

fn requiredSurveyMarkers(allocator: std.mem.Allocator, anchor_count: usize, case_count: usize, case_names: []const []const u8) ![]const []const u8 {
    var markers: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (markers.items) |marker| allocator.free(marker);
        markers.deinit(allocator);
    }
    try markers.append(allocator, try allocator.dupe(u8, "scripts/zigux/kconfig/confdata_bridge.zig"));
    try markers.append(allocator, try std.fmt.allocPrint(allocator, "`{d}` helper-local tests", .{anchor_count}));
    try markers.append(allocator, try std.fmt.allocPrint(allocator, "`confdata_cases` packet with {d} fixture cases", .{case_count}));
    try markers.append(allocator, try std.fmt.allocPrint(allocator, "The live `{d}`-anchor and `{d}`-case confdata packet", .{ anchor_count, case_count }));
    for (&[_][]const u8{
        "zig run scripts/zigux/check_kconfig_bridge.zig -- --self-test",
        "zig run scripts/zigux/check_phase2_kconfig_selftest_alignment.zig -- --self-test",
        "zig run scripts/zigux/check_phase2_kconfig_selftest_alignment.zig",
        "zig test scripts/zigux/kconfig/confdata_bridge.zig",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
    }) |literal| {
        try markers.append(allocator, try allocator.dupe(u8, literal));
    }
    if (case_names.len >= 2) {
        try markers.append(allocator, try allocator.dupe(u8, case_names[case_names.len - 2]));
        try markers.append(allocator, try allocator.dupe(u8, case_names[case_names.len - 1]));
    }
    return markers.toOwnedSlice(allocator);
}

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) ![]Issue {
    const bridge_path = try guard.joinPath(allocator, root, BRIDGE_REL);
    defer allocator.free(bridge_path);
    const survey_path = try guard.joinPath(allocator, root, SURVEY_REL);
    defer allocator.free(survey_path);
    const cases_path = try guard.joinPath(allocator, root, CASES_REL);
    defer allocator.free(cases_path);
    const manifest_path = try guard.joinPath(allocator, root, MANIFEST_REL);
    defer allocator.free(manifest_path);

    const bridge_text = try guard.readUtf8File(io, allocator, bridge_path);
    defer allocator.free(bridge_text);
    const survey_text = try guard.readUtf8File(io, allocator, survey_path);
    defer allocator.free(survey_text);
    const cases_text = try guard.readUtf8File(io, allocator, cases_path);
    defer allocator.free(cases_text);
    const cases_parsed = try guard.parseJsonValue(allocator, cases_text);
    defer cases_parsed.deinit();
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();

    var issues: std.ArrayList(Issue) = .empty;
    errdefer {
        for (issues.items) |issue| {
            allocator.free(issue.code);
            allocator.free(issue.value);
        }
        issues.deinit(allocator);
    }

    const anchors = try countTestAnchors(bridge_text);
    defer std.heap.page_allocator.free(anchors);
    const cases = try loadConfdataCases(cases_parsed.value);
    defer std.heap.page_allocator.free(cases);

    const manifest_object = switch (manifest_parsed.value) {
        .object => |object| object,
        else => {
            const code = try allocator.dupe(u8, "INVALID_CONFDATA_MANIFEST_PAYLOAD");
            const value = try std.fmt.allocPrint(allocator, "{s}", .{@tagName(manifest_parsed.value)});
            try issues.append(allocator, .{ .code = code, .value = value });
            return issues.toOwnedSlice(allocator);
        },
    };

    var case_names = try allocator.alloc([]const u8, cases.len);
    defer allocator.free(case_names);
    var input_packet = try allocator.alloc([]const u8, cases.len);
    defer allocator.free(input_packet);
    var expected_packet = try allocator.alloc([]const u8, cases.len);
    defer allocator.free(expected_packet);

    for (cases, 0..) |case_object, index| {
        const name = case_object.get("name") orelse return error.InvalidCases;
        const input_name = case_object.get("input") orelse return error.InvalidCases;
        const expected_name = case_object.get("expected") orelse return error.InvalidCases;
        case_names[index] = switch (name) {
            .string => |text| text,
            else => return error.InvalidCases,
        };
        input_packet[index] = switch (input_name) {
            .string => |text| text,
            else => return error.InvalidCases,
        };
        expected_packet[index] = switch (expected_name) {
            .string => |text| text,
            else => return error.InvalidCases,
        };
    }

    inline for (.{
        .{ "tool", "scripts/zigux/kconfig/confdata_bridge.zig" },
        .{ "status", "closed" },
        .{ "mode", "bounded config bridge" },
        .{ "fixture_root", "zigux/tests/fixtures/kconfig_bridge" },
        .{ "fixture_case_source", "zigux/tests/fixtures/kconfig_bridge/cases.json" },
    }) |pair| {
        const actual = manifest_object.get(pair[0]);
        if (actual == null or !guard.jsonValuesEqual(actual.?, .{ .string = pair[1] })) {
            const actual_text = try guard.jsonValueToDisplay(allocator, actual);
            defer allocator.free(actual_text);
            const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
            const value = try std.fmt.allocPrint(allocator, "{s}:actual={s}:expected={s}", .{ pair[0], actual_text, pair[1] });
            try issues.append(allocator, .{ .code = code, .value = value });
        }
    }
    if (manifest_object.get("case_count")) |actual_count| {
        if (!guard.jsonValuesEqual(actual_count, .{ .integer = @intCast(cases.len) })) {
            const actual_text = try guard.jsonValueToDisplay(allocator, actual_count);
            defer allocator.free(actual_text);
            const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
            const value = try std.fmt.allocPrint(allocator, "case_count:actual={s}:expected={d}", .{ actual_text, cases.len });
            try issues.append(allocator, .{ .code = code, .value = value });
        }
    } else {
        const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
        const value = try std.fmt.allocPrint(allocator, "case_count:actual=null:expected={d}", .{cases.len});
        try issues.append(allocator, .{ .code = code, .value = value });
    }
    try appendStringArrayMismatch(allocator, &issues, manifest_object, "cases", case_names);
    try appendStringArrayMismatch(allocator, &issues, manifest_object, "input_packet", input_packet);
    try appendStringArrayMismatch(allocator, &issues, manifest_object, "expected_packet", expected_packet);
    try appendStringArrayMismatch(allocator, &issues, manifest_object, "helper_local_anchors", anchors);

    const markers = try requiredSurveyMarkers(allocator, anchors.len, cases.len, case_names);
    defer {
        for (markers) |marker| allocator.free(marker);
        allocator.free(markers);
    }
    for (markers) |marker| {
        if (std.mem.indexOf(u8, survey_text, marker) == null) {
            const code = try allocator.dupe(u8, "MISSING_CONFDATA_SURVEY_MARKERS");
            const value = try allocator.dupe(u8, marker);
            try issues.append(allocator, .{ .code = code, .value = value });
        }
    }

    return issues.toOwnedSlice(allocator);
}

fn appendStringArrayMismatch(
    allocator: std.mem.Allocator,
    issues: *std.ArrayList(Issue),
    manifest_object: std.json.ObjectMap,
    field_name: []const u8,
    expected: []const []const u8,
) !void {
    const actual_value = manifest_object.get(field_name) orelse {
        const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
        const value = try std.fmt.allocPrint(allocator, "{s}:actual=null:expected={d}", .{ field_name, expected.len });
        try issues.append(allocator, .{ .code = code, .value = value });
        return;
    };
    const actual_array = switch (actual_value) {
        .array => |items| items.items,
        else => {
            const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
            const value = try std.fmt.allocPrint(allocator, "{s}:actual=non_array:expected={d}", .{ field_name, expected.len });
            try issues.append(allocator, .{ .code = code, .value = value });
            return;
        },
    };
    if (actual_array.len != expected.len) {
        const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
        const value = try std.fmt.allocPrint(allocator, "{s}:actual_len={d}:expected_len={d}", .{ field_name, actual_array.len, expected.len });
        try issues.append(allocator, .{ .code = code, .value = value });
        return;
    }
    for (actual_array, expected) |actual_item, expected_item| {
        const actual_text = switch (actual_item) {
            .string => |text| text,
            else => {
                const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
                const value = try std.fmt.allocPrint(allocator, "{s}:actual=non_string:expected={s}", .{ field_name, expected_item });
                try issues.append(allocator, .{ .code = code, .value = value });
                return;
            },
        };
        if (!std.mem.eql(u8, actual_text, expected_item)) {
            const code = try allocator.dupe(u8, "CONFDATA_MANIFEST_FIELD_MISMATCH");
            const value = try std.fmt.allocPrint(allocator, "{s}:actual={s}:expected={s}", .{ field_name, actual_text, expected_item });
            try issues.append(allocator, .{ .code = code, .value = value });
            return;
        }
    }
}

fn emitIssues(io: Io, allocator: std.mem.Allocator, issues: []const Issue) !u8 {
    var grouped = std.StringHashMap(std.ArrayList([]const u8)).init(allocator);
    defer {
        var it = grouped.iterator();
        while (it.next()) |entry| {
            for (entry.value_ptr.items) |value| allocator.free(value);
            entry.value_ptr.deinit(allocator);
        }
        grouped.deinit();
    }
    for (issues) |issue| {
        const result = try grouped.getOrPut(issue.code);
        if (!result.found_existing) result.value_ptr.* = .empty;
        try result.value_ptr.append(allocator, try allocator.dupe(u8, issue.value));
    }
    try guard.printLine(io, "PHASE2_CONFDATA_SURVEY_ALIGNMENT=fail", .{});
    var it = grouped.iterator();
    while (it.next()) |entry| {
        try guard.printLine(io, "{s}_START", .{entry.key_ptr.*});
        for (entry.value_ptr.items) |value| try guard.printLine(io, "{s}", .{value});
        try guard.printLine(io, "{s}_END", .{entry.key_ptr.*});
    }
    return 1;
}

fn buildSelfTestRoot(tmp: *guard.TempWorkspace) !void {
    const bridge =
        \\test "confdata bridge parses bounded config states" {
        \\}
        \\test "confdata bridge emits bounded json output" {
        \\}
        \\test "confdata bridge duplicate assignments coverage" {
        \\}
        \\test "confdata bridge duplicate malformed quoted assignment coverage" {
        \\}
        \\
    ;
    const cases =
        \\{
        \\  "confdata_cases": [
        \\    {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
        \\    {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
        \\    {"name": "duplicate_malformed_quoted_assignment", "input": "duplicate_malformed_quoted_assignment.config", "expected": "duplicate_malformed_quoted_assignment_expected.json"}
        \\  ]
        \\}
        \\
    ;
    const manifest =
        \\{
        \\  "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        \\  "status": "closed",
        \\  "mode": "bounded config bridge",
        \\  "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        \\  "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        \\  "case_count": 3,
        \\  "cases": ["sample", "duplicate_assignments", "duplicate_malformed_quoted_assignment"],
        \\  "input_packet": ["sample.config", "duplicate_assignments.config", "duplicate_malformed_quoted_assignment.config"],
        \\  "expected_packet": ["sample_expected.json", "duplicate_assignments_expected.json", "duplicate_malformed_quoted_assignment_expected.json"],
        \\  "helper_local_anchors": [
        \\    "confdata bridge parses bounded config states",
        \\    "confdata bridge emits bounded json output",
        \\    "confdata bridge duplicate assignments coverage",
        \\    "confdata bridge duplicate malformed quoted assignment coverage"
        \\  ]
        \\}
        \\
    ;
    const survey =
        \\# Phase 2 Confdata Bridge Survey
        \\
        \\`scripts/zigux/kconfig/confdata_bridge.zig` ships `4` helper-local tests.
        \\The current `confdata_cases` packet with 3 fixture cases stays aligned to `zigux/tests/fixtures/kconfig_bridge/cases.json`.
        \\The live `4`-anchor and `3`-case confdata packet remains reviewable through `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`.
        \\Duplicate packet coverage includes `duplicate_assignments` and `duplicate_malformed_quoted_assignment`.
        \\Replay routes: `zig run scripts/zigux/check_kconfig_bridge.zig -- --self-test`, `zig run scripts/zigux/check_phase2_kconfig_selftest_alignment.zig -- --self-test`, `zig run scripts/zigux/check_phase2_kconfig_selftest_alignment.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig`.
        \\
    ;
    try tmp.write(BRIDGE_REL, bridge);
    try tmp.write(CASES_REL, cases);
    try tmp.write(MANIFEST_REL, manifest);
    try tmp.write(SURVEY_REL, survey);
}

fn issuesContain(issues: []const Issue, code: []const u8, value: []const u8) bool {
    for (issues) |issue| {
        if (std.mem.eql(u8, issue.code, code) and std.mem.eql(u8, issue.value, value)) return true;
    }
    return false;
}

fn issuesContainPrefix(issues: []const Issue, code: []const u8, prefix: []const u8) bool {
    for (issues) |issue| {
        if (std.mem.eql(u8, issue.code, code) and std.mem.startsWith(u8, issue.value, prefix)) return true;
    }
    return false;
}

fn freeIssues(allocator: std.mem.Allocator, issues: []const Issue) void {
    for (issues) |issue| {
        allocator.free(issue.code);
        allocator.free(issue.value);
    }
    allocator.free(issues);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var checks: usize = 0;
    var tmp = try guard.TempWorkspace.init(io, allocator, "p2_confdata_survey");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);

    try buildSelfTestRoot(&tmp);
    const ok_issues = try collectIssues(io, allocator, root);
    defer freeIssues(allocator, ok_issues);
    try guard.expectSelfTest(ok_issues.len == 0);
    checks += 1;

    try buildSelfTestRoot(&tmp);
    const survey_path = try guard.joinPath(allocator, root, SURVEY_REL);
    defer allocator.free(survey_path);
    const survey_text = try guard.readUtf8File(io, allocator, survey_path);
    defer allocator.free(survey_text);
    const broken = try std.mem.replaceOwned(u8, allocator, survey_text, "`4` helper-local tests", "`3` helper-local tests");
    defer allocator.free(broken);
    try guard.writeUtf8File(io, survey_path, broken);
    const marker_issues = try collectIssues(io, allocator, root);
    defer freeIssues(allocator, marker_issues);
    try guard.expectSelfTest(issuesContain(marker_issues, "MISSING_CONFDATA_SURVEY_MARKERS", "`4` helper-local tests"));
    checks += 1;

    try buildSelfTestRoot(&tmp);
    const manifest_path = try guard.joinPath(allocator, root, MANIFEST_REL);
    defer allocator.free(manifest_path);
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();
    var manifest_object = switch (manifest_parsed.value) {
        .object => |object| object,
        else => return error.InvalidManifest,
    };
    try manifest_object.put(allocator, "case_count", .{ .integer = 2 });
    const manifest_text_broken = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text_broken);
    const broken_manifest = try std.mem.replaceOwned(u8, allocator, manifest_text_broken, "\"case_count\": 3", "\"case_count\": 2");
    defer allocator.free(broken_manifest);
    try guard.writeUtf8File(io, manifest_path, broken_manifest);
    const manifest_issues = try collectIssues(io, allocator, root);
    defer freeIssues(allocator, manifest_issues);
    try guard.expectSelfTest(issuesContainPrefix(manifest_issues, "CONFDATA_MANIFEST_FIELD_MISMATCH", "case_count:"));
    checks += 1;

    try buildSelfTestRoot(&tmp);
    const survey_text2 = try guard.readUtf8File(io, allocator, survey_path);
    defer allocator.free(survey_text2);
    const broken2 = try std.mem.replaceOwned(u8, allocator, survey_text2, "duplicate_malformed_quoted_assignment", "missing_duplicate_case");
    defer allocator.free(broken2);
    try guard.writeUtf8File(io, survey_path, broken2);
    const missing_case_issues = try collectIssues(io, allocator, root);
    defer freeIssues(allocator, missing_case_issues);
    try guard.expectSelfTest(issuesContain(missing_case_issues, "MISSING_CONFDATA_SURVEY_MARKERS", "duplicate_malformed_quoted_assignment"));
    checks += 1;

    try guard.expectSelfTest(checks == EXPECTED_SELF_TEST_CASE_COUNT);
    try guard.printLine(io, "PHASE2_CONFDATA_SURVEY_ALIGNMENT_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE2_CONFDATA_SURVEY_ALIGNMENT_SELF_TEST_CASE_COUNT={d}", .{checks});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
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

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    const issues = try collectIssues(io, allocator, root);
    defer freeIssues(allocator, issues);
    if (issues.len != 0) {
        std.process.exit(try emitIssues(io, allocator, issues));
    }

    const bridge_path = try guard.joinPath(allocator, root, BRIDGE_REL);
    defer allocator.free(bridge_path);
    const bridge_text = try guard.readUtf8File(io, allocator, bridge_path);
    defer allocator.free(bridge_text);
    const anchors = try countTestAnchors(bridge_text);
    defer std.heap.page_allocator.free(anchors);
    const cases_text = try guard.readUtf8File(io, allocator, try guard.joinPath(allocator, root, CASES_REL));
    defer allocator.free(cases_text);
    const cases_parsed = try guard.parseJsonValue(allocator, cases_text);
    defer cases_parsed.deinit();
    const cases = try loadConfdataCases(cases_parsed.value);
    defer std.heap.page_allocator.free(cases);

    try guard.printLine(io, "PHASE2_CONFDATA_SURVEY_ALIGNMENT=pass", .{});
    try guard.printLine(io, "PHASE2_CONFDATA_SURVEY_ALIGNMENT_HELPER_ANCHOR_COUNT={d}", .{anchors.len});
    try guard.printLine(io, "PHASE2_CONFDATA_SURVEY_ALIGNMENT_CASE_COUNT={d}", .{cases.len});
}