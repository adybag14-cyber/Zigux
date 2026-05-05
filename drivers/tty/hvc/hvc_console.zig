const std = @import("std");

pub const max_nr_hvc_consoles: usize = 16;
pub const outbuf_capacity: usize = 16;
pub const removed_vtermno: u32 = std.math.maxInt(u32);
pub const eagain: isize = -11;
pub const close_wait_hz_divisor: usize = 100;

pub const FlushIntent = enum {
    none,
    retry_after_eagain,
    final_drain,
};

pub const FlushProgress = enum {
    no_progress,
    partial_write,
    fully_written,
    dropped_on_error,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_simple_driver_starter: bool,
    touches_tty_registration: bool,
    touches_polling_kthread: bool,
    touches_live_hypervisor_io: bool,
};

pub const SlotSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    usable_for_console: bool,
};

pub const CloseRequest = struct {
    hung_up: bool = false,
    port_initialized: bool = false,
    open_count_before_close: usize = 1,
};

pub const CloseBoundarySnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    hung_up: bool,
    close_skipped: bool,
    port_initialized: bool,
    open_count_before_close: usize,
    open_count_after_close: usize,
    final_close: bool,
    close_wait_required: bool,
    close_wait_hz_divisor: usize,
    clears_port_initialized: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
};

pub const CleanupHandoffRequest = struct {
    hung_up: bool = false,
    final_close: bool = true,
    tty_port_reference_live: bool = true,
};

pub const CleanupHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    close_skipped: bool,
    final_close: bool,
    tty_port_reference_live: bool,
    tty_port_put_requested: bool,
    drops_tty_port_reference: bool,
    deferred_final_release: bool,
};

pub const RemoveHandoffRequest = struct {
    console_index_registered: bool = true,
    tty_present: bool = true,
};

pub const RemoveHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    clears_console_slot_binding: bool,
    keeps_irq_for_followup_hangup: bool,
    drops_init_kref_port_reference: bool,
    tty_vhangup_requested: bool,
    tty_kref_put_after_vhangup: bool,
    teardown_via_hangup_pending: bool,
    host_io_pending: bool,
};

pub const TtyRegistrationRequest = struct {
    console_index_matches_boot_console: bool = true,
    notifier_target_present: bool = true,
};

pub const TtyRegistrationHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    tty_driver_registration_requested: bool,
    tty_device_registration_requested: bool,
    console_registration_requested: bool,
    keeps_console_binding_until_remove: bool,
    close_wait_owned_by_hvc_close: bool,
    khvcd_wakeup_reviewable: bool,
    khvcd_worker_execution_deferred: bool,
    notifier_target_present: bool,
    notifier_callbacks_deferred: bool,
    host_io_deferred: bool,
    remove_handoff_still_required: bool,
};

pub const SysrqHandoffRequest = struct {
    console_index_matches_boot_console: bool = true,
    sysrq_break_seen: bool = true,
    notifier_target_present: bool = true,
};

pub const SysrqHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    console_index_matches_boot_console: bool,
    sysrq_break_seen: bool,
    sysrq_dispatch_reviewable: bool,
    sysrq_dispatch_requested: bool,
    notifier_target_present: bool,
    notifier_callbacks_deferred: bool,
    khvcd_worker_execution_deferred: bool,
    host_io_deferred: bool,
    remove_handoff_still_required: bool,
};

pub const NotifierHandoffRequest = struct {
    tty_registration_ready: bool = true,
    sysrq_dispatch_requested: bool = true,
    notifier_target_present: bool = true,
};

pub const NotifierHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    tty_registration_ready: bool,
    sysrq_dispatch_requested: bool,
    notifier_target_present: bool,
    notifier_registration_reviewable: bool,
    notifier_registration_requested: bool,
    notifier_callbacks_deferred: bool,
    notifier_unregister_deferred: bool,
    khvcd_worker_execution_deferred: bool,
    host_io_deferred: bool,
    remove_handoff_still_required: bool,
};

pub const WriteSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    adapter_present: bool,
    framed_len: usize,
    framed: [outbuf_capacity * 2]u8,
    remaining_len: usize,
    remaining: [outbuf_capacity * 2]u8,
    flush_intent: FlushIntent,
    flush_progress: FlushProgress,
    final_flush: bool,
    dropped_on_error: bool,
};

pub const HvcConsoleLab = struct {
    const Self = @This();

    slot_index: usize,
    vtermno: u32 = removed_vtermno,
    adapter_present: bool = false,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "hvc_console_lab",
            .anchor = "drivers/tty/hvc/hvc_console.c",
            .provides_simple_driver_starter = true,
            .touches_tty_registration = true,
            .touches_polling_kthread = false,
            .touches_live_hypervisor_io = false,
        };
    }

    pub fn init(slot_index: usize) !Self {
        try validateConsoleSlot(slot_index);
        return .{ .slot_index = slot_index };
    }

    pub fn instantiate(self: *Self, vtermno: u32) SlotSnapshot {
        self.vtermno = vtermno;
        self.adapter_present = true;
        return self.slotSnapshot();
    }

    pub fn teardown(self: *Self) SlotSnapshot {
        self.vtermno = removed_vtermno;
        self.adapter_present = false;
        return self.slotSnapshot();
    }

    pub fn slotSnapshot(self: *const Self) SlotSnapshot {
        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = self.adapter_present,
            .usable_for_console = self.adapter_present and self.vtermno != removed_vtermno,
        };
    }

    pub fn summarizeCloseBoundary(self: *const Self, request: CloseRequest) !CloseBoundarySnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;
        if (request.open_count_before_close == 0) return error.InvalidOpenCount;

        const close_skipped = request.hung_up;
        const open_count_after_close = if (close_skipped)
            request.open_count_before_close
        else
            request.open_count_before_close - 1;
        const final_close = !close_skipped and open_count_after_close == 0;
        const close_wait_required = final_close and request.port_initialized;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = self.adapter_present,
            .hung_up = request.hung_up,
            .close_skipped = close_skipped,
            .port_initialized = request.port_initialized,
            .open_count_before_close = request.open_count_before_close,
            .open_count_after_close = open_count_after_close,
            .final_close = final_close,
            .close_wait_required = close_wait_required,
            .close_wait_hz_divisor = close_wait_hz_divisor,
            .clears_port_initialized = close_wait_required,
            .keeps_console_binding = true,
            .tty_registration_pending = true,
        };
    }

    pub fn summarizeCleanupHandoff(
        self: *const Self,
        request: CleanupHandoffRequest,
    ) !CleanupHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;
        if (!request.final_close and !request.hung_up) {
            return error.CleanupRequiresFinalCloseOrHangup;
        }
        if (!request.tty_port_reference_live) {
            return error.CleanupRequiresTtyPortReference;
        }
        const final_close = request.final_close and !request.hung_up;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = slot.slot_index,
            .vtermno = slot.vtermno,
            .adapter_present = slot.adapter_present,
            .close_skipped = request.hung_up,
            .final_close = final_close,
            .tty_port_reference_live = request.tty_port_reference_live,
            .tty_port_put_requested = true,
            .drops_tty_port_reference = true,
            .deferred_final_release = true,
        };
    }

    pub fn summarizeRemoveHandoff(
        self: *const Self,
        request: RemoveHandoffRequest,
    ) !RemoveHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = slot.slot_index,
            .vtermno = slot.vtermno,
            .adapter_present = slot.adapter_present,
            .clears_console_slot_binding = request.console_index_registered,
            .keeps_irq_for_followup_hangup = request.tty_present,
            .drops_init_kref_port_reference = true,
            .tty_vhangup_requested = request.tty_present,
            .tty_kref_put_after_vhangup = request.tty_present,
            .teardown_via_hangup_pending = request.tty_present,
            .host_io_pending = request.tty_present,
        };
    }

    pub fn summarizeTtyRegistrationHandoff(
        self: *const Self,
        request: TtyRegistrationRequest,
    ) !TtyRegistrationHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = self.adapter_present,
            .tty_driver_registration_requested = true,
            .tty_device_registration_requested = true,
            .console_registration_requested = request.console_index_matches_boot_console,
            .keeps_console_binding_until_remove = request.console_index_matches_boot_console,
            .close_wait_owned_by_hvc_close = true,
            .khvcd_wakeup_reviewable = true,
            .khvcd_worker_execution_deferred = true,
            .notifier_target_present = request.notifier_target_present,
            .notifier_callbacks_deferred = request.notifier_target_present,
            .host_io_deferred = true,
            .remove_handoff_still_required = true,
        };
    }

    pub fn summarizeSysrqHandoff(
        self: *const Self,
        request: SysrqHandoffRequest,
    ) !SysrqHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        const sysrq_dispatch_requested = request.console_index_matches_boot_console and
            request.sysrq_break_seen;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = slot.adapter_present,
            .console_index_matches_boot_console = request.console_index_matches_boot_console,
            .sysrq_break_seen = request.sysrq_break_seen,
            .sysrq_dispatch_reviewable = true,
            .sysrq_dispatch_requested = sysrq_dispatch_requested,
            .notifier_target_present = request.notifier_target_present,
            .notifier_callbacks_deferred = sysrq_dispatch_requested and request.notifier_target_present,
            .khvcd_worker_execution_deferred = true,
            .host_io_deferred = true,
            .remove_handoff_still_required = true,
        };
    }

    pub fn summarizeNotifierHandoff(
        self: *const Self,
        request: NotifierHandoffRequest,
    ) !NotifierHandoffSnapshot {
        const slot = self.slotSnapshot();
        if (!slot.usable_for_console) return error.ConsoleUnavailable;

        const notifier_registration_requested = request.tty_registration_ready and
            request.notifier_target_present;
        const notifier_callbacks_deferred = request.sysrq_dispatch_requested and
            request.notifier_target_present;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .vtermno = self.vtermno,
            .adapter_present = self.adapter_present,
            .tty_registration_ready = request.tty_registration_ready,
            .sysrq_dispatch_requested = request.sysrq_dispatch_requested,
            .notifier_target_present = request.notifier_target_present,
            .notifier_registration_reviewable = true,
            .notifier_registration_requested = notifier_registration_requested,
            .notifier_callbacks_deferred = notifier_callbacks_deferred,
            .notifier_unregister_deferred = request.notifier_target_present,
            .khvcd_worker_execution_deferred = true,
            .host_io_deferred = true,
            .remove_handoff_still_required = true,
        };
    }

    pub fn stageWrite(self: *const Self, input: []const u8, put_result: isize) !WriteSnapshot {
        if (!self.slotSnapshot().usable_for_console) return error.ConsoleUnavailable;

        var framed: [outbuf_capacity * 2]u8 = undefined;
        const framed_len = try frameConsoleWrite(input, &framed);

        var remaining: [outbuf_capacity * 2]u8 = undefined;
        @memset(&remaining, 0);

        const summary = summarizeFlushProgress(framed[0..framed_len], put_result, &remaining);

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .adapter_present = self.adapter_present,
            .framed_len = framed_len,
            .framed = framed,
            .remaining_len = summary.remaining_len,
            .remaining = remaining,
            .flush_intent = summary.flush_intent,
            .flush_progress = summary.flush_progress,
            .final_flush = true,
            .dropped_on_error = summary.dropped_on_error,
        };
    }
};

pub fn validateConsoleSlot(slot_index: usize) !void {
    if (slot_index >= max_nr_hvc_consoles) return error.InvalidConsoleSlot;
}

const FlushProgressSummary = struct {
    remaining_len: usize,
    flush_intent: FlushIntent,
    flush_progress: FlushProgress,
    dropped_on_error: bool,
};

fn summarizeFlushProgress(
    framed: []const u8,
    put_result: isize,
    remaining: *[outbuf_capacity * 2]u8,
) FlushProgressSummary {
    if (put_result <= 0) {
        if (put_result == eagain) {
            std.mem.copyForwards(u8, remaining[0..framed.len], framed);
            return .{
                .remaining_len = framed.len,
                .flush_intent = .retry_after_eagain,
                .flush_progress = .no_progress,
                .dropped_on_error = false,
            };
        }

        return .{
            .remaining_len = 0,
            .flush_intent = .none,
            .flush_progress = .dropped_on_error,
            .dropped_on_error = true,
        };
    }

    const written = @min(@as(usize, @intCast(put_result)), framed.len);
    const remaining_len = framed.len - written;
    if (remaining_len > 0) {
        std.mem.copyForwards(u8, remaining[0..remaining_len], framed[written..]);
    }

    return .{
        .remaining_len = remaining_len,
        .flush_intent = .final_drain,
        .flush_progress = if (remaining_len == 0) .fully_written else .partial_write,
        .dropped_on_error = false,
    };
}

fn frameConsoleWrite(input: []const u8, output: *[outbuf_capacity * 2]u8) !usize {
    if (input.len > outbuf_capacity) return error.InputTooLarge;

    var index: usize = 0;
    var previous_was_cr = false;

    for (input) |char| {
        if (char == '\n' and !previous_was_cr) {
            output[index] = '\r';
            index += 1;
        }

        output[index] = char;
        index += 1;
        previous_was_cr = char == '\r';
    }

    return index;
}
