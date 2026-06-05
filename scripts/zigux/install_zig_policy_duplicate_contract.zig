const std = @import("std");

const installer_path = "scripts/zigux/install-zig.py";

fn readInstallerSource() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        installer_path,
        std.testing.allocator,
        .limited(192 * 1024),
    );
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "installer tracks duplicate keys while loading policy JSON" {
    const source = try readInstallerSource();
    defer std.testing.allocator.free(source);

    try expectContains(source, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(source, "self.duplicate_keys: list[str] = []");
    try expectContains(source, "if key in self and key not in self.duplicate_keys:");
    try expectContains(source, "self.duplicate_keys.append(key)");
    try expectContains(source, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(source, "if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:");
    try expectContains(source, "duplicate toolchain policy keys");

    try expectOrdered(
        source,
        "class DuplicateTrackingDict(dict[str, object]):",
        "def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:",
    );
    try expectOrdered(
        source,
        "object_pairs_hook=DuplicateTrackingDict",
        "duplicate toolchain policy keys",
    );
}

test "installer rejects duplicate archive sha target entries" {
    const source = try readInstallerSource();
    defer std.testing.allocator.free(source);

    try expectContains(source, "archive_sha256 = payload.get('archive_sha256')");
    try expectContains(source, "if isinstance(archive_sha256, DuplicateTrackingDict) and archive_sha256.duplicate_keys:");
    try expectContains(source, "duplicate archive_sha256 targets");
    try expectContains(source, "+ ', '.join(archive_sha256.duplicate_keys)");
    try expectContains(source, "digest = archive_sha256.get(target_key)");

    try expectOrdered(
        source,
        "if isinstance(archive_sha256, DuplicateTrackingDict) and archive_sha256.duplicate_keys:",
        "digest = archive_sha256.get(target_key)",
    );
    try expectOrdered(
        source,
        "duplicate archive_sha256 targets",
        "digest = archive_sha256.get(target_key)",
    );
}

test "installer self-test covers duplicate top-level and archive target policies" {
    const source = try readInstallerSource();
    defer std.testing.allocator.free(source);

    try expectContains(source, "\"channel\":\"0.17.0-dev.758+748e7c5e3\",\"channel\":\"0.17.0-dev.90+abcdef\"");
    try expectContains(source, "assert 'duplicate toolchain policy keys' in str(exc)");
    try expectContains(source, "\"x86_64-linux\":\"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\",\"x86_64-linux\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"");
    try expectContains(source, "assert 'duplicate archive_sha256 targets' in str(exc)");

    try expectOrdered(
        source,
        "\"channel\":\"0.17.0-dev.758+748e7c5e3\",\"channel\":\"0.17.0-dev.90+abcdef\"",
        "assert 'duplicate toolchain policy keys' in str(exc)",
    );
    try expectOrdered(
        source,
        "\"x86_64-linux\":\"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\",\"x86_64-linux\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"",
        "assert 'duplicate archive_sha256 targets' in str(exc)",
    );
}
