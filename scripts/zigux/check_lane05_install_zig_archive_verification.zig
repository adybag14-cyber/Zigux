const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass";
pub const self_test_pass_marker = "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass";

const install_zig_rel = "scripts/zigux/install_zig.zig";
const toolchain_policy_rel = "scripts/zigux/zig-toolchain-policy.json";

const INSTALL_ZIG_MARKERS = [_][]const u8{
    "pub fn loadPolicyArchiveSha256(",
    "expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key)",
    "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator)",
    "if (expected_archive_sha256) |digest| {",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "ZIG_INSTALL_ARCHIVE_SHA256={s}",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
    "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
    "try copyDirRecursive(io, extracted_root, final_root)",
};

const EXACT_COUNT_MARKERS = [_][]const u8{
    "expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key)",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
};

const ORDERED_MARKERS = [_]struct { earlier: []const u8, later: []const u8 }{
    .{
        .earlier = "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator)",
        .later = "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    },
    .{
        .earlier = "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
        .later = "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
    },
    .{
        .earlier = "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
        .later = "try copyDirRecursive(io, extracted_root, final_root)",
    },
};

const Issue = struct {
    code: []const u8,
    value: []const u8,
    owned_value: ?[]u8 = null,
};

fn appendOwnedIssue(
    allocator: std.mem.Allocator,
    issues: *std.ArrayList(Issue),
    code: []const u8,
    value: []u8,
) !void {
    errdefer allocator.free(value);
    try issues.append(allocator, .{ .code = code, .value = value, .owned_value = value });
}

fn deinitIssues(allocator: std.mem.Allocator, issues: *std.ArrayList(Issue)) void {
    for (issues.items) |issue| {
        if (issue.owned_value) |value| allocator.free(value);
    }
    issues.deinit(allocator);
}

fn isExactCountMarker(marker: []const u8) bool {
    for (EXACT_COUNT_MARKERS) |exact| {
        if (std.mem.eql(u8, exact, marker)) return true;
    }
    return false;
}

fn isValidSha256Hex(digest: []const u8) bool {
    if (digest.len != 64) return false;
    for (digest) |ch| {
        const ok = (ch >= '0' and ch <= '9') or (ch >= 'a' and ch <= 'f');
        if (!ok) return false;
    }
    return true;
}

fn collectPolicyIssues(allocator: std.mem.Allocator, issues: *std.ArrayList(Issue), policy: std.json.Value) !void {
    const archive_sha256 = policy.object.get("archive_sha256") orelse {
        try issues.append(allocator, .{ .code = "INVALID_POLICY_FIELD", .value = "archive_sha256" });
        return;
    };
    if (archive_sha256 != .object or archive_sha256.object.count() == 0) {
        try issues.append(allocator, .{ .code = "INVALID_POLICY_FIELD", .value = "archive_sha256" });
        return;
    }

    const upgrade_policy = policy.object.get("upgrade_policy") orelse {
        try issues.append(allocator, .{ .code = "INVALID_POLICY_FIELD", .value = "upgrade_policy" });
        return;
    };
    if (upgrade_policy != .object) {
        try issues.append(allocator, .{ .code = "INVALID_POLICY_FIELD", .value = "upgrade_policy" });
        return;
    }

    const archive_target_scope = upgrade_policy.object.get("archive_target_scope") orelse {
        try issues.append(allocator, .{ .code = "INVALID_POLICY_FIELD", .value = "archive_target_scope" });
        return;
    };
    if (archive_target_scope != .array or archive_target_scope.array.items.len == 0) {
        try issues.append(allocator, .{ .code = "INVALID_POLICY_FIELD", .value = "archive_target_scope" });
        return;
    }

    for (archive_target_scope.array.items, 0..) |entry, index| {
        if (entry != .string or entry.string.len == 0) {
            const index_text = try std.fmt.allocPrint(allocator, "index={d}", .{index});
            try appendOwnedIssue(allocator, issues, "INVALID_ARCHIVE_TARGET", index_text);
            continue;
        }
        const target = entry.string;
        const digest_value = archive_sha256.object.get(target);
        if (digest_value == null or digest_value.? != .string or !isValidSha256Hex(digest_value.?.string)) {
            const target_copy = try allocator.dupe(u8, target);
            try appendOwnedIssue(allocator, issues, "INVALID_ARCHIVE_SHA256", target_copy);
        }
    }
}

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) !std.ArrayList(Issue) {
    var issues: std.ArrayList(Issue) = .empty;
    errdefer deinitIssues(allocator, &issues);

    const install_path = try guard.joinPath(allocator, root, install_zig_rel);
    defer allocator.free(install_path);
    const install_text = try guard.readUtf8File(io, allocator, install_path);
    defer allocator.free(install_text);

    const policy_path = try guard.joinPath(allocator, root, toolchain_policy_rel);
    defer allocator.free(policy_path);
    const policy_text = try guard.readUtf8File(io, allocator, policy_path);
    defer allocator.free(policy_text);
    const parsed_policy = try guard.parseJsonValue(allocator, policy_text);
    defer parsed_policy.deinit();

    for (INSTALL_ZIG_MARKERS) |marker| {
        const count = guard.countOccurrences(install_text, marker);
        if (count == 0) {
            try issues.append(allocator, .{ .code = "MISSING_INSTALL_MARKER", .value = marker });
        } else if (isExactCountMarker(marker) and count != 1) {
            const detail = try std.fmt.allocPrint(allocator, "{s}:count={d}", .{ marker, count });
            try appendOwnedIssue(allocator, &issues, "DUPLICATE_INSTALL_MARKER", detail);
        }
    }

    for (ORDERED_MARKERS) |pair| {
        const earlier_index = std.mem.indexOf(u8, install_text, pair.earlier);
        const later_index = std.mem.indexOf(u8, install_text, pair.later);
        if (earlier_index == null or later_index == null) continue;
        if (earlier_index.? >= later_index.?) {
            const detail = try std.fmt.allocPrint(allocator, "{s} -> {s}", .{ pair.earlier, pair.later });
            try appendOwnedIssue(allocator, &issues, "ORDER_MISMATCH", detail);
        }
    }

    try collectPolicyIssues(allocator, &issues, parsed_policy.value);

    return issues;
}

fn policyTargetCount(io: Io, allocator: std.mem.Allocator, root: []const u8) !usize {
    const policy_path = try guard.joinPath(allocator, root, toolchain_policy_rel);
    defer allocator.free(policy_path);
    const policy_text = try guard.readUtf8File(io, allocator, policy_path);
    defer allocator.free(policy_text);
    const parsed_policy = try guard.parseJsonValue(allocator, policy_text);
    defer parsed_policy.deinit();

    const upgrade_policy = parsed_policy.value.object.get("upgrade_policy") orelse return guard.GuardError.ValidationFailed;
    if (upgrade_policy != .object) return guard.GuardError.ValidationFailed;
    const archive_target_scope = upgrade_policy.object.get("archive_target_scope") orelse return guard.GuardError.ValidationFailed;
    if (archive_target_scope != .array) return guard.GuardError.ValidationFailed;
    return archive_target_scope.array.items.len;
}

fn emitIssues(io: Io, allocator: std.mem.Allocator, issues: []const Issue) !u8 {
    try guard.printLine(io, "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=fail", .{});

    var seen_codes: std.ArrayList([]const u8) = .empty;
    defer seen_codes.deinit(allocator);

    for (issues) |issue| {
        var already_seen = false;
        for (seen_codes.items) |code| {
            if (std.mem.eql(u8, code, issue.code)) {
                already_seen = true;
                break;
            }
        }
        if (already_seen) continue;
        try seen_codes.append(allocator, issue.code);
        try guard.printLine(io, "{s}_START", .{issue.code});
        for (issues) |entry| {
            if (std.mem.eql(u8, entry.code, issue.code)) {
                try guard.printLine(io, "{s}", .{entry.value});
            }
        }
        try guard.printLine(io, "{s}_END", .{issue.code});
    }
    return 1;
}

fn hasIssue(issues: []const Issue, code: []const u8, value: []const u8) bool {
    for (issues) |issue| {
        if (std.mem.eql(u8, issue.code, code) and std.mem.eql(u8, issue.value, value)) return true;
    }
    return false;
}

fn hasIssueCode(issues: []const Issue, code: []const u8) bool {
    for (issues) |issue| {
        if (std.mem.eql(u8, issue.code, code)) return true;
    }
    return false;
}

fn replaceOnce(allocator: std.mem.Allocator, text: []const u8, marker: []const u8, replacement: []const u8) ![]u8 {
    const index = std.mem.indexOf(u8, text, marker) orelse return error.MissingMarker;
    const prefix = text[0..index];
    const suffix = text[index + marker.len ..];
    return try std.fmt.allocPrint(allocator, "{s}{s}{s}", .{ prefix, replacement, suffix });
}

const self_test_install_zig =
    \\pub fn loadPolicyArchiveSha256(io: std.Io, allocator: std.mem.Allocator, policy_path: []const u8, target_key: []const u8) !?[]const u8 {
    \\    _ = .{ io, allocator, policy_path, target_key };
    \\    return '3' ** 64;
    \\}
    \\
    \\pub fn verifyArchiveSha256(io: std.Io, allocator: std.mem.Allocator, path: []const u8, expected_sha256: []const u8) ![]const u8 {
    \\    _ = .{ io, allocator, path };
    \\    return expected_sha256;
    \\}
    \\
    \\pub fn stageArchive(io: std.Io, local_archive: ?[]const u8, tarball_url: []const u8, archive_path: []const u8, allocator: std.mem.Allocator) !void {
    \\    _ = .{ io, local_archive, tarball_url, archive_path, allocator };
    \\}
    \\
    \\pub fn extractArchive(io: std.Io, allocator: std.mem.Allocator, archive_path: []const u8, dest_path: []const u8) ![]const u8 {
    \\    _ = .{ io, allocator, archive_path };
    \\    return dest_path;
    \\}
    \\
    \\pub fn copyDirRecursive(io: std.Io, source: []const u8, destination: []const u8) !void {
    \\    _ = .{ io, source, destination };
    \\}
    \\
    \\pub fn main() !void {
    \\    const io = undefined;
    \\    const allocator = undefined;
    \\    const policy_path = "scripts/zigux/zig-toolchain-policy.json";
    \\    const resolved = .{ .target_key = "x86_64-linux", .tarball_url = "https://example.invalid/archive.tar.xz" };
    \\    const expanded_archive: ?[]const u8 = null;
    \\    const staged_archive_path = "archive.tar.xz";
    \\    const extract_root = "tmp/extract";
    \\    const extracted_root = "tmp/extract/root";
    \\    const final_root = "out";
    \\    var expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key);
    \\    const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);
    \\    if (expected_archive_sha256) |digest| {
    \\        const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest);
    \\        try std.Io.File.stdout().writer(io, undefined).interface.print("ZIG_INSTALL_ARCHIVE_SHA256={s}\n", .{actual});
    \\        try std.Io.File.stdout().writer(io, undefined).interface.print("ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified\n", .{});
    \\    } else {
    \\        try std.Io.File.stdout().writer(io, undefined).interface.print("ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified\n", .{});
    \\    }
    \\    const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root);
    \\    try copyDirRecursive(io, extracted_root, final_root);
    \\    _ = .{ archive_source, extracted_name };
    \\}
    \\
;

const self_test_policy_json =
    \\{
    \\  "phase": "Phase 2",
    \\  "channel": "0.17.0-dev.1415+64dfaa568",
    \\  "minimum_version": "0.17.0-dev.1415+64dfaa568",
    \\  "archive_sha256": {
    \\    "x86_64-linux": "3333333333333333333333333333333333333333333333333333333333333333"
    \\  },
    \\  "upgrade_policy": {
    \\    "channel_minimum_lockstep": true,
    \\    "archive_target_scope": ["x86_64-linux"],
    \\    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"]
    \\  }
    \\}
    \\
;

fn buildSelfTestRoot(workspace: *guard.TempWorkspace) !void {
    try workspace.write(install_zig_rel, self_test_install_zig);
    try workspace.write(toolchain_policy_rel, self_test_policy_json);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var checks_run: u32 = 0;
    const expected_case_count: u32 = 8;

    var workspace = try guard.TempWorkspace.init(io, allocator, "lane05_install_archive_verify");
    defer workspace.deinit();
    const root = try workspace.rootPath(allocator);
    defer allocator.free(root);

    try buildSelfTestRoot(&workspace);
    {
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(issues.items.len == 0);
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const install_path = try guard.joinPath(allocator, root, install_zig_rel);
        defer allocator.free(install_path);
        const install_text = try guard.readUtf8File(io, allocator, install_path);
        defer allocator.free(install_text);
        const mutated = try replaceOnce(
            allocator,
            install_text,
            "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
            "",
        );
        defer allocator.free(mutated);
        try guard.writeUtf8File(io, install_path, mutated);
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(hasIssue(
            issues.items,
            "MISSING_INSTALL_MARKER",
            "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
        ));
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const install_path = try guard.joinPath(allocator, root, install_zig_rel);
        defer allocator.free(install_path);
        const install_text = try guard.readUtf8File(io, allocator, install_path);
        defer allocator.free(install_text);
        const mutated = try std.fmt.allocPrint(allocator, "{s}ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified\n", .{install_text});
        defer allocator.free(mutated);
        try guard.writeUtf8File(io, install_path, mutated);
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(hasIssue(
            issues.items,
            "DUPLICATE_INSTALL_MARKER",
            "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified:count=2",
        ));
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const install_path = try guard.joinPath(allocator, root, install_zig_rel);
        defer allocator.free(install_path);
        const install_text = try guard.readUtf8File(io, allocator, install_path);
        defer allocator.free(install_text);
        const mutated = try replaceOnce(
            allocator,
            install_text,
            "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);\n    if (expected_archive_sha256) |digest| {",
            "if (expected_archive_sha256) |digest| {\n        const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)\n    const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);",
        );
        defer allocator.free(mutated);
        try guard.writeUtf8File(io, install_path, mutated);
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(hasIssueCode(issues.items, "ORDER_MISMATCH"));
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const policy_path = try guard.joinPath(allocator, root, toolchain_policy_rel);
        defer allocator.free(policy_path);
        try guard.writeUtf8File(io, policy_path,
            \\{
            \\  "archive_sha256": {},
            \\  "upgrade_policy": { "archive_target_scope": ["x86_64-linux"] }
            \\}
            \\
        );
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(hasIssue(issues.items, "INVALID_POLICY_FIELD", "archive_sha256"));
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const policy_path = try guard.joinPath(allocator, root, toolchain_policy_rel);
        defer allocator.free(policy_path);
        try guard.writeUtf8File(io, policy_path,
            \\{
            \\  "archive_sha256": { "x86_64-linux": "3333333333333333333333333333333333333333333333333333333333333333", "x86_64-windows": "4444444444444444444444444444444444444444444444444444444444444444" },
            \\  "upgrade_policy": { "archive_target_scope": ["x86_64-linux", "x86_64-windows"] }
            \\}
            \\
        );
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(!hasIssue(issues.items, "UNEXPECTED_ARCHIVE_TARGET_COUNT", "2"));
        try guard.expectSelfTest(issues.items.len == 0);
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const policy_path = try guard.joinPath(allocator, root, toolchain_policy_rel);
        defer allocator.free(policy_path);
        try guard.writeUtf8File(io, policy_path,
            \\{
            \\  "archive_sha256": { "x86_64-linux": "short" },
            \\  "upgrade_policy": { "archive_target_scope": ["x86_64-linux"] }
            \\}
            \\
        );
        var issues = try collectIssues(io, allocator, root);
        defer deinitIssues(allocator, &issues);
        try guard.expectSelfTest(hasIssue(issues.items, "INVALID_ARCHIVE_SHA256", "x86_64-linux"));
        checks_run += 1;
    }

    try buildSelfTestRoot(&workspace);
    {
        const install_path = try guard.joinPath(allocator, root, install_zig_rel);
        defer allocator.free(install_path);
        std.Io.Dir.cwd().deleteFile(io, install_path) catch {};
        if (collectIssues(io, allocator, root)) |_| {
            try guard.expectSelfTest(false);
        } else |err| {
            try guard.expectSelfTest(err == guard.GuardError.IOError);
        }
        checks_run += 1;
    }

    try guard.expectSelfTest(checks_run == expected_case_count);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST_CASE_COUNT={d}", .{checks_run});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
    }

    if (self_test) {
        _ = try runSelfTest(io, allocator);
        return;
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var issues = collectIssues(io, allocator, root) catch |err| switch (err) {
        guard.GuardError.IOError => {
            try guard.printLine(io, "required file missing", .{});
            std.process.exit(1);
        },
        else => return err,
    };
    defer deinitIssues(allocator, &issues);

    if (issues.items.len != 0) {
        std.process.exit(try emitIssues(io, allocator, issues.items));
    }

    const target_count = try policyTargetCount(io, allocator, root);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try guard.printLine(io, "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_MARKER_COUNT={d}", .{INSTALL_ZIG_MARKERS.len});
    try guard.printLine(io, "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_TARGET_COUNT={d}", .{target_count});
}
