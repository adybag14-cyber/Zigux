const std = @import("std");

const type_names = @import("type_names.zig");

test "phase8 libbpf type-name helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(type_names, "libbpfBpfMapTypeStr"));
    try std.testing.expect(@hasDecl(type_names, "libbpfBpfAttachTypeStr"));
    try std.testing.expect(@hasDecl(type_names, "libbpfBpfLinkTypeStr"));
    try std.testing.expect(@hasDecl(type_names, "libbpfBpfProgTypeStr"));
    try std.testing.expect(@hasDecl(type_names, "formatLibbpfBpfMapType"));
    try std.testing.expect(@hasDecl(type_names, "formatLibbpfBpfAttachType"));
    try std.testing.expect(@hasDecl(type_names, "formatLibbpfBpfLinkType"));
    try std.testing.expect(@hasDecl(type_names, "formatLibbpfBpfProgType"));
}

test "phase8 libbpf type-name lookup outputs stay stable" {
    try std.testing.expectEqualStrings("ringbuf", type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expect(type_names.libbpfBpfMapTypeStr(35) == null);

    try std.testing.expectEqualStrings("perf_event", type_names.libbpfBpfAttachTypeStr(41).?);
    try std.testing.expect(type_names.libbpfBpfAttachTypeStr(59) == null);

    try std.testing.expectEqualStrings("sockmap", type_names.libbpfBpfLinkTypeStr(14).?);
    try std.testing.expect(type_names.libbpfBpfLinkTypeStr(15) == null);

    try std.testing.expectEqualStrings("netfilter", type_names.libbpfBpfProgTypeStr(32).?);
    try std.testing.expect(type_names.libbpfBpfProgTypeStr(33) == null);
}

test "phase8 libbpf type-name formatters keep known and unknown outputs stable" {
    var map_buffer: [64]u8 = undefined;
    var attach_buffer: [64]u8 = undefined;
    var link_buffer: [64]u8 = undefined;
    var prog_buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "ringbuf",
        try type_names.formatLibbpfBpfMapType(map_buffer[0..], 27),
    );
    try std.testing.expectEqualStrings(
        "unknown_map_type(35)",
        try type_names.formatLibbpfBpfMapType(map_buffer[0..], 35),
    );

    try std.testing.expectEqualStrings(
        "perf_event",
        try type_names.formatLibbpfBpfAttachType(attach_buffer[0..], 41),
    );
    try std.testing.expectEqualStrings(
        "unknown_attach_type(59)",
        try type_names.formatLibbpfBpfAttachType(attach_buffer[0..], 59),
    );

    try std.testing.expectEqualStrings(
        "sockmap",
        try type_names.formatLibbpfBpfLinkType(link_buffer[0..], 14),
    );
    try std.testing.expectEqualStrings(
        "unknown_link_type(15)",
        try type_names.formatLibbpfBpfLinkType(link_buffer[0..], 15),
    );

    try std.testing.expectEqualStrings(
        "netfilter",
        try type_names.formatLibbpfBpfProgType(prog_buffer[0..], 32),
    );
    try std.testing.expectEqualStrings(
        "unknown_prog_type(33)",
        try type_names.formatLibbpfBpfProgType(prog_buffer[0..], 33),
    );
}

test "phase8 libbpf type-name formatters still fail closed on short buffers" {
    var short_buffer: [8]u8 = undefined;

    try std.testing.expectError(
        error.NoSpaceLeft,
        type_names.formatLibbpfBpfAttachType(short_buffer[0..], 59),
    );
}
