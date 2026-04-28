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
        return self.handoff_stage == .released_without_substrate;
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
        released.handoff_stage = .released_without_substrate;
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

    pub fn keepsSharedHandoffContractExplicit(self: RuntimeLoadRequest) bool {
        return self.keepsCommandNameExplicit() and
            self.keepsInitExitContractExplicit() and
            self.keepsStageConsistentWithRuntimeSubstrate() and
            self.keepsAllocatorInitFlowConsistent();
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
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(@as(u32, 4), request.payload.bitmap.weight);

    const waiting = request.waitingOnRuntimeSubstrate();
    try std.testing.expectEqual(LoaderLane.bitmap, waiting.lane());
    try std.testing.expect(waiting.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!waiting.isReleasedWithoutSubstrate());
    try std.testing.expect(waiting.keepsStageConsistentWithRuntimeSubstrate());
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
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqual(@as(u32, 4), released.payload.bitmap.weight);
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
                .selftest_runs = 1,
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
    try std.testing.expect(request.keepsSharedHandoffContractExplicit());

    const waiting = request.waitingOnRuntimeSubstrate();
    try std.testing.expectEqual(LoaderLane.kretprobe, waiting.lane());
    try std.testing.expect(waiting.isWaitingOnRuntimeSubstrate());
    try std.testing.expect(!waiting.isReleasedWithoutSubstrate());
    try std.testing.expect(waiting.keepsStageConsistentWithRuntimeSubstrate());
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
    try std.testing.expect(released.keepsSharedHandoffContractExplicit());
    try std.testing.expectEqualStrings("register_kretprobe", released.payload.kretprobe.register_api);
}

test "runtime loader request rejects implicit init-exit and stage handoff contracts" {
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
            },
        },
    };
    try std.testing.expect(!missing_exit.keepsInitExitContractExplicit());
    try std.testing.expect(missing_exit.keepsStageConsistentWithRuntimeSubstrate());
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
            },
        },
    };
    try std.testing.expect(wrong_stage.keepsInitExitContractExplicit());
    try std.testing.expect(!wrong_stage.keepsStageConsistentWithRuntimeSubstrate());
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
            },
        },
    };
    try std.testing.expect(!empty_command_name.keepsCommandNameExplicit());
    try std.testing.expect(empty_command_name.keepsInitExitContractExplicit());
    try std.testing.expect(!empty_command_name.keepsSharedHandoffContractExplicit());

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
            .bitmap = .{
                .first_set = 0,
                .first_zero = 1,
                .weight = 1,
                .nbits = 64,
            },
        },
    }).waitingOnRuntimeSubstrate();
    try std.testing.expect(!no_substrate.isWaitingOnRuntimeSubstrate());
    try std.testing.expectEqual(LoaderStage.prepared, no_substrate.handoff_stage);
    try std.testing.expect(no_substrate.keepsStageConsistentWithRuntimeSubstrate());
}
