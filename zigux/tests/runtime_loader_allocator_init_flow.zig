const std = @import("std");
const runtime_loader = @import("runtime_loader");

const RuntimeLoadRequest = runtime_loader.RuntimeLoadRequest;

test "runtime loader request rejects allocator init-flow drift" {
    var caller_request = RuntimeLoadRequest{
        .module_name = "runtime_atomic64",
        .command_name = null,
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = runtime_loader.allocatorHandoffFor(.caller_provided),
        .payload = .{
            .atomic64 = .{
                .counter_snapshot = 7,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(caller_request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(caller_request.keepsSharedHandoffContractExplicit());

    caller_request.allocator_handoff.requires_explicit_caller = false;
    try std.testing.expect(!caller_request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(!caller_request.keepsSharedHandoffContractExplicit());

    var arena_request = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = runtime_loader.allocatorHandoffFor(.arena),
        .payload = .{
            .bitmap = .{
                .first_set = 0,
                .first_zero = 1,
                .weight = 4,
                .nbits = 64,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(arena_request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(arena_request.keepsSharedHandoffContractExplicit());

    arena_request.allocator_handoff.requires_reset_on_init = false;
    try std.testing.expect(!arena_request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(!arena_request.keepsSharedHandoffContractExplicit());

    var heap_request = RuntimeLoadRequest{
        .module_name = "runtime_bitmap",
        .command_name = null,
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .handoff_stage = .waiting_on_runtime_substrate,
        .allocator_handoff = runtime_loader.allocatorHandoffFor(.kernel_heap),
        .payload = .{
            .bitmap = .{
                .first_set = 0,
                .first_zero = 1,
                .weight = 4,
                .nbits = 64,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
    try std.testing.expect(heap_request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(heap_request.keepsSharedHandoffContractExplicit());

    heap_request.allocator_handoff.init_flow = .caller_prepared;
    try std.testing.expect(!heap_request.keepsAllocatorInitFlowConsistent());
    try std.testing.expect(!heap_request.keepsSharedHandoffContractExplicit());
}
