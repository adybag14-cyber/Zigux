const std = @import("std");

fn nameFromDenseTable(table: []const []const u8, value: i32) ?[]const u8 {
    if (value < 0) {
        return null;
    }

    const index: usize = @intCast(value);
    if (index >= table.len) {
        return null;
    }

    return table[index];
}

pub const attach_type_names = [_][]const u8{
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

pub const link_type_names = [_][]const u8{
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

pub const map_type_names = [_][]const u8{
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
    "devmap_hash",
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

pub const prog_type_names = [_][]const u8{
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

pub fn libbpfBpfAttachTypeStr(value: i32) ?[]const u8 {
    return nameFromDenseTable(&attach_type_names, value);
}

pub fn libbpfBpfLinkTypeStr(value: i32) ?[]const u8 {
    return nameFromDenseTable(&link_type_names, value);
}

pub fn libbpfBpfMapTypeStr(value: i32) ?[]const u8 {
    return nameFromDenseTable(&map_type_names, value);
}

pub fn libbpfBpfProgTypeStr(value: i32) ?[]const u8 {
    return nameFromDenseTable(&prog_type_names, value);
}

test "dense type-name helpers preserve the bounded libbpf string tables" {
    for (attach_type_names, 0..) |name, idx| {
        try std.testing.expectEqualStrings(name, libbpfBpfAttachTypeStr(@intCast(idx)).?);
    }
    for (link_type_names, 0..) |name, idx| {
        try std.testing.expectEqualStrings(name, libbpfBpfLinkTypeStr(@intCast(idx)).?);
    }
    for (map_type_names, 0..) |name, idx| {
        try std.testing.expectEqualStrings(name, libbpfBpfMapTypeStr(@intCast(idx)).?);
    }
    for (prog_type_names, 0..) |name, idx| {
        try std.testing.expectEqualStrings(name, libbpfBpfProgTypeStr(@intCast(idx)).?);
    }
}

test "known enum ordinals from tools/include/uapi/linux/bpf.h map to the expected names" {
    try std.testing.expectEqualStrings("xdp", libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("trace_fsession", libbpfBpfAttachTypeStr(58).?);

    try std.testing.expectEqualStrings("sockmap", libbpfBpfLinkTypeStr(14).?);

    try std.testing.expectEqualStrings("ringbuf", libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings("insn_array", libbpfBpfMapTypeStr(34).?);

    try std.testing.expectEqualStrings("tracing", libbpfBpfProgTypeStr(26).?);
    try std.testing.expectEqualStrings("netfilter", libbpfBpfProgTypeStr(32).?);
}

test "type-name helpers reject out-of-range values the same way as libbpf.c" {
    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfAttachTypeStr(-1));
    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfAttachTypeStr(@intCast(attach_type_names.len)));

    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfLinkTypeStr(-1));
    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfLinkTypeStr(@intCast(link_type_names.len)));

    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfMapTypeStr(-1));
    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfMapTypeStr(@intCast(map_type_names.len)));

    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfProgTypeStr(-1));
    try std.testing.expectEqual(@as(?[]const u8, null), libbpfBpfProgTypeStr(@intCast(prog_type_names.len)));
}
