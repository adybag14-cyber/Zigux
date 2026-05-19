const std = @import("std");

pub const anchor_path = "drivers/virtio/virtio_mmio.c";
pub const mmio_magic_value: u32 = 0x7472_6976;
pub const mmio_version_legacy: u32 = 1;
pub const mmio_version_modern: u32 = 2;
pub const default_vendor_id: u32 = 0x554d_4551;
pub const mmio_window_bytes: u32 = 0x100;

const max_queue_count = 8;
const max_config_bytes = 128;
const max_feature_words = 2;

pub const Register = enum {
    queue_sel,
    queue_num,
    queue_ready,
    device_features_sel,
    driver_features_sel,
    interrupt_ack,
    guest_page_size,
};

pub const ConfigWritePlanSummary = struct {
    anchor: []const u8,
    relative_offset: u32,
    absolute_offset: u32,
    planned_value: u32,
    config_generation: u32,
    within_config_window: bool,
};

pub const ConfigWriteDispositionSummary = struct {
    anchor: []const u8,
    relative_offset: u32,
    absolute_offset: u32,
    relative_end_offset: u32,
    absolute_end_offset: u32,
    previous_value: u32,
    planned_value: u32,
    config_generation: u32,
    changed_byte_mask: u4,
    has_changes: bool,
};

pub const FeatureNegotiationSummary = struct {
    anchor: []const u8,
    selected_device_feature_word: u32,
    selected_driver_feature_word: u32,
    device_feature_selector_in_range: bool,
    driver_feature_selector_in_range: bool,
    selected_feature_words_in_range: bool,
    device_feature_word: u32,
    driver_feature_word: u32,
    negotiated_feature_word: u32,
    device_only_feature_word: u32,
    driver_only_feature_word: u32,
    feature_words_match: bool,
    device_features_known: bool,
    driver_features_known: bool,
    negotiation_possible: bool,
};

pub const TransportIdentitySummary = struct {
    anchor: []const u8,
    magic_matches: bool,
    version_supported: bool,
    device_present: bool,
    vendor_id_present: bool,
    requires_legacy_guest_page_size: bool,
};

pub const ProbePreflightSummary = struct {
    anchor: []const u8,
    device_present: bool,
    vendor_id_present: bool,
    version_supported: bool,
    bounded_queue_register_window_ready: bool,
    interrupt_ack_ready: bool,
    legacy_guest_page_size_ready: bool,
    consumes_identity_snapshot: bool,
    ready_for_probe_handoff: bool,
};

pub const SelectedQueueReadinessSummary = struct {
    anchor: []const u8,
    selected_queue: u16,
    advertised_queue_size: u16,
    programmed_queue_size: u16,
    queue_size_programmed: bool,
    queue_size_matches_advertised: bool,
    queue_ready_for_handoff: bool,
};

pub const InterruptAckDispositionSummary = struct {
    anchor: []const u8,
    requested_bits: u32,
    pending_bits: u32,
    acknowledged_bits: u32,
    ignored_bits: u32,
    remaining_pending_bits: u32,
    has_acknowledgements: bool,
};

const QueueState = struct {
    advertised_size: u16 = 0,
    programmed_size: u16 = 0,
    ready: bool = false,
};

pub const VirtioMmioLab = struct {
    const Self = @This();

    magic_value: u32 = mmio_magic_value,
    version: u32 = mmio_version_modern,
    device_id: u32 = 0,
    vendor_id: u32 = default_vendor_id,
    interrupt_ack_mask: u32 = 0x3,
    interrupt_status: u32 = 0,
    legacy_guest_page_size: u32 = 0,
    selected_queue: u16 = 0,
    selected_device_feature_word: u32 = 0,
    selected_driver_feature_word: u32 = 0,
    config_generation: u32 = 0,
    queue_count: usize = 0,
    queues: [max_queue_count]QueueState = [_]QueueState{QueueState{}} ** max_queue_count,
    config_bytes_len: usize = 0,
    config_bytes: [max_config_bytes]u8 = [_]u8{0} ** max_config_bytes,
    device_feature_words: [max_feature_words]u32 = [_]u32{ 0, 0 },
    driver_feature_words: [max_feature_words]u32 = [_]u32{ 0, 0 },
    device_feature_words_known: [max_feature_words]bool = [_]bool{false} ** max_feature_words,
    driver_feature_words_known: [max_feature_words]bool = [_]bool{false} ** max_feature_words,
    pending_config_write: ?ConfigWritePlanSummary = null,

    pub fn init(device_id: u32, queue_sizes: []const u16) !Self {
        if (queue_sizes.len == 0) return error.EmptyQueueSet;
        if (queue_sizes.len > max_queue_count) return error.QueueCountTooLarge;
        var self = Self{
            .device_id = device_id,
            .queue_count = queue_sizes.len,
        };
        for (queue_sizes, 0..) |size, index| {
            if (size == 0) return error.EmptyQueueSize;
            self.queues[index].advertised_size = size;
        }
        return self;
    }

    pub fn stageConfigBytes(self: *Self, bytes: []const u8) !void {
        if (bytes.len > self.config_bytes.len) return error.ConfigWindowTooLarge;
        @memset(&self.config_bytes, 0);
        @memcpy(self.config_bytes[0..bytes.len], bytes);
        self.config_bytes_len = bytes.len;
        self.pending_config_write = null;
    }

    pub fn stageDeviceFeatureWord(self: *Self, word_index: u32, value: u32) !void {
        const index: usize = @intCast(word_index);
        if (index >= self.device_feature_words.len) return error.FeatureWordOutOfRange;
        self.device_feature_words[index] = value;
        self.device_feature_words_known[index] = true;
    }

    pub fn stageDriverFeatureWord(self: *Self, word_index: u32, value: u32) !void {
        const index: usize = @intCast(word_index);
        if (index >= self.driver_feature_words.len) return error.FeatureWordOutOfRange;
        self.driver_feature_words[index] = value;
        self.driver_feature_words_known[index] = true;
    }

    pub fn stageInterruptStatus(self: *Self, bits: u32) void {
        self.interrupt_status = bits;
    }

    pub fn bumpConfigGeneration(self: *Self) void {
        self.config_generation +%= 1;
        self.pending_config_write = null;
    }

    pub fn planConfigWriteOffset(self: *Self, offset: u32, planned_value: u32) !ConfigWritePlanSummary {
        if (offset < mmio_window_bytes) return error.ConfigWindowOffsetOutOfRange;
        const relative_offset = offset - mmio_window_bytes;
        const end = std.math.add(u32, relative_offset, 4) catch return error.ConfigWindowOffsetOutOfRange;
        if (end > self.config_bytes_len) return error.ConfigWindowOffsetOutOfRange;
        const plan = ConfigWritePlanSummary{
            .anchor = anchor_path,
            .relative_offset = relative_offset,
            .absolute_offset = offset,
            .planned_value = planned_value,
            .config_generation = self.config_generation,
            .within_config_window = true,
        };
        self.pending_config_write = plan;
        return plan;
    }

    pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {
        const plan = self.pending_config_write orelse return error.ConfigWritePlanUnavailable;
        if (plan.config_generation != self.config_generation) return error.ConfigWritePlanUnavailable;
        const previous_value = try self.readConfigWord(plan.relative_offset);
        const changed_byte_mask = changedByteMask(previous_value, plan.planned_value);
        return .{
            .anchor = plan.anchor,
            .relative_offset = plan.relative_offset,
            .absolute_offset = plan.absolute_offset,
            .relative_end_offset = plan.relative_offset + 3,
            .absolute_end_offset = plan.absolute_offset + 3,
            .previous_value = previous_value,
            .planned_value = plan.planned_value,
            .config_generation = plan.config_generation,
            .changed_byte_mask = changed_byte_mask,
            .has_changes = changed_byte_mask != 0,
        };
    }

    pub fn featureNegotiationSummary(self: *const Self) FeatureNegotiationSummary {
        const device_selector_in_range = self.selectedDeviceFeatureWordInRange();
        const driver_selector_in_range = self.selectedDriverFeatureWordInRange();
        const selected_feature_words_in_range = device_selector_in_range and driver_selector_in_range;

        const device_feature_word = if (device_selector_in_range)
            self.device_feature_words[self.selectedDeviceFeatureWordIndex()]
        else
            0;
        const driver_feature_word = if (driver_selector_in_range)
            self.driver_feature_words[self.selectedDriverFeatureWordIndex()]
        else
            0;
        const negotiated_feature_word = device_feature_word & driver_feature_word;
        const device_features_known = device_selector_in_range and
            self.device_feature_words_known[self.selectedDeviceFeatureWordIndex()];
        const driver_features_known = driver_selector_in_range and
            self.driver_feature_words_known[self.selectedDriverFeatureWordIndex()];

        return .{
            .anchor = anchor_path,
            .selected_device_feature_word = self.selected_device_feature_word,
            .selected_driver_feature_word = self.selected_driver_feature_word,
            .device_feature_selector_in_range = device_selector_in_range,
            .driver_feature_selector_in_range = driver_selector_in_range,
            .selected_feature_words_in_range = selected_feature_words_in_range,
            .device_feature_word = device_feature_word,
            .driver_feature_word = driver_feature_word,
            .negotiated_feature_word = negotiated_feature_word,
            .device_only_feature_word = device_feature_word & ~driver_feature_word,
            .driver_only_feature_word = driver_feature_word & ~device_feature_word,
            .feature_words_match = selected_feature_words_in_range and device_feature_word == driver_feature_word,
            .device_features_known = device_features_known,
            .driver_features_known = driver_features_known,
            .negotiation_possible = selected_feature_words_in_range and device_features_known and driver_features_known,
        };
    }

    pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {
        return .{
            .anchor = anchor_path,
            .magic_matches = self.magic_value == mmio_magic_value,
            .version_supported = self.version == mmio_version_legacy or self.version == mmio_version_modern,
            .device_present = self.device_id != 0,
            .vendor_id_present = self.vendor_id != 0,
            .requires_legacy_guest_page_size = self.version == mmio_version_legacy,
        };
    }

    pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {
        const queue = self.queueForSelection(self.selected_queue) orelse return error.QueueSelectionOutOfRange;
        return .{
            .anchor = anchor_path,
            .selected_queue = self.selected_queue,
            .advertised_queue_size = queue.advertised_size,
            .programmed_queue_size = queue.programmed_size,
            .queue_size_programmed = queue.programmed_size != 0,
            .queue_size_matches_advertised = queue.programmed_size != 0 and queue.programmed_size == queue.advertised_size,
            .queue_ready_for_handoff = queue.programmed_size != 0 and queue.ready,
        };
    }

    pub fn interruptAckDispositionSummary(
        self: *const Self,
        requested_bits: u32,
    ) InterruptAckDispositionSummary {
        const acknowledged_bits = requested_bits & self.interrupt_status & self.interrupt_ack_mask;
        return .{
            .anchor = anchor_path,
            .requested_bits = requested_bits,
            .pending_bits = self.interrupt_status,
            .acknowledged_bits = acknowledged_bits,
            .ignored_bits = requested_bits & ~acknowledged_bits,
            .remaining_pending_bits = self.interrupt_status & ~acknowledged_bits,
            .has_acknowledgements = acknowledged_bits != 0,
        };
    }

    pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {
        const identity = self.transportIdentitySummary();
        const queue_register_window_ready = self.queue_count != 0;
        const interrupt_ack_ready = self.interrupt_ack_mask != 0;
        const legacy_guest_page_size_ready = !identity.requires_legacy_guest_page_size or self.legacy_guest_page_size != 0;
        return .{
            .anchor = anchor_path,
            .device_present = identity.device_present,
            .vendor_id_present = identity.vendor_id_present,
            .version_supported = identity.version_supported,
            .bounded_queue_register_window_ready = queue_register_window_ready,
            .interrupt_ack_ready = interrupt_ack_ready,
            .legacy_guest_page_size_ready = legacy_guest_page_size_ready,
            .consumes_identity_snapshot = identity.magic_matches,
            .ready_for_probe_handoff = identity.magic_matches and identity.version_supported and identity.device_present and identity.vendor_id_present and queue_register_window_ready and interrupt_ack_ready and legacy_guest_page_size_ready,
        };
    }

    pub fn writeRegister(self: *Self, register: Register, value: u32) !u32 {
        switch (register) {
            .queue_sel => {
                if (value >= self.queue_count) return error.QueueSelectionOutOfRange;
                self.selected_queue = @intCast(value);
                return value;
            },
            .queue_num => {
                const queue = self.queueForSelection(self.selected_queue) orelse return error.QueueSelectionOutOfRange;
                if (value == 0) return error.EmptyQueueSize;
                if (value > queue.advertised_size) return error.QueueSizeExceedsAdvertised;
                queue.programmed_size = @intCast(value);
                return value;
            },
            .queue_ready => {
                const queue = self.queueForSelection(self.selected_queue) orelse return error.QueueSelectionOutOfRange;
                queue.ready = value != 0;
                return value;
            },
            .device_features_sel => {
                if (value >= self.device_feature_words.len) return error.FeatureWordOutOfRange;
                self.selected_device_feature_word = value;
                return value;
            },
            .driver_features_sel => {
                if (value >= self.driver_feature_words.len) return error.FeatureWordOutOfRange;
                self.selected_driver_feature_word = value;
                return value;
            },
            .interrupt_ack => {
                self.interrupt_ack_mask = value;
                return value;
            },
            .guest_page_size => {
                self.legacy_guest_page_size = value;
                return value;
            },
        }
    }

    fn queueForSelection(self: *const Self, selected: u16) ?*QueueState {
        if (selected >= self.queue_count) return null;
        return @constCast(&self.queues[selected]);
    }

    fn selectedDeviceFeatureWordInRange(self: *const Self) bool {
        return self.selected_device_feature_word < self.device_feature_words.len;
    }

    fn selectedDriverFeatureWordInRange(self: *const Self) bool {
        return self.selected_driver_feature_word < self.driver_feature_words.len;
    }

    fn selectedDeviceFeatureWordIndex(self: *const Self) usize {
        return @intCast(self.selected_device_feature_word);
    }

    fn selectedDriverFeatureWordIndex(self: *const Self) usize {
        return @intCast(self.selected_driver_feature_word);
    }

    fn readConfigWord(self: *const Self, relative_offset: u32) !u32 {
        const end = std.math.add(u32, relative_offset, 4) catch return error.ConfigWindowOffsetOutOfRange;
        if (end > self.config_bytes_len) return error.ConfigWindowOffsetOutOfRange;

        var value: u32 = 0;
        for (0..4) |index| {
            value |= @as(u32, self.config_bytes[relative_offset + index]) << @intCast(index * 8);
        }
        return value;
    }
};

fn changedByteMask(previous_value: u32, planned_value: u32) u4 {
    var mask: u4 = 0;
    inline for (0..4) |index| {
        const shift: u5 = @intCast(index * 8);
        const previous_byte = @as(u8, @truncate(previous_value >> shift));
        const planned_byte = @as(u8, @truncate(planned_value >> shift));
        if (previous_byte != planned_byte) {
            mask |= @as(u4, 1) << @intCast(index);
        }
    }
    return mask;
}

test "phase10 virtio mmio zero-valued staged feature words stay known for negotiation summaries" {
    var device = try VirtioMmioLab.init(71, &[_]u16{ 8, 16 });
    try device.stageDeviceFeatureWord(0, 0);
    try device.stageDriverFeatureWord(0, 0);

    const summary = device.featureNegotiationSummary();
    try std.testing.expect(summary.device_feature_selector_in_range);
    try std.testing.expect(summary.driver_feature_selector_in_range);
    try std.testing.expect(summary.selected_feature_words_in_range);
    try std.testing.expect(summary.device_features_known);
    try std.testing.expect(summary.driver_features_known);
    try std.testing.expect(summary.negotiation_possible);
    try std.testing.expect(summary.feature_words_match);
    try std.testing.expectEqual(@as(u32, 0), summary.device_feature_word);
    try std.testing.expectEqual(@as(u32, 0), summary.driver_feature_word);
    try std.testing.expectEqual(@as(u32, 0), summary.negotiated_feature_word);
    try std.testing.expectEqual(@as(u32, 0), summary.device_only_feature_word);
    try std.testing.expectEqual(@as(u32, 0), summary.driver_only_feature_word);
}

test "phase10 virtio mmio negotiation summary reports shared and mismatched feature bits" {
    var device = try VirtioMmioLab.init(76, &[_]u16{ 8, 16 });
    try device.stageDeviceFeatureWord(0, 0b1110);
    try device.stageDriverFeatureWord(0, 0b1011);

    const summary = device.featureNegotiationSummary();
    try std.testing.expect(summary.selected_feature_words_in_range);
    try std.testing.expect(summary.negotiation_possible);
    try std.testing.expect(!summary.feature_words_match);
    try std.testing.expectEqual(@as(u32, 0b1010), summary.negotiated_feature_word);
    try std.testing.expectEqual(@as(u32, 0b0100), summary.device_only_feature_word);
    try std.testing.expectEqual(@as(u32, 0b0001), summary.driver_only_feature_word);
}

test "phase10 virtio mmio negotiation summary exposes out-of-range selector drift" {
    var device = try VirtioMmioLab.init(80, &[_]u16{ 8, 16 });
    try device.stageDeviceFeatureWord(0, 0b0011);
    try device.stageDriverFeatureWord(0, 0b0101);
    device.selected_device_feature_word = 99;

    const summary = device.featureNegotiationSummary();
    try std.testing.expect(!summary.device_feature_selector_in_range);
    try std.testing.expect(summary.driver_feature_selector_in_range);
    try std.testing.expect(!summary.selected_feature_words_in_range);
    try std.testing.expectEqual(@as(u32, 0), summary.device_feature_word);
    try std.testing.expectEqual(@as(u32, 0b0101), summary.driver_feature_word);
    try std.testing.expect(!summary.device_features_known);
    try std.testing.expect(summary.driver_features_known);
    try std.testing.expect(!summary.feature_words_match);
    try std.testing.expect(!summary.negotiation_possible);
}

test "phase10 virtio mmio config-generation bumps clear stale planned config writes" {
    var device = try VirtioMmioLab.init(72, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0, 1, 2, 3, 4, 5, 6, 7 });
    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0xaabb_ccdd);
    try std.testing.expect((try device.configWriteDispositionSummary()).has_changes);
    device.bumpConfigGeneration();
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());
}

test "phase10 virtio mmio restaging config bytes clears stale planned config writes" {
    var device = try VirtioMmioLab.init(75, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });
    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x0203_0407);
    try std.testing.expect((try device.configWriteDispositionSummary()).has_changes);

    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x08, 0x07, 0x06, 0x05 });
    try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());

    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x0506_0709);
    const refreshed = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 0x0506_0708), refreshed.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0506_0709), refreshed.planned_value);
    try std.testing.expectEqual(@as(u4, 0b0001), refreshed.changed_byte_mask);
}

test "phase10 virtio mmio selected queue readiness exposes advertised and programmed sizes" {
    var device = try VirtioMmioLab.init(85, &[_]u16{ 8, 16 });

    _ = try device.writeRegister(.queue_sel, 1);
    var summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 1), summary.selected_queue);
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 0), summary.programmed_queue_size);
    try std.testing.expect(!summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 8);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 8), summary.programmed_queue_size);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(!summary.queue_size_matches_advertised);
    try std.testing.expect(!summary.queue_ready_for_handoff);

    _ = try device.writeRegister(.queue_num, 16);
    _ = try device.writeRegister(.queue_ready, 1);
    summary = try device.selectedQueueReadinessSummary();
    try std.testing.expectEqual(@as(u16, 16), summary.advertised_queue_size);
    try std.testing.expectEqual(@as(u16, 16), summary.programmed_queue_size);
    try std.testing.expect(summary.queue_size_programmed);
    try std.testing.expect(summary.queue_size_matches_advertised);
    try std.testing.expect(summary.queue_ready_for_handoff);
}

test "phase10 virtio mmio legacy probe preflight requires guest-page-size programming" {
    var device = try VirtioMmioLab.init(73, &[_]u16{ 8, 16 });
    device.version = mmio_version_legacy;
    var summary = device.probePreflightSummary();
    try std.testing.expect(!summary.legacy_guest_page_size_ready);
    try std.testing.expect(!summary.ready_for_probe_handoff);
    _ = try device.writeRegister(.guest_page_size, 4096);
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.legacy_guest_page_size_ready);
    try std.testing.expect(summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio probe preflight blocks unsupported identity and missing ownership fields" {
    var device = try VirtioMmioLab.init(83, &[_]u16{ 8, 16 });

    device.magic_value = 0;
    var summary = device.probePreflightSummary();
    try std.testing.expect(!summary.consumes_identity_snapshot);
    try std.testing.expect(summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    device.magic_value = mmio_magic_value;
    device.version = 99;
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.consumes_identity_snapshot);
    try std.testing.expect(!summary.version_supported);
    try std.testing.expect(summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    device.version = mmio_version_modern;
    device.device_id = 0;
    summary = device.probePreflightSummary();
    try std.testing.expect(!summary.device_present);
    try std.testing.expect(summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    device.device_id = 83;
    device.vendor_id = 0;
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.device_present);
    try std.testing.expect(!summary.vendor_id_present);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit" {
    var device = try VirtioMmioLab.init(84, &[_]u16{8});

    device.queue_count = 0;
    var summary = device.probePreflightSummary();
    try std.testing.expect(!summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    device.queue_count = 1;
    device.interrupt_ack_mask = 0;
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(!summary.interrupt_ack_ready);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    device.interrupt_ack_mask = 0x3;
    summary = device.probePreflightSummary();
    try std.testing.expect(summary.bounded_queue_register_window_ready);
    try std.testing.expect(summary.interrupt_ack_ready);
    try std.testing.expect(summary.ready_for_probe_handoff);
}

test "phase10 virtio mmio interrupt-ack disposition keeps bounded queue and config bits explicit" {
    var device = try VirtioMmioLab.init(77, &[_]u16{ 8, 16 });
    device.stageInterruptStatus(0b111);

    const summary = device.interruptAckDispositionSummary(0b111);
    try std.testing.expectEqual(@as(u32, 0b111), summary.requested_bits);
    try std.testing.expectEqual(@as(u32, 0b111), summary.pending_bits);
    try std.testing.expectEqual(@as(u32, 0b011), summary.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0b100), summary.ignored_bits);
    try std.testing.expectEqual(@as(u32, 0b100), summary.remaining_pending_bits);
    try std.testing.expect(summary.has_acknowledgements);
    try std.testing.expectEqual(@as(u32, 0b111), device.interrupt_status);

    _ = try device.writeRegister(.interrupt_ack, 0b001);
    const queue_only = device.interruptAckDispositionSummary(0b011);
    try std.testing.expectEqual(@as(u32, 0b001), queue_only.acknowledged_bits);
    try std.testing.expectEqual(@as(u32, 0b010), queue_only.ignored_bits);
    try std.testing.expectEqual(@as(u32, 0b110), queue_only.remaining_pending_bits);
}

test "phase10 virtio mmio disposition reports byte-level deltas without mutating config bytes" {
    var device = try VirtioMmioLab.init(74, &[_]u16{ 8, 16 });
    try device.stageConfigBytes(&[_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0x05, 0x04, 0x03, 0x02 });
    const before = device.config_bytes;

    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x0203_0407);
    const one_byte_change = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 4), one_byte_change.relative_offset);
    try std.testing.expectEqual(@as(u32, mmio_window_bytes + 4), one_byte_change.absolute_offset);
    try std.testing.expectEqual(@as(u32, 7), one_byte_change.relative_end_offset);
    try std.testing.expectEqual(@as(u32, mmio_window_bytes + 7), one_byte_change.absolute_end_offset);
    try std.testing.expectEqual(@as(u32, 0x0203_0405), one_byte_change.previous_value);
    try std.testing.expectEqual(@as(u32, 0x0203_0407), one_byte_change.planned_value);
    try std.testing.expectEqual(@as(u4, 0b0001), one_byte_change.changed_byte_mask);
    try std.testing.expect(one_byte_change.has_changes);
    try std.testing.expectEqualSlices(u8, before[0..8], device.config_bytes[0..8]);

    _ = try device.planConfigWriteOffset(mmio_window_bytes + 4, 0x0203_0405);
    const no_op = try device.configWriteDispositionSummary();
    try std.testing.expectEqual(@as(u32, 0x0203_0405), no_op.previous_value);
    try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);
    try std.testing.expect(!no_op.has_changes);
    try std.testing.expectEqualSlices(u8, before[0..8], device.config_bytes[0..8]);
}
