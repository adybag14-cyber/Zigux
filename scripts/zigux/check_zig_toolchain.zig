const std = @import("std");
const Io = std.Io;
const policy = @import("toolchain_policy.zig");

pub const default_policy_path = "scripts/zigux/zig-toolchain-policy.json";

pub fn emitPolicySummary(io: Io, allocator: std.mem.Allocator, policy_path: []const u8) !u8 {
    const json_bytes = std.Io.Dir.cwd().readFileAlloc(io, policy_path, allocator, .unlimited) catch |err| switch (err) {
        error.FileNotFound => {
            try printLine(io, "ZIG_TOOLCHAIN_POLICY_STATUS=missing", .{});
            try printLine(io, "ZIG_TOOLCHAIN_POLICY_PATH={s}", .{policy_path});
            return 0;
        },
        else => return err,
    };
    defer allocator.free(json_bytes);

    var loaded = policy.loadPolicyFromJson(allocator, json_bytes) catch |err| {
        try printLine(io, "ZIG_TOOLCHAIN_POLICY_STATUS=invalid", .{});
        try printLine(io, "ZIG_TOOLCHAIN_POLICY_PATH={s}", .{policy_path});
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{@errorName(err)});
        return 1;
    };
    defer policy.freePolicy(allocator, &loaded);

    try printLine(io, "ZIG_TOOLCHAIN_POLICY_STATUS=present", .{});
    try printLine(io, "ZIG_TOOLCHAIN_POLICY_PATH={s}", .{policy_path});
    try printLine(io, "ZIG_TOOLCHAIN_PHASE={s}", .{loaded.phase});
    try printLine(io, "ZIG_TOOLCHAIN_PINNED_CHANNEL={s}", .{loaded.channel});
    try printLine(io, "ZIG_TOOLCHAIN_MIN_SUPPORTED={s}", .{loaded.minimum_version});
    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={d}", .{loaded.archive_sha256.count()});

    var targets_buffer: [512]u8 = undefined;
    var targets_len: usize = 0;
    for (loaded.upgrade_policy.archive_target_scope, 0..) |target, index| {
        if (index != 0) {
            targets_buffer[targets_len] = ',';
            targets_len += 1;
        }
        const copied = try std.fmt.bufPrint(targets_buffer[targets_len..], "{s}", .{target});
        targets_len += copied.len;
    }
    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGETS={s}", .{targets_buffer[0..targets_len]});

    var routes_buffer: [512]u8 = undefined;
    var routes_len: usize = 0;
    for (loaded.upgrade_policy.required_make_routes, 0..) |route, index| {
        if (index != 0) {
            routes_buffer[routes_len] = ',';
            routes_len += 1;
        }
        const copied = try std.fmt.bufPrint(routes_buffer[routes_len..], "{s}", .{route});
        routes_len += copied.len;
    }
    try printLine(io, "ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES={s}", .{routes_buffer[0..routes_len]});
    try printLine(
        io,
        "ZIG_TOOLCHAIN_PIN_POLICY={s}",
        .{if (loaded.upgrade_policy.channel_minimum_lockstep) "exact" else "minimum_only"},
    );
    return 0;
}

fn printLine(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [512]u8 = undefined;
    var writer = Io.File.stdout().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

const SelfTestError = error{SelfTestFailed};

fn expectSelfTest(condition: bool) SelfTestError!void {
    if (!condition) return SelfTestError.SelfTestFailed;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var case_count: usize = 0;

    const release = try policy.parseZigVersion("0.16.0");
    try expectSelfTest(release.major == 0);
    try expectSelfTest(release.minor == 16);
    try expectSelfTest(release.release_rank == 1);
    case_count += 1;

    const dev = try policy.parseZigVersion("0.17.0-dev.877+a3ae499dc");
    try expectSelfTest(dev.dev_build == 877);
    case_count += 1;

    const newer_dev = try policy.parseZigVersion("0.17.0-dev.999+abcdef");
    const older_dev = try policy.parseZigVersion("0.17.0-dev.877+a3ae499dc");
    try expectSelfTest(!newer_dev.lessThan(older_dev));
    case_count += 1;

    const release_build = try policy.parseZigVersion("0.17.0");
    try expectSelfTest(!release_build.lessThan(newer_dev));
    case_count += 1;

    var filename_buffer: [128]u8 = undefined;
    const filename = try policy.policyArchiveFilename("x86_64-linux", "0.17.0-dev.877+a3ae499dc", &filename_buffer);
    try expectSelfTest(std.mem.eql(u8, filename, "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz"));
    case_count += 1;

    try expectSelfTest(policy.archiveNameHasDuplicateSuffix(
        "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc (1).tar.xz",
        "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz",
    ));
    case_count += 1;

    const present = try policy.evaluateToolchainVersion(
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try expectSelfTest(present.status == .present);
    case_count += 1;

    const not_pinned = try policy.evaluateToolchainVersion(
        "0.17.0",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try expectSelfTest(not_pinned.status == .not_pinned);
    case_count += 1;

    const too_old = try policy.evaluateToolchainVersion(
        "0.17.0-dev.757+abcdef",
        "0.17.0-dev.877+a3ae499dc",
        null,
    );
    try expectSelfTest(too_old.status == .too_old);
    case_count += 1;

    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(allocator, json);
    defer policy.freePolicy(allocator, &loaded);
    try expectSelfTest(std.mem.eql(u8, loaded.channel, "0.17.0-dev.877+a3ae499dc"));
    case_count += 1;

    try printLine(io, "ZIG_TOOLCHAIN_SELF_TEST=pass", .{});
    try printLine(io, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={d}", .{case_count});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var policy_only = false;
    var self_test = false;
    var policy_path: []const u8 = default_policy_path;

    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--policy-only")) {
            policy_only = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--policy")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            policy_path = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    if (policy_only) {
        std.process.exit(try emitPolicySummary(io, allocator, policy_path));
    }

    var stderr_buffer: [256]u8 = undefined;
    var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
    try stderr_writer.interface.writeAll(
        "usage: check_zig_toolchain.zig [--self-test] [--policy-only] [--policy <path>]\n",
    );
    try stderr_writer.interface.flush();
    std.process.exit(2);
}

test "policy-only summary accepts live policy" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);
    try std.testing.expectEqualStrings("Phase 2", loaded.phase);
    try std.testing.expect(loaded.upgrade_policy.channel_minimum_lockstep);
}