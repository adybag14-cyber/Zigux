const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

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

fn isLowerHexCommitId(text: []const u8) bool {
    if (text.len != 40) return false;
    for (text) |ch| {
        if (!std.ascii.isHex(ch) or std.ascii.isUpper(ch)) return false;
    }
    return true;
}

test "phase 7 argv_split survey manifest records the parked runtime leaf surface without an active follow-up" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(manifest_json);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");
    defer allocator.free(slice_note);

    const shared_make_wrapper_note = try readRepoFile(
        allocator,
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    );
    defer allocator.free(shared_make_wrapper_note);

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);

    const helper_impl = try readRepoFile(allocator, "lib/argv_split.zig");
    defer allocator.free(helper_impl);

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");
    defer allocator.free(helper_tests);

    const fixture_module = try readRepoFile(allocator, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    defer allocator.free(fixture_module);

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-argv-split-packet.py");
    defer allocator.free(checker);

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const review_checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);

    const samples_root = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_root);

    const validate_phase7 = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validate_phase7);

    const zigux_makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(zigux_makefile);

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-Y07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expect(isLowerHexCommitId(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/argv_split.c", manifest.anchor);
    try std.testing.expect(std.mem.containsAtLeast(u8, slice_note, 1, "PHASE7_LANE_KEY=P7-Y07"));
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/argv_split.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 95), manifest.survey_summary.argv_split_c_lines);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    try expectContains(slice_note, "first-NUL C-string bounds on both counting and splitting");
    try expectContains(slice_note, "strict non-goal behavior where quote characters stay inside the returned tokens");
    try expectContains(slice_note, "stronger ownership and pointer discipline through the explicit `argvSplitWithArgc()` count mirror, `cArgv()` export, and `argvFree()` / `deinit()` teardown path");
    try expectContains(slice_note, "helper-local owned-storage handoff reviewability through the internal `argvSplitOwnedStorage()` path, including blank owned-storage fallback to the canonical empty storage and exported argv sentinels");
    try expectContains(slice_note, "copied-buffer ownership so later source mutation does not affect split results");
    try expectContains(slice_note, "copied whitespace separator runs are zeroed across the owned storage copy so each exported token stays in-place NUL-terminated");
    try expectContains(slice_note, "separate non-blank callers keep owned storage, argv slices, and exported C-argv views distinct across results");
    try expectContains(slice_note, "tearing down one non-blank result does not disturb another caller's owned storage or exported C-argv view");
    try expectContains(slice_note, "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`");
    try expectContains(slice_note, "blank-input teardown on one caller keeps the shared empty storage and exported argv sentinels stable for another caller");
    try expectContains(slice_note, "exported storage and argv views resetting back to the canonical empty sentinels after teardown");
    try expectContains(slice_note, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectContains(slice_note, "python3 scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(slice_note, "run the dedicated manifest-backed Phase 7 survey gate from `repo_root`");
    try expectContains(slice_note, "`make -C zigux phase7-argv-split-survey`");
    try expectContains(slice_note, "- `argvSplitWithArgc()`");
    try expectContains(slice_note, "- `cArgv()`");
    try expectContains(slice_note, "- `argvFree()` plus `deinit()`");
    try expectCount(slice_note, "null-terminated pointer-vector access through `cArgv()`", 1);
    try expectCount(slice_note, "zigux/tests/phase7_argv_split_manifest.json", 2);
    try expectContains(shared_make_wrapper_note, "PHASE7_LANE_KEY=P7-Y05");
    try expectContains(shared_make_wrapper_note, "`scripts/zigux/validate-phase7.py`");
    try expectContains(
        shared_make_wrapper_note,
        "`make -C zigux phase7-validate` and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface",
    );
    try expectContains(
        shared_make_wrapper_note,
        "this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`",
    );

    try expectContains(build_file, "\"phase7_argv_split.zig\"");
    try expectContains(build_file, "\"phase7_argv_split_survey.zig\"");
    try expectContains(build_file, "\"phase7-argv-split-tests\"");
    try expectContains(build_file, "\"phase7-argv-split-survey-tests\"");
    try expectContains(build_file, "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));");

    try expectContains(helper_impl, "const empty_argv_null_terminated: []const ?[*:0]const u8 = &.{null};");
    try expectContains(helper_impl, "        self.* = .{\n            .storage = empty_storage_view,\n            .argv = &.{},\n            .argv_null_terminated = empty_argv_null_terminated,\n        };\n");
    try expectContains(helper_impl, "pub fn countArgc");
    try expectContains(helper_impl, "pub fn argvSplit");
    try expectContains(helper_impl, "pub fn argvSplitWithArgc");
    try expectContains(helper_impl, "pub fn argvFree");
    try expectContains(helper_impl, "pub fn cArgv");
    try expectContains(helper_impl, "test \"argvSplit preserves C-string termination for the final token and argv vector\"");
    try expectContains(helper_impl, "test \"argvSplitOwnedStorage reuses the caller-owned storage copy\"");
    try expectContains(helper_impl, "test \"argvSplitOwnedStorage frees blank caller-owned storage and reuses exported sentinels\"");
    try expectContains(helper_impl, "test \"argvSplit sizes argc and tokens from the owned copy prefix when copied storage contains an early NUL\"");
    try expectContains(helper_impl, "test \"argvSplit zeroes copied whitespace separators across the tokenized buffer\"");
    try expectContains(helper_impl, "test \"argvSplit treats whitespace before the first NUL as blank input\"");
    try expectContains(helper_impl, "test \"argvSplit reuses the exported empty argv view for blank input\"");
    try expectContains(helper_impl, "test \"ArgvSplitResult deinit clears exported storage and argv views\"");
    try expectContains(helper_impl, "test \"argvSplit frees intermediate allocations when allocator failure interrupts setup\"");
    try expectContains(helper_impl, "test \"argvSplit reports overflow before sizing the null-terminated argv vector\"");
    try expectContains(helper_impl, "test \"ArgvSplitResult deinit is idempotent after the exported views are cleared\"");

    try expectContains(helper_tests, "const phase7_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");");
    try expectContains(helper_tests, "phase 7 argvSplit matches focused parity fixtures");
    try expectContains(helper_tests, "phase 7 argvSplit token buffer does not alias the source text");
    try expectContains(helper_tests, "phase 7 argvSplit leaves the caller buffer bytes untouched while returning owned tokens");
    try expectContains(helper_tests, "try std.testing.expectEqualSlices(u8, &original, &source);");
    try expectContains(helper_tests, "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy");
    try expectContains(helper_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter");
    try expectContains(helper_tests, "phase 7 argvSplit keeps the exported C argv vector sized to argc plus one sentinel");
    try expectContains(helper_tests, "try std.testing.expectEqual(argc + 1, split.argv_null_terminated.len);");
    try expectContains(helper_tests, "try std.testing.expect(split.cArgv() == split.argv_null_terminated.ptr);");
    try expectContains(helper_tests, "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned");
    try expectContains(helper_tests, "phase 7 blank argvSplit input reuses the empty exported argv view");
    try expectContains(helper_tests, "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space");
    try expectContains(helper_tests, "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable");
    try expectContains(helper_tests, "phase 7 argvSplit deinit clears exported storage and argv views");
    try expectContains(helper_tests, "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result");
    try expectContains(helper_tests, "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable");
    try expectContains(helper_tests, "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup");
    try expectContains(helper_tests, "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers");
    try expectContains(helper_tests, "phase 7 argvFree on one live split result does not disturb another caller");
    try expectContains(helper_tests, "phase 7 argvSplit deinit on one live split result does not disturb another caller");
    try expectContains(helper_tests, "phase 7 blank argvSplit teardown on one caller keeps shared empty sentinels stable for another caller");
    try expectContains(helper_tests, "phase 7 blank argvSplit deinit on one caller keeps shared empty sentinels stable for another caller");
    try expectContains(helper_tests, "split.cArgv()");

    try expectContains(fixture_module, ".name = \"whitespace before first NUL stays blank\",");
    try expectContains(fixture_module, ".name = \"leading NUL truncates to zero argv entries\",");
    try expectContains(fixture_module, ".name = \"first NUL stops counting and splitting\",");
    try expectContains(fixture_module, ".name = \"quote characters stay inside returned tokens\",");

    try expectContains(checker, "\"zigux/tests/phase7_argv_split.zig\"");
    try expectContains(checker, "\"zigux/tests/phase7_argv_split_survey.zig\"");
    try expectContains(checker, "\"zigux/tests/phase7_argv_split_manifest.json\"");
    try expectContains(checker, "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"");
    try expectContains(checker, "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy");
    try expectContains(checker, "phase 7 argvSplit keeps the exported C argv vector sized to argc plus one sentinel");
    try expectContains(checker, "phase 7 blank argvSplit teardown on one caller keeps shared empty sentinels stable for another caller");
    try expectContains(checker, "test \\\"argvSplitOwnedStorage reuses the caller-owned storage copy\\\"");
    try expectContains(checker, "test \\\"ArgvSplitResult deinit is idempotent after the exported views are cleared\\\"");

    try expectContains(scripts_root, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_argv_split_manifest.json");
    try expectContains(scripts_root, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectContains(scripts_root, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(scripts_root, "scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "`make -C zigux phase7`");

    try expectContains(tests_root, "`scripts/zigux/check-phase7-argv-split-packet.py`");
    try expectContains(tests_root, "`scripts/zigux/check-phase7-build-wiring.py`");
    try expectContains(tests_root, "the dedicated `zigux/tests/phase7_argv_split_survey.zig` argvSplit survey gate");
    try expectContains(tests_root, "`make -C zigux phase7-validate`");
    try expectContains(tests_root, "`make -C zigux phase7`");

    try expectContains(docs_root, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample");
    try expectContains(docs_root, "lib/argv_split.zig");
    try expectContains(docs_root, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(docs_root, "zigux/tests/phase7_argv_split_manifest.json");
    try expectContains(docs_root, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(docs_root, "scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(docs_root, "zigux/tests/phase7_build.zig");

    try expectContains(review_checklist, "shared Phase 7 leaf-helper packet");
    try expectContains(review_checklist, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(review_checklist, "zigux/tests/phase7_argv_split.zig");
    try expectContains(review_checklist, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(review_checklist, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectContains(review_checklist, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(review_checklist, "`make -C zigux phase7-validate`");
    try expectContains(review_checklist, "`make -C zigux phase7`");

    try expectContains(samples_root, "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;");
    try expectContains(samples_root, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(samples_root, "lib/argv_split.zig");
    try expectContains(samples_root, "zigux/tests/phase7_argv_split.zig");
    try expectContains(samples_root, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(samples_root, "zigux/tests/phase7_argv_split_manifest.json");
    try expectContains(samples_root, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(samples_root, "zigux/tests/phase7_build.zig");

    try expectContains(validate_phase7, "\"zigux/tests/phase7_argv_split.zig\"");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_argv_split_survey.zig\"");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_argv_split_manifest.json\"");
    try expectContains(validate_phase7, "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-argv-split-packet.py\"");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-build-wiring.py\"");

    try expectContains(zigux_makefile, "phase7-validate:");
    try expectContains(zigux_makefile, "scripts/zigux/check-phase7-argv-split-packet.py --self-test");
    try expectContains(zigux_makefile, "cd $(ZIGUX_ROOT) && $(ZIG) build phase7-argv-split-survey --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(zigux_makefile, "scripts/zigux/check-phase7-build-wiring.py --self-test");
    try expectContains(zigux_makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(zigux_makefile, "phase7: phase7-validate phase7-test");

    try expectContains(workflow, "Validate Phase 7 runtime helper gates");
    try expectContains(workflow, "make -C zigux phase7-validate");
    try expectContains(workflow, "Run Phase 7 runtime helper tests");
    try expectContains(workflow, "make -C zigux phase7-test");

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_helper = false;
    var saw_survey_gate = false;
    var saw_packet_checker = false;

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

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-packet-checker")) {
            saw_packet_checker = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("scripts/zigux/check-phase7-argv-split-packet.py", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expectEqual(manifest.gaps.len, starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_packet_checker);
}
