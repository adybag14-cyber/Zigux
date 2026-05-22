const abi = @import("abi_bindings");
const narrow = @import("narrow");

pub const AccessBoundary = enum {
    typed_safe,
    volatile_mmio_window,
    raw_pointer_bridge,
};

pub const Surface = narrow.Surface;

pub const UnsafeScopeError = error{UnsafeScopeDenied};

fn fromNarrowAccessBoundary(boundary: narrow.AccessBoundary) AccessBoundary {
    return switch (boundary) {
        .typed_safe => .typed_safe,
        .volatile_mmio_window => .volatile_mmio_window,
        .raw_pointer_bridge => .raw_pointer_bridge,
    };
}

pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {
    return narrow.scopeFromInteropPolicyBytes(scope, reserved);
}

pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {
    return narrow.scopeFromInteropPolicy(policy);
}

pub fn scopeFromByte(scope: u8) ?abi.UnsafeScope {
    return narrow.scopeFromByte(scope);
}

pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {
    return narrow.permitsVolatileMmio(mode);
}

pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {
    return narrow.permitsRawPointerBridge(mode);
}

pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.permitsRawPointerBridgeInteropPolicy(policy);
}

pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.allowsRawPointerBridgeInteropPolicy(policy);
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgeInteropPolicy(policy);
}

pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.allowsRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn permitsRawPointerBridgeByte(scope: u8) bool {
    return narrow.permitsRawPointerBridgePolicyBytes(scope, 0);
}
