const std = @import("std");
const testing = std.testing;

const installer_source = @embedFile("install-zig.py");

fn findAfter(haystack: []const u8, needle: []const u8, start: usize) !usize {
    const offset = std.mem.indexOf(u8, haystack[start..], needle) orelse {
        std.debug.print("missing marker after {d}: {s}\n", .{ start, needle });
        return error.MissingMarker;
    };
    return start + offset;
}

fn requireContains(needle: []const u8) !void {
    _ = try findAfter(installer_source, needle, 0);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_pos = try findAfter(installer_source, first, 0);
    const second_pos = try findAfter(installer_source, second, first_pos + first.len);
    try testing.expect(second_pos > first_pos);
}

fn requireChain(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        cursor = try findAfter(installer_source, marker, cursor);
        cursor += marker.len;
    }
}

test "explicit versions may continue when the download index is unavailable" {
    try requireChain(&.{
        "def load_index(channel: str) -> dict:",
        "try:\n        return read_index()",
        "except (TimeoutError, urllib.error.URLError):",
        "if not is_explicit_version(channel):\n            raise",
        "return {}",
    });
}

test "non-explicit channels still fail closed on index lookup errors" {
    try requireChain(&.{
        "globals()['read_index'] = lambda: (_ for _ in ()).throw(TimeoutError('timed out'))",
        "assert load_index('0.17.0-dev.758+748e7c5e3') == {}",
        "try:\n            load_index('master')",
        "except TimeoutError:",
        "raise AssertionError('expected non-explicit channel timeout to fail')",
    });
}

test "empty explicit-version index resolves through inferred archive URLs" {
    try requireChain(&.{
        "def resolve_target(index: dict, channel: str, arch_key: str, system_key: str) -> tuple[str, str, str]:",
        "target_key = f'{arch_key}-{system_key}'",
        "if channel == CANONICAL_RELEASE_CHANNEL:",
        "return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
        "entry = index.get(channel)",
        "if entry is None and VERSION_KEY_RE.fullmatch(channel):",
        "if entry is None:",
        "return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
    });
}

test "main resolve-only route uses the fallback index before reporting status" {
    try requireChain(&.{
        "index = load_index(channel)",
        "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)",
        "print(f'ZIG_INSTALL_URL={tarball_url}')",
        "if args.resolve_only:",
        "print('ZIG_INSTALL_STATUS=resolved')",
        "return 0",
    });
    try requireOrder(
        "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)",
        "print(f'ZIG_INSTALL_URL={tarball_url}')",
    );
}

test "installer self-test keeps explicit index fallback coverage counted" {
    try requireContains("print('ZIG_INSTALL_SELF_TEST=pass')");
    try requireContains("print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}
