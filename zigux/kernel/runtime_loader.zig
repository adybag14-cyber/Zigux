const std = @import("std");
const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");

pub const LoaderStage = enum(u8) {
    idle,
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const LoaderLane = enum(u8) {
    bitmap,
    kretprobe,
};

pub const AllocatorHandoff = struct {
    mode: abi.AllocatorMode,
    init_flow: allocator_policy.InitFlow,
    requires_explicit_caller: bool,
    permits_global_fallback: bool,
    initializes_owned_state: bool,
    requires_reset_on_init: bool,
};

pub const BitmapPayload = struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
    nbits: u32,
};

pub const KretprobePayload = struct {
    register_api: []const u8,
    unregister_api: []const u8,
    symbol_name: []const u8,
    maxactive: usize,
    private_data_bytes: usize,
    active_instances: usize,
    skipped_kernel_threads: usize,
    nmissed: usize,
    last_retval: usize,
    last_duration_ns: i64,
    selftest_runs: usize,
    entry_timestamp_armed: bool,
};

pub const LoaderPayload = union(LoaderLane) {
    bitmap: BitmapPayload,
    kretprobe: KretprobePayload,
};

pub const RuntimeLoadRequest = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: LoaderStage,
    allocator_handoff: AllocatorHandoff,
    payload: LoaderPayload,

    pub fn lane(self: RuntimeLoadRequest) LoaderLane {
        return std.meta.activeTag(self.payload);
    }

    pub fn isWaitingOnRuntimeSubstrate(self: RuntimeLoadRequest) bool {
        return self.requires_runtime_substrate and self.handoff_stage == .waiting_on_runtime_substrate;
    }
};

pub fn allocatorHandoffFor(mode: abi.AllocatorMode) AllocatorHandoff {
    return .{
        .mode = mode,
        .init_flow = allocator_policy.initFlowFor(mode),
        .requires_explicit_caller = allocator_policy.requiresExplicitCaller(mode),
        .permits_global_fallback = allocator_policy.permitsGlobalFallback(mode),
        .initializes_owned_state = allocator_policy.initializesOwnedState(mode),
        .requires_reset_on_init = allocator_policy.requiresResetOnInit(mode),
    };
}

test "runtime loader allocator handoff keeps policy fields machine-checkable" {
    const handoff = allocatorHandoffFor(.kernel_heap);

    try std.testing.expectEqual(abi.AllocatorMode.kernel_heap, handoff.mode);
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned, handoff.init_flow);
    try std.testing.expect(!handoff.requires_explicit_caller);
    try std.testing.expect(handoff.permits_global_fallback);
    try std.testing.expect(handoff.initializes_owned_state);
    try std.testing.expect(!handoff.requires_reset_on_init);
}

test "runtime loader request keeps bitmap handoff state explicit" {
    const request = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .bitmap = .{
                .first_set = 0,
                .first_zero = 1,
                .weight = 4,
                .nbits = 128,
            },
        },
    };

    try std.testing.expectEqual(LoaderLane.bitmap, request.lane());
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expectEqual(@as(u32, 4), request.payload.bitmap.weight);
}

test "runtime loader request keeps kretprobe handoff state explicit" {
    const request = RuntimeLoadRequest{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .kretprobe = .{
                .register_api = "register_kretprobe",
                .unregister_api = "unregister_kretprobe",
                .symbol_name = "do_sys_openat2",
                .maxactive = 20,
                .private_data_bytes = 8,
                .active_instances = 0,
                .skipped_kernel_threads = 1,
                .nmissed = 1,
                .last_retval = 42,
                .last_duration_ns = 75,
                .selftest_runs = 1,
                .entry_timestamp_armed = false,
            },
        },
    };

    try std.testing.expectEqual(LoaderLane.kretprobe, request.lane());
    try std.testing.expectEqualStrings("register_kretprobe", request.payload.kretprobe.register_api);
    try std.testing.expectEqual(@as(usize, 1), request.payload.kretprobe.nmissed);
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
}
