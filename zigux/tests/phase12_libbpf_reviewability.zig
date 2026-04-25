const std = @import("std");
const cpu_mask = @import("cpu_mask");
const bpf_type_names = @import("bpf_type_names");

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
    gaps: []const Gap,
};

fn pathExists(io: std.Io, path: []const u8) !bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    return true;
}

test "phase12 libbpf reviewability gate matches the current zigux_segments file state" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_libbpf_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);

    var saw_landed_manifest = false;
    var saw_landed_type_names = false;
    var saw_landed_cpu_mask = false;
    var saw_ready_next_logging = false;
    var saw_blocked_object_loader = false;

    for (manifest.gaps) |gap| {
        if (!std.mem.startsWith(u8, gap.zigux_destination, "tools/lib/bpf/zigux_segments/")) {
            continue;
        }

        const exists = try pathExists(io_instance.io(), gap.zigux_destination);
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            try std.testing.expect(exists);
        } else if (std.mem.eql(u8, gap.status, "ready_next") or std.mem.eql(u8, gap.status, "blocked_on_object_model")) {
            try std.testing.expect(!exists);
        }

        if (std.mem.eql(u8, gap.id, "phase12-libbpf-segment-manifest-foundation")) {
            saw_landed_manifest = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-type-name-helper-foundation")) {
            saw_landed_type_names = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-cpu-mask-helper-foundation")) {
            saw_landed_cpu_mask = true;
            try std.testing.expect(exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-logging-helper")) {
            saw_ready_next_logging = true;
            try std.testing.expect(!exists);
        }
        if (std.mem.eql(u8, gap.id, "phase12-libbpf-object-loader-and-program-load")) {
            saw_blocked_object_loader = true;
            try std.testing.expect(!exists);
        }
    }

    try std.testing.expect(saw_landed_manifest);
    try std.testing.expect(saw_landed_type_names);
    try std.testing.expect(saw_landed_cpu_mask);
    try std.testing.expect(saw_ready_next_logging);
    try std.testing.expect(saw_blocked_object_loader);
}

test "phase12 libbpf reviewability gate still compiles the landed helper foundations" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,3");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expectEqualStrings("xdp", bpf_type_names.libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("ringbuf", bpf_type_names.libbpfBpfMapTypeStr(27).?);
}
