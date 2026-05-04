const std = @import("std");

const SurveySummary = struct {
    cmdline_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_fixture_modules: usize,
    preexisting_phase7_parity_fixture_present: bool,
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase 7 cmdline survey keeps the helper-only handoff explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(roadmap);

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const zigux_makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(zigux_makefile);

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(samples_readme);

    const phase7_cmdline_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-cmdline-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase7_cmdline_slice);

    const phase7_cmdline_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_cmdline.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase7_cmdline_tests);

    const phase7_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase7_build);

    const helper_cmdline = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/cmdline.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(helper_cmdline);

    const next_arg_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(next_arg_fixture);

    const parity_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_cmdline.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(parity_fixture);

    const build_inventory = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_build_inventory.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(build_inventory);

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_cmdline_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed_manifest = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        manifest_json,
        .{},
    );
    defer parsed_manifest.deinit();

    const manifest = parsed_manifest.value;

    try expectContains(roadmap, "## Phase 7: In-Kernel Leaf Libraries");
    try expectContains(roadmap, "lib/cmdline.c");
    try expectContains(roadmap, "- `lib/cmdline.zig`");
    try expectContains(roadmap, "runtime-safe leaf helpers");
    try expectContains(roadmap, "integration with validation substrate");

    try expectContains(docs_readme, "the same sample-root catalog also keeps the current no-`samples/zigux/*cmdline*` boundary explicit");
    try expectContains(docs_readme, "cmdline evidence stays under the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, and `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig` instead of looking like a missing Phase 5 sample port.");
    try expectContains(review_checklist, "if the change touches shared sample-root or helper-bundle notes for cmdline work");
    try expectContains(review_checklist, "current `master` ships no `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(review_checklist, "the shipped cmdline evidence remains the separate Phase 7 helper bundle under `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig`");

    try expectContains(tests_readme, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(tests_readme, "zigux/tests/fixtures/phase7_cmdline_c_harness.c");
    try expectContains(tests_readme, "scripts/zigux/check-phase7-cmdline-parity.py");
    try expectContains(tests_readme, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(tests_readme, "helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`");
    try expectContains(tests_readme, "cannot import fixtures outside the helper module path");
    try expectContains(tests_readme, "keep the `next_arg()` edge corpus reviewable in both places");
    try expectContains(samples_readme, "no `samples/zigux/*cmdline*` Phase 5 reference sample");

    try expectContains(zigux_makefile, "phase7-validate:");
    try expectContains(zigux_makefile, "python3 scripts/zigux/validate-phase7.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/validate-phase7.py");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-build-inventory.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-build-inventory.py");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-make-wrapper.py");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-cmdline-parity.py");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-argv-split-parity.py");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(zigux_makefile, "phase7-test:");
    try expectContains(zigux_makefile, "zig build test --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(zigux_makefile, "phase7: phase7-validate phase7-test");

    try expectContains(build_inventory, "\"repo_root_path\": \"../..\"");
    try expectContains(build_inventory, "\"phase7_cmdline_survey.zig\"");
    try expectContains(build_inventory, "\"phase7-cmdline-survey-tests\"");
    try expectContains(build_inventory, "\"shared_validation_gates\": [");
    try expectContains(build_inventory, "\"scripts/zigux/validate-phase7.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-build-inventory.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-make-wrapper.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-cmdline-parity.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-argv-split-packet.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-argv-split-parity.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-rbtree-parity.py\"");
    try expectContains(build_inventory, "\"shared_validation_commands\": [");
    try expectContains(build_inventory, "\"scripts/zigux/validate-phase7.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-build-inventory.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-make-wrapper.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-cmdline-parity.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-argv-split-packet.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-argv-split-packet.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-argv-split-parity.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-argv-split-parity.py\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-rbtree-parity.py --self-test\"");
    try expectContains(build_inventory, "\"scripts/zigux/check-phase7-rbtree-parity.py\"");
    try expectContains(build_inventory, "\"shared_test_command\": \"zig build test --build-file zigux/tests/phase7_build.zig --summary all\"");

    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOptions preserves descending-range and partial-parse stop behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOptions keeps array-capacity stop behavior explicit when a range is only partially stored") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 memparse preserves suffix scaling and stop index semantics") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 parseOptionStr matches C empty-option edge behavior around commas") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 parseOptionStr matches only exact bare options") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 numeric helpers reject explicit leading plus signs to stay with cmdline.c simple_strtoull semantics") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOption matches malformed-token classification from the Linux KUnit corpus") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOption matches leading-integer pointer advance from the Linux KUnit corpus") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOption matches trailing-integer pointer advance from the Linux KUnit corpus") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 getOptions matches malformed-range counting from the Linux KUnit corpus") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_tests, "phase 7 nextArg matches serialized edge fixtures") != null);

    try expectContains(phase7_cmdline_slice, "zigux/tests/phase7_cmdline.zig");
    try expectContains(phase7_cmdline_slice, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(phase7_cmdline_slice, "zigux/tests/phase7_cmdline_manifest.json");
    try expectContains(phase7_cmdline_slice, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(phase7_cmdline_slice, "zigux/tests/fixtures/phase7_cmdline_c_harness.c");
    try expectContains(phase7_cmdline_slice, "scripts/zigux/check-phase7-cmdline-parity.py");
    try expectContains(phase7_cmdline_slice, "The committed C parity replay through `scripts/zigux/check-phase7-cmdline-parity.py` stays coupled to that validation substrate so the helper-only slice remains externally reviewable.");
    try expectContains(phase7_cmdline_slice, "`python3 scripts/zigux/validate-phase7.py --self-test`");
    try expectContains(phase7_cmdline_slice, "`make -C zigux phase7-validate`");
    try expectContains(phase7_cmdline_slice, "prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs");
    try expectContains(phase7_cmdline_slice, "zig build test --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(phase7_cmdline_slice, "runtime-safe leaf helpers");
    try expectContains(phase7_cmdline_slice, "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig`.");
    try expectContains(phase7_cmdline_slice, "helper-local test runs cannot import that fixture from outside the helper module path");
    try expectContains(phase7_cmdline_slice, "`zig test lib/cmdline.zig` keeps a mirrored `next_arg()` edge corpus beside `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` because helper-local test runs cannot import that fixture from outside the helper module path; keep both packets aligned when those serialized cases change");
    try expectContains(phase7_cmdline_slice, "malformed token classification and malformed range counting ported from the in-tree `lib/tests/cmdline_kunit.c` corpus");
    try expectContains(phase7_cmdline_slice, "KUnit-derived pointer-advance semantics for malformed-prefix, leading-integer, and trailing-integer `get_option()` inputs");
    try expectContains(phase7_cmdline_slice, "a machine-checked manifest that records the `lib/cmdline.c` anchor and the landed Phase 7 review surfaces");
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "descending-range and unparseable-suffix early stop behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "array-capacity stop behavior when a hyphen range is only partially stored") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "memory-size suffix scaling with accurate parse-stop reporting") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "rejection of explicit leading-plus numeric inputs") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "exact bare-option matching for comma-delimited flags") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "C-style stop-at-NUL handling for bare-option scans") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "`parse_option_str()` empty-needle parity now mirrors the live C helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase7_cmdline_slice, "empty option names only match empty segments at the start of the scan or between commas") != null);

    try expectContains(helper_cmdline, "const next_arg_cases = [_]NextArgCase{");
    try expectContains(helper_cmdline, ".name = \"quoted value with trailing token\",");
    try expectContains(helper_cmdline, ".name = \"quoted bare token with trailing token\",");
    try expectContains(helper_cmdline, ".name = \"unquoted value keeps punctuation until whitespace\",");
    try expectContains(helper_cmdline, ".name = \"empty quoted value becomes empty string\",");
    try expectContains(helper_cmdline, ".name = \"first equals wins inside the value\",");
    try expectContains(helper_cmdline, ".name = \"quoted value without trailing token leaves empty rest\",");
    try expectContains(helper_cmdline, ".name = \"unterminated quoted value consumes the token tail\",");
    try expectContains(helper_cmdline, ".name = \"leading equals sign stays in the parameter token\",");
    try expectContains(helper_cmdline, ".name = \"trailing spaces after key=value trim to empty rest\",");
    try expectContains(helper_cmdline, ".input = \"root=\\\"/dev/sda 1\\\" ro\",");
    try expectContains(helper_cmdline, ".input = \"\\\"noparam value\\\" next\",");
    try expectContains(helper_cmdline, ".input = \"console=ttyS0,115200n8 panic=-1\",");
    try expectContains(helper_cmdline, ".input = \"rdinit=\\\"\\\" quiet\",");
    try expectContains(helper_cmdline, ".input = \"key=alpha=beta tail\",");
    try expectContains(helper_cmdline, ".input = \"mode=\\\"fast boot\\\"\",");
    try expectContains(helper_cmdline, ".input = \"mode=\\\"fast boot\",");
    try expectContains(helper_cmdline, ".input = \"=bad next\",");
    try expectContains(helper_cmdline, ".input = \"mode=fast   \",");
    try expectContains(helper_cmdline, "for (next_arg_cases) |case| {");

    try expectContains(next_arg_fixture, "pub const next_arg_cases = [_]NextArgCase{");
    try expectContains(next_arg_fixture, ".name = \"quoted value with trailing token\",");
    try expectContains(next_arg_fixture, ".name = \"quoted bare token with trailing token\",");
    try expectContains(next_arg_fixture, ".name = \"unquoted value keeps punctuation until whitespace\",");
    try expectContains(next_arg_fixture, ".name = \"empty quoted value becomes empty string\",");
    try expectContains(next_arg_fixture, ".name = \"first equals wins inside the value\",");
    try expectContains(next_arg_fixture, ".name = \"quoted value without trailing token leaves empty rest\",");
    try expectContains(next_arg_fixture, ".name = \"unterminated quoted value consumes the token tail\",");
    try expectContains(next_arg_fixture, ".name = \"leading equals sign stays in the parameter token\",");
    try expectContains(next_arg_fixture, ".name = \"trailing spaces after key=value trim to empty rest\",");
    try expectContains(next_arg_fixture, ".input = \"root=\\\"/dev/sda 1\\\" ro\",");
    try expectContains(next_arg_fixture, ".input = \"\\\"noparam value\\\" next\",");
    try expectContains(next_arg_fixture, ".input = \"console=ttyS0,115200n8 panic=-1\",");
    try expectContains(next_arg_fixture, ".input = \"rdinit=\\\"\\\" quiet\",");
    try expectContains(next_arg_fixture, ".input = \"key=alpha=beta tail\",");
    try expectContains(next_arg_fixture, ".input = \"mode=\\\"fast boot\\\"\",");
    try expectContains(next_arg_fixture, ".input = \"mode=\\\"fast boot\",");
    try expectContains(next_arg_fixture, ".input = \"=bad next\",");
    try expectContains(next_arg_fixture, ".input = \"mode=fast   \",");

    try expectContains(parity_fixture, "\"nul_stop_bare_scan\": false");

    try std.testing.expectEqualStrings("P7-L05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("d46fb91493e6e9126d5111bf0e5b21184e0ec1d1", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/cmdline.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/cmdline.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 241), manifest.survey_summary.cmdline_c_lines);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_parity_fixture_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expect(manifest.gaps.len >= 7);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_helper = false;
    var saw_shared_fixtures = false;
    var saw_parity_fixture = false;
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

        if (std.mem.eql(u8, gap.id, "phase7-cmdline-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/cmdline.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-cmdline-shared-fixtures")) {
            saw_shared_fixtures = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "serialized next_arg() edge corpus") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-cmdline-parity-fixture-layer")) {
            saw_parity_fixture = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_cmdline.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "externally reviewable") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-cmdline-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase7_cmdline_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "machine-checked survey gate") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_shared_fixtures);
    try std.testing.expect(saw_parity_fixture);
    try std.testing.expect(saw_survey_gate);

    try expectContains(phase7_build, "phase7_cmdline_survey.zig");
    try expectContains(phase7_build, "phase7-cmdline-survey-tests");
    try expectContains(phase7_build, "cmdline_survey_root_module,\n        repo_root,");
}
