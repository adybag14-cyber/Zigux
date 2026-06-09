const std = @import("std");

const checker_path = "check-zig-toolchain.py";
const checker_source = @embedFile(checker_path);

fn requireContains(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        std.debug.print("missing marker in {s}: {s}\n", .{ checker_path, marker });
        return error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse {
        std.debug.print("missing ordered marker in {s}: {s}\n", .{ checker_path, before });
        return error.MissingMarker;
    };
    const after_index = std.mem.indexOf(u8, source, after) orelse {
        std.debug.print("missing ordered marker in {s}: {s}\n", .{ checker_path, after });
        return error.MissingMarker;
    };
    try std.testing.expect(before_index < after_index);
}

test "archive target scope is checked before explicit archive resolution" {
    const source = checker_source;

    try requireContains(source, "def resolve_policy_archive(");
    try requireContains(source, "archive_targets = [str(target) for target in payload[\"upgrade_policy\"][\"archive_target_scope\"]]");
    try requireContains(source, "if target is not None and target not in archive_targets:");
    try requireContains(source, "f\"archive target {target!r} is outside archive_target_scope in {policy_path}: \"");
    try requireContains(source, "return target, Path(explicit_archive)");

    try requireOrdered(source, "if target is not None and target not in archive_targets:", "if explicit_archive is not None:");
    try requireOrdered(source, "f\"archive target {target!r} is outside archive_target_scope in {policy_path}: \"", "return target, Path(explicit_archive)");
}

test "multi-target archive policy requires an explicit target" {
    const source = checker_source;

    try requireContains(source, "if len(archive_targets) != 1:");
    try requireContains(source, "raise ValueError(\"archive target must be explicit when policy covers multiple archive targets\")");
    try requireOrdered(source, "if explicit_archive is not None:", "if len(archive_targets) != 1:");
    try requireOrdered(source, "archive target must be explicit when policy covers multiple archive targets", "return target, Path(explicit_archive)");
}

test "implicit archive candidates are filtered by requested target before selection" {
    const source = checker_source;

    try requireContains(source, "candidates = iter_repo_local_archive_candidates(root=root, policy_path=policy_path)");
    try requireContains(source, "candidates = [(candidate_target, candidate_path) for candidate_target, candidate_path in candidates if candidate_target == target]");
    try requireContains(source, "candidate_target, candidate_path = select_matching_policy_archive(");
    try requireOrdered(source, "if target is not None:\n        candidates = [(candidate_target, candidate_path) for candidate_target, candidate_path in candidates if candidate_target == target]", "candidate_target, candidate_path = select_matching_policy_archive(");
}

test "archive-only CLI reports invalid out-of-scope targets" {
    const source = checker_source;

    try requireContains(source, "parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try requireContains(source, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try requireContains(source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}\")");
    try requireContains(source, "if args.archive_target is not None:");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");

    try requireOrdered(source, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)", "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try requireOrdered(source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")", "if args.archive_target is not None:");
    try requireOrdered(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")", "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try requireOrdered(source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")", "return 1");
}

test "checker self-test keeps out-of-scope and unpinned archive target cases" {
    const source = checker_source;

    try requireContains(source, "lambda: resolve_policy_archive(str(duplicate_archive_path), \"aarch64-linux\", root=root, policy_path=policy_path)");
    try requireContains(source, "\"outside archive_target_scope\"");
    try requireContains(source, "lambda: validate_policy_archive(duplicate_archive_path, \"aarch64-linux\", policy_path=policy_path)");
    try requireContains(source, "\"is not pinned\"");
    try requireContains(source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try requireContains(source, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
}
