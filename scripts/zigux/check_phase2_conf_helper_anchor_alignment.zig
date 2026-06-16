const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const CONF_BRIDGE_REL = "scripts/zigux/kconfig/conf_bridge.zig";
const CASES_REL = "zigux/tests/fixtures/kconfig_bridge/cases.json";

const GENERAL_ANCHOR_MODE_SURFACE = "conf bridge mode surface stays aligned with conf.c long options";
const GENERAL_ANCHOR_SILENT = "conf bridge emits silent flag before mode flag";
const GENERAL_ANCHOR_MODE_ARG = "mode argument validation rejects bridge option shaped defconfig payload";
const GENERAL_ANCHOR_SYNC_NOSILENT = "bridge options parser accepts syncconfig nosilentupdate";
const GENERAL_ANCHOR_UNEXPECTED = "bridge options parser rejects unexpected options for mode";
const MODE_ANCHOR_DEFCONFIG = "conf bridge emits defconfig mode argument before kconfig";
const MODE_ANCHOR_SAVEDEFCONFIG = "conf bridge emits savedefconfig mode argument before kconfig";
const MODE_ANCHOR_RAND_OVERRIDE = "conf bridge emits explicit randconfig allconfig override when present";
const MODE_ANCHOR_RAND_OMIT = "conf bridge omits randconfig allconfig sentinel without explicit override";
const MODE_ANCHOR_ALLCONFIG = "conf bridge emits alldefconfig argv and env";
const MODE_ANCHOR_ALLCONFIG_OVERRIDE = "conf bridge emits explicit empty allconfig override for allmodconfig";

fn collectTestAnchors(source: []const u8, allocator: std.mem.Allocator) !std.StringHashMap(void) {
    var anchors = std.StringHashMap(void).init(allocator);
    var iter = std.mem.splitScalar(u8, source, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (!std.mem.startsWith(u8, line, "test \"")) continue;
        const end_quote = std.mem.indexOfScalar(u8, line[6..], '"') orelse continue;
        const anchor = line[6 .. 6 + end_quote];
        try anchors.put(try allocator.dupe(u8, anchor), {});
    }
    return anchors;
}

fn collectModeEnum(source: []const u8, allocator: std.mem.Allocator) ![]const []const u8 {
    const marker = "pub const Mode = enum {";
    const start = std.mem.indexOf(u8, source, marker) orelse return error.MissingModeEnum;
    const after = start + marker.len;
    const end = std.mem.indexOfPos(u8, source, after, "\n};") orelse return error.MissingModeEnum;
    const body = std.mem.trim(u8, source[after..end], " \t\r\n");
    var modes: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (modes.items) |mode| allocator.free(mode);
        modes.deinit(allocator);
    }
    var iter = std.mem.splitScalar(u8, body, ',');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r\n");
        if (line.len == 0) continue;
        if (std.mem.indexOf(u8, line, "pub fn") != null) break;
        const comma = std.mem.indexOfScalar(u8, line, ',') orelse 0;
        _ = comma;
        const mode_name = std.mem.trim(u8, line, " \t\r\n,");
        if (mode_name.len == 0) continue;
        try modes.append(allocator, try allocator.dupe(u8, mode_name));
    }
    return modes.toOwnedSlice(allocator);
}

fn expectAnchor(issues: *std.ArrayList([]const u8), allocator: std.mem.Allocator, anchors: *const std.StringHashMap(void), key: []const u8, anchor: []const u8) !void {
    _ = anchors.get(anchor) orelse {
        const issue = try std.fmt.allocPrint(allocator, "{s}: missing helper anchor '{s}'", .{ key, anchor });
        try issues.append(allocator, issue);
        return;
    };
}

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) ![]const []const u8 {
    const bridge_path = try guard.joinPath(allocator, root, CONF_BRIDGE_REL);
    defer allocator.free(bridge_path);
    const cases_path = try guard.joinPath(allocator, root, CASES_REL);
    defer allocator.free(cases_path);
    const source = try guard.readUtf8File(io, allocator, bridge_path);
    defer allocator.free(source);
    const cases_text = try guard.readUtf8File(io, allocator, cases_path);
    defer allocator.free(cases_text);
    const parsed = try guard.parseJsonValue(allocator, cases_text);
    defer parsed.deinit();

    var issues: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (issues.items) |issue| allocator.free(issue);
        issues.deinit(allocator);
    }

    var anchors = try collectTestAnchors(source, allocator);
    defer {
        var it = anchors.iterator();
        while (it.next()) |entry| allocator.free(entry.key_ptr.*);
        anchors.deinit();
    }
    const enum_modes = try collectModeEnum(source, allocator);
    defer {
        for (enum_modes) |mode| allocator.free(mode);
        allocator.free(enum_modes);
    }

    const root_object = switch (parsed.value) {
        .object => |object| object,
        else => {
            const issue = try std.fmt.allocPrint(allocator, "{s}: expected object root", .{CASES_REL});
            try issues.append(allocator, issue);
            return issues.toOwnedSlice(allocator);
        },
    };
    const conf_cases_value = root_object.get("conf_cases") orelse {
        const issue = try std.fmt.allocPrint(allocator, "{s}: expected conf_cases array", .{CASES_REL});
        try issues.append(allocator, issue);
        return issues.toOwnedSlice(allocator);
    };
    const conf_cases = switch (conf_cases_value) {
        .array => |items| items,
        else => {
            const issue = try std.fmt.allocPrint(allocator, "{s}: expected conf_cases array", .{CASES_REL});
            try issues.append(allocator, issue);
            return issues.toOwnedSlice(allocator);
        },
    };

    var case_modes: std.ArrayList([]const u8) = .empty;
    defer case_modes.deinit(allocator);
    var silent_case_count: usize = 0;
    var mode_arg_case_count: usize = 0;
    var randconfig_override_case_count: usize = 0;
    var randconfig_plain_case_count: usize = 0;
    var allconfig_sentinel_case_count: usize = 0;
    var allconfig_override_case_count: usize = 0;
    var syncconfig_nosilent_case_count: usize = 0;

    for (conf_cases.items, 0..) |raw_case, index| {
        const case_object = switch (raw_case) {
            .object => |object| object,
            else => {
                const issue = try std.fmt.allocPrint(allocator, "{s}[{d}]: expected object case", .{ CASES_REL, index });
                try issues.append(allocator, issue);
                continue;
            },
        };
        const mode_value = case_object.get("mode") orelse {
            const issue = try std.fmt.allocPrint(allocator, "conf_cases[{d}]: missing string mode", .{index});
            try issues.append(allocator, issue);
            continue;
        };
        const expected_value = case_object.get("expected") orelse {
            const issue = try std.fmt.allocPrint(allocator, "conf_cases[{d}]: missing string expected", .{index});
            try issues.append(allocator, issue);
            continue;
        };
        const mode = switch (mode_value) {
            .string => |text| text,
            else => {
                const issue = try std.fmt.allocPrint(allocator, "conf_cases[{d}]: missing string mode", .{index});
                try issues.append(allocator, issue);
                continue;
            },
        };
        switch (expected_value) {
            .string => {},
            else => {
                const issue = try std.fmt.allocPrint(allocator, "conf_cases[{d}]: missing string expected", .{index});
                try issues.append(allocator, issue);
                continue;
            },
        }
        try case_modes.append(allocator, mode);
        if (case_object.get("silent")) |silent| {
            if (silent == .bool and silent.bool) silent_case_count += 1;
        }
        if (case_object.get("mode_arg") != null) mode_arg_case_count += 1;
        if (std.mem.eql(u8, mode, "syncconfig") and case_object.get("nosilentupdate") != null) syncconfig_nosilent_case_count += 1;
        if (std.mem.eql(u8, mode, "randconfig") and case_object.get("allconfig") != null) randconfig_override_case_count += 1;
        if (std.mem.eql(u8, mode, "randconfig") and case_object.get("allconfig") == null) randconfig_plain_case_count += 1;
        if ((std.mem.eql(u8, mode, "allnoconfig") or std.mem.eql(u8, mode, "allyesconfig") or std.mem.eql(u8, mode, "allmodconfig") or std.mem.eql(u8, mode, "alldefconfig")) and case_object.get("allconfig") == null) allconfig_sentinel_case_count += 1;
        if ((std.mem.eql(u8, mode, "allnoconfig") or std.mem.eql(u8, mode, "allyesconfig") or std.mem.eql(u8, mode, "allmodconfig") or std.mem.eql(u8, mode, "alldefconfig")) and case_object.get("allconfig") != null) allconfig_override_case_count += 1;
    }

    if (case_modes.items.len != enum_modes.len or !modesEqual(case_modes.items, enum_modes)) {
        const issue = try std.fmt.allocPrint(allocator, "conf case modes drift from Mode enum: expected {any}, got {any}", .{ enum_modes, case_modes.items });
        try issues.append(allocator, issue);
    }

    try expectAnchor(&issues, allocator, &anchors, "mode surface", GENERAL_ANCHOR_MODE_SURFACE);
    if (silent_case_count > 0) try expectAnchor(&issues, allocator, &anchors, "silent packet", GENERAL_ANCHOR_SILENT);
    if (mode_arg_case_count > 0) {
        try expectAnchor(&issues, allocator, &anchors, "mode arg rejection packet", GENERAL_ANCHOR_MODE_ARG);
        try expectAnchor(&issues, allocator, &anchors, "defconfig mode arg anchor", MODE_ANCHOR_DEFCONFIG);
        try expectAnchor(&issues, allocator, &anchors, "savedefconfig mode arg anchor", MODE_ANCHOR_SAVEDEFCONFIG);
    }
    if (syncconfig_nosilent_case_count > 0) try expectAnchor(&issues, allocator, &anchors, "syncconfig nosilent packet", GENERAL_ANCHOR_SYNC_NOSILENT);
    if (randconfig_override_case_count > 0) try expectAnchor(&issues, allocator, &anchors, "randconfig allconfig override packet", MODE_ANCHOR_RAND_OVERRIDE);
    if (randconfig_plain_case_count > 0) try expectAnchor(&issues, allocator, &anchors, "randconfig no-sentinel packet", MODE_ANCHOR_RAND_OMIT);
    if (allconfig_sentinel_case_count > 0) try expectAnchor(&issues, allocator, &anchors, "allconfig sentinel packet", MODE_ANCHOR_ALLCONFIG);
    if (allconfig_override_case_count > 0) try expectAnchor(&issues, allocator, &anchors, "allconfig explicit override packet", MODE_ANCHOR_ALLCONFIG_OVERRIDE);
    try expectAnchor(&issues, allocator, &anchors, "unexpected-option packet", GENERAL_ANCHOR_UNEXPECTED);

    return issues.toOwnedSlice(allocator);
}

fn modesEqual(left: []const []const u8, right: []const []const u8) bool {
    if (left.len != right.len) return false;
    for (left, right) |a, b| {
        if (!std.mem.eql(u8, a, b)) return false;
    }
    return true;
}

fn buildSelfTestRoot(tmp: *guard.TempWorkspace) !void {
    const bridge =
        \\const std = @import("std");
        \\
        \\pub const Mode = enum {
        \\    oldaskconfig,
        \\    syncconfig,
        \\    oldconfig,
        \\    allnoconfig,
        \\    allyesconfig,
        \\    allmodconfig,
        \\    alldefconfig,
        \\    randconfig,
        \\    defconfig,
        \\    savedefconfig,
        \\    listnewconfig,
        \\    helpnewconfig,
        \\    olddefconfig,
        \\    yes2modconfig,
        \\    mod2yesconfig,
        \\    mod2noconfig,
        \\};
        \\
        \\test "conf bridge mode surface stays aligned with conf.c long options" {
        \\}
        \\test "conf bridge emits silent flag before mode flag" {
        \\}
        \\test "mode argument validation rejects bridge option shaped defconfig payload" {
        \\}
        \\test "bridge options parser accepts syncconfig nosilentupdate" {
        \\}
        \\test "bridge options parser rejects unexpected options for mode" {
        \\}
        \\test "conf bridge emits defconfig mode argument before kconfig" {
        \\}
        \\test "conf bridge emits savedefconfig mode argument before kconfig" {
        \\}
        \\test "conf bridge emits explicit randconfig allconfig override when present" {
        \\}
        \\test "conf bridge omits randconfig allconfig sentinel without explicit override" {
        \\}
        \\test "conf bridge emits alldefconfig argv and env" {
        \\}
        \\test "conf bridge emits explicit empty allconfig override for allmodconfig" {
        \\}
        \\
    ;
    const cases =
        \\{
        \\  "conf_cases": [
        \\    {"mode": "oldaskconfig", "expected": "oldaskconfig_expected.json"},
        \\    {"mode": "syncconfig", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
        \\    {"mode": "oldconfig", "expected": "oldconfig_expected.json"},
        \\    {"mode": "allnoconfig", "expected": "allnoconfig_expected.json"},
        \\    {"mode": "allyesconfig", "expected": "allyesconfig_expected.json"},
        \\    {"mode": "allmodconfig", "allconfig": "", "expected": "allmodconfig_expected.json"},
        \\    {"mode": "alldefconfig", "expected": "alldefconfig_expected.json"},
        \\    {"mode": "randconfig", "allconfig": "allrandom.config", "expected": "randconfig_expected.json"},
        \\    {"mode": "defconfig", "mode_arg": "mini_defconfig", "expected": "defconfig_expected.json"},
        \\    {"mode": "savedefconfig", "mode_arg": "defconfig.out", "expected": "savedefconfig_expected.json"},
        \\    {"mode": "listnewconfig", "silent": true, "expected": "listnewconfig_expected.json"},
        \\    {"mode": "helpnewconfig", "silent": true, "expected": "helpnewconfig_expected.json"},
        \\    {"mode": "olddefconfig", "expected": "olddefconfig_expected.json"},
        \\    {"mode": "yes2modconfig", "expected": "yes2modconfig_expected.json"},
        \\    {"mode": "mod2yesconfig", "expected": "mod2yesconfig_expected.json"},
        \\    {"mode": "mod2noconfig", "expected": "mod2noconfig_expected.json"}
        \\  ]
        \\}
        \\
    ;
    try tmp.write(CONF_BRIDGE_REL, bridge);
    try tmp.write(CASES_REL, cases);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var checks: usize = 0;
    var tmp = try guard.TempWorkspace.init(io, allocator, "p2_conf_helper_anchor");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);

    try buildSelfTestRoot(&tmp);
    const ok_issues = try collectIssues(io, allocator, root);
    defer {
        for (ok_issues) |issue| allocator.free(issue);
        allocator.free(ok_issues);
    }
    try guard.expectSelfTest(ok_issues.len == 0);
    checks += 1;

    try buildSelfTestRoot(&tmp);
    const bridge_path = try guard.joinPath(allocator, root, CONF_BRIDGE_REL);
    defer allocator.free(bridge_path);
    {
        const source = try guard.readUtf8File(io, allocator, bridge_path);
        defer allocator.free(source);
        const replaced = try std.mem.replaceOwned(u8, allocator, source, "test \"conf bridge emits explicit randconfig allconfig override when present\" {\n}\n", "");
        defer allocator.free(replaced);
        if (!std.mem.eql(u8, replaced, source)) {
            try guard.writeUtf8File(io, bridge_path, replaced);
            const issues = try collectIssues(io, allocator, root);
            defer {
                for (issues) |issue| allocator.free(issue);
                allocator.free(issues);
            }
            try guard.expectSelfTest(anyStartsWith(issues, "randconfig allconfig override packet:"));
            checks += 1;
        }
    }

    try buildSelfTestRoot(&tmp);
    {
        const source = try guard.readUtf8File(io, allocator, bridge_path);
        defer allocator.free(source);
        const replaced_def = try std.mem.replaceOwned(u8, allocator, source, "test \"conf bridge emits defconfig mode argument before kconfig\" {\n}\n", "");
        defer allocator.free(replaced_def);
        if (!std.mem.eql(u8, replaced_def, source)) {
            try guard.writeUtf8File(io, bridge_path, replaced_def);
            const issues = try collectIssues(io, allocator, root);
            defer {
                for (issues) |issue| allocator.free(issue);
                allocator.free(issues);
            }
            try guard.expectSelfTest(anyStartsWith(issues, "defconfig mode arg anchor:"));
            checks += 1;
        }
    }

    try buildSelfTestRoot(&tmp);
    {
        const source = try guard.readUtf8File(io, allocator, bridge_path);
        defer allocator.free(source);
        const replaced_silent = try std.mem.replaceOwned(u8, allocator, source, "test \"conf bridge emits silent flag before mode flag\" {\n}\n", "");
        defer allocator.free(replaced_silent);
        if (!std.mem.eql(u8, replaced_silent, source)) {
            try guard.writeUtf8File(io, bridge_path, replaced_silent);
            const issues = try collectIssues(io, allocator, root);
            defer {
                for (issues) |issue| allocator.free(issue);
                allocator.free(issues);
            }
            try guard.expectSelfTest(anyStartsWith(issues, "silent packet:"));
            checks += 1;
        }
    }

    try buildSelfTestRoot(&tmp);
    const cases_path = try guard.joinPath(allocator, root, CASES_REL);
    defer allocator.free(cases_path);
    const cases_text = try guard.readUtf8File(io, allocator, cases_path);
    defer allocator.free(cases_text);
    const parsed = try guard.parseJsonValue(allocator, cases_text);
    defer parsed.deinit();
    const reversed_cases =
        \\{
        \\  "conf_cases": [
        \\    {"mode": "mod2noconfig", "expected": "mod2noconfig_expected.json"},
        \\    {"mode": "mod2yesconfig", "expected": "mod2yesconfig_expected.json"},
        \\    {"mode": "yes2modconfig", "expected": "yes2modconfig_expected.json"},
        \\    {"mode": "olddefconfig", "expected": "olddefconfig_expected.json"},
        \\    {"mode": "helpnewconfig", "silent": true, "expected": "helpnewconfig_expected.json"},
        \\    {"mode": "listnewconfig", "silent": true, "expected": "listnewconfig_expected.json"},
        \\    {"mode": "savedefconfig", "mode_arg": "defconfig.out", "expected": "savedefconfig_expected.json"},
        \\    {"mode": "defconfig", "mode_arg": "mini_defconfig", "expected": "defconfig_expected.json"},
        \\    {"mode": "randconfig", "allconfig": "allrandom.config", "expected": "randconfig_expected.json"},
        \\    {"mode": "alldefconfig", "expected": "alldefconfig_expected.json"},
        \\    {"mode": "allmodconfig", "allconfig": "", "expected": "allmodconfig_expected.json"},
        \\    {"mode": "allyesconfig", "expected": "allyesconfig_expected.json"},
        \\    {"mode": "allnoconfig", "expected": "allnoconfig_expected.json"},
        \\    {"mode": "oldconfig", "expected": "oldconfig_expected.json"},
        \\    {"mode": "syncconfig", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
        \\    {"mode": "oldaskconfig", "expected": "oldaskconfig_expected.json"}
        \\  ]
        \\}
        \\
    ;
    try guard.writeUtf8File(io, cases_path, reversed_cases);
    const drift_issues = try collectIssues(io, allocator, root);
    defer {
        for (drift_issues) |issue| allocator.free(issue);
        allocator.free(drift_issues);
    }
    try guard.expectSelfTest(anyStartsWith(drift_issues, "conf case modes drift from Mode enum:"));
    checks += 1;

    try guard.printLine(io, "PHASE2_CONF_HELPER_ALIGNMENT_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE2_CONF_HELPER_ALIGNMENT_SELF_TEST_CASE_COUNT={d}", .{checks});
    return 0;
}

fn anyStartsWith(issues: []const []const u8, prefix: []const u8) bool {
    for (issues) |issue| {
        if (std.mem.startsWith(u8, issue, prefix)) return true;
    }
    return false;
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
    defer {
        for (issues) |issue| allocator.free(issue);
        allocator.free(issues);
    }
    if (issues.len != 0) {
        try guard.printLine(io, "PHASE2_CONF_HELPER_ALIGNMENT=fail", .{});
        for (issues) |issue| try guard.printLine(io, "{s}", .{issue});
        std.process.exit(1);
    }
    try guard.printLine(io, "PHASE2_CONF_HELPER_ALIGNMENT=pass", .{});
}