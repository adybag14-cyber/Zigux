const std = @import("std");

const map_type_names = [_]?[]const u8{
    "unspec",
    "hash",
    "array",
    "prog_array",
    "perf_event_array",
    "percpu_hash",
    "percpu_array",
    "stack_trace",
    "cgroup_array",
    "lru_hash",
    "lru_percpu_hash",
    "lpm_trie",
    "array_of_maps",
    "hash_of_maps",
    "devmap",
    "devmap_hash",
    "sockmap",
    "cpumap",
    "xskmap",
    "sockhash",
    "cgroup_storage",
    "reuseport_sockarray",
    "percpu_cgroup_storage",
    "queue",
    "stack",
    "sk_storage",
    "struct_ops",
    "ringbuf",
    "inode_storage",
    "task_storage",
    "bloom_filter",
    "user_ringbuf",
    "cgrp_storage",
    "arena",
    "insn_array",
};

const attach_type_names = [_]?[]const u8{
    "cgroup_inet_ingress",
    "cgroup_inet_egress",
    "cgroup_inet_sock_create",
    "cgroup_sock_ops",
    "sk_skb_stream_parser",
    "sk_skb_stream_verdict",
    "cgroup_device",
    "sk_msg_verdict",
    "cgroup_inet4_bind",
    "cgroup_inet6_bind",
    "cgroup_inet4_connect",
    "cgroup_inet6_connect",
    "cgroup_inet4_post_bind",
    "cgroup_inet6_post_bind",
    "cgroup_udp4_sendmsg",
    "cgroup_udp6_sendmsg",
    "lirc_mode2",
    "flow_dissector",
    "cgroup_sysctl",
    "cgroup_udp4_recvmsg",
    "cgroup_udp6_recvmsg",
    "cgroup_getsockopt",
    "cgroup_setsockopt",
    "trace_raw_tp",
    "trace_fentry",
    "trace_fexit",
    "modify_return",
    "lsm_mac",
    "trace_iter",
    "cgroup_inet4_getpeername",
    "cgroup_inet6_getpeername",
    "cgroup_inet4_getsockname",
    "cgroup_inet6_getsockname",
    "xdp_devmap",
    "cgroup_inet_sock_release",
    "xdp_cpumap",
    "sk_lookup",
    "xdp",
    "sk_skb_verdict",
    "sk_reuseport_select",
    "sk_reuseport_select_or_migrate",
    "perf_event",
    "trace_kprobe_multi",
    "lsm_cgroup",
    "struct_ops",
    "netfilter",
    "tcx_ingress",
    "tcx_egress",
    "trace_uprobe_multi",
    "cgroup_unix_connect",
    "cgroup_unix_sendmsg",
    "cgroup_unix_recvmsg",
    "cgroup_unix_getpeername",
    "cgroup_unix_getsockname",
    "netkit_primary",
    "netkit_peer",
    "trace_kprobe_session",
    "trace_uprobe_session",
    "trace_fsession",
};

const link_type_names = [_]?[]const u8{
    "unspec",
    "raw_tracepoint",
    "tracing",
    "cgroup",
    "iter",
    "netns",
    "xdp",
    "perf_event",
    "kprobe_multi",
    "struct_ops",
    "netfilter",
    "tcx",
    "uprobe_multi",
    "netkit",
    "sockmap",
};

const prog_type_names = [_]?[]const u8{
    "unspec",
    "socket_filter",
    "kprobe",
    "sched_cls",
    "sched_act",
    "tracepoint",
    "xdp",
    "perf_event",
    "cgroup_skb",
    "cgroup_sock",
    "lwt_in",
    "lwt_out",
    "lwt_xmit",
    "sock_ops",
    "sk_skb",
    "cgroup_device",
    "sk_msg",
    "raw_tracepoint",
    "cgroup_sock_addr",
    "lwt_seg6local",
    "lirc_mode2",
    "sk_reuseport",
    "flow_dissector",
    "cgroup_sysctl",
    "raw_tracepoint_writable",
    "cgroup_sockopt",
    "tracing",
    "struct_ops",
    "ext",
    "lsm",
    "sk_lookup",
    "syscall",
    "netfilter",
};

pub fn libbpfBpfMapTypeStr(map_type: u32) ?[]const u8 {
    if (map_type >= map_type_names.len) return null;
    return map_type_names[map_type];
}

pub fn libbpfBpfAttachTypeStr(attach_type: u32) ?[]const u8 {
    if (attach_type >= attach_type_names.len) return null;
    return attach_type_names[attach_type];
}

pub fn libbpfBpfLinkTypeStr(link_type: u32) ?[]const u8 {
    if (link_type >= link_type_names.len) return null;
    return link_type_names[link_type];
}

pub fn libbpfBpfProgTypeStr(prog_type: u32) ?[]const u8 {
    if (prog_type >= prog_type_names.len) return null;
    return prog_type_names[prog_type];
}

fn formatTypeName(
    buffer: []u8,
    known_name: ?[]const u8,
    unknown_prefix: []const u8,
    raw_value: u32,
) error{NoSpaceLeft}![]const u8 {
    if (known_name) |name| {
        return std.fmt.bufPrint(buffer, "{s}", .{name});
    }

    return std.fmt.bufPrint(buffer, "{s}({d})", .{ unknown_prefix, raw_value });
}

pub fn formatLibbpfBpfMapType(buffer: []u8, map_type: u32) error{NoSpaceLeft}![]const u8 {
    return formatTypeName(buffer, libbpfBpfMapTypeStr(map_type), "unknown_map_type", map_type);
}

pub fn formatLibbpfBpfAttachType(buffer: []u8, attach_type: u32) error{NoSpaceLeft}![]const u8 {
    return formatTypeName(buffer, libbpfBpfAttachTypeStr(attach_type), "unknown_attach_type", attach_type);
}

pub fn formatLibbpfBpfLinkType(buffer: []u8, link_type: u32) error{NoSpaceLeft}![]const u8 {
    return formatTypeName(buffer, libbpfBpfLinkTypeStr(link_type), "unknown_link_type", link_type);
}

pub fn formatLibbpfBpfProgType(buffer: []u8, prog_type: u32) error{NoSpaceLeft}![]const u8 {
    return formatTypeName(buffer, libbpfBpfProgTypeStr(prog_type), "unknown_prog_type", prog_type);
}

fn expectDenseNameTable(table: []const ?[]const u8) !void {
    for (table) |entry| {
        try std.testing.expect(entry != null);
        try std.testing.expect(entry.?.len != 0);
    }
}

fn expectFormatterMatchesKnownEntries(
    comptime formatter: fn ([]u8, u32) error{NoSpaceLeft}![]const u8,
    table: []const ?[]const u8,
) !void {
    var buffer: [64]u8 = undefined;

    for (table, 0..) |entry, index| {
        try std.testing.expect(entry != null);
        try std.testing.expectEqualStrings(
            entry.?,
            try formatter(buffer[0..], @intCast(index)),
        );
    }
}

test "map type names stay table-driven and bounded" {
    try std.testing.expectEqualStrings("unspec", libbpfBpfMapTypeStr(0).?);
    try std.testing.expectEqualStrings("ringbuf", libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings("insn_array", libbpfBpfMapTypeStr(34).?);
    try std.testing.expect(libbpfBpfMapTypeStr(99) == null);
}

test "attach type names keep the current helper-first surface reviewable" {
    try std.testing.expectEqualStrings("cgroup_inet_ingress", libbpfBpfAttachTypeStr(0).?);
    try std.testing.expectEqualStrings("cgroup_inet_sock_release", libbpfBpfAttachTypeStr(34).?);
    try std.testing.expectEqualStrings("perf_event", libbpfBpfAttachTypeStr(41).?);
    try std.testing.expectEqualStrings("cgroup_unix_connect", libbpfBpfAttachTypeStr(49).?);
    try std.testing.expectEqualStrings("trace_fsession", libbpfBpfAttachTypeStr(58).?);
    try std.testing.expect(libbpfBpfAttachTypeStr(99) == null);
}

test "link type names stay explicit and bounded" {
    try std.testing.expectEqualStrings("unspec", libbpfBpfLinkTypeStr(0).?);
    try std.testing.expectEqualStrings("perf_event", libbpfBpfLinkTypeStr(7).?);
    try std.testing.expectEqualStrings("sockmap", libbpfBpfLinkTypeStr(14).?);
    try std.testing.expect(libbpfBpfLinkTypeStr(99) == null);
}

test "program type names stay explicit and bounded" {
    try std.testing.expectEqualStrings("unspec", libbpfBpfProgTypeStr(0).?);
    try std.testing.expectEqualStrings("sk_reuseport", libbpfBpfProgTypeStr(21).?);
    try std.testing.expectEqualStrings("tracing", libbpfBpfProgTypeStr(26).?);
    try std.testing.expectEqualStrings("netfilter", libbpfBpfProgTypeStr(32).?);
    try std.testing.expect(libbpfBpfProgTypeStr(99) == null);
}

test "stable formatters keep known names unchanged and unknown ids reviewable" {
    var map_buffer: [32]u8 = undefined;
    var attach_buffer: [40]u8 = undefined;
    var link_buffer: [32]u8 = undefined;
    var prog_buffer: [32]u8 = undefined;

    try std.testing.expectEqualStrings("ringbuf", try formatLibbpfBpfMapType(map_buffer[0..], 27));
    try std.testing.expectEqualStrings("unknown_map_type(99)", try formatLibbpfBpfMapType(map_buffer[0..], 99));

    try std.testing.expectEqualStrings("perf_event", try formatLibbpfBpfAttachType(attach_buffer[0..], 41));
    try std.testing.expectEqualStrings("unknown_attach_type(88)", try formatLibbpfBpfAttachType(attach_buffer[0..], 88));

    try std.testing.expectEqualStrings("sockmap", try formatLibbpfBpfLinkType(link_buffer[0..], 14));
    try std.testing.expectEqualStrings("unknown_link_type(42)", try formatLibbpfBpfLinkType(link_buffer[0..], 42));

    try std.testing.expectEqualStrings("netfilter", try formatLibbpfBpfProgType(prog_buffer[0..], 32));
    try std.testing.expectEqualStrings("unknown_prog_type(77)", try formatLibbpfBpfProgType(prog_buffer[0..], 77));
}

test "all shipped libbpf type-name formatters round-trip every in-range value" {
    try expectFormatterMatchesKnownEntries(formatLibbpfBpfMapType, map_type_names[0..]);
    try expectFormatterMatchesKnownEntries(formatLibbpfBpfAttachType, attach_type_names[0..]);
    try expectFormatterMatchesKnownEntries(formatLibbpfBpfLinkType, link_type_names[0..]);
    try expectFormatterMatchesKnownEntries(formatLibbpfBpfProgType, prog_type_names[0..]);
}

test "stable formatters keep one-past-table ids readable" {
    var map_buffer: [64]u8 = undefined;
    var attach_buffer: [64]u8 = undefined;
    var link_buffer: [64]u8 = undefined;
    var prog_buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "unknown_map_type(35)",
        try formatLibbpfBpfMapType(map_buffer[0..], map_type_names.len),
    );
    try std.testing.expectEqualStrings(
        "unknown_attach_type(59)",
        try formatLibbpfBpfAttachType(attach_buffer[0..], attach_type_names.len),
    );
    try std.testing.expectEqualStrings(
        "unknown_link_type(15)",
        try formatLibbpfBpfLinkType(link_buffer[0..], link_type_names.len),
    );
    try std.testing.expectEqualStrings(
        "unknown_prog_type(33)",
        try formatLibbpfBpfProgType(prog_buffer[0..], prog_type_names.len),
    );
}

test "all shipped libbpf name tables stay dense for every in-range value" {
    try expectDenseNameTable(map_type_names[0..]);
    try expectDenseNameTable(attach_type_names[0..]);
    try expectDenseNameTable(link_type_names[0..]);
    try expectDenseNameTable(prog_type_names[0..]);
}