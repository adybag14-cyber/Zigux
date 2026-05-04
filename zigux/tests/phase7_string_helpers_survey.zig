const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 string helpers survey keeps the roadmap and sample-root boundary explicit" {
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

    const script_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(script_readme);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const string_helpers_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-string-helpers-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(string_helpers_slice);

    const string_helpers_helper = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/string_helpers.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(string_helpers_helper);

    const string_helpers_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_string_helpers.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(string_helpers_tests);

    const string_helpers_manifest = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_string_helpers_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(string_helpers_manifest);

    const escape_vectors = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(escape_vectors);

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(samples_readme);

    const phase7_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase7_build);

    const validate_phase7 = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/validate-phase7.py",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(validate_phase7);

    const build_inventory_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-build-inventory.py",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_inventory_checker);

    const build_inventory_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_build_inventory.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(build_inventory_fixture);

    const make_wrapper_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-make-wrapper.py",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(make_wrapper_checker);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const expected_sample_files = [_][]const u8{
        "samples/zigux/bytestream_fifo.zig",
        "samples/zigux/kobject_example.zig",
        "samples/zigux/kretprobe_example.zig",
        "samples/zigux/trace_events_sample.zig",
        "samples/zigux/runtime_atomic64.zig",
        "samples/zigux/runtime_atomic64_loader.zig",
        "samples/zigux/runtime_bitmap.zig",
        "samples/zigux/runtime_bitmap_loader.zig",
        "samples/zigux/runtime_bitmap_top_bit_contract.zig",
        "samples/zigux/runtime_bitmap_top_bit_build.zig",
        "samples/zigux/runtime_kretprobe.zig",
        "samples/zigux/runtime_kretprobe_loader.zig",
        "samples/zigux/runtime_trace_events.zig",
        "samples/zigux/runtime_trace_events_loader.zig",
    };
    for (expected_sample_files) |path| {
        try std.Io.Dir.cwd().access(io_instance.io(), path, .{});
    }

    var samples_dir = try std.Io.Dir.cwd().openDir(io_instance.io(), "samples/zigux", .{ .iterate = true });
    defer samples_dir.close(io_instance.io());

    var samples_iter = samples_dir.iterate();
    while (try samples_iter.next(io_instance.io())) |entry| {
        if (entry.kind != .file) continue;
        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;
        try std.testing.expect(std.mem.indexOf(u8, entry.name, "string") == null);
    }

    try expectContains(roadmap, "## Phase 5: Samples and Reference Patterns");
    try expectContains(roadmap, "samples/kfifo/bytestream-example.c");
    try expectContains(roadmap, "samples/kobject/kobject-example.c");
    try expectContains(roadmap, "samples/kprobes/kretprobe_example.c");
    try expectContains(roadmap, "samples/trace_events/trace-events-sample.c");
    try expectContains(roadmap, "Recommended Zigux destinations:");
    try expectContains(roadmap, "- `samples/zigux/`");

    try expectContains(roadmap, "## Phase 7: In-Kernel Leaf Libraries");
    try expectContains(roadmap, "lib/string_helpers.c");
    try expectContains(roadmap, "- `lib/string_helpers.zig`");

    try expectContains(samples_readme, "Phase 5 reference samples");
    try expectContains(samples_readme, "samples/zigux/bytestream_fifo.zig");
    try expectContains(samples_readme, "samples/zigux/kobject_example.zig");
    try expectContains(samples_readme, "samples/zigux/kretprobe_example.zig");
    try expectContains(samples_readme, "samples/zigux/trace_events_sample.zig");
    try expectContains(samples_readme, "Later runtime starters, loader-side follow-ons, and blocked pilots");
    try expectContains(samples_readme, "samples/zigux/runtime_atomic64.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_bitmap.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_bitmap_top_bit_contract.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_bitmap_top_bit_build.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_kretprobe.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_trace_events.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_trace_events_loader.zig");
    try expectContains(samples_readme, "runtime bitmap packet rooted in `lib/test_bitmap.c` now includes `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` companion replay");
    try expectContains(samples_readme, "`samples/zigux/runtime_trace_events.zig` is still a sample-only blocked Phase 9 pilot on current `master`; the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now");
    try expectContains(samples_readme, "no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(samples_readme, "keep string-helper evidence under the separate Phase 7 helper bundle");
    try expectContains(samples_readme, "treat any new `samples/zigux/*string*.zig` file as review-blocking until the roadmap-backed Phase 7 helper bundle is intentionally widened");
    try expectContains(samples_readme, "verify no Phase 5 string sample has appeared under this sample root");
    try expectContains(samples_readme, "verify the shipped string-helper and cmdline evidence still live under the separate Phase 7 helper bundle and shared build gate: `python3 scripts/zigux/validate-phase7.py`");

    try expectContains(docs_readme, "`samples/zigux/README.md` is the shared Phase 5 sample-root catalog");
    try expectContains(docs_readme, "the Phase 7 string-helpers slice is intentionally helper-only");
    try expectContains(docs_readme, "current `master` ships no `samples/zigux/*string*` reference sample");
    try expectContains(docs_readme, "sample-root follow-up should not treat that absence as a missing Phase 5 port");

    try expectContains(review_checklist, "shared sample-root or helper-bundle notes for string work");
    try expectContains(review_checklist, "ships no `samples/zigux/*string*` Phase 5 reference sample");
    try expectContains(review_checklist, "the shipped string-helper evidence remains the separate Phase 7 helper bundle");
    try expectContains(review_checklist, "`lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, and `zigux/tests/phase7_build.zig`");

    try expectContains(script_readme, "`validate-phase7.py`");
    try expectContains(script_readme, "`check-phase7-build-inventory.py`");
    try expectContains(script_readme, "`check-phase7-make-wrapper.py`");
    try expectContains(script_readme, "`make -C zigux phase7-validate` is the validator-first entrypoint for the current Phase 7 flow.");

    try expectContains(
        tests_readme,
        "keep the current Phase 7 helper packet reviewable through `zigux/tests/phase7_build.zig`, `zigux/tests/fixtures/phase7_build_inventory.json`, `make -C zigux phase7-test`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-cmdline-parity.py`, and `scripts/zigux/check-phase7-rbtree-parity.py` instead of widening into ad hoc helper-local bootstrap rules",
    );
    try expectContains(
        tests_readme,
        "keep `scripts/zigux/validate-phase7.py --self-test`, `scripts/zigux/check-phase7-build-inventory.py --self-test`, and `scripts/zigux/check-phase7-make-wrapper.py --self-test` in the same packet",
    );

    try expectContains(string_helpers_slice, "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.");
    try expectContains(string_helpers_slice, "Current `master` keeps string-helper reviewability in the helper and test bundle");
    try expectContains(string_helpers_slice, "the four Phase 5 `samples/zigux/` anchors remain `bytestream_fifo`, `kobject_example`, `kretprobe_example`, and `trace_events_sample`.");
    try expectContains(string_helpers_slice, "zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig");
    try expectContains(string_helpers_slice, "zigux/tests/phase7_string_helpers_manifest.json");
    try expectContains(string_helpers_slice, "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_survey.zig`, and `zigux/tests/phase7_build.zig`.");
    try expectContains(string_helpers_slice, "`python3 scripts/zigux/validate-phase7.py --self-test`");
    try expectContains(string_helpers_slice, "`make -C zigux phase7-validate`");
    try expectContains(string_helpers_slice, "`zig build test --build-file zigux/tests/phase7_build.zig --summary all`");
    try expectContains(string_helpers_slice, "prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs");
    try expectContains(string_helpers_slice, "`parse_int_array()` over the bounded allocator-backed starter path");
    try expectContains(string_helpers_slice, "`parse_int_array_user()` over the bounded copy-and-parse starter path");
    try expectContains(string_helpers_slice, "`kstrdup_quotable()` over the bounded escape-then-duplicate path");
    try expectContains(string_helpers_slice, "`kstrdup_and_replace()` over the bounded duplicate-then-rewrite ownership-safe path");
    try expectContains(string_helpers_slice, "`kasprintf_strarray_raw()` over the bounded direct C-style null-terminated pointer-array starter path");
    try expectContains(string_helpers_slice, "`kfree_strarray_raw()` over the bounded counted partial-teardown path for partially initialized string arrays");
    try expectContains(string_helpers_slice, "`kasprintf_strarray()` over the bounded sequential prefix-index ownership path");
    try expectContains(string_helpers_slice, "`kfree_strarray()` over the bounded repeated-teardown-safe release path");
    try expectContains(string_helpers_slice, "one allocator-backed `kasprintf_strarray_raw()` proof that keeps the direct C-style null-terminated pointer-array form explicit beside the higher-level Zig wrapper");
    try expectContains(string_helpers_slice, "one counted `kfree_strarray_raw()` proof that frees a partially initialized pointer-array prefix without requiring later entries to exist");
    try expectContains(string_helpers_slice, "one `kfree_strarray()` proof that keeps first-NUL prefix handling, zero-count sentinel reuse, and repeated teardown safe");
    try expectContains(string_helpers_slice, "shared wrapper proofs that `string_unescape_inplace()`, `string_unescape_any()`, and `string_unescape_any_inplace()` preserve `UNESCAPE_ANY`, stop at the first written NUL, and leave trailing storage untouched");
    try expectContains(string_helpers_slice, "`STRING_UNITS_NO_SPACE` and `STRING_UNITS_NO_BYTES` formatting flags plus snprintf-style truncation accounting for `string_get_size()`");
    try expectContains(string_helpers_slice, "truncation accounting that returns the full would-be escaped length without promising an appended terminator through one dedicated gate assertion");

    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "scripts/zigux/check-phase7-build-inventory.py --self-test");
    try expectContains(makefile, "scripts/zigux/check-phase7-build-inventory.py");
    try expectContains(makefile, "scripts/zigux/check-phase7-make-wrapper.py --self-test");
    try expectContains(makefile, "scripts/zigux/check-phase7-make-wrapper.py");
    try expectContains(makefile, "phase7-test:");
    try expectContains(makefile, "$(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all");

    try expectContains(phase7_build, "phase7_string_helpers_survey.zig");
    try expectContains(phase7_build, "phase7-string-helpers-tests");
    try expectContains(phase7_build, "phase7-string-helpers-survey-tests");

    try expectContains(validate_phase7, "check-phase7-build-inventory.py --self-test");
    try expectContains(validate_phase7, "zigux/tests/fixtures/phase7_build_inventory.json");
    try expectContains(validate_phase7, "(\"zigux/tests/phase7_string_helpers_survey.zig\", phase7_string_helpers_survey, required_phase7_string_helpers_survey_markers),");
    try expectContains(validate_phase7, "\"zigux\" / \"tests\" / \"phase7_string_helpers_manifest.json\"");

    try expectContains(build_inventory_checker, "PHASE7_BUILD_INVENTORY_SELF_TEST=pass");
    try expectContains(build_inventory_checker, "PHASE7_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=23");

    try expectContains(build_inventory_fixture, "\"shared_validation_gates\": [");
    try expectContains(build_inventory_fixture, "\"shared_validation_commands\": [");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-build-inventory.py\"");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-build-inventory.py --self-test\"");

    try expectContains(make_wrapper_checker, "PHASE7_MAKE_WRAPPER_SELF_TEST=pass");
    try expectContains(make_wrapper_checker, "check-phase7-make-wrapper.py --self-test");

    try expectContains(string_helpers_helper, "pub const KasprintfStrarrayResult = struct");
    try expectContains(string_helpers_helper, "const empty_kasprintf_strarray_null_terminated: []const ?[*:0]const u8 = &.{null};");
    try expectContains(string_helpers_helper, "pub fn deinit(self: *KasprintfStrarrayResult, allocator: std.mem.Allocator) void");
    try expectContains(string_helpers_helper, "pub fn cArray(self: *const KasprintfStrarrayResult) [*]const ?[*:0]const u8");
    try expectContains(string_helpers_helper, "pub fn kasprintfStrarrayRaw(");
    try expectContains(string_helpers_helper, "pub fn kfreeStrarrayRaw(allocator: std.mem.Allocator, array: ?[]?[*:0]u8, count: usize) void");
    try expectContains(string_helpers_helper, "pub fn kasprintfStrarray(");
    try expectContains(string_helpers_helper, "pub fn kfreeStrarray(allocator: std.mem.Allocator, result: *KasprintfStrarrayResult) void");

    try expectContains(string_helpers_tests, "fixtures/phase7_string_helpers_escape_vectors.zig");
    try expectContains(string_helpers_tests, "phase 7 parseIntArray keeps the counted get_options contract explicit");
    try expectContains(string_helpers_tests, "phase 7 parseIntArrayUser keeps count-bounded copy semantics explicit");
    try expectContains(string_helpers_tests, "phase 7 kstrdupQuotable reuses the bounded escape subset for log-safe duplication");
    try expectContains(string_helpers_tests, "phase 7 kstrdupAndReplace keeps ownership and first-NUL replacement boundaries explicit");
    try expectContains(string_helpers_tests, "phase 7 kasprintfStrarrayRaw keeps direct C-style pointer ownership explicit");
    try expectContains(string_helpers_tests, "phase 7 kfreeStrarrayRaw keeps counted partial teardown safe");
    try expectContains(string_helpers_tests, "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator");
    try expectContains(string_helpers_tests, "phase 7 kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe");
    try expectContains(string_helpers_tests, "phase 7 string helper wrappers keep shared any-flag and C-string ownership rules");
    try expectContains(string_helpers_tests, "phase 7 escape flag masks stay aligned with the Linux helper contract");
    try expectContains(string_helpers_tests, "phase 7 stringGetSize returns snprintf-style length on truncation");
    try expectContains(string_helpers_tests, "phase 7 stringEscapeMem covers the bounded escape subset");
    try expectContains(string_helpers_tests, "phase 7 stringEscapeMem reports truncated output length without forcing a terminator");

    try expectContains(string_helpers_manifest, "\"lane_key\": \"P7-L04\"");
    try expectContains(string_helpers_manifest, "\"anchor\": \"lib/string_helpers.c\"");
    try expectContains(string_helpers_manifest, "\"lib/string_helpers.zig\"");
    try expectContains(string_helpers_manifest, "\"phase7-string-helpers-manifest-packet\"");
    try expectContains(string_helpers_manifest, "\"zigux/tests/phase7_string_helpers_manifest.json\"");
    try expectContains(string_helpers_manifest, "\"zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig\"");

    try expectContains(escape_vectors, "pub const unescape_cases");
    try expectContains(escape_vectors, "pub const escape_cases");
}
