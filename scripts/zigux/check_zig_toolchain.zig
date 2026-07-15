const std = @import("std");
const Io = std.Io;
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

pub const default_policy_path = "scripts/zigux/zig-toolchain-policy.json";
pub const fallback_min_version = "0.16.0";
pub const default_root = ".";

fn printLine(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [512]u8 = undefined;
    var writer = Io.File.stdout().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

pub fn loadPolicyFromPath(
    io: Io,
    allocator: std.mem.Allocator,
    policy_path: []const u8,
) !?policy.ToolchainPolicy {
    const json_bytes = std.Io.Dir.cwd().readFileAlloc(io, policy_path, allocator, .unlimited) catch |err| switch (err) {
        error.FileNotFound => return null,
        else => return err,
    };
    defer allocator.free(json_bytes);
    return try policy.loadPolicyFromJson(allocator, json_bytes);
}

pub fn loadMinVersion(
    io: Io,
    allocator: std.mem.Allocator,
    policy_path: []const u8,
) ![]const u8 {
    if (try loadPolicyFromPath(io, allocator, policy_path)) |loaded_value| {
        var loaded = loaded_value;
        defer policy.freePolicy(allocator, &loaded);
        return try allocator.dupe(u8, loaded.minimum_version);
    }
    return try allocator.dupe(u8, fallback_min_version);
}

pub fn loadPinnedChannel(
    io: Io,
    allocator: std.mem.Allocator,
    policy_path: []const u8,
) !?[]const u8 {
    if (try loadPolicyFromPath(io, allocator, policy_path)) |loaded_value| {
        var loaded = loaded_value;
        defer policy.freePolicy(allocator, &loaded);
        return try allocator.dupe(u8, loaded.channel);
    }
    return null;
}

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

pub const ArchiveOnlyOptions = struct {
    policy_path: []const u8 = default_policy_path,
    root: []const u8 = default_root,
    explicit_archive: ?[]const u8 = null,
    explicit_target: ?[]const u8 = null,
    allow_missing: bool = false,
};

pub fn emitArchiveOnly(io: Io, allocator: std.mem.Allocator, options: ArchiveOnlyOptions) !u8 {
    var loaded_storage: ?policy.ToolchainPolicy = null;
    var loaded_ptr: ?*policy.ToolchainPolicy = null;
    var archive_target: ?[]const u8 = null;
    var archive_path: ?[]const u8 = null;

    defer {
        if (archive_target) |target| allocator.free(target);
        if (archive_path) |path| allocator.free(path);
    }

    if (try loadPolicyFromPath(io, allocator, options.policy_path)) |loaded| {
        loaded_storage = loaded;
        loaded_ptr = &loaded_storage.?;
    }

    var expected_sha: ?[]const u8 = null;
    var expected_filename: ?[]const u8 = null;
    var filename_buffer: [160]u8 = undefined;

    if (loaded_ptr) |loaded| {
        const resolved = resolver.resolvePolicyArchive(
            io,
            allocator,
            loaded,
            options.root,
            options.explicit_archive,
            options.explicit_target,
        ) catch |err| {
            const note = switch (err) {
                resolver.ResolverError.AmbiguousArchive => try resolver.formatResolvePolicyArchiveError(
                    allocator,
                    resolver.ResolverError.AmbiguousArchive,
                    loaded,
                    options.explicit_target,
                    options.explicit_archive,
                ),
                resolver.ResolverError.InvalidArgument => try resolver.formatResolvePolicyArchiveError(
                    allocator,
                    resolver.ResolverError.InvalidArgument,
                    loaded,
                    options.explicit_target,
                    options.explicit_archive,
                ),
                else => try std.fmt.allocPrint(allocator, "{s}", .{@errorName(err)}),
            };
            defer allocator.free(note);
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid", .{});
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}", .{options.explicit_archive orelse "unresolved"});
            if (options.explicit_target) |target| {
                try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{target});
            }
            try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{note});
            return 1;
        };
        if (resolved.target) |target| archive_target = try allocator.dupe(u8, target);
        if (resolved.path) |path| archive_path = try allocator.dupe(u8, path);
        resolver.freeResolvedArchive(allocator, resolved);

        if (archive_target) |target| {
            const meta = resolver.expectedArchiveMetadata(loaded, target, &filename_buffer) catch |err| {
                const note = switch (err) {
                    resolver.ResolverError.InvalidArgument => try resolver.formatResolvePolicyArchiveError(
                        allocator,
                        resolver.ResolverError.InvalidArgument,
                        loaded,
                        options.explicit_target,
                        options.explicit_archive,
                    ),
                    else => try std.fmt.allocPrint(allocator, "{s}", .{@errorName(err)}),
                };
                defer allocator.free(note);
                try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid", .{});
                try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}", .{options.explicit_archive orelse "unresolved"});
                if (options.explicit_target) |explicit| {
                    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{explicit});
                }
                try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{note});
                return 1;
            };
            expected_sha = meta.expected_sha;
            expected_filename = meta.expected_filename;
        }
    } else if (options.explicit_archive) |archive| {
        archive_path = try allocator.dupe(u8, archive);
        if (options.explicit_target) |target| archive_target = try allocator.dupe(u8, target);
    }

    if (options.explicit_archive != null and archive_path != null) {
        if (try resolver.describeInvalidExplicitArchivePath(io, allocator, archive_path.?)) |invalid_note| {
            defer allocator.free(invalid_note);
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid", .{});
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}", .{archive_path.?});
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{archive_target orelse "unresolved"});
            if (expected_filename) |filename| {
                try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={s}", .{filename});
            }
            if (expected_sha) |sha| {
                try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={s}", .{sha});
            }
            try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{invalid_note});
            return 1;
        }
    }

    const archive_path_is_file = if (archive_path) |path| resolver.pathIsFile(io, path) else false;
    if (archive_path == null or !archive_path_is_file) {
        const search_roots = try resolver.iterArchiveSearchRoots(allocator, options.root);
        defer resolver.freeSearchRoots(allocator, search_roots);
        const diagnostic = try resolver.describeMissingArchive(
            allocator,
            archive_path,
            options.explicit_archive,
            search_roots,
        );
        defer resolver.freeMissingArchiveDiagnostic(allocator, diagnostic);

        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing", .{});
        try printLine(
            io,
            "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}",
            .{archive_path orelse options.explicit_archive orelse "unresolved"},
        );
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{archive_target orelse "unresolved"});
        if (expected_filename) |filename| {
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={s}", .{filename});
        }
        if (expected_sha) |sha| {
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={s}", .{sha});
        }
        if (diagnostic.search_roots_summary) |summary| {
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={s}", .{summary});
        }
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{diagnostic.message});
        return if (options.allow_missing) 0 else 1;
    }

    if (loaded_ptr == null) {
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid", .{});
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}", .{archive_path.?});
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{archive_target orelse "unresolved"});
        try printLine(io, "ZIG_TOOLCHAIN_NOTE=toolchain policy not found", .{});
        return 1;
    }

    const target_for_validation = archive_target orelse "unresolved";
    const file_name = std.fs.path.basename(archive_path.?);
    const validation = resolver.validatePolicyArchive(
        io,
        allocator,
        loaded_ptr.?,
        archive_path.?,
        target_for_validation,
        file_name,
    ) catch |err| {
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid", .{});
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}", .{archive_path.?});
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{archive_target orelse "unresolved"});
        if (expected_filename) |filename| {
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={s}", .{filename});
        }
        if (expected_sha) |sha| {
            try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={s}", .{sha});
        }
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{@errorName(err)});
        return 1;
    };
    defer resolver.freeArchiveValidation(allocator, validation);

    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_STATUS={s}", .{validation.status});
    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_PATH={s}", .{archive_path.?});
    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}", .{archive_target orelse "unresolved"});
    if (expected_filename) |filename| {
        try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={s}", .{filename});
    }
    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={s}", .{validation.expected_sha});
    try printLine(io, "ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={s}", .{validation.actual_sha});
    if (validation.note) |note| {
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{note});
        return 1;
    }
    return 0;
}

pub const ZigCheckOptions = struct {
    policy_path: []const u8 = default_policy_path,
    root: []const u8 = default_root,
    explicit_zig: ?[]const u8 = null,
    min_version: ?[]const u8 = null,
    allow_missing: bool = false,
};

pub fn emitZigCheck(io: Io, allocator: std.mem.Allocator, options: ZigCheckOptions) !u8 {
    var zig: ?[]const u8 = null;
    var min_version_raw: ?[]const u8 = null;
    var expected_channel_raw: ?[]const u8 = null;
    var version: ?[]const u8 = null;
    var pinned_for_resolution: ?[]const u8 = null;

    defer {
        if (zig) |path| allocator.free(path);
        if (min_version_raw) |text| allocator.free(text);
        if (expected_channel_raw) |text| allocator.free(text);
        if (version) |text| allocator.free(text);
        if (pinned_for_resolution) |text| allocator.free(text);
    }

    if (options.min_version == null) {
        pinned_for_resolution = try loadPinnedChannel(io, allocator, options.policy_path);
    }

    zig = resolver.resolveZigExecutable(
        io,
        allocator,
        options.root,
        options.explicit_zig,
        pinned_for_resolution,
    ) catch |err| {
        min_version_raw = options.min_version orelse try loadMinVersion(io, allocator, options.policy_path);
        if (options.min_version == null) {
            expected_channel_raw = try loadPinnedChannel(io, allocator, options.policy_path);
        }
        try printLine(io, "ZIG_TOOLCHAIN_STATUS=invalid", .{});
        try printLine(io, "ZIG_TOOLCHAIN_PATH={s}", .{options.explicit_zig orelse "unresolved"});
        try printLine(io, "ZIG_TOOLCHAIN_MIN_SUPPORTED={s}", .{min_version_raw.?});
        if (expected_channel_raw) |channel| {
            try printLine(io, "ZIG_TOOLCHAIN_PINNED_CHANNEL={s}", .{channel});
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=exact", .{});
        } else if (options.min_version != null) {
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only", .{});
        } else {
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=unresolved", .{});
        }
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{@errorName(err)});
        return 1;
    };

    min_version_raw = options.min_version orelse try loadMinVersion(io, allocator, options.policy_path);
    if (options.min_version == null) {
        expected_channel_raw = try loadPinnedChannel(io, allocator, options.policy_path);
    }
    _ = try policy.parseZigVersion(min_version_raw.?);
    if (expected_channel_raw) |channel| {
        _ = try policy.parseZigVersion(channel);
    }

    if (zig == null) {
        const search_roots = try resolver.iterZigSearchRoots(allocator, options.root);
        defer resolver.freeSearchRoots(allocator, search_roots);
        const diagnostic = try resolver.describeMissingZig(allocator, expected_channel_raw, search_roots);
        defer resolver.freeMissingZigDiagnostic(allocator, diagnostic);

        try printLine(io, "ZIG_TOOLCHAIN_STATUS=missing", .{});
        try printLine(io, "ZIG_TOOLCHAIN_PATH=unresolved", .{});
        try printLine(io, "ZIG_TOOLCHAIN_MIN_SUPPORTED={s}", .{min_version_raw.?});
        if (expected_channel_raw) |channel| {
            try printLine(io, "ZIG_TOOLCHAIN_PINNED_CHANNEL={s}", .{channel});
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=exact", .{});
        } else {
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only", .{});
        }
        try printLine(io, "ZIG_TOOLCHAIN_SEARCH_ROOTS={s}", .{diagnostic.search_roots_summary});
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{diagnostic.message});
        return if (options.allow_missing) 0 else 1;
    }

    version = resolver.readZigVersion(io, allocator, zig.?) catch |err| {
        try printLine(io, "ZIG_TOOLCHAIN_STATUS=invalid", .{});
        try printLine(io, "ZIG_TOOLCHAIN_PATH={s}", .{zig.?});
        if (version) |reported| {
            try printLine(io, "ZIG_TOOLCHAIN_VERSION={s}", .{reported});
        }
        try printLine(io, "ZIG_TOOLCHAIN_MIN_SUPPORTED={s}", .{min_version_raw orelse "unresolved"});
        if (expected_channel_raw) |channel| {
            try printLine(io, "ZIG_TOOLCHAIN_PINNED_CHANNEL={s}", .{channel});
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=exact", .{});
        } else if (options.min_version != null) {
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only", .{});
        } else {
            try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=unresolved", .{});
        }
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{@errorName(err)});
        return 1;
    };

    const evaluation = try policy.evaluateToolchainVersion(
        version.?,
        min_version_raw.?,
        expected_channel_raw,
    );

    const exit_code: u8 = if (evaluation.status == .present) 0 else 1;
    try printLine(io, "ZIG_TOOLCHAIN_STATUS={s}", .{resolver.toolchainStatusName(evaluation.status)});
    try printLine(io, "ZIG_TOOLCHAIN_PATH={s}", .{zig.?});
    try printLine(io, "ZIG_TOOLCHAIN_VERSION={s}", .{version.?});
    try printLine(io, "ZIG_TOOLCHAIN_MIN_SUPPORTED={s}", .{min_version_raw.?});
    if (expected_channel_raw) |channel| {
        try printLine(io, "ZIG_TOOLCHAIN_PINNED_CHANNEL={s}", .{channel});
        try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=exact", .{});
    } else {
        try printLine(io, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only", .{});
    }
    if (evaluation.note) |note| {
        try printLine(io, "ZIG_TOOLCHAIN_NOTE={s}", .{note});
    }
    return exit_code;
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
    try expectSelfTest(std.mem.eql(u8, loaded.channel, "0.17.0-dev.1415+64dfaa568"));
    case_count += 1;

    const zig_roots = try resolver.iterZigSearchRoots(allocator, ".");
    defer resolver.freeSearchRoots(allocator, zig_roots);
    try expectSelfTest(zig_roots.len > 0);
    case_count += 1;

    const archive_roots = try resolver.iterArchiveSearchRoots(allocator, ".");
    defer resolver.freeSearchRoots(allocator, archive_roots);
    var has_third_party = false;
    for (archive_roots) |root| {
        if (std.mem.endsWith(u8, root, "/third_party")) has_third_party = true;
    }
    try expectSelfTest(has_third_party);
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
    var archive_only = false;
    var self_test = false;
    var allow_missing = false;
    var policy_path: []const u8 = default_policy_path;
    var explicit_archive: ?[]const u8 = null;
    var explicit_target: ?[]const u8 = null;
    var explicit_zig: ?[]const u8 = null;
    var min_version: ?[]const u8 = null;

    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--policy-only")) {
            policy_only = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--archive-only")) {
            archive_only = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--allow-missing")) {
            allow_missing = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--policy")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            policy_path = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--archive")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_archive = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--archive-target")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_target = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_zig = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--min-version")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            min_version = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    if (policy_only) {
        std.process.exit(try emitPolicySummary(io, allocator, policy_path));
    }

    if (archive_only) {
        std.process.exit(try emitArchiveOnly(io, allocator, .{
            .policy_path = policy_path,
            .explicit_archive = explicit_archive,
            .explicit_target = explicit_target,
            .allow_missing = allow_missing,
        }));
    }

    if (explicit_archive != null or explicit_target != null) {
        var stderr_buffer: [256]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("archive flags require --archive-only\n");
        try stderr_writer.interface.flush();
        std.process.exit(2);
    }

    std.process.exit(try emitZigCheck(io, allocator, .{
        .policy_path = policy_path,
        .explicit_zig = explicit_zig,
        .min_version = min_version,
        .allow_missing = allow_missing,
    }));
}

test "policy-only summary accepts live policy" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);
    try std.testing.expectEqualStrings("Phase 2", loaded.phase);
    try std.testing.expect(loaded.upgrade_policy.channel_minimum_lockstep);
}
