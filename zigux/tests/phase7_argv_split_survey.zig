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

    const argv_split_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(argv_split_fixture);

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

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const build_inventory_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_build_inventory.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(build_inventory_fixture);

    const scripts_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const argv_split_packet_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-argv-split-packet.py",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(argv_split_packet_checker);

    const argv_split_parity_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-argv-split-parity.py",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(argv_split_parity_checker);

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("c9c1299e37e06c409264a94fbe4ab36a7dcc8b4f", manifest.surveyed_commit);
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
    var saw_shared_fixtures = false;
    var saw_packet_checker = false;
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

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-shared-fixtures")) {
            saw_shared_fixtures = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_argv_split_vectors.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-packet-checker")) {
            saw_packet_checker = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("scripts/zigux/check-phase7-argv-split-packet.py", gap.zigux_destination);
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
    try std.testing.expect(saw_shared_fixtures);
    try std.testing.expect(saw_packet_checker);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_helper, "pub fn argvFree") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_helper, "leading_nul_expected") != null);
    try expectContains(argv_split_helper, "const empty_argv_null_terminated: []const ?[*:0]const u8 = &.{null};");
    try expectContains(argv_split_helper, "const empty_storage_view = empty_storage_null_terminated[0..0 :0];");
    try expectContains(argv_split_helper, "if (self.argv_null_terminated.ptr != empty_argv_null_terminated.ptr) {");
    try expectContains(argv_split_helper, "if (self.storage.ptr != empty_storage_view.ptr) {");
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "const phase7_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit matches focused parity fixtures") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit deinit clears exported storage and argv views") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup") != null);
    try expectContains(argv_split_tests, "try std.testing.expect(split.storage.ptr == blank.storage.ptr);");
    try expectContains(argv_split_tests, "try std.testing.expect(split.argv_null_terminated.ptr == blank.argv_null_terminated.ptr);");
    try std.testing.expect(std.mem.indexOf(u8, argv_split_fixture, "pub const argv_split_cases = [_]ArgvSplitCase{") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_fixture, ".name = \"leading NUL truncates to zero argv entries\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_fixture, ".name = \"first NUL stops counting and splitting\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_fixture, ".name = \"quote characters stay inside returned tokens\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "zigux/tests/fixtures/phase7_argv_split_vectors.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "The dedicated Phase 7 review gate now imports a focused fixture module under `zigux/tests/fixtures/phase7_argv_split_vectors.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "explicit shared integration through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, and `zigux/tests/phase7_build.zig`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, argv_split_slice, "prove the shared Phase 7 validator packet plus the build-inventory, make-wrapper, and argv_split parity gates still fail closed before the helper replay runs") != null);
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
    try expectContains(manifest_json, "\"id\": \"phase7-argv-split-shared-fixtures\"");
    try expectContains(manifest_json, "\"id\": \"phase7-argv-split-packet-checker\"");
    try expectContains(phase7_build, "phase7-argv-split-survey-tests");
    try expectContains(phase7_build, "repo_root");
    try expectContains(makefile, "scripts/zigux/check-phase7-argv-split-packet.py --self-test");
    try expectContains(makefile, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(makefile, "scripts/zigux/check-phase7-argv-split-parity.py --self-test");
    try expectContains(makefile, "scripts/zigux/check-phase7-argv-split-parity.py");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-argv-split-packet.py\"");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-argv-split-packet.py --self-test\"");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-argv-split-parity.py\"");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-argv-split-parity.py --self-test\"");
    try expectContains(scripts_readme, "`check-phase7-argv-split-packet.py`");
    try expectContains(scripts_readme, "`check-phase7-argv-split-parity.py`");
    try expectContains(
        tests_readme,
        "`scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
    );
    try expectContains(
        tests_readme,
        "`scripts/zigux/check-phase7-argv-split-packet.py`",
    );
    try expectContains(
        tests_readme,
        "`scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
    );
    try expectContains(
        tests_readme,
        "`scripts/zigux/check-phase7-argv-split-parity.py`",
    );
    try expectContains(argv_split_packet_checker, "ROOT / \"scripts\" / \"zigux\" / \"check-phase7-argv-split-parity.py\"");
    try expectContains(argv_split_packet_checker, "ROOT / \"zigux\" / \"tests\" / \"phase7_argv_split_survey.zig\"");
    try expectContains(argv_split_packet_checker, "ROOT / \"zigux\" / \"tests\" / \"phase7_argv_split_manifest.json\"");
    try expectContains(argv_split_packet_checker, "\"phase7-argv-split-packet-checker\": \"scripts/zigux/check-phase7-argv-split-packet.py\"");
    try expectContains(argv_split_packet_checker, "print(\"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass\")");
    try expectContains(argv_split_packet_checker, "print(\"PHASE7_ARGV_SPLIT_PACKET=pass\")");
    try expectContains(argv_split_parity_checker, "SOURCE = ROOT / \"lib\" / \"argv_split.c\"");
    try expectContains(argv_split_parity_checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase7_argv_split.json\"");
    try expectContains(argv_split_parity_checker, "HARNESS = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase7_argv_split_c_harness.c\"");
    try expectContains(argv_split_parity_checker, "PHASE7_ARGV_SPLIT_PARITY_SELF_TEST_CASE_COUNT=4");
}
