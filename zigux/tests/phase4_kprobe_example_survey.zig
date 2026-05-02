const std = @import("std");
const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";

const SurveySummary = struct {
    kprobes_makefile_replay_present: bool,
    anchor_kernel_clone_present: bool,
    zig_sample_present: bool,
    phase4_build_present: bool,
    makefile_target_present: bool,
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
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_replay: []const u8,
    isolated_survey_replay: []const u8,
    shared_build_replay: []const u8,
    threshold_posture: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

const SiblingManifest = struct {
    phase: []const u8,
    surveyed_commit: []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "phase4 kprobe_example survey manifest records the landed survey gate and remaining sample gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_kprobe_example_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L23", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kprobes/kprobe_example.c", manifest.anchor);
    try std.testing.expectEqualStrings(
        "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
        manifest.current_replay,
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase4-kprobe-example-survey",
        manifest.isolated_survey_replay,
    );
    try std.testing.expectEqualStrings(
        "phase4-kprobe-example-survey-tests",
        manifest.shared_build_replay,
    );
    try std.testing.expectEqualStrings(
        "c_anchor_only_until_kprobe_example_starter_lands",
        manifest.threshold_posture,
    );
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings(
        "samples/zigux/kprobe_example.zig",
        manifest.roadmap_destinations[0],
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.gaps.len);

    const sibling_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sibling_manifest_json);
    const sibling_parsed = try std.json.parseFromSlice(
        SiblingManifest,
        std.testing.allocator,
        sibling_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer sibling_parsed.deinit();
    const sibling_manifest = sibling_parsed.value;
    try std.testing.expectEqualStrings("Phase 4", sibling_manifest.phase);
    try std.testing.expectEqualStrings(current_surveyed_commit, sibling_manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(sibling_manifest.surveyed_commit));

    const anchor = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/kprobes/kprobe_example.c",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(anchor);
    const kprobes_makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/kprobes/Makefile",
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(kprobes_makefile);
    const phase4_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_build.zig",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(phase4_build);
    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const zig_sample_present = blk: {
        std.Io.Dir.cwd().access(io_instance.io(), "samples/zigux/kprobe_example.zig", .{}) catch |err| switch (err) {
            error.FileNotFound => break :blk false,
            else => return err,
        };
        break :blk true;
    };

    const live_summary = SurveySummary{
        .kprobes_makefile_replay_present =
            std.mem.indexOf(u8, kprobes_makefile, "obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o") != null,
        .anchor_kernel_clone_present =
            std.mem.indexOf(u8, anchor, "kernel_clone") != null and
            std.mem.indexOf(u8, anchor, "register_kprobe") != null and
            std.mem.indexOf(u8, anchor, "MODULE_DESCRIPTION") != null,
        .zig_sample_present = zig_sample_present,
        .phase4_build_present =
            std.mem.indexOf(u8, phase4_build, "phase4_kprobe_example_survey.zig") != null and
            std.mem.indexOf(u8, phase4_build, manifest.shared_build_replay) != null and
            std.mem.indexOf(u8, phase4_build, "phase4-kprobe-example-survey") != null,
        .makefile_target_present =
            std.mem.indexOf(u8, makefile, "phase4-kprobe-example-survey") != null and
            std.mem.indexOf(u8, makefile, "phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig") != null,
    };
    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_manifest_gap = false;
    var saw_gate_gap = false;
    var saw_anchor_gap = false;
    var saw_sample_gap = false;

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

        if (std.mem.eql(u8, gap.id, "phase4-kprobe-example-survey-manifest")) {
            saw_manifest_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings(
                "zigux/tests/phase4_kprobe_example_manifest.json",
                gap.zigux_destination,
            );
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "manifest-backed survey packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "C-anchor-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-kprobe-example-survey-gate")) {
            saw_gate_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings(
                "zigux/tests/phase4_kprobe_example_survey.zig",
                gap.zigux_destination,
            );
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 4 build") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "prose-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-kprobe-example-c-anchor-replay")) {
            saw_anchor_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/kprobes/kprobe_example.c", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "C-anchor-only") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase4-kprobe-example-zig-sample")) {
            saw_sample_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/kprobe_example.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "still absent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "starter under `samples/zigux/`") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 3), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_manifest_gap);
    try std.testing.expect(saw_gate_gap);
    try std.testing.expect(saw_anchor_gap);
    try std.testing.expect(saw_sample_gap);
}
