const std = @import("std");

const sample_markers = [_][]const u8{
    ".name = \"runtime_atomic64\"",
    ".anchor = \"lib/atomic64_test.c\"",
    ".provides_selftest_hook = true",
    "test \"runtime atomic64 sample keeps descriptor and lifecycle contract explicit\"",
    "test \"runtime atomic64 sample keeps arithmetic and guard paths reviewable\"",
    "test \"runtime atomic64 sample rejects re-selftest without disturbing lifecycle summaries\"",
    "test \"runtime atomic64 sample rejects re-init without disturbing initialized, selftest-complete, and exited summaries\"",
    "test \"runtime atomic64 sample rejects re-exit without disturbing exited summaries\"",
};

const loader_markers = [_][]const u8{
    "test \"runtime atomic64 loader keeps blocked publication and depmod surfaces out of the loader-facing payload\"",
    "test \"runtime atomic64 loader keeps loader-facing seed and descriptor explicit\"",
    "test \"runtime atomic64 loader keeps loaded seed stable through selftest and exit\"",
    "test \"runtime atomic64 loader keeps direct exit without selftest explicit\"",
    "test \"runtime atomic64 loader keeps post-selftest mutation explicit before exit\"",
    "test \"runtime atomic64 loader rejects re-init without disturbing summaries\"",
    "test \"runtime atomic64 loader rejects re-selftest without disturbing summaries\"",
    "test \"runtime atomic64 loader rejects re-exit without disturbing exited summaries\"",
};

const module_markers = [_][]const u8{
    "test \"runtime atomic64 sample advertises the bounded pilot-module contract\"",
    "test \"runtime atomic64 sample keeps selftest summary replay explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps lifecycle snapshot replay explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps initialized-stage exit replay explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps captured initialized summary replay explicit across later selftest and exit at the module boundary\"",
    "test \"runtime atomic64 sample keeps post-selftest mutation replay explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps post-selftest bitwise replay explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps captured selftest summary replay explicit across later mutation and exit at the module boundary\"",
    "test \"runtime atomic64 sample keeps zero and negative guard-return replay explicit after selftest at the module boundary\"",
    "test \"runtime atomic64 sample keeps rejected re-init rollback explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps rejected re-selftest rollback explicit at the module boundary\"",
    "test \"runtime atomic64 sample keeps rejected re-exit rollback explicit at the module boundary\"",
};

const diff_markers = [_][]const u8{
    "test \"runtime atomic64 diff gate replays bounded atomic64_test.c arithmetic, exchange, cmpxchg, add_unless, and bitwise expectations\"",
    "test \"runtime atomic64 diff gate keeps inc_not_zero and dec_if_positive guard paths explicit\"",
    "test \"runtime atomic64 diff gate keeps selftest family coverage explicit\"",
    "test \"runtime atomic64 diff gate rejects an empty threshold replay batch\"",
    "test \"runtime atomic64 diff gate keeps a deterministic threshold replay batch ready for future perf baselines\"",
    "pub fn runThresholdReplay(iterations: usize) !ThresholdReplaySummary",
};

const manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 9\"",
    "\"lane_key\": \"P9-L07\"",
    "\"sample_path\": \"samples/zigux/runtime_atomic64.zig\"",
    "\"loader_path\": \"samples/zigux/runtime_atomic64_loader.zig\"",
    "\"module_path\": \"zigux/tests/runtime_atomic64_module.zig\"",
    "\"diff_path\": \"zigux/tests/runtime_atomic64_diff.zig\"",
    "\"survey_path\": \"zigux/tests/runtime_atomic64_survey.zig\"",
    "\"ownership_map_path\": \"Documentation/zigux/phase9-runtime-pilot-ownership-map.md\"",
    "\"validation_entrypoint\": \"zig test zigux/tests/runtime_atomic64_survey.zig\"",
    "\"descriptor_and_anchor\"",
    "\"diff_threshold_replay_determinism\"",
    "\"Keep `kernel/workqueue.c` framed as a study-only freeze-map anchor; this packet stays review-only beside that boundary and is not runtime-substrate delivery evidence.\"",
    "\"freeze_map_study_boundary_governance_record\"",
    "\"workqueue-facing runtime-substrate delivery claims\"",
};

const survey_note_markers = [_][]const u8{
    "`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in the study-only bucket, so this packet stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue delivery.",
    "Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from the landed atomic64 notes, starter packet, direct loader companion, or visible shared-loader reminder packet.",
    "owner: the direct atomic64 starter packet owned by `P9-L16`, with this survey carrying the same Phase 9 freeze-boundary review record for `P9-L16`",
    "status bucket: review-only direct starter packet plus the visible direct loader companion, visible cross-family parity witness, and visible shared-loader reminder packet beside the study-only `kernel/workqueue.c` boundary",
    "reopen rule: any attempt to treat this packet as runtime-substrate delivery or to move `kernel/workqueue.c` out of study-only posture must reopen through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` with fresh reviewable evidence",
};

const ownership_markers = [_][]const u8{
    "## Runtime Atomic64 Family Owner",
    "`samples/zigux/runtime_atomic64.zig`",
    "`samples/zigux/runtime_atomic64_loader.zig`",
    "`zigux/tests/runtime_atomic64_manifest.json`",
    "`zigux/tests/runtime_atomic64_survey.zig`",
    "`zigux/tests/runtime_atomic64_diff.zig`",
    "`zigux/tests/runtime_atomic64_module.zig`",
    "bounded `phase9-runtime-atomic64-tests`",
};

fn readRepoFileAlloc(root: anytype, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try root.readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn writeFixtureFile(root: anytype, path: []const u8, contents: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    if (std.fs.path.dirname(path)) |dir_name| {
        try root.createDirPath(io_instance.io(), dir_name);
    }
    try root.writeFile(io_instance.io(), .{
        .sub_path = path,
        .data = contents,
    });
}

fn validateAtomic64Packet(root: anytype) !void {
    const sample_file = try readRepoFileAlloc(root, "samples/zigux/runtime_atomic64.zig", 128 * 1024);
    defer std.testing.allocator.free(sample_file);
    const loader_file = try readRepoFileAlloc(root, "samples/zigux/runtime_atomic64_loader.zig", 128 * 1024);
    defer std.testing.allocator.free(loader_file);
    const module_file = try readRepoFileAlloc(root, "zigux/tests/runtime_atomic64_module.zig", 128 * 1024);
    defer std.testing.allocator.free(module_file);
    const diff_file = try readRepoFileAlloc(root, "zigux/tests/runtime_atomic64_diff.zig", 128 * 1024);
    defer std.testing.allocator.free(diff_file);
    const manifest_file = try readRepoFileAlloc(root, "zigux/tests/runtime_atomic64_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_file);
    const survey_note_file = try readRepoFileAlloc(
        root,
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(survey_note_file);
    const ownership_map_file = try readRepoFileAlloc(
        root,
        "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(ownership_map_file);

    inline for (sample_markers) |marker| try expectContains(sample_file, marker);
    inline for (loader_markers) |marker| try expectContains(loader_file, marker);
    inline for (module_markers) |marker| try expectContains(module_file, marker);
    inline for (diff_markers) |marker| try expectContains(diff_file, marker);
    inline for (manifest_markers) |marker| try expectContains(manifest_file, marker);
    inline for (survey_note_markers) |marker| try expectContains(survey_note_file, marker);
    inline for (ownership_markers) |marker| try expectContains(ownership_map_file, marker);
}

test "phase9 runtime atomic64 survey gate matches the bounded atomic64 runtime packet" {
    try validateAtomic64Packet(std.fs.cwd());
}

test "phase9 runtime atomic64 survey self-test fixtures stay aligned" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const sample_text = try std.mem.join(std.testing.allocator, "\n", &sample_markers);
    defer std.testing.allocator.free(sample_text);
    const loader_text = try std.mem.join(std.testing.allocator, "\n", &loader_markers);
    defer std.testing.allocator.free(loader_text);
    const module_text = try std.mem.join(std.testing.allocator, "\n", &module_markers);
    defer std.testing.allocator.free(module_text);
    const diff_text = try std.mem.join(std.testing.allocator, "\n", &diff_markers);
    defer std.testing.allocator.free(diff_text);
    const manifest_text = try std.mem.join(std.testing.allocator, "\n", &manifest_markers);
    defer std.testing.allocator.free(manifest_text);
    const survey_note_text = try std.mem.join(std.testing.allocator, "\n", &survey_note_markers);
    defer std.testing.allocator.free(survey_note_text);
    const ownership_text = try std.mem.join(std.testing.allocator, "\n", &ownership_markers);
    defer std.testing.allocator.free(ownership_text);

    try writeFixtureFile(tmp.dir, "samples/zigux/runtime_atomic64.zig", sample_text);
    try writeFixtureFile(tmp.dir, "samples/zigux/runtime_atomic64_loader.zig", loader_text);
    try writeFixtureFile(tmp.dir, "zigux/tests/runtime_atomic64_module.zig", module_text);
    try writeFixtureFile(tmp.dir, "zigux/tests/runtime_atomic64_diff.zig", diff_text);
    try writeFixtureFile(tmp.dir, "zigux/tests/runtime_atomic64_manifest.json", manifest_text);
    try writeFixtureFile(
        tmp.dir,
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
        survey_note_text,
    );
    try writeFixtureFile(
        tmp.dir,
        "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
        ownership_text,
    );

    try validateAtomic64Packet(tmp.dir);
}
