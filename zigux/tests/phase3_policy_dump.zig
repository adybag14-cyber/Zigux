const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");
const narrow_surface = @import("narrow_surface");

fn panicName(mode: ?abi.PanicMode) []const u8 {
    return switch (mode orelse return "invalid") {
        .abort => "abort",
        .bug => "bug",
        .warn => "warn",
    };
}

fn allocatorName(mode: ?abi.AllocatorMode) []const u8 {
    return switch (mode orelse return "invalid") {
        .caller_provided => "caller_provided",
        .kernel_heap => "kernel_heap",
        .arena => "arena",
    };
}

fn initFlowName(flow: ?allocator_policy.InitFlow) []const u8 {
    return switch (flow orelse return "invalid") {
        .caller_prepared => "caller_prepared",
        .helper_owned => "helper_owned",
        .helper_owned_with_reset => "helper_owned_with_reset",
    };
}

fn unsafeName(scope: ?abi.UnsafeScope) []const u8 {
    return switch (scope orelse return "invalid") {
        .none => "none",
        .volatile_mmio => "volatile_mmio",
        .raw_pointer_bridge => "raw_pointer_bridge",
    };
}

fn printPolicy(name: []const u8, policy: abi.InteropPolicy) void {
    const panic_mode = panic_policy.modeFromInteropPolicy(policy);
    const allocator_mode = allocator_policy.modeFromInteropPolicy(policy);
    const init_flow = if (allocator_mode) |mode| allocator_policy.initFlowFor(mode) else null;
    const helper_scope = unsafe_policy.scopeFromInteropPolicy(policy);
    const narrow_scope = narrow_surface.scopeFromInteropPolicy(policy);

    std.debug.print(
        "{s}|panic={s}|allocator={s}|init_flow={s}|explicit_caller={any}|owned_state={any}|reset_on_init={any}|unsafe={s}|typed_only={any}|global_fallback={any}|warn_only={any}|mmio={any}|raw_bridge={any}|audit={any}|narrow={s}\n",
        .{
            name,
            panicName(panic_mode),
            allocatorName(allocator_mode),
            initFlowName(init_flow),
            allocator_mode != null and allocator_policy.requiresExplicitCaller(allocator_mode.?),
            allocator_mode != null and allocator_policy.initializesOwnedState(allocator_mode.?),
            allocator_mode != null and allocator_policy.requiresResetOnInit(allocator_mode.?),
            unsafeName(helper_scope),
            unsafe_policy.allowsTypedOnlyAccessInteropPolicy(policy),
            allocator_mode != null and allocator_policy.permitsGlobalFallback(allocator_mode.?),
            panic_mode != null and panic_policy.permitsWarningOnlyContinuation(panic_mode.?),
            helper_scope != null and unsafe_policy.permitsVolatileMmio(helper_scope.?),
            helper_scope != null and unsafe_policy.permitsRawPointerBridge(helper_scope.?),
            helper_scope != null and unsafe_policy.requiresDedicatedAudit(helper_scope.?),
            unsafeName(narrow_scope),
        },
    );
}

pub fn main() !void {
    const policies = [_]struct {
        name: []const u8,
        policy: abi.InteropPolicy,
    }{
        .{ .name = "safe-default", .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 } },
        .{ .name = "mmio-bug", .policy = .{ .panic_mode = 1, .allocator_mode = 1, .unsafe_scope = 1, .reserved = 0 } },
        .{ .name = "raw-bridge-warn", .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 0 } },
        .{ .name = "reserved-invalid", .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 } },
    };

    for (policies) |entry| {
        printPolicy(entry.name, entry.policy);
    }
}
