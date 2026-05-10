const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor_path: []const u8,
    anchor_blob_sha: []const u8,
    sample_path: []const u8,
    sample_present: bool,
    current_replay: []const u8,
    local_lab_replay: []const u8,
    makefile_wrapper: []const u8,
    survey_note: []const u8,
    survey_owner: []const u8,
    rollback_owner: []const u8,
    shared_gate_evidence_packet_present: bool,
    validation_entrypoint: []const u8,
    review_prompts: []const []const u8,
    non_goals: []const []const u8,
};

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) return false;
    }
    return true;
}

test "phase4 test_fsmount gap manifest keeps the parked survey explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L24", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("samples/vfs/test-fsmount.c", manifest.anchor_path);
    try std.testing.expect(isLowerHexSha(manifest.anchor_blob_sha));
    try std.testing.expectEqualStrings("samples/zigux/test_fsmount.zig", manifest.sample_path);
    try std.testing.expect(!manifest.sample_present);
    try std.testing.expectEqualStrings("make M=samples/vfs", manifest.current_replay);
    try std.testing.expectEqualStrings(
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        manifest.local_lab_replay,
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase4-test-fsmount-survey",
        manifest.makefile_wrapper,
    );
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        manifest.survey_note,
    );
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.survey_owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(!manifest.shared_gate_evidence_packet_present);
    try std.testing.expectEqualStrings(
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        manifest.validation_entrypoint,
    );
    try std.testing.expectEqual(@as(usize, 5), manifest.review_prompts.len);
    try std.testing.expectEqualStrings(
        "the survey keeps the Linux anchor path and blob sha explicit while the Zig starter stays absent",
        manifest.review_prompts[0],
    );
    try std.testing.expectEqualStrings(
        "the packet keeps the live VFS replay command plus the dedicated local and Linux-style survey wrappers explicit without implying a shipped Zig sample",
        manifest.review_prompts[1],
    );
    try std.testing.expectEqualStrings(
        "the direct validation entrypoint intentionally stays aligned to the dedicated build-step survey wrapper, so the parked packet cannot silently retarget one replay surface without the other",
        manifest.review_prompts[2],
    );
    try std.testing.expectEqualStrings(
        "the owner and rollback owner remain Validation and Perf Team while the packet stays adjacent to the shared Phase 4 validator-first route",
        manifest.review_prompts[3],
    );
    try std.testing.expectEqualStrings(
        "the packet stays outside the shared gate-evidence target set while the shared validator still rereads it through the dedicated exact-readback checker",
        manifest.review_prompts[4],
    );
    try std.testing.expectEqual(@as(usize, 3), manifest.non_goals.len);
    try std.testing.expectEqualStrings("shipped test_fsmount Zig starter", manifest.non_goals[0]);
    try std.testing.expectEqualStrings("shared gate-evidence promotion", manifest.non_goals[1]);
    try std.testing.expectEqualStrings("approved fsmount perf threshold", manifest.non_goals[2]);
}

test "phase4 test_fsmount gap survey note stays honest about the parked boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    const required_markers = [_][]const u8{
        "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_survey",
        "PHASE4_LANE_KEY=P4-L24",
        "PHASE4_ANCHOR_PATH=samples/vfs/test-fsmount.c",
        "PHASE4_SAMPLE_PATH=samples/zigux/test_fsmount.zig",
        "PHASE4_SAMPLE_PRESENT=false",
        "PHASE4_CURRENT_REPLAY=make M=samples/vfs",
        "PHASE4_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        "PHASE4_MAKEFILE_WRAPPER=make -C zigux phase4-test-fsmount-survey",
        "PHASE4_SURVEY_OWNER=Validation and Perf Team",
        "PHASE4_ROLLBACK_OWNER=Validation and Perf Team",
        "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false",
        "zigux/tests/phase4_test_fsmount_manifest.json",
        "zigux/tests/phase4_test_fsmount_survey.zig",
        "`samples/zigux/test_fsmount.zig` is still absent",
        "the dedicated local survey wrapper now lives at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
        "the shared validator route already rereads this parked packet through `scripts/zigux/check-phase4-gate-evidence.py`",
        "Keep this parked packet adjacent to the shared gate-evidence note,",
        "claiming that the shared Phase 4 exact-readback gate already carries this packet",
        "claiming approved hard perf thresholds for the test_fsmount anchor",
    };

    for (required_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, note, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, note, manifest.anchor_blob_sha) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.validation_entrypoint) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.local_lab_replay) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.makefile_wrapper) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "claiming a shipped Zig starter") != null);
}

test "phase4 test_fsmount survey build replay stays aligned with the parked packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    const phase4_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase4_build);

    const required_build_markers = [_][]const u8{
        "root_source_file = b.path(\"phase4_test_fsmount_survey.zig\")",
        "name = \"phase4-test-fsmount-survey-tests\"",
        "\"phase4-test-fsmount-survey\"",
        "Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter",
    };

    for (required_build_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, phase4_build, marker) != null);
    }

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            phase4_build,
            "test_step.dependOn(&run_test_fsmount_survey_tests.step);",
        ) == null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            note,
            "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, note, "stays outside the shared gate-evidence packet") != null,
    );
}

test "phase4 test_fsmount survey keeps matrix and exact-readback checker anchors explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);

    const gate_evidence_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase4-gate-evidence.py",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(gate_evidence_checker);

    const required_matrix_markers = [_][]const u8{
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "zigux/tests/phase4_test_fsmount_manifest.json",
        "zigux/tests/phase4_test_fsmount_survey.zig",
        "keep the dedicated parked survey packet and the dedicated local survey wrapper adjacent to the shared Phase 4 exact-readback packet",
    };
    for (required_matrix_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, marker) != null);
    }

    const required_checker_markers = [_][]const u8{
        "TEST_FSMOUNT_NOTE_PATH = Path(\"Documentation/zigux/phase4-test-fsmount-gap-survey.md\")",
        "TEST_FSMOUNT_MANIFEST_PATH = Path(\"zigux/tests/phase4_test_fsmount_manifest.json\")",
        "TEST_FSMOUNT_SURVEY_PATH = Path(\"zigux/tests/phase4_test_fsmount_survey.zig\")",
        "def validate_test_fsmount_gap_packet(root: Path) -> list[str]:",
        "missing.extend(validate_test_fsmount_gap_packet(root))",
        "shared validator route now picks that same parked packet up through `scripts/zigux/check-phase4-gate-evidence.py` while `samples/zigux/test_fsmount.zig` remains absent on current `master`",
    };
    for (required_checker_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, gate_evidence_checker, marker) != null);
    }
}

test "phase4 test_fsmount survey keeps the dedicated Makefile replay route explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const required_makefile_markers = [_][]const u8{
        "phase4-test-fsmount-survey",
        "phase4-test-fsmount-survey:",
        "$(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    };
    for (required_makefile_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, makefile, marker) != null);
    }
}
