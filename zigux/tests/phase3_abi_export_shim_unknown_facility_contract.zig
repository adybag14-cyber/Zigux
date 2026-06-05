const std = @import("std");
const testing = std.testing;

const export_shim = @import("export_shim");

test "export shim keeps unknown flagged facilities outside the known status lane" {
    const unknown_error = export_shim.ExportStatus{
        .code = -5,
        .facility = 0x7fff,
        .flags = 1,
    };
    const unknown_positive_flagged = export_shim.ExportStatus{
        .code = 7,
        .facility = 0x7ffe,
        .flags = 1,
    };
    const unknown_unflagged = export_shim.ExportStatus{
        .code = 0,
        .facility = 0x7ffd,
        .flags = 0,
    };
    const known_error = export_shim.errorStatus(-5, .helpers);

    try testing.expect(!export_shim.statusIsOk(unknown_error));
    try testing.expect(!export_shim.statusIsOk(unknown_positive_flagged));
    try testing.expect(export_shim.statusIsOk(unknown_unflagged));
    try testing.expect(!export_shim.statusIsOk(known_error));

    try testing.expect(!export_shim.statusHasKnownFacility(unknown_error));
    try testing.expect(!export_shim.statusHasKnownFacility(unknown_positive_flagged));
    try testing.expect(!export_shim.statusHasKnownFacility(unknown_unflagged));
    try testing.expect(export_shim.statusHasKnownFacility(known_error));

    try testing.expectEqual(@as(?export_shim.Facility, null), export_shim.facilityFromInt(unknown_error.facility));
    try testing.expectEqual(@as(?export_shim.Facility, null), export_shim.facilityFromInt(unknown_positive_flagged.facility));
    try testing.expectEqual(@as(?export_shim.Facility, null), export_shim.facilityFromInt(unknown_unflagged.facility));
    try testing.expectEqual(@as(?export_shim.Facility, .helpers), export_shim.facilityFromInt(known_error.facility));
}
