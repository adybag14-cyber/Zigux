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
};

pub fn libbpfBpfMapTypeStr(map_type: u32) ?[]const u8 {
    if (map_type >= map_type_names.len) return null;
    return map_type_names[map_type];
}

pub fn libbpfBpfAttachTypeStr(attach_type: u32) ?[]const u8 {
    if (attach_type >= attach_type_names.len) return null;
    return attach_type_names[attach_type];
}

test "map type names stay table-driven and bounded" {
    try std.testing.expectEqualStrings("unspec", libbpfBpfMapTypeStr(0).?);
    try std.testing.expectEqualStrings("ringbuf", libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings("insn_array", libbpfBpfMapTypeStr(34).?);
    try std.testing.expect(libbpfBpfMapTypeStr(99) == null);
}

test "attach type names keep the bounded heavy-helper surface reviewable" {
    try std.testing.expectEqualStrings("cgroup_inet_ingress", libbpfBpfAttachTypeStr(0).?);
    try std.testing.expectEqualStrings("xdp_devmap", libbpfBpfAttachTypeStr(33).?);
    try std.testing.expectEqualStrings("xdp", libbpfBpfAttachTypeStr(37).?);
    try std.testing.expect(libbpfBpfAttachTypeStr(99) == null);
}
