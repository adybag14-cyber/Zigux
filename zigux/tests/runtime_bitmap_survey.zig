const std = @import("std");

const present_bitmap_family_files = [_][]const u8{
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "samples/zigux/README.md",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/phase9_build.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_direct_init_contract.zig",
    "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
};

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectPresent(path: []const u8) !void {
    const payload = try readRepoFileAlloc(path, 64 * 1024);
    defer std.testing.allocator.free(payload);
}

test "phase9 runtime bitmap survey gate matches the manifest-backed direct-diff bitmap packet" {
    const survey_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-bitmap-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_slice_note);

    const lane_sequencing_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(lane_sequencing_note);

    const samples_readme = try readRepoFileAlloc(
        "samples/zigux/README.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(samples_readme);

    const manifest = try readRepoFileAlloc(
        "zigux/tests/runtime_bitmap_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const sample_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(sample_file);

    const cold_guard_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(cold_guard_file);

    const loader_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap_loader.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(loader_file);

    const direct_init_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap_direct_init_contract.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(direct_init_file);

    const module_file = try readRepoFileAlloc(
        "zigux/tests/runtime_bitmap_module.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_file);

    const diff_file = try readRepoFileAlloc(
        "zigux/tests/runtime_bitmap_diff.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(diff_file);

    const top_bit_file = try readRepoFileAlloc(
        "samples/zigux/runtime_bitmap_top_bit_contract.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(top_bit_file);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L08`");
    try expectContains(survey_note, "`PHASE9_SURVEYED_COMMIT=2026-05-22-runtime-bitmap-diff-returned`");
    try expectContains(survey_note, "scope: partial reminder packet, direct sample proof, direct direct-init companion proof, direct cold-stage guard proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit companion proof, and no broader runtime-loader parity claim");
    try expectContains(survey_note, "trusted current-tree contents reads on 2026-05-22 do materialize");
    try expectContains(survey_note, "trusted current-tree contents reads on 2026-05-25 also materialize `samples/zigux/runtime_bitmap_direct_init_contract.zig` as a bounded direct-init normalization companion for the same Phase 9 packet");
    try expectContains(survey_note, "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(survey_note, "the current runtime bitmap reminder packet is still `partial_packet_with_diff_but_without_broader_runtime_loader_parity`");
    try expectContains(survey_note, "manifest-backed ownership packet");
    try expectContains(survey_note, "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample");
    try expectContains(survey_note, "Keep the direct sample zero-length and rejected range-mutation replay explicit when reminder text summarizes sample-local range, summary, and parse stability.");
    try expectContains(survey_note, "Keep the direct-init companion explicit when reminder text summarizes sample-local init normalization, unsorted duplicate input collapse, nth-set ordering, and formatted sparse-summary stability.");
    try expectContains(survey_note, "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion; it is visible on the trusted path and the shared `zigux/tests/phase9_build.zig` bundle now reruns it through the dedicated `phase9-runtime-bitmap-cold-stage-guard-tests` route plus the aggregate `phase9-runtime-bitmap-tests` handle.");
    try expectNotContains(survey_note, "returns missing for `zigux/tests/runtime_bitmap_diff.zig`");

    try expectContains(module_slice_note, "`PHASE9_SLICE=runtime-bitmap-partial-slice`");
    try expectContains(module_slice_note, "`PHASE9_SURVEYED_COMMIT=2026-05-22-runtime-bitmap-diff-returned`");
    try expectContains(module_slice_note, "scope: partial runtime bitmap reminder packet, direct sample proof, direct direct-init companion proof, direct cold-stage guard proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim");
    try expectContains(module_slice_note, "## Current visible slice");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap_direct_init_contract.zig`");
    try expectContains(module_slice_note, "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(module_slice_note, "none on the trusted current-tree read path");
    try expectContains(module_slice_note, "`phase9-runtime-bitmap-direct-init-contract-tests`");
    try expectContains(module_slice_note, "The shared `zigux/tests/phase9_build.zig` bundle reruns the direct sample, direct-init companion, cold-stage guard, loader, module, survey, diff gate, and top-bit companion through the dedicated `phase9-runtime-bitmap-direct-init-contract-tests`, `phase9-runtime-bitmap-cold-stage-guard-tests`, and `phase9-runtime-bitmap-top-bit-tests` routes plus the aggregate `phase9-runtime-bitmap-tests` handle.");

    try expectContains(lane_sequencing_note, "### 3. The runtime bitmap side now returns a broader direct packet without promoting the broader shared runtime-loader boundaries");
    try expectContains(lane_sequencing_note, "`zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` now return on the trusted path as the module-side descriptor and lifecycle packet plus the bounded diff-side summary replay packet");
    try expectContains(lane_sequencing_note, "the returned bitmap module gate and diff gate now stay inside that same bounded packet instead of the older repo-reality-gap bucket");
    try expectContains(lane_sequencing_note, "no shared reminder surface should present the bounded runtime bitmap packet as equal to the shipped trace-events packet or as proof that every broader runtime boundary returned");

    try expectContains(samples_readme, "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`");
    try expectContains(samples_readme, "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`");
    try expectContains(samples_readme, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(samples_readme, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(samples_readme, "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.");
    try expectContains(samples_readme, "Keep `zigux/tests/runtime_bitmap_module.zig` explicit as the module-side descriptor and lifecycle replay packet for the same runtime bitmap starter.");
    try expectContains(samples_readme, "Keep `zigux/tests/runtime_bitmap_diff.zig` explicit as the bounded diff-side summary replay packet for the same runtime bitmap starter.");
    try expectContains(samples_readme, "Keep that broader bitmap-side visibility from being used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.");

    try expectContains(manifest, "\"phase\": \"Phase 9\"");
    try expectContains(manifest, "\"lane_key\": \"P9-L08\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"surveyed_commit\": \"e306440f579ded71e8441c1a513af6fd12bbbfdd\"");
    try expectContains(manifest, "\"sample_path\": \"samples/zigux/runtime_bitmap.zig\"");
    try expectContains(manifest, "\"loader_path\": \"samples/zigux/runtime_bitmap_loader.zig\"");
    try expectContains(manifest, "\"cold_stage_guard_path\": \"samples/zigux/runtime_bitmap_cold_stage_guard.zig\"");
    try expectContains(manifest, "\"module_path\": \"zigux/tests/runtime_bitmap_module.zig\"");
    try expectContains(manifest, "\"diff_path\": \"zigux/tests/runtime_bitmap_diff.zig\"");
    try expectContains(manifest, "\"top_bit_path\": \"samples/zigux/runtime_bitmap_top_bit_contract.zig\"");
    try expectContains(manifest, "\"validation_entrypoint\": \"phase9-runtime-bitmap-tests\"");
    try expectContains(manifest, "Keep the runtime bitmap family Phase 9 only; it is not one of the four approved Phase 5 reference samples.");
    try expectContains(manifest, "\"descriptor_and_anchor\"");
    try expectContains(manifest, "\"sample_re_selftest_summary_stability\"");
    try expectContains(manifest, "\"loader_loaded_summary_stability\"");
    try expectContains(manifest, "\"module_descriptor_and_contract\"");
    try expectContains(manifest, "\"module_selftest_summary_replay\"");
    try expectContains(manifest, "\"module_lifecycle_summary_replay\"");
    try expectContains(manifest, "\"module_initialized_exit_summary_stability\"");
    try expectContains(manifest, "\"module_post_selftest_mutation_and_copy\"");
    try expectContains(manifest, "\"module_source_target_lifecycle_guards\"");
    try expectContains(manifest, "\"diff_summary_replay\"");
    try expectContains(manifest, "\"diff_copy_tail_clearing\"");
    try expectContains(manifest, "\"diff_exit_lifecycle_guards\"");
    try expectContains(manifest, "\"top_bit_contract\"");
    try expectContains(manifest, "\"sample_range_guard_non_destructive\"");
    try expectContains(manifest, "\"cold_stage_selftest_and_exit_guards\"");
    try expectContains(manifest, "\"cold_stage_mutation_and_source_lifecycle_guards\"");
    try expectContains(manifest, "Keep the direct sample zero-length and rejected range-mutation replay explicit when the manifest summarizes direct sample range, summary, and parse stability.");
    try expectContains(manifest, "Keep the cold-stage selftest, exit, mutation, and source-lifecycle guard companion explicit when the manifest summarizes the sample-root runtime bitmap packet.");
    try expectContains(manifest, "Keep the direct sample initialized-to-exit summary-stability guard explicit when the manifest summarizes runtime lifecycle evidence.");
    try expectContains(manifest, "Keep the direct sample re-init guards explicit when the manifest summarizes runtime lifecycle evidence.");
    try expectContains(manifest, "Keep the loader empty-payload direct-exit guard explicit when the manifest summarizes runtime lifecycle evidence.");
    try expectContains(manifest, "Keep the newer loader re-init, re-selftest, and direct-exit summary guards explicit when the manifest summarizes runtime lifecycle evidence.");
    try expectContains(manifest, "Keep the module-side descriptor, selftest-summary, lifecycle-summary, mutation-and-copy, and source-target guard proofs explicit when the manifest summarizes the direct module packet.");
    try expectContains(manifest, "Keep the diff-side summary replay, copy-tail clearing, and exit-guard coverage explicit when the manifest summarizes the bounded runtime bitmap packet.");
    try expectContains(manifest, "\"loadable runtime bitmap module parity\"");
    try expectContains(manifest, "\"shared runtime-loader command-name or argv-policy controls\"");

    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-direct-init-contract-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-diff-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-cold-stage-guard-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try expectContains(phase9_build, "runtime_bitmap_cold_stage_guard");

    try expectContains(sample_file, "pub const sample_review_focus = [_]SampleFocus");
    try expectContains(sample_file, ".top_bit_contract,");
    try expectContains(sample_file, "pub fn reviewContract() ReviewContract");
    try expectContains(sample_file, "pub fn runSelftest(self: *Self) !SelftestSummary");
    try expectContains(sample_file, "runtime bitmap sample rejects re-selftest without disturbing lifecycle summaries");
    try expectContains(sample_file, "runtime bitmap sample rejects re-init without disturbing initialized summaries");
    try expectContains(sample_file, "runtime bitmap sample keeps initialized summary stable across direct exit without selftest");
    try expectContains(sample_file, "runtime bitmap sample rejects re-init after exit without disturbing lifecycle summaries");
    try expectContains(sample_file, "runtime bitmap sample keeps zero-length and rejected range mutations non-destructive");

    try expectContains(cold_guard_file, "test \"runtime bitmap sample keeps cold-stage selftest and exit guards explicit\"");
    try expectContains(cold_guard_file, "test \"runtime bitmap sample keeps cold-stage mutation guards and source-lifecycle checks explicit\"");

    try expectContains(loader_file, "runtime bitmap loader keeps an empty loader payload explicit through direct exit");
    try expectContains(loader_file, "runtime bitmap loader keeps loader-facing bitmap payload explicit");
    try expectContains(loader_file, "runtime bitmap loader keeps loaded cross-word summary stable through selftest and exit");
    try expectContains(loader_file, "runtime bitmap loader rejects re-selftest without disturbing lifecycle summaries");
    try expectContains(loader_file, "runtime bitmap loader rejects re-init after a loaded payload without disturbing the initialized summary");
    try expectContains(loader_file, "runtime bitmap loader rejects re-init after exit without disturbing the exited summary");
    try expectContains(loader_file, "runtime bitmap loader keeps initialized loaded summary stable across direct exit without selftest");
    try expectContains(loader_file, "runtime bitmap loader rejects malformed loader payloads without leaving initialized state");

    try expectContains(direct_init_file, "test \"runtime bitmap sample normalizes unsorted duplicate direct init bits without inflating summaries\"");
    try expectContains(direct_init_file, "try std.testing.expectEqualStrings(\"0,5,64,70\", formatted);");

    try expectContains(module_file, "test \"runtime bitmap sample advertises the bounded pilot-module contract\"");
    try expectContains(module_file, "test \"runtime bitmap sample keeps selftest summary replay explicit at the module boundary\"");
    try expectContains(module_file, "test \"runtime bitmap sample keeps lifecycle summary replay explicit at the module boundary\"");
    try expectContains(module_file, "test \"runtime bitmap sample keeps initialized-stage exit replay explicit at the module boundary\"");
    try expectContains(module_file, "test \"runtime bitmap sample keeps post-selftest mutation and copy replay explicit at the module boundary\"");
    try expectContains(module_file, "test \"runtime bitmap sample keeps source and target lifecycle guards explicit at the module boundary\"");

    try expectContains(diff_file, "test \"runtime bitmap diff gate replays bounded summary and sparse nth-set expectations\"");
    try expectContains(diff_file, "test \"runtime bitmap diff gate keeps copy parity explicit after a cleared tail mutation\"");
    try expectContains(diff_file, "test \"runtime bitmap diff gate keeps selftest and exit lifecycle guards explicit\"");
    try expectContains(diff_file, "try std.testing.expectEqual(@as(?u32, 70), target.nthSetBit(6));");

    try expectContains(top_bit_file, "runtime bitmap sample keeps the highest valid bit explicit");
    try expectContains(top_bit_file, "runtime bitmap sample keeps top-bit lifecycle mutation explicit");
    try expectContains(top_bit_file, "runtime bitmap sample rejects exited top-bit source copies without disturbing the target sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample rejects cold top-bit source copies without disturbing the target sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample rejects copy reentry after target exit without disturbing either sample leg");
    try expectContains(top_bit_file, "runtime bitmap sample copies selftest-complete top-bit state into an initialized target without disturbing the source sample leg");

    inline for (present_bitmap_family_files) |path| {
        try expectPresent(path);
    }
}
