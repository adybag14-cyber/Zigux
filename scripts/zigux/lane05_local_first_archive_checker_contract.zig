const std = @import("std");

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrderMarker,
};

const source_path = @import("build_options").source_path;

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireExactCount(text: []const u8, marker: []const u8, expected: usize) ContractError!void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, text, cursor, marker)) |index| {
        count += 1;
        cursor = index + marker.len;
    }
    if (count == 0) return error.MissingMarker;
    if (count != expected) return error.DuplicateMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn checkLocalFirstArchiveChecker(source: []const u8) ContractError!void {
    const policy_markers = [_][]const u8{
        "POLICY_MARKERS = (",
        "LOCAL_ARCHIVE_MARKERS = (",
        "RETAINED_STEP_PAIRS = (",
        "README_SELF_TEST_STEP =",
        "README_CHECK_STEP =",
        "STAGE_HELPER_SELF_TEST_STEP =",
        "NEXT_PHASE_STEP =",
        "REPO_ARCHIVE_PARTS_DIR =",
        "LOCAL_PARTS_GUARD =",
        "STAGE_HELPER_CMD =",
        "STAGE_HELPER_ROOT_ARG =",
        "STAGE_HELPER_PARTS_ARG =",
    };
    for (policy_markers) |marker| try requireContains(source, marker);

    const workflow_markers = [_][]const u8{
        "require_marker(text, CHECKOUT_STEP,",
        "require_marker(text, SETUP_STEP,",
        "require_marker(text, TOOLCHAIN_SELF_TEST_STEP,",
        "require_marker(text, POLICY_STEP,",
        "require_marker(text, ARCHIVE_CHECK_STEP,",
        "require_marker(text, SELF_TEST_STEP,",
        "require_marker(text, CHECK_STEP,",
        "require_marker(text, README_SELF_TEST_STEP,",
        "require_marker(text, README_CHECK_STEP,",
        "require_marker(text, STAGE_HELPER_SELF_TEST_STEP,",
        "require_marker(text, THIRD_PARTY_PATH,",
    };
    for (workflow_markers) |marker| try requireContains(source, marker);

    const exact_count_markers = [_][]const u8{
        "require_exact_count(text, SETUP_STEP, 1",
        "require_exact_count(text, TOOLCHAIN_SELF_TEST_STEP, 1",
        "require_exact_count(text, POLICY_STEP, 1",
        "require_exact_line_count(text, f\"run: {POLICY_CMD}\", 1",
        "require_exact_count(text, ARCHIVE_CHECK_STEP, 1",
        "require_exact_line_count(text, f\"run: {ARCHIVE_CHECK_CMD}\", 1",
        "require_exact_count(text, SELF_TEST_STEP, 1",
        "require_exact_line_count(text, f\"run: {SELF_TEST_CMD}\", 1",
        "require_exact_count(text, CHECK_STEP, 1",
        "require_exact_line_count(text, f\"run: {CHECK_CMD}\", 1",
        "require_exact_count(text, README_SELF_TEST_STEP, 1",
        "require_exact_line_count(text, f\"run: {README_SELF_TEST_CMD}\", 1",
        "require_exact_count(text, README_CHECK_STEP, 1",
        "require_exact_line_count(text, f\"run: {README_CHECK_CMD}\", 1",
        "require_exact_count(text, STAGE_HELPER_SELF_TEST_STEP, 1",
        "require_exact_line_count(text, f\"run: {STAGE_HELPER_SELF_TEST_CMD}\", 1",
        "require_exact_count(text, REPO_ARCHIVE_PARTS_DIR, 1",
        "require_exact_count(text, LOCAL_PARTS_GUARD, 1",
        "require_exact_count(text, STAGE_HELPER_CMD, 2",
        "require_exact_count(text, STAGE_HELPER_ROOT_ARG, 1",
        "require_exact_count(text, STAGE_HELPER_PARTS_ARG, 1",
        "require_exact_line_count(text, THIRD_PARTY_PATH, 1",
    };
    for (exact_count_markers) |marker| try requireContains(source, marker);

    const order_markers = [_][]const u8{
        "require_order(text, CHECKOUT_STEP, SETUP_STEP",
        "require_order(text, SETUP_STEP, TOOLCHAIN_SELF_TEST_STEP",
        "require_order(text, TOOLCHAIN_SELF_TEST_STEP, POLICY_STEP",
        "require_order(text, POLICY_STEP, ARCHIVE_CHECK_STEP",
        "require_order(text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP",
        "require_order(text, SELF_TEST_STEP, CHECK_STEP",
        "require_order(text, CHECK_STEP, README_SELF_TEST_STEP",
        "require_order(text, README_SELF_TEST_STEP, README_CHECK_STEP",
        "require_order(text, README_CHECK_STEP, STAGE_HELPER_SELF_TEST_STEP",
        "require_order(text, STAGE_HELPER_SELF_TEST_STEP, NEXT_PHASE_STEP",
        "require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH",
        "require_order(text, THIRD_PARTY_PATH, TOOLS_PATH",
        "require_order(text, LOCAL_PARTS_GUARD, STAGE_HELPER_CMD",
        "require_order(text, STAGE_HELPER_CMD, STAGE_HELPER_ROOT_ARG",
        "require_order(text, STAGE_HELPER_ROOT_ARG, STAGE_HELPER_PARTS_ARG",
        "require_order(text, \"if try_local_archive; then\",",
        "require_order(text, 'elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then'",
        "require_order(text, 'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then'",
    };
    for (order_markers) |marker| try requireContains(source, marker);

    const self_test_markers = [_][]const u8{
        "missing_policy_load =",
        "missing_repo_archive_parts_dir =",
        "missing_parts_dir_guard =",
        "missing_stage_helper_call =",
        "missing_stage_helper_self_test =",
        "missing_local_validation =",
        "duplicate_third_party_path =",
        "reordered_stage_helper =",
        "reordered_fallback =",
        "LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass",
    };
    for (self_test_markers) |marker| try requireContains(source, marker);

    try requireExactCount(source, "require_exact_count(text, STAGE_HELPER_CMD, 2", 1);
    try requireExactCount(source, "require_exact_line_count(text, THIRD_PARTY_PATH, 1", 1);
    try requireOrder(source, "for marker in POLICY_MARKERS:", "for marker in LOCAL_ARCHIVE_MARKERS:");
    try requireOrder(source, "for marker in LOCAL_ARCHIVE_MARKERS:", "require_marker(text, CHECKOUT_STEP,");
    try requireOrder(source, "missing_stage_helper_call =", "missing_stage_helper_self_test =");
    try requireOrder(source, "reordered_stage_helper =", "reordered_fallback =");
}

fn loadSource(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        source_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "lane05 local-first archive checker pins source marker families" {
    const source = try loadSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try checkLocalFirstArchiveChecker(source);
}

test "lane05 local-first archive checker rejects missing parts-dir exact-count guard" {
    const stale_source =
        \\POLICY_MARKERS = (
        \\LOCAL_ARCHIVE_MARKERS = (
        \\RETAINED_STEP_PAIRS = (
        \\README_SELF_TEST_STEP =
        \\README_CHECK_STEP =
        \\STAGE_HELPER_SELF_TEST_STEP =
        \\NEXT_PHASE_STEP =
        \\REPO_ARCHIVE_PARTS_DIR =
        \\LOCAL_PARTS_GUARD =
        \\STAGE_HELPER_CMD =
        \\STAGE_HELPER_ROOT_ARG =
        \\STAGE_HELPER_PARTS_ARG =
        \\require_marker(text, CHECKOUT_STEP,
        \\require_marker(text, SETUP_STEP,
        \\require_marker(text, TOOLCHAIN_SELF_TEST_STEP,
        \\require_marker(text, POLICY_STEP,
        \\require_marker(text, ARCHIVE_CHECK_STEP,
        \\require_marker(text, SELF_TEST_STEP,
        \\require_marker(text, CHECK_STEP,
        \\require_marker(text, README_SELF_TEST_STEP,
        \\require_marker(text, README_CHECK_STEP,
        \\require_marker(text, STAGE_HELPER_SELF_TEST_STEP,
        \\require_marker(text, THIRD_PARTY_PATH,
        \\require_exact_count(text, SETUP_STEP, 1
        \\require_exact_count(text, TOOLCHAIN_SELF_TEST_STEP, 1
        \\require_exact_count(text, POLICY_STEP, 1
        \\require_exact_line_count(text, f"run: {POLICY_CMD}", 1
    ;

    try std.testing.expectError(error.MissingMarker, checkLocalFirstArchiveChecker(stale_source));
}

test "lane05 local-first archive checker rejects duplicate stage-helper exact-count guard" {
    const source = try loadSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const stale_source = try std.mem.concat(
        std.testing.allocator,
        u8,
        &.{
            source,
            "\nrequire_exact_count(text, STAGE_HELPER_CMD, 2\n",
        },
    );
    defer std.testing.allocator.free(stale_source);

    try std.testing.expectError(error.DuplicateMarker, checkLocalFirstArchiveChecker(stale_source));
}

test "lane05 local-first archive checker rejects reordered fallback self-test coverage" {
    const stale_source =
        \\POLICY_MARKERS = (
        \\LOCAL_ARCHIVE_MARKERS = (
        \\RETAINED_STEP_PAIRS = (
        \\README_SELF_TEST_STEP =
        \\README_CHECK_STEP =
        \\STAGE_HELPER_SELF_TEST_STEP =
        \\NEXT_PHASE_STEP =
        \\REPO_ARCHIVE_PARTS_DIR =
        \\LOCAL_PARTS_GUARD =
        \\STAGE_HELPER_CMD =
        \\STAGE_HELPER_ROOT_ARG =
        \\STAGE_HELPER_PARTS_ARG =
        \\require_marker(text, CHECKOUT_STEP,
        \\require_marker(text, SETUP_STEP,
        \\require_marker(text, TOOLCHAIN_SELF_TEST_STEP,
        \\require_marker(text, POLICY_STEP,
        \\require_marker(text, ARCHIVE_CHECK_STEP,
        \\require_marker(text, SELF_TEST_STEP,
        \\require_marker(text, CHECK_STEP,
        \\require_marker(text, README_SELF_TEST_STEP,
        \\require_marker(text, README_CHECK_STEP,
        \\require_marker(text, STAGE_HELPER_SELF_TEST_STEP,
        \\require_marker(text, THIRD_PARTY_PATH,
        \\require_exact_count(text, SETUP_STEP, 1
        \\require_exact_count(text, TOOLCHAIN_SELF_TEST_STEP, 1
        \\require_exact_count(text, POLICY_STEP, 1
        \\require_exact_line_count(text, f"run: {POLICY_CMD}", 1
        \\require_exact_count(text, ARCHIVE_CHECK_STEP, 1
        \\require_exact_line_count(text, f"run: {ARCHIVE_CHECK_CMD}", 1
        \\require_exact_count(text, SELF_TEST_STEP, 1
        \\require_exact_line_count(text, f"run: {SELF_TEST_CMD}", 1
        \\require_exact_count(text, CHECK_STEP, 1
        \\require_exact_line_count(text, f"run: {CHECK_CMD}", 1
        \\require_exact_count(text, README_SELF_TEST_STEP, 1
        \\require_exact_line_count(text, f"run: {README_SELF_TEST_CMD}", 1
        \\require_exact_count(text, README_CHECK_STEP, 1
        \\require_exact_line_count(text, f"run: {README_CHECK_CMD}", 1
        \\require_exact_count(text, STAGE_HELPER_SELF_TEST_STEP, 1
        \\require_exact_line_count(text, f"run: {STAGE_HELPER_SELF_TEST_CMD}", 1
        \\require_exact_count(text, REPO_ARCHIVE_PARTS_DIR, 1
        \\require_exact_count(text, LOCAL_PARTS_GUARD, 1
        \\require_exact_count(text, STAGE_HELPER_CMD, 2
        \\require_exact_count(text, STAGE_HELPER_ROOT_ARG, 1
        \\require_exact_count(text, STAGE_HELPER_PARTS_ARG, 1
        \\require_exact_line_count(text, THIRD_PARTY_PATH, 1
        \\require_order(text, CHECKOUT_STEP, SETUP_STEP
        \\require_order(text, SETUP_STEP, TOOLCHAIN_SELF_TEST_STEP
        \\require_order(text, TOOLCHAIN_SELF_TEST_STEP, POLICY_STEP
        \\require_order(text, POLICY_STEP, ARCHIVE_CHECK_STEP
        \\require_order(text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP
        \\require_order(text, SELF_TEST_STEP, CHECK_STEP
        \\require_order(text, CHECK_STEP, README_SELF_TEST_STEP
        \\require_order(text, README_SELF_TEST_STEP, README_CHECK_STEP
        \\require_order(text, README_CHECK_STEP, STAGE_HELPER_SELF_TEST_STEP
        \\require_order(text, STAGE_HELPER_SELF_TEST_STEP, NEXT_PHASE_STEP
        \\require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH
        \\require_order(text, THIRD_PARTY_PATH, TOOLS_PATH
        \\require_order(text, LOCAL_PARTS_GUARD, STAGE_HELPER_CMD
        \\require_order(text, STAGE_HELPER_CMD, STAGE_HELPER_ROOT_ARG
        \\require_order(text, STAGE_HELPER_ROOT_ARG, STAGE_HELPER_PARTS_ARG
        \\require_order(text, "if try_local_archive; then",
        \\require_order(text, 'elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then'
        \\require_order(text, 'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then'
        \\missing_policy_load =
        \\missing_repo_archive_parts_dir =
        \\missing_parts_dir_guard =
        \\missing_stage_helper_call =
        \\missing_stage_helper_self_test =
        \\missing_local_validation =
        \\duplicate_third_party_path =
        \\reordered_fallback =
        \\reordered_stage_helper =
        \\LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass
        \\for marker in POLICY_MARKERS:
        \\for marker in LOCAL_ARCHIVE_MARKERS:
        \\require_marker(text, CHECKOUT_STEP,
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkLocalFirstArchiveChecker(stale_source));
}
