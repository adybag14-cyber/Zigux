const std = @import("std");
const bpf_type_names = @import("bpf_type_names");

test "phase 8 bpf type-name segment imports cleanly" {
    _ = bpf_type_names;
}

test "phase 8 bpf type-name segment exposes libbpf string helpers" {
    try std.testing.expectEqualStrings("xdp", bpf_type_names.libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("sockmap", bpf_type_names.libbpfBpfLinkTypeStr(14).?);
    try std.testing.expectEqualStrings("ringbuf", bpf_type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings("netfilter", bpf_type_names.libbpfBpfProgTypeStr(32).?);

    try std.testing.expectEqual(@as(?[]const u8, null), bpf_type_names.libbpfBpfAttachTypeStr(99));
    try std.testing.expectEqual(@as(?[]const u8, null), bpf_type_names.libbpfBpfLinkTypeStr(-1));
}

test "phase 8 bpf type-name segment keeps the dense libbpf tables aligned with the helper surface" {
    try std.testing.expectEqual(@as(usize, 59), bpf_type_names.attach_type_names.len);
    try std.testing.expectEqual(@as(usize, 15), bpf_type_names.link_type_names.len);
    try std.testing.expectEqual(@as(usize, 35), bpf_type_names.map_type_names.len);
    try std.testing.expectEqual(@as(usize, 33), bpf_type_names.prog_type_names.len);

    try std.testing.expectEqualStrings("cgroup_storage", bpf_type_names.map_type_names[19]);
    try std.testing.expectEqualStrings("percpu_cgroup_storage", bpf_type_names.map_type_names[21]);
    try std.testing.expectEqualStrings("trace_fsession", bpf_type_names.attach_type_names[58]);
}
