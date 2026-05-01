const std = @import("std");

const SurveySummary = struct {
    argv_split_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_fixture_modules: usize,
    preexisting_phase7_build_present: bool,
    preexisting_phase7_doc_present: bool,
    preexisting_phase7_helper_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 argv_split survey manifest records the parked runtime leaf surface without an active follow-up" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_argv_split_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const argv_split_helper = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/argv_split.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(argv_split_helper);

    const argv_split_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_argv_split.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(argv_split_tests);

    const argv_split_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-argv-split-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(argv_split_slice);

    const phase7_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase7_build);

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("ac615fab1a13cf24fc9a45abf09b1500fb1e2ac9", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/argv_split.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/argv_split.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 95), manifest.survey_summary.argv_split_c_lines);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expect(manifest.gaps.len >= 6);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_helper = false;
    var saw_survey_gate = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/argv_split.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase7_argv_split_survey.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(starter_landed_count >= 6);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_helper, "pub fn argvFree") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_helper, "leading_nul_expected") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit deinit clears exported storage and argv views") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, and `zigux/tests/phase7_build.zig`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "prove the shared Phase 7 validator packet still fails closed before the helper replay runs") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`python3 scripts/zigux/validate-phase7.py --self-test`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`python3 scripts/zigux/check-phase7-build-inventory.py`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`python3 scripts/zigux/check-phase7-make-wrapper.py`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`make -C zigux phase7-validate`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`zig build test --build-file zigux/tests/phase7_build.zig --summary all`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`zig test zigux/tests/phase7_argv_split_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "keep the roadmap survey record machine-checked from `repo_root`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "The manifest-backed survey packet stays rooted at `repo_root` through `zigux/tests/phase7_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "`argv_free()` via `argvFree()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "optional argc reporting that stays in sync with the returned argv length") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "leading-NUL truncation to zero argv entries before any later bytes are considered") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "repeated blank-input `argvFree()` teardown safety so the shared empty sentinel state survives explicit release without allocator backing") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "teardown cleanup that clears the exported storage handle alongside the argv views after `ArgvSplitResult.deinit()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "repeated teardown safety so an already-cleared `ArgvSplitResult` can be passed through `deinit()` again without freeing the shared empty sentinel state") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "allocator-failure cleanup that proves the shared Phase 7 gate also exercises the intermediate allocation teardown path already covered by the direct helper tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_build, "phase7-argv-split-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_build, "repo_root") != null);
}
