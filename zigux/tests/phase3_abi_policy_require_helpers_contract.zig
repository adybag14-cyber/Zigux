const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");

fn policy(panic_mode: u8, allocator_mode: u8, unsafe_scope: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = panic_mode,
        .allocator_mode = allocator_mode,
        .unsafe_scope = unsafe_scope,
        .reserved = reserved,
    };
}

test "phase3 policy require helpers accept only the requested panic escalation" {
    const abort_policy = policy(abi.PANIC_ABORT, abi.ALLOC_ARENA, abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    const bug_policy = policy(abi.PANIC_BUG, abi.ALLOC_CALLER_PROVIDED, abi.UNSAFE_NONE, 0);
    const warn_policy = policy(abi.PANIC_WARN, abi.ALLOC_KERNEL_HEAP, abi.UNSAFE_VOLATILE_MMIO, 0);
    const reserved = policy(abi.PANIC_WARN, abi.ALLOC_ARENA, abi.UNSAFE_RAW_POINTER_BRIDGE, 1);

    try panic_policy.requireEscalation(.abort, .immediate_abort);
    try panic_policy.requireEscalationByte(abi.PANIC_BUG, .kernel_bug);
    try panic_policy.requireEscalationPolicyBytes(abi.PANIC_WARN, 0, .warning_only);
    try panic_policy.requireEscalationInteropPolicy(abort_policy, .immediate_abort);
    try panic_policy.requireEscalationInteropPolicy(bug_policy, .kernel_bug);
    try panic_policy.requireEscalationInteropPolicy(warn_policy, .warning_only);

    try std.testing.expectError(
        error.UnexpectedEscalation,
        panic_policy.requireEscalationInteropPolicy(warn_policy, .kernel_bug),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationInteropPolicy(reserved, .warning_only),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireEscalationByte(9, .warning_only),
    );
}

test "phase3 policy require helpers accept only the requested panic action" {
    const abort_policy = policy(abi.PANIC_ABORT, abi.ALLOC_KERNEL_HEAP, abi.UNSAFE_VOLATILE_MMIO, 0);
    const bug_policy = policy(abi.PANIC_BUG, abi.ALLOC_ARENA, abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    const warn_policy = policy(abi.PANIC_WARN, abi.ALLOC_CALLER_PROVIDED, abi.UNSAFE_NONE, 0);
    const reserved = policy(abi.PANIC_ABORT, abi.ALLOC_CALLER_PROVIDED, abi.UNSAFE_NONE, 1);

    try panic_policy.requireAction(.abort, .abort_now);
    try panic_policy.requireActionByte(abi.PANIC_BUG, .bug_check);
    try panic_policy.requireActionPolicyBytes(abi.PANIC_WARN, 0, .warn_and_return);
    try panic_policy.requireActionInteropPolicy(abort_policy, .abort_now);
    try panic_policy.requireActionInteropPolicy(bug_policy, .bug_check);
    try panic_policy.requireActionInteropPolicy(warn_policy, .warn_and_return);

    try std.testing.expectError(
        error.UnexpectedAction,
        panic_policy.requireActionInteropPolicy(bug_policy, .warn_and_return),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionInteropPolicy(reserved, .abort_now),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        panic_policy.requireActionByte(9, .bug_check),
    );
}

test "phase3 policy require helpers accept only the requested allocator init flow" {
    const caller_policy = policy(abi.PANIC_WARN, abi.ALLOC_CALLER_PROVIDED, abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    const heap_policy = policy(abi.PANIC_ABORT, abi.ALLOC_KERNEL_HEAP, abi.UNSAFE_NONE, 0);
    const arena_policy = policy(abi.PANIC_BUG, abi.ALLOC_ARENA, abi.UNSAFE_VOLATILE_MMIO, 0);
    const reserved = policy(abi.PANIC_BUG, abi.ALLOC_ARENA, abi.UNSAFE_VOLATILE_MMIO, 1);

    try allocator_policy.requireInitFlow(.caller_provided, .caller_prepared);
    try allocator_policy.requireInitFlowByte(abi.ALLOC_KERNEL_HEAP, .helper_owned);
    try allocator_policy.requireInitFlowPolicyBytes(abi.ALLOC_ARENA, 0, .helper_owned_with_reset);
    try allocator_policy.requireInitFlowInteropPolicy(caller_policy, .caller_prepared);
    try allocator_policy.requireInitFlowInteropPolicy(heap_policy, .helper_owned);
    try allocator_policy.requireInitFlowInteropPolicy(arena_policy, .helper_owned_with_reset);

    try std.testing.expectError(
        error.UnexpectedInitFlow,
        allocator_policy.requireInitFlowInteropPolicy(arena_policy, .helper_owned),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowInteropPolicy(reserved, .helper_owned_with_reset),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        allocator_policy.requireInitFlowByte(9, .caller_prepared),
    );
}

test "phase3 policy require helpers keep unrelated policy bytes out of scope" {
    const panic_focus = policy(abi.PANIC_WARN, 9, 9, 0);
    const allocator_focus = policy(9, abi.ALLOC_ARENA, 9, 0);

    try panic_policy.requireEscalationInteropPolicy(panic_focus, .warning_only);
    try panic_policy.requireActionInteropPolicy(panic_focus, .warn_and_return);
    try allocator_policy.requireInitFlowInteropPolicy(allocator_focus, .helper_owned_with_reset);

    try std.testing.expectError(
        error.UnexpectedEscalation,
        panic_policy.requireEscalationInteropPolicy(panic_focus, .kernel_bug),
    );
    try std.testing.expectError(
        error.UnexpectedInitFlow,
        allocator_policy.requireInitFlowInteropPolicy(allocator_focus, .helper_owned),
    );
}
