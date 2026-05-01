const std = @import("std");
const devres = @import("devres");

test "phase13 devres direct ioremap wrappers reject missing release record allocation" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoremapAcquirePlain(.{
        .release_record_allocated = false,
        .mapped_address = 0x2200,
    }));
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoremapAcquireUc(.{
        .release_record_allocated = false,
        .mapped_address = 0x2400,
    }));
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoremapAcquireWc(.{
        .release_record_allocated = false,
        .mapped_address = 0x2600,
    }));
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoremapAcquireNp(.{
        .release_record_allocated = false,
        .mapped_address = 0x2800,
    }));
}
