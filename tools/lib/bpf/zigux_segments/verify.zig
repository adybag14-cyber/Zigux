const std = @import("std");

const file_path_handle_bridge = @import("file_path_handle_bridge.zig");
const logging = @import("logging.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const pin_path = @import("pin_path.zig");
const type_names = @import("type_names.zig");

fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {
    try std.testing.expect(@hasDecl(Module, decl_name));
}

test "materialized tools/lib/bpf Zigux segments compile together and keep their focused tests live" {
    std.testing.refAllDecls(file_path_handle_bridge);
    std.testing.refAllDecls(logging);
    std.testing.refAllDecls(online_cpu_routing);
    std.testing.refAllDecls(perf_buffer_poll);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(type_names);
}

test "materialized tools/lib/bpf Zigux segments keep their landed bounded entrypoints explicit" {
    try expectHasDecl(logging, "parseLogLevelSetting");
    try expectHasDecl(logging, "shouldLog");
    try expectHasDecl(logging, "shouldLogWithEnv");
    try expectHasDecl(logging, "formatUnrecognizedLogLevel");
    try expectHasDecl(logging, "libbpfMajorVersion");
    try expectHasDecl(logging, "libbpfMinorVersion");
    try expectHasDecl(logging, "libbpfVersionString");
    try expectHasDecl(logging, "libbpfErrorMessage");
    try expectHasDecl(logging, "formatLibbpfError");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndex");
    try expectHasDecl(perf_buffer_poll, "summarizeReadyBufferAttemptLookup");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptLookup");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndexReturn");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "resolvePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferFdLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdAtIndex");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFd");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdLookupReturn");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdLookupReturnAtIndex");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferWindowLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSizeAtIndex");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSize");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturn");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturnAtIndex");
    try expectHasDecl(pin_path, "pathnameConcat");
    try expectHasDecl(pin_path, "sanitizePinPath");
    try expectHasDecl(pin_path, "validatePinName");
    try expectHasDecl(pin_path, "validatePinRootPath");
    try expectHasDecl(pin_path, "buildMapPinPath");
    try expectHasDecl(pin_path, "buildValidatedMapPinPath");
    try expectHasDecl(pin_path, "buildSanitizedMapPinPath");
    try expectHasDecl(pin_path, "buildValidatedSanitizedMapPinPath");
    try expectHasDecl(type_names, "libbpfBpfAttachTypeStr");
    try expectHasDecl(type_names, "libbpfBpfMapTypeStr");
    try expectHasDecl(type_names, "libbpfBpfLinkTypeStr");
    try expectHasDecl(type_names, "libbpfBpfProgTypeStr");
    try expectHasDecl(type_names, "formatLibbpfBpfAttachType");
    try expectHasDecl(type_names, "formatLibbpfBpfMapType");
    try expectHasDecl(type_names, "formatLibbpfBpfLinkType");
    try expectHasDecl(type_names, "formatLibbpfBpfProgType");
}

test "materialized tools/lib/bpf bridge and routing helpers keep their landed entrypoints explicit" {
    try expectHasDecl(file_path_handle_bridge, "buildProcFdinfoPath");
    try expectHasDecl(file_path_handle_bridge, "parseFdinfoLine");
    try expectHasDecl(file_path_handle_bridge, "applyFdinfoMapInfoLine");
    try expectHasDecl(file_path_handle_bridge, "parseFdinfoMapInfo");
    try expectHasDecl(file_path_handle_bridge, "summarizeFdinfoMapInfo");
    try expectHasDecl(file_path_handle_bridge, "mapReuseObservationFromFdinfo");
    try expectHasDecl(file_path_handle_bridge, "resolveReusedMapName");
    try expectHasDecl(file_path_handle_bridge, "normalizeObservedReuseMapFlags");
    try expectHasDecl(file_path_handle_bridge, "summarizeMapReuseCompatibility");
    try expectHasDecl(file_path_handle_bridge, "isMapReuseCompatible");
    try expectHasDecl(file_path_handle_bridge, "resolveReusePinnedMapAttempt");
    try expectHasDecl(file_path_handle_bridge, "planTokenPreparation");
    try expectHasDecl(online_cpu_routing, "advanceOnlineCpuCursor");
    try expectHasDecl(online_cpu_routing, "summarizeNextOnlineCpuRoute");
    try expectHasDecl(online_cpu_routing, "summarizeOnlineCpuRouting");
}

test "materialized tools/lib/bpf Zigux segments keep stable type-name formatter outputs explicit" {
    var map_buffer: [32]u8 = undefined;
    var attach_buffer: [40]u8 = undefined;
    var link_buffer: [32]u8 = undefined;
    var prog_buffer: [32]u8 = undefined;

    try std.testing.expectEqualStrings("ringbuf", try type_names.formatLibbpfBpfMapType(map_buffer[0..], 27));
    try std.testing.expectEqualStrings("unknown_map_type(99)", try type_names.formatLibbpfBpfMapType(map_buffer[0..], 99));

    try std.testing.expectEqualStrings("perf_event", try type_names.formatLibbpfBpfAttachType(attach_buffer[0..], 41));
    try std.testing.expectEqualStrings("unknown_attach_type(88)", try type_names.formatLibbpfBpfAttachType(attach_buffer[0..], 88));

    try std.testing.expectEqualStrings("sockmap", try type_names.formatLibbpfBpfLinkType(link_buffer[0..], 14));
    try std.testing.expectEqualStrings("unknown_link_type(42)", try type_names.formatLibbpfBpfLinkType(link_buffer[0..], 42));

    try std.testing.expectEqualStrings("netfilter", try type_names.formatLibbpfBpfProgType(prog_buffer[0..], 32));
    try std.testing.expectEqualStrings("unknown_prog_type(77)", try type_names.formatLibbpfBpfProgType(prog_buffer[0..], 77));
}
