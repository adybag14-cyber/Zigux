const std = @import("std");
const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");
const dev_t_bindings = @import("dev_t_bindings");
const uapi_dev_t = @import("uapi_dev_t");

test "phase3 export shim and uapi keep canonical boundary layout" {
    const header: export_shim.Header = export_shim.header(0x55);
    const uapi_header: uapi_version.Header = uapi_version.boundaryHeader(0x55);
    const future_compatible: export_shim.Header =
        export_shim.compatibleHeader(export_shim.header_size + 16, 0x55);
    const undersized: export_shim.Header =
        export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);
    const uapi_undersized: uapi_version.Header =
        uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x55);
    const version_mismatch: export_shim.Header = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x55,
    );
    const accepted_canonical = export_shim.acceptHeader(header).?;
    const accepted_future = export_shim.acceptHeader(future_compatible).?;
    const uapi_accepted_canonical = uapi_version.acceptHeader(uapi_header).?;
    const uapi_accepted_future = uapi_version.acceptHeader(future_compatible).?;

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.BoundaryHeader, "size"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.BoundaryHeader, "flags"));
    try std.testing.expectEqual(@sizeOf(export_shim.Header), @sizeOf(uapi_version.Header));

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));

    try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));
    try std.testing.expectEqual(header, uapi_header);
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(uapi_header));
    try std.testing.expectEqual(export_shim.HeaderCompatibility.canonical, accepted_canonical.compatibility);
    try std.testing.expectEqual(header, accepted_canonical.canonical);
    try std.testing.expectEqual(uapi_version.Compatibility.canonical, uapi_accepted_canonical.compatibility);
    try std.testing.expectEqual(uapi_header, uapi_accepted_canonical.canonical);

    try std.testing.expect(export_shim.isCompatibleHeader(future_compatible));
    try std.testing.expect(uapi_version.isCompatible(future_compatible));
    try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible));
    try std.testing.expect(!uapi_version.isCanonical(future_compatible));
    try std.testing.expectEqual(
        export_shim.HeaderCompatibility.future_compatible,
        export_shim.headerCompatibility(future_compatible).?,
    );
    try std.testing.expectEqual(
        export_shim.HeaderCompatibility.future_compatible,
        accepted_future.compatibility,
    );
    try std.testing.expectEqual(
        uapi_version.Compatibility.future_compatible,
        uapi_version.compatibility(future_compatible).?,
    );
    try std.testing.expectEqual(
        uapi_version.Compatibility.future_compatible,
        uapi_accepted_future.compatibility,
    );
    try std.testing.expectEqual(header, accepted_future.canonical);
    try std.testing.expectEqual(uapi_header, uapi_accepted_future.canonical);
    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible).?);
    try std.testing.expectEqual(uapi_header, uapi_version.canonicalizeHeader(future_compatible).?);

    try std.testing.expectEqual(undersized, uapi_undersized);
    try std.testing.expect(export_shim.headerCompatibility(undersized) == null);
    try std.testing.expect(uapi_version.compatibility(uapi_undersized) == null);
    try std.testing.expect(export_shim.acceptHeader(undersized) == null);
    try std.testing.expect(uapi_version.acceptHeader(uapi_undersized) == null);
    try std.testing.expect(!export_shim.isCompatibleHeader(undersized));
    try std.testing.expect(!uapi_version.isCompatible(uapi_undersized));
    try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(uapi_undersized) == null);

    try std.testing.expect(export_shim.headerCompatibility(version_mismatch) == null);
    try std.testing.expect(uapi_version.compatibility(version_mismatch) == null);
    try std.testing.expect(export_shim.acceptHeader(version_mismatch) == null);
    try std.testing.expect(uapi_version.acceptHeader(version_mismatch) == null);
    try std.testing.expect(export_shim.canonicalizeHeader(version_mismatch) == null);
    try std.testing.expect(uapi_version.canonicalizeHeader(version_mismatch) == null);
}

test "phase3 export shim keeps compatibility status relays explicit" {
    const canonical = export_shim.boundaryHeader(0x66);
    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 32, 0x66);
    const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x66);
    const version_mismatch = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x66,
    );

    const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);
    const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);
    const undersized_status = export_shim.compatibilityStatus(undersized, -22, .drivers);
    const mismatch_status = export_shim.compatibilityStatus(version_mismatch, -71, .kernel);

    try std.testing.expect(export_shim.isOk(canonical_status));
    try std.testing.expect(export_shim.isOk(future_status));
    try std.testing.expectEqual(@as(i32, 0), canonical_status.code);
    try std.testing.expectEqual(@as(i32, 0), future_status.code);

    try std.testing.expect(!export_shim.isOk(undersized_status));
    try std.testing.expectEqual(@as(i32, -22), undersized_status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), undersized_status.flags);

    try std.testing.expect(!export_shim.isOk(mismatch_status));
    try std.testing.expectEqual(@as(i32, -71), mismatch_status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), mismatch_status.flags);
}

test "phase3 export shim evaluation mirrors the uapi boundary classification" {
    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 24, 0x77);
    const version_mismatch = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x77,
    );

    const export_future = export_shim.evaluateHeader(future_compatible, -75, .helpers);
    const uapi_future = uapi_version.evaluateHeader(future_compatible);

    try std.testing.expect(export_future.isAccepted());
    try std.testing.expect(uapi_future.isAccepted());
    try std.testing.expectEqual(uapi_future.compatibility().?, export_future.compatibility().?);
    try std.testing.expectEqual(uapi_future.canonical().?, export_future.canonical().?);
    try std.testing.expectEqual(uapi_future.sizeDelta(), export_future.sizeDelta());
    try std.testing.expect(export_shim.isOk(export_future.status));

    const export_mismatch = export_shim.evaluateHeader(version_mismatch, -71, .kernel);
    const uapi_mismatch = uapi_version.evaluateHeader(version_mismatch);

    try std.testing.expect(!export_mismatch.isAccepted());
    try std.testing.expect(!uapi_mismatch.isAccepted());
    try std.testing.expect(export_mismatch.compatibility() == null);
    try std.testing.expect(uapi_mismatch.compatibility() == null);
    try std.testing.expect(export_mismatch.canonical() == null);
    try std.testing.expect(uapi_mismatch.canonical() == null);
    try std.testing.expectEqual(uapi_mismatch.sizeDelta(), export_mismatch.sizeDelta());
    try std.testing.expect(!export_shim.isOk(export_mismatch.status));
}

test "phase3 uapi dev_t starter keeps curated boundary parity explicit" {
    try std.testing.expectEqual(dev_t_bindings.minor_bits, uapi_dev_t.minor_bits);
    try std.testing.expectEqual(dev_t_bindings.minor_mask, uapi_dev_t.minor_mask);
    try std.testing.expectEqual(dev_t_bindings.max_major, uapi_dev_t.major_max);
    try std.testing.expect(uapi_dev_t.majorValid(uapi_dev_t.major_max));
    try std.testing.expect(uapi_dev_t.minorValid(uapi_dev_t.minor_mask));
    try std.testing.expect(uapi_dev_t.rangeFits(uapi_dev_t.minor_mask - 3, 4));
    try std.testing.expectEqual(
        try dev_t_bindings.lastInRange(uapi_dev_t.major_max, uapi_dev_t.minor_mask - 3, 4),
        try uapi_dev_t.lastInRange(uapi_dev_t.major_max, uapi_dev_t.minor_mask - 3, 4),
    );
    try std.testing.expectError(error.RangeExhausted, uapi_dev_t.lastInRange(1, uapi_dev_t.minor_mask - 1, 3));
}
