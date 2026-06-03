const std = @import("std");

const current = .{
    .target = "x86_64-linux",
    .channel = "0.17.0-dev.758+748e7c5e3",
    .sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6",
    .expected_size = 59_410_844,
    .canonical_repo = "adybag14-cyber/zig",
    .canonical_tag = "upstream-748e7c5e39fc",
};

const historical = .{
    .channel = "0.17.0-dev.87+9b177a7d2",
    .sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    .expected_size = 58_159_088,
};

fn filename(target: []const u8, channel: []const u8) []const u8 {
    if (std.mem.eql(u8, target, current.target) and std.mem.eql(u8, channel, current.channel)) {
        return "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
    }
    if (std.mem.eql(u8, target, current.target) and std.mem.eql(u8, channel, historical.channel)) {
        return "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";
    }
    return "";
}

fn repoArchivePath(name: []const u8) []const u8 {
    if (std.mem.eql(u8, name, filename(current.target, current.channel))) {
        return "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
    }
    return "";
}

fn repoPartsPath(name: []const u8) []const u8 {
    if (std.mem.eql(u8, name, filename(current.target, current.channel))) {
        return "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts";
    }
    return "";
}

fn canonicalReleaseUrl(name: []const u8) []const u8 {
    if (std.mem.eql(u8, name, filename(current.target, current.channel))) {
        return "https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
    }
    return "";
}

fn ziglangBuildsUrl(name: []const u8) []const u8 {
    if (std.mem.eql(u8, name, filename(current.target, current.channel))) {
        return "https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
    }
    return "";
}

const FallbackStep = enum {
    repo_local_archive_or_parts,
    canonical_github_release,
    community_mirrors,
    ziglang_builds,
};

const setup_order = [_]FallbackStep{
    .repo_local_archive_or_parts,
    .canonical_github_release,
    .community_mirrors,
    .ziglang_builds,
};

fn indexOf(step: FallbackStep) usize {
    for (setup_order, 0..) |entry, index| {
        if (entry == step) return index;
    }
    unreachable;
}

test "current Lane 05 archive identity matches the canonical release packet" {
    const name = filename(current.target, current.channel);

    try std.testing.expectEqualStrings(
        "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        name,
    );
    try std.testing.expectEqualStrings(
        "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        repoArchivePath(name),
    );
    try std.testing.expectEqualStrings(
        "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts",
        repoPartsPath(name),
    );
    try std.testing.expectEqualStrings(
        "https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        canonicalReleaseUrl(name),
    );
    try std.testing.expectEqualStrings(
        "https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        ziglangBuildsUrl(name),
    );
    try std.testing.expectEqual(@as(usize, 59_410_844), current.expected_size);
    try std.testing.expectEqualStrings(
        "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6",
        current.sha256,
    );
}

test "bootstrap fallback order prefers trusted repo payload before network sources" {
    try std.testing.expect(indexOf(.repo_local_archive_or_parts) < indexOf(.canonical_github_release));
    try std.testing.expect(indexOf(.canonical_github_release) < indexOf(.community_mirrors));
    try std.testing.expect(indexOf(.community_mirrors) < indexOf(.ziglang_builds));
}

test "historical attached archive cannot satisfy the current fallback contract" {
    try std.testing.expect(!std.mem.eql(u8, current.channel, historical.channel));
    try std.testing.expect(!std.mem.eql(u8, current.sha256, historical.sha256));
    try std.testing.expect(current.expected_size != historical.expected_size);

    const historical_name = filename(current.target, historical.channel);
    try std.testing.expectEqualStrings(
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        historical_name,
    );
    try std.testing.expectEqualStrings("", repoArchivePath(historical_name));
    try std.testing.expectEqualStrings("", repoPartsPath(historical_name));
    try std.testing.expectEqualStrings("", canonicalReleaseUrl(historical_name));
    try std.testing.expectEqualStrings("", ziglangBuildsUrl(historical_name));
}
