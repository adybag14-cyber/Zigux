const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const export_shim = @import("export_shim");
const header_family = @import("header_family_binding");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");

test "phase3 abi keeps shared layout assertions wired into the replay" {
    try layout_assert.assertPublishedAbiLayouts();
    layout_assert.assertInteropPolicyModeValues();
    layout_assert.assertNotifierResultValues();
}

test "phase3 abi keeps export shim compatibility and status helpers reviewable" {
    const canonical = export_shim.canonicalHeader(0x41);
    const expanded = abi.compatibleHeader(export_shim.header_size + 16, 0x41);
    const stale = export_shim.BoundaryHeader{
        .size = export_shim.header_size,
        .abi_version = export_shim.abi_version + 1,
        .flags = 0,
    };
    const canonicalized = export_shim.canonicalizeHeader(expanded);

    try std.testing.expect(export_shim.headerIsCanonical(canonical));
    try std.testing.expect(export_shim.headerIsCompatible(canonical));
    try std.testing.expect(!export_shim.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(canonical));

    try std.testing.expect(!export_shim.headerIsCanonical(expanded));
    try std.testing.expect(export_shim.headerIsCompatible(expanded));
    try std.testing.expect(export_shim.extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 16), export_shim.requestedExtraBytes(expanded));

    try std.testing.expect(!export_shim.headerIsCanonical(stale));
    try std.testing.expect(!export_shim.headerIsCompatible(stale));
    try std.testing.expect(!export_shim.extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, export_shim.header_size), canonicalized.size);
    try std.testing.expectEqual(@as(u16, export_shim.abi_version), canonicalized.abi_version);
    try std.testing.expectEqual(expanded.flags, canonicalized.flags);

    const ok = export_shim.okStatus(.helpers);
    const err = export_shim.errorStatus(-71, .drivers);
    const positive = export_shim.errorStatus(7, .kernel);
    const abi_ok = abi.okStatus(.helpers);
    const abi_err = abi.makeStatus(-71, .drivers);
    const abi_positive = abi.makeStatus(7, .kernel);

    try std.testing.expect(export_shim.statusIsOk(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.helpers)), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);
    try std.testing.expect(std.meta.eql(ok, abi_ok));

    try std.testing.expect(!export_shim.statusIsOk(err));
    try std.testing.expectEqual(@as(i32, -71), err.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.drivers)), err.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), err.flags);
    try std.testing.expect(std.meta.eql(err, abi_err));

    try std.testing.expect(export_shim.statusIsOk(positive));
    try std.testing.expectEqual(@as(i32, 7), positive.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), positive.facility);
    try std.testing.expectEqual(@as(u16, 0), positive.flags);
    try std.testing.expect(std.meta.eql(positive, abi_positive));
}

test "phase3 abi keeps raw boundary header rejection and shim validation aligned" {
    const undersized = abi.BoundaryHeader{
        .size = @sizeOf(abi.BoundaryHeader) - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x52,
    };
    const stale = abi.BoundaryHeader{
        .size = @sizeOf(abi.BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x52,
    };
    const expanded = abi.compatibleHeader(@sizeOf(abi.BoundaryHeader) + 4, 0x52);
    const undersized_status = export_shim.validateBoundaryHeader(undersized);
    const stale_status = export_shim.validateBoundaryHeader(stale);
    const expanded_status = export_shim.validateBoundaryHeader(expanded);

    try std.testing.expect(!abi.headerIsCanonical(undersized));
    try std.testing.expect(!abi.headerIsCompatible(undersized));
    try std.testing.expect(!abi.extendsBoundary(undersized));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(undersized));

    try std.testing.expect(!abi.headerIsCanonical(stale));
    try std.testing.expect(!abi.headerIsCompatible(stale));
    try std.testing.expect(!abi.extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(stale));

    try std.testing.expect(header_family.boundaryHeaderIsCanonicalSize(stale.size));
    try std.testing.expect(header_family.boundaryHeaderIsCompatibleSize(stale.size));
    try std.testing.expect(!header_family.boundaryHeaderIsCompatibleSize(undersized.size));
    try std.testing.expect(!header_family.boundaryHeaderIsCanonical(undersized));
    try std.testing.expect(!header_family.boundaryHeaderIsCompatible(undersized));
    try std.testing.expect(!header_family.boundaryHeaderExtendsBoundary(undersized));
    try std.testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(undersized));
    try std.testing.expect(!header_family.boundaryHeaderIsCanonical(stale));
    try std.testing.expect(!header_family.boundaryHeaderIsCompatible(stale));
    try std.testing.expect(!header_family.boundaryHeaderExtendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(stale));

    try std.testing.expect(export_shim.statusIsOk(expanded_status));
    try std.testing.expect(!export_shim.statusIsOk(undersized_status));
    try std.testing.expect(!export_shim.statusIsOk(stale_status));
    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), expanded_status));
    try std.testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), undersized_status));
    try std.testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), stale_status));
}

test "phase3 abi keeps version and dev_t relays explicit" {
    const current = export_shim.currentVersion();
    const fields = export_shim.makeDevTFields(42, 7);
    const valid = export_shim.validateDeviceNumber(42, 7);
    const invalid = export_shim.validateDeviceNumber(4_096, 0);
    const valid_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(42, 7),
        export_shim.makeDevTFields(42, 9),
    );
    const invalid_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(42, 9),
        export_shim.makeDevTFields(42, 7),
    );

    try std.testing.expectEqual(@as(u32, 0), current.abi_major);
    try std.testing.expectEqual(@as(u32, 1), current.abi_minor);
    try std.testing.expectEqual(@as(u32, 1), current.header_family_revision);

    try std.testing.expectEqual(@as(u32, 42), fields.major);
    try std.testing.expectEqual(@as(u32, 7), fields.minor);

    try std.testing.expect(export_shim.statusIsOk(valid));
    try std.testing.expect(!export_shim.statusIsOk(invalid));
    try std.testing.expectEqual(@as(i32, -22), invalid.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid.flags);

    try std.testing.expect(export_shim.statusIsOk(valid_range));
    try std.testing.expect(!export_shim.statusIsOk(invalid_range));
    try std.testing.expectEqual(@as(i32, -22), invalid_range.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_range.flags);
}

test "phase3 abi keeps export-shim version validation and dev_t roundtrip relays explicit" {
    const current = export_shim.currentVersion();
    const stale_major = export_shim.Version{
        .abi_major = current.abi_major + 1,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision,
    };
    const stale_minor = export_shim.Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor + 1,
        .header_family_revision = current.header_family_revision,
    };
    const stale_revision = export_shim.Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision + 1,
    };
    const valid = export_shim.validateVersion(current);
    const invalid_major = export_shim.validateVersion(stale_major);
    const invalid_minor = export_shim.validateVersion(stale_minor);
    const invalid_revision = export_shim.validateVersion(stale_revision);

    try std.testing.expect(export_shim.versionMatchesCurrent(current));
    try std.testing.expect(!export_shim.versionMatchesCurrent(stale_major));
    try std.testing.expect(!export_shim.versionMatchesCurrent(stale_minor));
    try std.testing.expect(!export_shim.versionMatchesCurrent(stale_revision));

    try std.testing.expect(export_shim.statusIsOk(valid));
    try std.testing.expect(!export_shim.statusIsOk(invalid_major));
    try std.testing.expect(!export_shim.statusIsOk(invalid_minor));
    try std.testing.expect(!export_shim.statusIsOk(invalid_revision));
    try std.testing.expectEqual(@as(i32, -22), invalid_major.code);
    try std.testing.expectEqual(@as(i32, -22), invalid_minor.code);
    try std.testing.expectEqual(@as(i32, -22), invalid_revision.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_major.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_major.flags);

    const fields = export_shim.makeDevTFields(11, 29);
    const encoded = export_shim.encodeDeviceNumber(fields) orelse return error.TestUnexpectedResult;
    const decoded = export_shim.decodeDeviceNumber(encoded);
    const valid_fields = export_shim.validateDeviceFields(fields);
    const invalid_fields = export_shim.validateDeviceFields(export_shim.makeDevTFields(4_096, 0));

    try std.testing.expectEqual(@as(u32, 11), decoded.major);
    try std.testing.expectEqual(@as(u32, 29), decoded.minor);
    try std.testing.expect(export_shim.statusIsOk(valid_fields));
    try std.testing.expect(!export_shim.statusIsOk(invalid_fields));
    try std.testing.expectEqual(@as(i32, -22), invalid_fields.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_fields.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_fields.flags);
}

test "phase3 abi keeps Linux-facing header-family relays aligned with the shared ABI helpers" {
    const current = header_family.currentVersion();
    const stale = header_family.Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision + 1,
    };
    const canonical = header_family.currentBoundaryHeader(0x33);
    const expanded = header_family.compatibleBoundaryHeader(@sizeOf(header_family.BoundaryHeader) + 12, 0x33);
    const normalized = header_family.canonicalizeBoundaryHeader(expanded);
    const fields = header_family.initDevTFields(11, 29);
    const earlier = header_family.initDevTFields(11, 28);
    const encoded = header_family.makeDeviceNumber(fields.major, fields.minor);
    const decoded = header_family.fieldsFromDeviceNumber(encoded);
    const version_ok = header_family.validateVersionStatus(current);
    const version_bad = header_family.validateVersionStatus(stale);
    const fields_ok = header_family.validateDevTFieldsStatus(fields);
    const fields_bad = header_family.validateDevTComponentsStatus(header_family.max_major + 1, 0);
    const range_ok = header_family.validateDevTRangeStatus(earlier, fields);
    const range_bad = header_family.validateDevTRangeStatus(fields, earlier);

    try std.testing.expect(std.meta.eql(current, export_shim.currentVersion()));
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), header_family.abi_version);
    try std.testing.expectEqual(@as(u32, 1), header_family.uapi_dev_t_packet_present);

    try std.testing.expect(std.meta.eql(canonical, export_shim.canonicalHeader(0x33)));
    try std.testing.expect(header_family.boundaryHeaderHasCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(header_family.boundaryHeaderIsCanonicalSize(canonical.size));
    try std.testing.expect(header_family.boundaryHeaderIsCompatibleSize(canonical.size));
    try std.testing.expect(header_family.boundaryHeaderIsCanonical(canonical));
    try std.testing.expect(header_family.boundaryHeaderIsCompatible(canonical));
    try std.testing.expect(!header_family.boundaryHeaderExtendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), header_family.boundaryHeaderRequestedExtraBytes(canonical));

    try std.testing.expect(!header_family.boundaryHeaderIsCanonical(expanded));
    try std.testing.expect(header_family.boundaryHeaderIsCompatible(expanded));
    try std.testing.expect(header_family.boundaryHeaderExtendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 12), header_family.boundaryHeaderRequestedExtraBytes(expanded));
    try std.testing.expectEqual(@as(u32, 12), export_shim.requestedExtraBytes(expanded));

    try std.testing.expectEqual(@as(u32, @intCast(header_family.header_size)), normalized.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), normalized.abi_version);
    try std.testing.expectEqual(expanded.flags, normalized.flags);

    try std.testing.expect(header_family.validateDevTFields(fields));
    try std.testing.expectEqual(@as(u32, 11), header_family.majorFromDeviceNumber(encoded));
    try std.testing.expectEqual(@as(u32, 29), header_family.minorFromDeviceNumber(encoded));
    try std.testing.expectEqual(fields.major, decoded.major);
    try std.testing.expectEqual(fields.minor, decoded.minor);

    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), version_ok));
    try std.testing.expect(!export_shim.statusIsOk(version_bad));
    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), fields_ok));
    try std.testing.expect(!export_shim.statusIsOk(fields_bad));
    try std.testing.expect(std.meta.eql(export_shim.okStatus(.kernel), range_ok));
    try std.testing.expect(!export_shim.statusIsOk(range_bad));
}

test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {
    const safe_policy = abi.defaultInteropPolicy();
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 9,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(safe_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(mmio_policy));
    try std.testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(raw_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(safe_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(mmio_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(mmio_policy));
    try std.testing.expect(allocator_policy.requiresResetOnInitInteropPolicy(raw_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(unsafe_policy.permitsNoUnsafeInteropPolicy(safe_policy));
    try std.testing.expect(!unsafe_policy.permitsNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(unsafe_policy.permitsVolatileMmioInteropPolicy(mmio_policy));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditInteropPolicy(raw_policy));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(unknown_policy));
}

test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {
    const safe_policy = abi.defaultInteropPolicy();

    try std.testing.expectEqual(@as(u8, abi.PANIC_ABORT), safe_policy.panic_mode);
    try std.testing.expectEqual(@as(u8, abi.ALLOC_CALLER_PROVIDED), safe_policy.allocator_mode);
    try std.testing.expectEqual(@as(u8, abi.UNSAFE_NONE), safe_policy.unsafe_scope);
    try std.testing.expectEqual(@as(u8, 0), safe_policy.reserved);

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromByte(abi.PANIC_ABORT));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.causesImmediateHaltByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.permitsWarningOnlyContinuationByte(abi.PANIC_WARN));
    try std.testing.expect(!panic_policy.recognizesInteropPolicyBytes(abi.PANIC_WARN, 1));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(allocator_policy.requiresExplicitCallerByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.initializesOwnedStateByte(abi.ALLOC_ARENA));
    try std.testing.expect(allocator_policy.requiresResetOnInitByte(abi.ALLOC_ARENA));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(abi.ALLOC_ARENA, 1));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.scopeFromByte(abi.UNSAFE_NONE));
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, .typed_safe),
        unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_NONE),
    );
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, .volatile_mmio_window),
        unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_VOLATILE_MMIO),
    );
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, .raw_pointer_bridge),
        unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expect(unsafe_policy.permitsVolatileMmioByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 1));
}

test "phase3 abi keeps malformed notifier list relays visible through the shared ABI surface" {
    const rising_tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const rising_head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_tail),
        .priority = 2,
    };
    const increase = abi.firstChainPriorityIncrease(&rising_head) orelse return error.TestUnexpectedResult;

    try std.testing.expect(!abi.chainHasNonincreasingPriority(&rising_head));
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 8), increase.current_priority);

    var list_head = abi.ListHead{ .next = 0, .prev = 0 };
    var list_first = abi.ListHead{ .next = 0, .prev = 0 };
    var list_second = abi.ListHead{ .next = 0, .prev = 0 };

    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_head);

    const list_break = abi.firstBrokenBacklink(&list_head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.listHasConsistentBacklinks(&list_head));
    try std.testing.expect(!abi.listHasConsistentBacklinks(null));
    try std.testing.expectEqual(@as(usize, 1), list_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_first)), list_break.expected_prev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&list_head)), list_break.actual_prev);

    var hlist_head = abi.HListHead{ .first = 0 };
    var hlist_first = abi.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = abi.HListNode{ .next = 0, .pprev = 0 };

    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_head.first);

    const hlist_break = abi.firstBrokenPrevLink(&hlist_head) orelse return error.TestUnexpectedResult;
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expect(!abi.hlistHasConsistentPrevLinks(null));
    try std.testing.expectEqual(@as(usize, 1), hlist_break.current_index);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_first.next)), hlist_break.expected_pprev);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&hlist_head.first)), hlist_break.actual_pprev);
}