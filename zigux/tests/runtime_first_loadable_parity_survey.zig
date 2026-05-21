const std = @import("std");

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

test "phase9 first-loadable parity note matches the surviving shared packet" {
    const parity_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-first-loadable-runtime-module-parity.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(parity_note);

    const sample_root_readme = try readRepoFileAlloc(
        "../../samples/zigux/README.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(sample_root_readme);

    const atomic_survey_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-runtime-atomic64-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic_survey_note);

    const atomic_module_slice = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic_module_slice);

    const manifest = try readRepoFileAlloc(
        "runtime_bitmap_manifest.json",
        16 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    const phase9_build = try readRepoFileAlloc(
        "phase9_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(parity_note, "`PHASE9_STATUS=active`");
    try expectContains(parity_note, "`PHASE9_LANE_KEY=P9-L02`");
    try expectContains(parity_note, "`PHASE9_SURVEYED_COMMIT=2026-05-21-first-loadable-parity-bitmap-manifest-readback`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-atomic64-survey.md`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-bitmap-survey.md`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(parity_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(parity_note, "manifest-backed ownership packet");
    try expectContains(parity_note, "phase9-runtime-atomic64-diff");
    try expectContains(parity_note, "the build-local `phase9-runtime-atomic64-module-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-atomic64-sample-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-loader-shared-tests` route name");
    try expectContains(parity_note, "the shared `phase9-first-loadable-runtime-module-parity-survey-tests` handle");
    try expectContains(
        parity_note,
        "those sample-test and loader-shared route names are reminder vocabulary rather than proof that the underlying packet returned",
    );
    try expectContains(parity_note, "does not yet materialize that target as a coherent cross-family packet");
    try expectContains(parity_note, "must not claim shipped cross-family loader parity");
    try expectContains(
        parity_note,
        "must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity on current `master`.",
    );
    try expectContains(parity_note, "Leave `P9-L02` parked after this shared note refresh");

    try expectContains(sample_root_readme, "Fresh trusted mixed reread on 2026-05-20 also restored a narrower runtime bitmap sample-side packet on current `master`");
    try expectContains(sample_root_readme, "direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(sample_root_readme, "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit");
    try expectContains(sample_root_readme, "`zigux/tests/runtime_bitmap_module.zig` plus `zigux/tests/runtime_bitmap_diff.zig` still remain absent on the same trusted path");
    try expectContains(sample_root_readme, "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned");
    try expectContains(sample_root_readme, "Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.");
    try expectContains(sample_root_readme, "Keep the neighboring `zigux/tests/phase9_build.zig` route names framed only as bounded rerun handles for the visible sample, loader, survey, top-bit, and manifest-backed packet while the module and diff legs stay absent on the trusted path.");

    try expectContains(atomic_survey_note, "`PHASE9_STATUS=active`");
    try expectContains(atomic_survey_note, "`PHASE9_SLICE=runtime-atomic64-survey`");
    try expectContains(atomic_survey_note, "`PHASE9_LANE_KEY=P9-L04`");
    try expectContains(atomic_survey_note, "`PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-atomic64-direct-packet-truthfulness`");
    try expectContains(
        atomic_survey_note,
        "scope: direct atomic64 note-plus-test packet truthfulness together with the visible shared first-loadable reminder surfaces only",
    );
    try expectContains(atomic_survey_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(atomic_survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(
        atomic_survey_note,
        "Trusted current-master reads in this runtime still do not return these family-local atomic64 files on the same path:",
    );
    try expectContains(atomic_survey_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(atomic_survey_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(atomic_survey_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(atomic_survey_note, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(
        atomic_survey_note,
        "It is not a completed loadable runtime-module path, it does not clear the broader runtime-substrate blocker, and it does not currently rematerialize the family-local sample, loader, survey, or manifest surfaces on the trusted read path used in this run.",
    );
    try expectContains(
        atomic_survey_note,
        "No dedicated `make -C zigux phase9-runtime-atomic64-test` route is currently materialized on current `master`",
    );

    try expectContains(atomic_module_slice, "`PHASE9_STATUS=active`");
    try expectContains(atomic_module_slice, "`PHASE9_SLICE=runtime-atomic64-module-starter`");
    try expectContains(atomic_module_slice, "`PHASE9_LANE_KEY=P9-L04`");
    try expectContains(atomic_module_slice, "`PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-atomic64-direct-packet-truthfulness`");
    try expectContains(
        atomic_module_slice,
        "scope: selftest-hook and guarded lifecycle reviewability through the direct atomic64 note-plus-test packet, plus the adjacent shared reminder surfaces only",
    );
    try expectContains(atomic_module_slice, "## Direct Packet");
    try expectContains(atomic_module_slice, "## Adjacent Shared Reminder Packet");
    try expectContains(
        atomic_module_slice,
        "the direct atomic64 packet is narrower than the older loader-facing wording implied",
    );
    try expectContains(
        atomic_module_slice,
        "That means the honest current atomic64 packet is the direct note-plus-test packet together with a bounded shared-reminder packet.",
    );
    try expectContains(
        atomic_module_slice,
        "No dedicated family-local survey gate or manifest file currently returns on the trusted current-master path used in this run",
    );
    try expectContains(
        atomic_module_slice,
        "`zigux/tests/phase9_build.zig` currently keeps the direct `phase9-runtime-atomic64-diff` rerun and the build-local `phase9-runtime-atomic64-sample-tests` handle explicit;",
    );

    try expectContains(manifest, "\"phase\": \"Phase 9\"");
    try expectContains(manifest, "\"lane_key\": \"P9-L08\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"surveyed_commit\": \"2026-05-21-runtime-bitmap-manifest-restored\"");
    try expectContains(manifest, "\"sample_path\": \"samples/zigux/runtime_bitmap.zig\"");
    try expectContains(manifest, "\"loader_path\": \"samples/zigux/runtime_bitmap_loader.zig\"");
    try expectContains(manifest, "\"top_bit_path\": \"samples/zigux/runtime_bitmap_top_bit_contract.zig\"");

    try expectContains(phase9_build, "\"phase9-runtime-atomic64-diff\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-bitmap-top-bit-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-loader-allocator-init-flow-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-trace-events-loader-substrate-drift-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectContains(phase9_build, "\"phase9-first-loadable-runtime-module-parity-survey-tests\"");
    try expectContains(phase9_build, "\"runtime_first_loadable_parity_survey.zig\"");
    try expectContains(phase9_build, "\"Run the Phase 9 first-loadable runtime-module parity survey tests.\"");
    try expectContains(phase9_build, "\"phase9-runtime-atomic64-sample-tests\"");
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-atomic64-loader-tests\"") == null);
    try expectContains(phase9_build, "\"phase9-runtime-atomic64-module-tests\"");
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-atomic64-survey-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-bitmap-module-tests\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "\"phase9-runtime-bitmap-diff-tests\"") == null);
}
