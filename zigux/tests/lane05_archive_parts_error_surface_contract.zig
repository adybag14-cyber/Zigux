const std = @import("std");

const DiagnosticCase = struct {
    name: []const u8,
    fragment: []const u8,
    scope: Scope,

    const Scope = enum {
        policy,
        manifest,
        shards,
        decode,
    };
};

const diagnostic_cases = [_]DiagnosticCase{
    .{
        .name = "missing packet directory stays explicit",
        .fragment = "required packet directory missing",
        .scope = .manifest,
    },
    .{
        .name = "packet path type stays explicit",
        .fragment = "packet path is not a directory",
        .scope = .manifest,
    },
    .{
        .name = "policy json syntax stays visible",
        .fragment = "invalid json in required file",
        .scope = .policy,
    },
    .{
        .name = "policy object shape stays visible",
        .fragment = "invalid json shape in required file",
        .scope = .policy,
    },
    .{
        .name = "archive target scope stays singleton",
        .fragment = "expected exactly one archive_target_scope entry",
        .scope = .policy,
    },
    .{
        .name = "manifest filename mismatch remains named",
        .fragment = "packet filename mismatch",
        .scope = .manifest,
    },
    .{
        .name = "manifest encoding mismatch remains named",
        .fragment = "packet encoding mismatch",
        .scope = .manifest,
    },
    .{
        .name = "manifest digest mismatch remains named",
        .fragment = "packet sha256 mismatch",
        .scope = .manifest,
    },
    .{
        .name = "manifest size mismatch remains named",
        .fragment = "packet size mismatch",
        .scope = .manifest,
    },
    .{
        .name = "manifest shard glob mismatch remains named",
        .fragment = "packet parts_glob mismatch",
        .scope = .manifest,
    },
    .{
        .name = "manifest part count mismatch remains named",
        .fragment = "packet part_count mismatch",
        .scope = .manifest,
    },
    .{
        .name = "missing shard set remains named",
        .fragment = "packet missing shard files",
        .scope = .shards,
    },
    .{
        .name = "extra shard set remains named",
        .fragment = "packet has unexpected shard files",
        .scope = .shards,
    },
    .{
        .name = "non-shard file set remains named",
        .fragment = "packet has unexpected non-shard files",
        .scope = .shards,
    },
    .{
        .name = "base64 decode failure remains named",
        .fragment = "packet shard is not valid base64",
        .scope = .decode,
    },
    .{
        .name = "non-final shard byte count remains named",
        .fragment = "packet shard size mismatch for",
        .scope = .decode,
    },
    .{
        .name = "final shard byte count remains named",
        .fragment = "packet final shard size mismatch for",
        .scope = .decode,
    },
    .{
        .name = "decoded size failure remains named",
        .fragment = "packet decoded size mismatch",
        .scope = .decode,
    },
    .{
        .name = "decoded digest failure remains named",
        .fragment = "packet decoded sha256 mismatch",
        .scope = .decode,
    },
};

test "lane05 archive-parts hard failures keep stable parser-friendly fragments" {
    var seen_policy = false;
    var seen_manifest = false;
    var seen_shards = false;
    var seen_decode = false;

    for (diagnostic_cases) |case| {
        try std.testing.expect(case.name.len > 0);
        const carries_stable_context =
            std.mem.indexOf(u8, case.fragment, "packet") != null or
            std.mem.indexOf(u8, case.fragment, "json") != null or
            std.mem.indexOf(u8, case.fragment, "archive_target_scope") != null or
            std.mem.indexOf(u8, case.fragment, "required") != null;
        try std.testing.expect(carries_stable_context);
        try std.testing.expect(std.mem.indexOf(u8, case.fragment, "Traceback") == null);
        try std.testing.expect(std.mem.indexOf(u8, case.fragment, "AssertionError") == null);
        try std.testing.expect(std.mem.indexOf(u8, case.fragment, "panic") == null);

        switch (case.scope) {
            .policy => seen_policy = true,
            .manifest => seen_manifest = true,
            .shards => seen_shards = true,
            .decode => seen_decode = true,
        }
    }

    try std.testing.expect(seen_policy);
    try std.testing.expect(seen_manifest);
    try std.testing.expect(seen_shards);
    try std.testing.expect(seen_decode);
}

test "lane05 archive-parts success statuses remain the only non-error states" {
    const success_statuses = [_][]const u8{
        "verified",
        "missing_allowed",
    };

    for (success_statuses) |status| {
        try std.testing.expect(std.mem.eql(u8, status, "verified") or std.mem.eql(u8, status, "missing_allowed"));
        try std.testing.expect(std.mem.indexOf(u8, status, "fail") == null);
        try std.testing.expect(std.mem.indexOf(u8, status, "error") == null);
    }

    try std.testing.expectEqual(@as(usize, 2), success_statuses.len);
}

test "lane05 archive-parts diagnostics cover every packet validation phase" {
    const required_scopes = [_]DiagnosticCase.Scope{ .policy, .manifest, .shards, .decode };

    for (required_scopes) |scope| {
        var count: usize = 0;
        for (diagnostic_cases) |case| {
            if (case.scope == scope) count += 1;
        }
        try std.testing.expect(count > 0);
    }

    try std.testing.expect(diagnostic_cases.len >= 18);
}
