const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");

pub const abi_version: u16 = abi.ABI_VERSION;

comptime {
    const hdr = export_shim.header(0);
    if (hdr.size != @sizeOf(abi.BoundaryHeader)) {
        @compileError("uapi version must track the export shim boundary header size");
    }
    if (hdr.abi_version != abi_version) {
        @compileError("uapi version must track the export shim ABI version");
    }
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}

test "phase3 uapi version stays aligned with export shim header defaults" {
    const hdr = export_shim.header(0x24);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), hdr.size);
    try std.testing.expectEqual(abi_version, hdr.abi_version);
    try std.testing.expectEqual(@as(u16, 0x24), hdr.flags);
}
