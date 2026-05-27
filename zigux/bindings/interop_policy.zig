const std = @import("std");
const abi = @import("abi_bindings");

pub const Policy = abi.InteropPolicy;
pub const PanicMode = abi.PanicMode;
pub const AllocatorMode = abi.AllocatorMode;
pub const UnsafeScope = abi.UnsafeScope;

pub const OwnershipClass = enum(u8) {
    borrowed = 0,
    kernel_owned = 1,
    arena_owned = 2,
};

pub const UnsafeAuditClass = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub const policy_size: usize = abi.interop_policy_size;
pub const policy_align: usize = abi.interop_policy_align;
pub const panic_mode_offset: usize = abi.interop_policy_panic_mode_offset;
pub const allocator_mode_offset: usize = abi.interop_policy_allocator_mode_offset;
pub const unsafe_scope_offset: usize = abi.interop_policy_unsafe_scope_offset;
pub const reserved_offset: usize = abi.interop_policy_reserved_offset;

pub fn default() Policy {
    return abi.defaultInteropPolicy();
}

pub fn reservedClear(policy: Policy) bool {
    return abi.interopPolicyReservedClear(policy);
}

pub fn panicModeFromByte(mode: u8) ?PanicMode {
    return abi.panicModeFromByte(mode);
}

pub fn allocatorModeFromByte(mode: u8) ?AllocatorMode {
    return abi.allocatorModeFromByte(mode);
}

pub fn unsafeScopeFromByte(scope: u8) ?UnsafeScope {
    return abi.unsafeScopeFromByte(scope);
}

pub fn panicModeFromPolicy(policy: Policy) ?PanicMode {
    return abi.panicModeFromInteropPolicy(policy);
}

pub fn allocatorModeFromPolicy(policy: Policy) ?AllocatorMode {
    return abi.allocatorModeFromInteropPolicy(policy);
}

pub fn unsafeScopeFromPolicy(policy: Policy) ?UnsafeScope {
    return abi.unsafeScopeFromInteropPolicy(policy);
}

pub fn recognizes(policy: Policy) bool {
    return abi.interopPolicyIsRecognized(policy);
}

pub fn ownershipClassFromAllocatorMode(mode: AllocatorMode) OwnershipClass {
    return switch (mode) {
        .caller_provided => .borrowed,
        .kernel_heap => .kernel_owned,
        .arena => .arena_owned,
    };
}

pub fn ownershipClassFromPolicy(policy: Policy) ?OwnershipClass {
    return ownershipClassFromAllocatorMode(allocatorModeFromPolicy(policy) orelse return null);
}

pub fn requiresExplicitCallerOwnership(mode: AllocatorMode) bool {
    return ownershipClassFromAllocatorMode(mode) == .borrowed;
}

pub fn requiresExplicitCallerOwnershipPolicy(policy: Policy) bool {
    return ownershipClassFromPolicy(policy) == .borrowed;
}

pub fn permitsKernelOwnedFallback(mode: AllocatorMode) bool {
    return ownershipClassFromAllocatorMode(mode) == .kernel_owned;
}

pub fn permitsKernelOwnedFallbackPolicy(policy: Policy) bool {
    return ownershipClassFromPolicy(policy) == .kernel_owned;
}

pub fn requiresArenaReset(mode: AllocatorMode) bool {
    return ownershipClassFromAllocatorMode(mode) == .arena_owned;
}

pub fn requiresArenaResetPolicy(policy: Policy) bool {
    return ownershipClassFromPolicy(policy) == .arena_owned;
}

pub fn causesImmediateHalt(mode: PanicMode) bool {
    return switch (mode) {
        .abort, .bug => true,
        .warn => false,
    };
}

pub fn causesImmediateHaltPolicy(policy: Policy) bool {
    return causesImmediateHalt(panicModeFromPolicy(policy) orelse return false);
}

pub fn unsafeAuditClassFromScope(scope: UnsafeScope) UnsafeAuditClass {
    return switch (scope) {
        .none => .none,
        .volatile_mmio => .volatile_mmio,
        .raw_pointer_bridge => .raw_pointer_bridge,
    };
}

pub fn unsafeAuditClassFromPolicy(policy: Policy) ?UnsafeAuditClass {
    return unsafeAuditClassFromScope(unsafeScopeFromPolicy(policy) orelse return null);
}

pub fn requiresDedicatedUnsafeAudit(scope: UnsafeScope) bool {
    return unsafeAuditClassFromScope(scope) != .none;
}

pub fn requiresDedicatedUnsafeAuditPolicy(policy: Policy) bool {
    return requiresDedicatedUnsafeAudit(unsafeScopeFromPolicy(policy) orelse return false);
}

test "interop policy binding keeps the published layout contract" {
    try std.testing.expectEqual(@as(usize, 4), policy_size);
    try std.testing.expectEqual(@as(usize, 1), policy_align);
    try std.testing.expectEqual(@as(usize, 0), panic_mode_offset);
    try std.testing.expectEqual(@as(usize, 1), allocator_mode_offset);
    try std.testing.expectEqual(@as(usize, 2), unsafe_scope_offset);
    try std.testing.expectEqual(@as(usize, 3), reserved_offset);
}

test "interop policy binding keeps the default policy borrowed and fully safe" {
    const policy = default();

    try std.testing.expect(recognizes(policy));
    try std.testing.expect(reservedClear(policy));
    try std.testing.expectEqual(@as(?PanicMode, .abort), panicModeFromPolicy(policy));
    try std.testing.expectEqual(@as(?AllocatorMode, .caller_provided), allocatorModeFromPolicy(policy));
    try std.testing.expectEqual(@as(?UnsafeScope, .none), unsafeScopeFromPolicy(policy));
    try std.testing.expectEqual(@as(?OwnershipClass, .borrowed), ownershipClassFromPolicy(policy));
    try std.testing.expectEqual(@as(?UnsafeAuditClass, .none), unsafeAuditClassFromPolicy(policy));
    try std.testing.expect(requiresExplicitCallerOwnershipPolicy(policy));
    try std.testing.expect(!permitsKernelOwnedFallbackPolicy(policy));
    try std.testing.expect(!requiresArenaResetPolicy(policy));
    try std.testing.expect(causesImmediateHaltPolicy(policy));
    try std.testing.expect(!requiresDedicatedUnsafeAuditPolicy(policy));
}

test "interop policy binding classifies kernel-owned mmio policies explicitly" {
    const policy = Policy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };

    try std.testing.expect(recognizes(policy));
    try std.testing.expectEqual(@as(?OwnershipClass, .kernel_owned), ownershipClassFromPolicy(policy));
    try std.testing.expectEqual(@as(?UnsafeAuditClass, .volatile_mmio), unsafeAuditClassFromPolicy(policy));
    try std.testing.expect(!requiresExplicitCallerOwnershipPolicy(policy));
    try std.testing.expect(permitsKernelOwnedFallbackPolicy(policy));
    try std.testing.expect(!requiresArenaResetPolicy(policy));
    try std.testing.expect(causesImmediateHaltPolicy(policy));
    try std.testing.expect(requiresDedicatedUnsafeAuditPolicy(policy));
}

test "interop policy binding classifies arena raw-pointer policies explicitly" {
    const policy = Policy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };

    try std.testing.expect(recognizes(policy));
    try std.testing.expectEqual(@as(?OwnershipClass, .arena_owned), ownershipClassFromPolicy(policy));
    try std.testing.expectEqual(@as(?UnsafeAuditClass, .raw_pointer_bridge), unsafeAuditClassFromPolicy(policy));
    try std.testing.expect(!requiresExplicitCallerOwnershipPolicy(policy));
    try std.testing.expect(!permitsKernelOwnedFallbackPolicy(policy));
    try std.testing.expect(requiresArenaResetPolicy(policy));
    try std.testing.expect(!causesImmediateHaltPolicy(policy));
    try std.testing.expect(requiresDedicatedUnsafeAuditPolicy(policy));
}

test "interop policy binding rejects reserved and unknown policy bytes" {
    const reserved = Policy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };
    const unknown = Policy{
        .panic_mode = 9,
        .allocator_mode = 9,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expect(!recognizes(reserved));
    try std.testing.expect(!recognizes(unknown));
    try std.testing.expectEqual(@as(?OwnershipClass, null), ownershipClassFromPolicy(reserved));
    try std.testing.expectEqual(@as(?OwnershipClass, null), ownershipClassFromPolicy(unknown));
    try std.testing.expectEqual(@as(?UnsafeAuditClass, null), unsafeAuditClassFromPolicy(reserved));
    try std.testing.expectEqual(@as(?UnsafeAuditClass, null), unsafeAuditClassFromPolicy(unknown));
    try std.testing.expect(!causesImmediateHaltPolicy(unknown));
    try std.testing.expect(!requiresDedicatedUnsafeAuditPolicy(reserved));
}
