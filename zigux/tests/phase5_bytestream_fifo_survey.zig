const std = @import("std");

const ExactCheck = struct {
    id: []const u8,
    kind: []const u8,
    expected: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    sample_path: []const u8,
    validation_entrypoint: []const u8,
    review_prompts: []const []const u8,
    exact_checks: []const ExactCheck,
    non_goals: []const []const u8,
};

test "phase 5 bytestream fifo manifest records the exact bounded checks" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L06", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    for (manifest.surveyed_commit) |char| {
        try std.testing.expect(std.ascii.isHex(char));
        try std.testing.expect(!std.ascii.isUpper(char));
    }
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/bytestream_fifo.zig", manifest.sample_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoint, "phase5_build.zig") != null);
    try std.testing.expectEqual(@as(usize, 5), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    var saw_descriptor_prompt = false;
    var saw_manifest_prompt = false;
    var saw_docs_prompt = false;
    var saw_storage_prompt = false;
    var saw_exact_sequence = false;
    var saw_snapshot = false;
    var saw_capacity = false;
    var saw_storage_contract = false;
    var saw_focus_list = false;
    var saw_lifecycle = false;
    var saw_lifecycle_guards = false;

    for (manifest.review_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);

        if (std.mem.indexOf(u8, prompt, "requires_runtime_substrate false") != null) {
            saw_descriptor_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "phase5_build.zig") != null) {
            saw_manifest_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "sample-backed survey note") != null and
            std.mem.indexOf(u8, prompt, "review checklist") != null)
        {
            saw_docs_prompt = true;
        }
        if (std.mem.indexOf(u8, prompt, "fixed embedded backing") != null) {
            saw_storage_prompt = true;
        }
    }

    for (manifest.exact_checks, 0..) |check, i| {
        try std.testing.expect(check.id.len > 0);
        try std.testing.expect(check.kind.len > 0);
        try std.testing.expect(check.expected.len > 0);

        if (std.mem.eql(u8, check.id, "final-drain-sequence")) {
            saw_exact_sequence = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "3,4,5,6,7,8,9,0,1,20") != null);
        }
        if (std.mem.eql(u8, check.id, "snapshot-before-final-drain")) {
            saw_snapshot = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "non-destructive snapshot") != null);
        }
        if (std.mem.eql(u8, check.id, "fill-to-capacity")) {
            saw_capacity = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "20 through 42 inclusive") != null);
        }
        if (std.mem.eql(u8, check.id, "storage-backing-contract")) {
            saw_storage_contract = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "fixed embedded 32-byte ring buffer") != null);
        }
        if (std.mem.eql(u8, check.id, "lifecycle-boundary")) {
            saw_lifecycle = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "requires init before replay") != null);
        }
        if (std.mem.eql(u8, check.id, "checked-focus-list")) {
            saw_focus_list = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "exactly six focus areas") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "ownership_and_lifetime") != null);
        }
        if (std.mem.eql(u8, check.id, "lifecycle-guards-and-counters")) {
            saw_lifecycle_guards = true;
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "after exit") != null);
            try std.testing.expect(std.mem.indexOf(u8, check.expected, "init_runs and exit_runs at 1") != null);
        }

        for (manifest.exact_checks[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, check.id, other.id));
        }
    }

    try std.testing.expect(saw_descriptor_prompt);
    try std.testing.expect(saw_manifest_prompt);
    try std.testing.expect(saw_docs_prompt);
    try std.testing.expect(saw_storage_prompt);
    try std.testing.expect(saw_exact_sequence);
    try std.testing.expect(saw_snapshot);
    try std.testing.expect(saw_capacity);
    try std.testing.expect(saw_storage_contract);
    try std.testing.expect(saw_focus_list);
    try std.testing.expect(saw_lifecycle);
    try std.testing.expect(saw_lifecycle_guards);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "procfs parity"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "kfifo_from_user or kfifo_to_user parity"));
}

test "phase 5 bytestream fifo contributor docs stay aligned with the shipped review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase5-kfifo-sample-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(readme);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_bytestream_fifo_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_bytestream_fifo_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fixed embedded") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "procfs, user-copy, locking, and runtime registration remain out of scope") != null);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "manifest-backed survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "sample-backed survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "exact replay contract") != null);

    try std.testing.expect(std.mem.indexOf(u8, readme, "all four roadmap sample anchors") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "samples/zigux/bytestream_fifo.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "phase5-kfifo-sample-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme, "Phase 9 runtime pilot tranche") != null);
}
