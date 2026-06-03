const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, checker_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, checker_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var rest: []const u8 = checker_source;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "archive-only CLI exposes and reports the explicit archive target" {
    try requireContains("parser.add_argument(\"--archive-only\", action=\"store_true\"");
    try requireContains("parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try requireContains("archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try requireContains("if args.archive_target is not None:\n                print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")");
    try requireContains("print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");

    try requireOrdered("parser.add_argument(\"--archive-only\"", "parser.add_argument(\"--archive-target\"");
    try std.testing.expect(countOccurrences("ZIG_TOOLCHAIN_ARCHIVE_TARGET=") >= 4);
}

test "explicit archive target is fail-closed against archive_target_scope" {
    try requireContains("archive_targets = [str(target) for target in payload[\"upgrade_policy\"][\"archive_target_scope\"]]");
    try requireContains("if target is not None and target not in archive_targets:");
    try requireContains("f\"archive target {target!r} is outside archive_target_scope in {policy_path}: \"");
    try requireContains("if len(archive_targets) != 1:\n                raise ValueError(\"archive target must be explicit when policy covers multiple archive targets\")");
    try requireContains("if archive_target not in payload[\"archive_sha256\"]:");
    try requireContains("raise ValueError(f\"archive target {archive_target!r} is not pinned in {policy_path}\")");

    try requireOrdered("archive_targets = [str(target) for target in payload", "if target is not None and target not in archive_targets:");
    try requireOrdered(
        "if target is not None and target not in archive_targets:",
        "    if explicit_archive is not None:\n        if target is None:",
    );
}

test "self-test keeps target-scope and not-pinned coverage live" {
    try requireContains("resolve_policy_archive(str(duplicate_archive_path), \"aarch64-linux\", root=root, policy_path=policy_path)");
    try requireContains("\"outside archive_target_scope\"");
    try requireContains("validate_policy_archive(duplicate_archive_path, \"aarch64-linux\", policy_path=policy_path)");
    try requireContains("\"is not pinned\"");
}
