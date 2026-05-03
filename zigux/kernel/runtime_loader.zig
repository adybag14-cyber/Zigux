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
    atomic64,
    bitmap,
    kretprobe,
};

pub const Atomic64Payload = struct {
    counter_snapshot: i64,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
};

pub const AllocatorHandoff = struct {
    mode: abi.AllocatorMode,
    init_flow: allocator_policy.InitFlow,
    requires_explicit_caller: bool,
    permits_global_fallback: bool,
    initializes_owned_state: bool,
    requires_reset_on_init: bool,

    pub fn keepsInitFlowConsistent(self: AllocatorHandoff) bool {
        const expected = allocatorHandoffFor(self.mode);
        return self.init_flow == expected.init_flow and
            self.requires_explicit_caller == expected.requires_explicit_caller and
            self.permits_global_fallback == expected.permits_global_fallback and
            self.initializes_owned_state == expected.initializes_owned_state and
            self.requires_reset_on_init == expected.requires_reset_on_init;
    }
};

pub const BitmapPayload = struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
    nbits: u32,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
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
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    entry_timestamp_armed: bool,
};

pub const LoaderPayload = union(LoaderLane) {
    atomic64: Atomic64Payload,
    bitmap: BitmapPayload,
    kretprobe: KretprobePayload,
};

pub const RuntimeLoadRequest = struct {
    module_name: []const u8,
    command_name: ?[]const u8,
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

    pub fn isReleasedWithoutSubstrate(self: RuntimeLoadRequest) bool {
        return self.requires_runtime_substrate and self.handoff_stage == .released_without_substrate;
    }

    pub fn waitingOnRuntimeSubstrate(self: RuntimeLoadRequest) RuntimeLoadRequest {
        var waiting = self;
        waiting.handoff_stage = if (waiting.requires_runtime_substrate)
            .waiting_on_runtime_substrate
        else
            .prepared;
        return waiting;
    }

    pub fn releasedWithoutSubstrate(self: RuntimeLoadRequest) RuntimeLoadRequest {
        var released = self;
        released.handoff_stage = if (released.requires_runtime_substrate)
            .released_without_substrate
        else
            .prepared;
        return released;
    }

    pub fn keepsCommandNameExplicit(self: RuntimeLoadRequest) bool {
        return if (self.command_name) |command_name| command_name.len > 0 else true;
    }

    pub fn keepsInitExitContractExplicit(self: RuntimeLoadRequest) bool {
        return self.module_name.len > 0 and
            self.anchor.len > 0 and
            self.entry_symbol.len > 0 and
            self.exit_symbol.len > 0 and
            !std.mem.eql(u8, self.entry_symbol, self.exit_symbol);
    }

    pub fn keepsLaneIdentityExplicit(self: RuntimeLoadRequest) bool {
        return switch (self.payload) {
            .atomic64 => std.mem.eql(u8, self.module_name, "runtime_atomic64") and
                std.mem.eql(u8, self.anchor, "lib/atomic64_test.c"),
            .bitmap => std.mem.eql(u8, self.module_name, "runtime_bitmap") and
                std.mem.eql(u8, self.anchor, "lib/test_bitmap.c"),
            .kretprobe => std.mem.eql(u8, self.module_name, "runtime_kretprobe") and
                std.mem.eql(u8, self.anchor, "samples/kprobes/kretprobe_example.c"),
        };
    }

    pub fn keepsStagedInitExitNamingExplicit(self: RuntimeLoadRequest) bool {
        return std.mem.endsWith(u8, self.entry_symbol, "_init") and
            std.mem.endsWith(u8, self.exit_symbol, "_exit");
    }

    pub fn keepsStageConsistentWithRuntimeSubstrate(self: RuntimeLoadRequest) bool {
        return if (self.requires_runtime_substrate)
            self.handoff_stage == .waiting_on_runtime_substrate or
                self.handoff_stage == .released_without_substrate
        else
            self.handoff_stage == .prepared;
    }

    pub fn keepsAllocatorInitFlowConsistent(self: RuntimeLoadRequest) bool {
        return self.allocator_handoff.keepsInitFlowConsistent();
    }

    pub fn keepsSelftestHookConsistent(self: RuntimeLoadRequest) bool {
        const selftest_runs = switch (self.payload) {
            .atomic64 => |payload| payload.selftest_runs,
            .bitmap => |payload| payload.selftest_runs,
            .kretprobe => |payload| payload.selftest_runs,
        };
        return self.provides_selftest_hook or selftest_runs == 0;
    }

    pub fn keepsPreExecutionLifecycleBoundaryExplicit(self: RuntimeLoadRequest) bool {
        if (std.mem.eql(u8, self.entry_symbol, "module_init") or
            std.mem.eql(u8, self.exit_symbol, "module_exit"))
        {
            return false;
        }

        return switch (self.payload) {
            .atomic64, .bitmap => true,
            .kretprobe => |payload| payload.register_api.len > 0 and
                payload.unregister_api.len > 0 and
                !std.mem.eql(u8, payload.register_api, payload.unregister_api) and
                !std.mem.eql(u8, payload.register_api, "module_init") and
                !std.mem.eql(u8, payload.unregister_api, "module_exit") and
                !std.mem.eql(u8, payload.register_api, self.entry_symbol) and
                !std.mem.eql(u8, payload.unregister_api, self.exit_symbol),
        };
    }

    pub fn keepsLifecyclePayloadConsistent(self: RuntimeLoadRequest) bool {
        const counters_ordered = switch (self.payload) {
            .atomic64 => |payload| payload.init_runs >= 1 and
                payload.selftest_runs <= payload.init_runs and
                payload.exit_runs <= payload.init_runs,
            .bitmap => |payload| payload.init_runs >= 1 and
                payload.selftest_runs <= payload.init_runs and
                payload.exit_runs <= payload.init_runs,
            .kretprobe => |payload| payload.init_runs >= 1 and
                payload.selftest_runs <= payload.init_runs and
                payload.exit_runs <= payload.init_runs,
        };
        if (!counters_ordered) return false;

        return switch (self.handoff_stage) {
            .waiting_on_runtime_substrate, .released_without_substrate => switch (self.payload) {
                .atomic64 => |payload| payload.exit_runs == 0,
                .bitmap => |payload| payload.exit_runs == 0,
                .kretprobe => |payload| payload.exit_runs == 0,
            },
            .idle, .prepared => true,
        };
    }

    pub fn keepsSharedHandoffContractExplicit(self: RuntimeLoadRequest) bool {
        return self.keepsCommandNameExplicit() and
            self.keepsInitExitContractExplicit() and
            self.keepsLaneIdentityExplicit() and
            self.keepsStagedInitExitNamingExplicit() and
            self.keepsStageConsistentWithRuntimeSubstrate() and
            self.keepsAllocatorInitFlowConsistent() and
            self.keepsSelftestHookConsistent() and
            self.keepsPreExecutionLifecycleBoundaryExplicit() and
            self.keepsLifecyclePayloadConsistent();
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
    try std.testing.expect(handoff.keepsInitFlowConsistent());
}

test "runtime loader allocator handoff stays internally consistent across all allocator modes" {
    const caller = allocatorHandoffFor(.caller_provided);
    try std.testing.expectEqual(allocator_policy.InitFlow.caller_prepared, caller.init_flow);
    try std.testing.expect(caller.requires_explicit_caller);
    try std.testing.expect(!caller.permits_global_fallback);
    try std.testing.expect(!caller.initializes_owned_state);
    try std.testing.expect(!caller.requires_reset_on_init);
    try std.testing.expect(caller.keepsInitFlowConsistent());

    const heap = allocatorHandoffFor(.kernel_heap);
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned, heap.init_flow);
    try std.testing.expect(!heap.requires_explicit_caller);
    try std.testing.expect(heap.permits_global_fallback);
    try std.testing.expect(heap.initializes_owned_state);
    try std.testing.expect(!heap.requires_reset_on_init);
    try std.testing.expect(heap.keepsInitFlowConsistent());

    const arena = allocatorHandoffFor(.arena);
    try std.testing.expectEqual(allocator_policy.InitFlow.helper_owned_with_reset, arena.init_flow);
    try std.testing.expect(!arena.requires_explicit_caller);
    try std.testing.expect(arena.permits_global_fallback);
    try std.testing.expect(arena.initializes_owned_state);
    try std.testing.expect(arena.requires_reset_on_init);
    try std.testing.expect(arena.keepsInitFlowConsistent());
}

test "runtime loader request keeps bitmap handoff state explicit" {
    const request = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
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
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };

    try std.testing.expectEqual(LoaderLane.bitmap, request.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(request.keepsInitExitContractExplicit());
    try std.testing.expect(request.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(request.keepsSelftestHookConsistent());
    try std.testing.expect(request.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(request.keepsLifecyclePayloadConsistent());
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(@as(u32, 4), request.payload.bitmap.weight);
    try std.testing.expectEqual(@as(usize, 1), request.payload.bitmap.selftest_runs);

    const waiting = request.waitingOnRuntimeSubstrate();
    try std.testing.expectEqual(LoaderLane.bitmap, waiting.lane());
    try std.testing.expect(waiting.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!waiting.isReleasedWithoutSubstrate());
    try std.testing.expect(waiting.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(waiting.keepsSelftestHookConsistent());
    try std.testing.expect(waiting.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expectEqual(@as(u32, 4), waiting.payload.bitmap.weight);

    const released = request.releasedWithoutSubstrate();
    try std.testing.expectEqual(LoaderLane.bitmap, released.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), released.command_name);
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.keepsInitExitContractExplicit());
    try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(released.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(released.keepsSelftestHookConsistent());
    try std.testing.expect(released.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(released.keepsLifecyclePayloadConsistent());
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(@as(u32, 4), released.payload.bitmap.weight);
}

test "runtime loader request keeps atomic64 handoff state explicit" {
    const request = RuntimeLoadRequest{
        .module_name = "runtime_atomic64",
        .command_name = null,
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .atomic64 = .{
                .counter_snapshot = 0x1111_2222_3333_4444,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };

    try std.testing.expectEqual(LoaderLane.atomic64, request.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(request.keepsInitExitContractExplicit());
    try std.testing.expect(request.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(request.keepsSelftestHookConsistent());
    try std.testing.expect(request.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(request.keepsLifecyclePayloadConsistent());
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(@as(i64, 0x1111_2222_3333_4444), request.payload.atomic64.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), request.payload.atomic64.selftest_runs);

    const waiting = request.waitingOnRuntimeSubstrate();
    try std.testing.expectEqual(LoaderLane.atomic64, waiting.lane());
    try std.testing.expect(waiting.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!waiting.isReleasedWithoutSubstrate());
    try std.testing.expect(waiting.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(waiting.keepsSelftestHookConsistent());
    try std.testing.expect(waiting.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expectEqual(@as(i64, 0x1111_2222_3333_4444), waiting.payload.atomic64.counter_snapshot);

    const released = request.releasedWithoutSubstrate();
    try std.testing.expectEqual(LoaderLane.atomic64, released.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), released.command_name);
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.keepsInitExitContractExplicit());
    try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(released.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(released.keepsSelftestHookConsistent());
    try std.testing.expect(released.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(released.keepsLifecyclePayloadConsistent());
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(@as(i64, 0x1111_2222_3333_4444), released.payload.atomic64.counter_snapshot);
}

test "runtime loader request keeps kretprobe handoff state explicit" {
    const request = RuntimeLoadRequest{
        .module_name = "runtime_kretprobe",
        .command_name = null,
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
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
                .entry_timestamp_armed = false,
            },
        },
    };

    try std.testing.expectEqual(LoaderLane.kretprobe, request.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);
    try std.testing.expectEqualStrings("register_kretprobe", request.payload.kretprobe.register_api);
    try std.testing.expectEqual(@as(usize, 1), request.payload.kretprobe.nmissed);
    try std.testing.expect(request.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(request.keepsCommandNameExplicit());
    try std.testing.expect(request.keepsInitExitContractExplicit());
    try std.testing.expect(request.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(request.keepsSelftestHookConsistent());
    try std.testing.expect(request.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(request.keepsLifecyclePayloadConsistent());
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());

    const waiting = request.waitingOnRuntimeSubstrate();
    try std.testing.expectEqual(LoaderLane.kretprobe, waiting.lane());
    try std.testing.expect(waiting.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!waiting.isReleasedWithoutSubstrate());
    try std.testing.expect(waiting.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(waiting.keepsSelftestHookConsistent());
    try std.testing.expect(waiting.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expectEqualStrings("register_kretprobe", waiting.payload.kretprobe.register_api);

    const released = request.releasedWithoutSubstrate();
    try std.testing.expectEqual(LoaderLane.kretprobe, released.lane());
    try std.testing.expectEqual(@as(?[]const u8, null), released.command_name);
    try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(released.isReleasedWithoutSubstrate());
    try std.testing.expect(released.keepsCommandNameExplicit());
    try std.testing.expect(released.keepsInitExitContractExplicit());
    try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(released.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(released.keepsSelftestHookConsistent());
    try std.testing.expect(released.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(released.keepsLifecyclePayloadConsistent());
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqualStrings("register_kretprobe", released.payload.kretprobe.register_api);
}

test "runtime loader request preserves explicit command names across runtime-lane transitions" {
    const requests = [_]RuntimeLoadRequest{
        .{
            .module_name = "runtime_atomic64",
            .command_name = "perf-runtime-atomic64",
            .anchor = "lib/atomic64_test.c",
            .entry_symbol = "zigux_runtime_atomic64_init",
            .exit_symbol = "zigux_runtime_atomic64_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .handoff_stage = .prepared,
            .allocator_handoff = allocatorHandoffFor(.kernel_heap),
            .payload = .{
                .atomic64 = .{
                    .counter_snapshot = 99,
                    .init_runs = 1,
                    .selftest_runs = 1,
                    .exit_runs = 0,
                },
            },
        },
        .{
            .module_name = "runtime_bitmap",
            .command_name = "perf-runtime-bitmap",
            .anchor = "lib/test_bitmap.c",
            .entry_symbol = "zigux_runtime_bitmap_init",
            .exit_symbol = "zigux_runtime_bitmap_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .handoff_stage = .prepared,
            .allocator_handoff = allocatorHandoffFor(.kernel_heap),
            .payload = .{
                .bitmap = .{
                    .first_set = 0,
                    .first_zero = 1,
                    .weight = 4,
                    .nbits = 128,
                    .init_runs = 1,
                    .selftest_runs = 1,
                    .exit_runs = 0,
                },
            },
        },
        .{
            .module_name = "runtime_kretprobe",
            .command_name = "perf-runtime-kretprobe",
            .anchor = "samples/kprobes/kretprobe_example.c",
            .entry_symbol = "zigux_runtime_kretprobe_init",
            .exit_symbol = "zigux_runtime_kretprobe_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .handoff_stage = .prepared,
            .allocator_handoff = allocatorHandoffFor(.kernel_heap),
            .payload = .{
                .kretprobe = .{
                    .register_api = "register_kretprobe",
                    .unregister_api = "unregister_kretprobe",
                    .symbol_name = "do_sys_openat2",
                    .maxactive = 20,
                    .private_data_bytes = 24,
                    .active_instances = 0,
                    .skipped_kernel_threads = 1,
                    .nmissed = 1,
                    .last_retval = 42,
                    .last_duration_ns = 75,
                    .init_runs = 1,
                    .selftest_runs = 1,
                    .exit_runs = 0,
                    .entry_timestamp_armed = false,
                },
            },
        },
    };

    for (requests) |request| {
        try std.testing.expect(request.command_name != null);
        try std.testing.expect(request.keepsCommandNameExplicit());
        try std.testing.expect(request.keepsInitExitContractExplicit());
        try std.testing.expect(request.keepsSelftestHookConsistent());
        try std.testing.expect(request.keepsPreExecutionLifecycleBoundaryExplicit());
        try std.testing.expect(!request.isWaitingOnRuntimeSubstrate());
        try std.testing.expect(!request.isReleasedWithoutSubstrate());
        try std.testing.expect(!request.keepsStageConsistentWithRuntimeSubstrate());
        try std.testing.expect(request.keepsLifecyclePayloadConsistent());
        try std.testing.expect(!request.keepsSharedHandoffContractExplicit());

        const waiting = request.waitingOnRuntimeSubstrate();
        try std.testing.expect(waiting.command_name != null);
        try std.testing.expectEqualStrings(request.command_name.?, waiting.command_name.?);
        try std.testing.expectEqual(request.lane(), waiting.lane());
        try std.testing.expect(waiting.isWaitingOnRuntimeSubstrate());
        try std.testing.expect(!waiting.isReleasedWithoutSubstrate());
        try std.testing.expect(waiting.keepsCommandNameExplicit());
        try std.testing.expect(waiting.keepsInitExitContractExplicit());
        try std.testing.expect(waiting.keepsStageConsistentWithRuntimeSubstrate());
        try std.testing.expect(waiting.keepsSelftestHookConsistent());
        try std.testing.expect(waiting.keepsPreExecutionLifecycleBoundaryExplicit());
        try std.testing.expect(waiting.keepsLifecyclePayloadConsistent());
        try std.testing.expect(waiting.keepsSharedHandoffContractExplicit());

        const released = waiting.releasedWithoutSubstrate();
        try std.testing.expect(released.command_name != null);
        try std.testing.expectEqualStrings(waiting.command_name.?, released.command_name.?);
        try std.testing.expectEqual(waiting.lane(), released.lane());
        try std.testing.expect(!released.isWaitingOnRuntimeSubstrate());
        try std.testing.expect(released.isReleasedWithoutSubstrate());
        try std.testing.expect(released.keepsCommandNameExplicit());
        try std.testing.expect(released.keepsInitExitContractExplicit());
        try std.testing.expect(released.keepsStageConsistentWithRuntimeSubstrate());
        try std.testing.expect(released.keepsSelftestHookConsistent());
        try std.testing.expect(released.keepsPreExecutionLifecycleBoundaryExplicit());
        try std.testing.expect(released.keepsLifecyclePayloadConsistent());
        try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    }
}

test "runtime loader request rejects ambiguous staged init-exit naming" {
    const wrong_entry_suffix = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_start",
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
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(wrong_entry_suffix.keepsInitExitContractExplicit());
    try std.testing.expect(!wrong_entry_suffix.keepsStagedInitExitNamingExplicit());
    try std.testing.expect(wrong_entry_suffix.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(!wrong_entry_suffix.keepsSharedHandoffContractExplicit());

    const swapped_suffixes = RuntimeLoadRequest{
        .module_name = "runtime_kretprobe",
        .command_name = null,
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_exit",
        .exit_symbol = "zigux_runtime_kretprobe_init",
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
                .private_data_bytes = 24,
                .active_instances = 0,
                .skipped_kernel_threads = 0,
                .nmissed = 0,
                .last_retval = 0,
                .last_duration_ns = 0,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
                .entry_timestamp_armed = false,
            },
        },
    };
    try std.testing.expect(swapped_suffixes.keepsInitExitContractExplicit());
    try std.testing.expect(!swapped_suffixes.keepsStagedInitExitNamingExplicit());
    try std.testing.expect(swapped_suffixes.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(!swapped_suffixes.keepsSharedHandoffContractExplicit());
}

test "runtime loader request rejects implicit init-exit and live lifecycle handoff contracts" {
    const missing_exit = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "",
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
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 2,
            },
        },
    };
    try std.testing.expect(!missing_exit.keepsInitExitContractExplicit());
    try std.testing.expect(missing_exit.keepsSelftestHookConsistent());
    try std.testing.expect(missing_exit.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(missing_exit.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(!missing_exit.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!missing_exit.keepsSharedHandoffContractExplicit());

    const wrong_stage = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .prepared,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .bitmap = .{
                .first_set = 0,
                .first_zero = 1,
                .weight = 4,
                .nbits = 128,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(wrong_stage.keepsInitExitContractExplicit());
    try std.testing.expect(wrong_stage.keepsSelftestHookConsistent());
    try std.testing.expect(wrong_stage.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(!wrong_stage.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(wrong_stage.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!wrong_stage.keepsSharedHandoffContractExplicit());

    const empty_command_name = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = "",
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
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(!empty_command_name.keepsCommandNameExplicit());
    try std.testing.expect(empty_command_name.keepsInitExitContractExplicit());
    try std.testing.expect(empty_command_name.keepsSelftestHookConsistent());
    try std.testing.expect(empty_command_name.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(empty_command_name.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!empty_command_name.keepsSharedHandoffContractExplicit());

    const missing_selftest_hook = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .bitmap = .{
                .first_set = 0,
                .first_zero = 1,
                .weight = 4,
                .nbits = 128,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(missing_selftest_hook.keepsInitExitContractExplicit());
    try std.testing.expect(!missing_selftest_hook.keepsSelftestHookConsistent());
    try std.testing.expect(missing_selftest_hook.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(missing_selftest_hook.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!missing_selftest_hook.keepsSharedHandoffContractExplicit());

    const live_initcall_symbol = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "module_init",
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
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(live_initcall_symbol.keepsInitExitContractExplicit());
    try std.testing.expect(live_initcall_symbol.keepsSelftestHookConsistent());
    try std.testing.expect(!live_initcall_symbol.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(live_initcall_symbol.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(live_initcall_symbol.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!live_initcall_symbol.keepsSharedHandoffContractExplicit());

    const live_registration_label = RuntimeLoadRequest{
        .module_name = "runtime_kretprobe",
        .command_name = null,
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .kretprobe = .{
                .register_api = "zigux_runtime_kretprobe_init",
                .unregister_api = "unregister_kretprobe",
                .symbol_name = "do_sys_openat2",
                .maxactive = 20,
                .private_data_bytes = 24,
                .active_instances = 0,
                .skipped_kernel_threads = 0,
                .nmissed = 0,
                .last_retval = 0,
                .last_duration_ns = 0,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
                .entry_timestamp_armed = false,
            },
        },
    };
    try std.testing.expect(live_registration_label.keepsInitExitContractExplicit());
    try std.testing.expect(live_registration_label.keepsSelftestHookConsistent());
    try std.testing.expect(!live_registration_label.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(live_registration_label.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(live_registration_label.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!live_registration_label.keepsSharedHandoffContractExplicit());

    const released_with_exit_counter = RuntimeLoadRequest{
        .module_name = "runtime_kretprobe",
        .command_name = null,
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .released_without_substrate,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .kretprobe = .{
                .register_api = "register_kretprobe",
                .unregister_api = "unregister_kretprobe",
                .symbol_name = "do_sys_openat2",
                .maxactive = 20,
                .private_data_bytes = 24,
                .active_instances = 0,
                .skipped_kernel_threads = 0,
                .nmissed = 0,
                .last_retval = 0,
                .last_duration_ns = 0,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 1,
                .entry_timestamp_armed = false,
            },
        },
    };
    try std.testing.expect(released_with_exit_counter.keepsInitExitContractExplicit());
    try std.testing.expect(released_with_exit_counter.keepsSelftestHookConsistent());
    try std.testing.expect(released_with_exit_counter.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(released_with_exit_counter.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(!released_with_exit_counter.keepsLifecyclePayloadConsistent());
    try std.testing.expect(!released_with_exit_counter.keepsSharedHandoffContractExplicit());

    const no_substrate = (RuntimeLoadRequest{
        .module_name = "runtime_atomic64",
        .command_name = null,
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .requires_runtime_substrate = false,
        .provides_selftest_hook = true,
        .handoff_stage = .idle,
        .allocator_handoff = allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .atomic64 = .{
                .counter_snapshot = 1,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
            },
        },
    }).waitingOnRuntimeSubstrate();
    try std.testing.expect(!no_substrate.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!no_substrate.isReleasedWithoutSubstrate());
    try std.testing.expectEqual(LoaderStage.prepared, no_substrate.handoff_stage);
    try std.testing.expect(no_substrate.keepsSelftestHookConsistent());
    try std.testing.expect(no_substrate.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(no_substrate.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(no_substrate.keepsSharedHandoffContractExplicit());

    const no_substrate_released = no_substrate.releasedWithoutSubstrate();
    try std.testing.expect(!no_substrate_released.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!no_substrate_released.isReleasedWithoutSubstrate());
    try std.testing.expectEqual(LoaderStage.prepared, no_substrate_released.handoff_stage);
    try std.testing.expect(no_substrate_released.keepsSelftestHookConsistent());
    try std.testing.expect(no_substrate_released.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(no_substrate_released.keepsStageConsistentWithRuntimeSubstrate());
    try std.testing.expect(no_substrate_released.keepsSharedHandoffContractExplicit());
}

test "runtime loader request rejects cross-lane identity drift" {
    const wrong_bitmap_anchor = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/atomic64_test.c",
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
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(wrong_bitmap_anchor.keepsInitExitContractExplicit());
    try std.testing.expect(!wrong_bitmap_anchor.keepsLaneIdentityExplicit());
    try std.testing.expect(wrong_bitmap_anchor.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(!wrong_bitmap_anchor.keepsSharedHandoffContractExplicit());

    const wrong_kretprobe_module = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
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
                .private_data_bytes = 24,
                .active_instances = 0,
                .skipped_kernel_threads = 0,
                .nmissed = 0,
                .last_retval = 0,
                .last_duration_ns = 0,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
                .entry_timestamp_armed = false,
            },
        },
    };
    try std.testing.expect(wrong_kretprobe_module.keepsInitExitContractExplicit());
    try std.testing.expect(!wrong_kretprobe_module.keepsLaneIdentityExplicit());
    try std.testing.expect(wrong_kretprobe_module.keepsPreExecutionLifecycleBoundaryExplicit());
    try std.testing.expect(!wrong_kretprobe_module.keepsSharedHandoffContractExplicit());
}
