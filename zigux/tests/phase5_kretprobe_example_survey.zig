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

const read_limit = 64 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(read_limit));
}

fn manifestById(manifest: Manifest, id: []const u8) ?ExactCheck {
    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, id)) return check;
    }
    return null;
}

fn isLowerHexCommitSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        const is_digit = byte >= '0' and byte <= '9';
        const is_lower_hex = byte >= 'a' and byte <= 'f';
        if (!is_digit and !is_lower_hex) return false;
    }
    return true;
}

test "phase5 kretprobe manifest records the restored direct replay packet" {
    const manifest_json = try readFile(std.testing.allocator, "zigux/tests/phase5_kretprobe_example_manifest.json");
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P5-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/kretprobe_example.zig", manifest.sample_path);
    try std.testing.expectEqualStrings("zig test zigux/tests/phase5_kretprobe_example_survey.zig", manifest.validation_entrypoint);
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    const anchor_check = manifestById(manifest, "descriptor-anchor") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, anchor_check.expected, "non-runtime reference-sample lane") != null);

    const retarget_check = manifestById(manifest, "retarget-replay") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, retarget_check.expected, "do_sys_openat2") != null);

    const recovery_check = manifestById(manifest, "recovery-replay") orelse return error.MissingExactCheck;
    try std.testing.expect(std.mem.indexOf(u8, recovery_check.expected, "recovered duration 60") != null);
}

test "phase5 kretprobe survey note and manifest stay aligned with the restored packet" {
    const manifest_json = try readFile(std.testing.allocator, "zigux/tests/phase5_kretprobe_example_manifest.json");
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase5-kretprobe-sample-survey.md");
    defer std.testing.allocator.free(survey_note);
    const surveyed_commit_line = try std.fmt.allocPrint(std.testing.allocator, "PHASE5_SURVEYED_COMMIT={s}", .{manifest.surveyed_commit});
    defer std.testing.allocator.free(surveyed_commit_line);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit_line) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_LANE_KEY=P5-L18") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase5_kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase5_kretprobe_example_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase5_kretprobe_example_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRetargetReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runLifecycleGuardReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runOwnershipReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRecoveryReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5-sample-review-guide.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scripts/zigux/README.md") != null);

    const prompt = manifest.review_prompts[1];
    try std.testing.expect(std.mem.indexOf(u8, prompt, "survey gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, prompt, "next bounded follow-through") != null);
}
