const std = @import("std");

pub const max_nr_hvc_consoles: usize = 16;
pub const alloc_tty_adapters: usize = 8;
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

pub const HvOpsHeaderSurface = struct {
    has_get_chars: bool,
    has_put_chars: bool,
    has_flush: bool,
    has_notifier_add: bool,
    has_notifier_del: bool,
    has_notifier_hangup: bool,
    has_tiocmget: bool,
    has_tiocmset: bool,
    has_dtr_rts: bool,
};

pub const HeaderParitySnapshot = struct {
    anchor: []const u8,
    max_nr_hvc_consoles: usize,
    alloc_tty_adapters: usize,
    exports_instantiate: bool,
    exports_alloc: bool,
    exports_remove: bool,
    exports_poll: bool,
    exports_resize: bool,
    hv_ops: HvOpsHeaderSurface,
    keeps_tty_registration_out_of_scope: bool,
    keeps_live_hypervisor_io_out_of_scope: bool,
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

pub const TtyRegistrationHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    setup_hvc_console_pending: bool,
    tty_registration_pending: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    khvcd_kick_on_open: bool,
    khvcd_kick_on_unthrottle: bool,
    khvcd_polling_pending: bool,
    notifier_callbacks_pending: bool,
    host_io_pending: bool,
};

pub const KhvcdPollingContractRequest = struct {
    close: CloseRequest = .{},
    notifier_add_pending: bool = false,
    notifier_del_pending: bool = false,
    notifier_hangup_pending: bool = false,
    read_poll_pending: bool = false,
    write_poll_pending: bool = false,
};

pub const KhvcdPollingContractSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    final_close_wait_required: bool,
    clears_port_initialized_on_final_close: bool,
    keeps_console_binding: bool,
    tty_registration_pending: bool,
    khvcd_polling_pending: bool,
    notifier_driven_wakeup: bool,
    poll_driven_wakeup: bool,
    khvcd_wakeup_required: bool,
    reschedule_required: bool,
    notifier_add_pending: bool,
    notifier_del_pending: bool,
    notifier_hangup_pending: bool,
    read_poll_pending: bool,
    write_poll_pending: bool,
    teardown_host_io_pending: bool,
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
            .touches_tty_registration = false,
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

    pub fn summarizeTtyRegistrationHandoff(self: *const Self, request: CloseRequest) !TtyRegistrationHandoffSnapshot {
        const close = try self.summarizeCloseBoundary(request);

        return .{
            .anchor = descriptor().anchor,
            .slot_index = close.slot_index,
            .vtermno = close.vtermno,
            .adapter_present = close.adapter_present,
            .setup_hvc_console_pending = true,
            .tty_registration_pending = true,
            .final_close_wait_required = close.close_wait_required,
            .clears_port_initialized_on_final_close = close.clears_port_initialized,
            .keeps_console_binding = close.keeps_console_binding,
            .khvcd_kick_on_open = true,
            .khvcd_kick_on_unthrottle = true,
            .khvcd_polling_pending = true,
            .notifier_callbacks_pending = true,
            .host_io_pending = true,
        };
    }

    pub fn summarizeKhvcdPollingContract(
        self: *const Self,
        request: KhvcdPollingContractRequest,
    ) !KhvcdPollingContractSnapshot {
        const handoff = try self.summarizeTtyRegistrationHandoff(request.close);
        const notifier_driven_wakeup = request.notifier_add_pending or
            request.notifier_del_pending or
            request.notifier_hangup_pending;
        const poll_driven_wakeup = request.read_poll_pending or request.write_poll_pending;

        return .{
            .anchor = descriptor().anchor,
            .slot_index = handoff.slot_index,
            .vtermno = handoff.vtermno,
            .adapter_present = handoff.adapter_present,
            .final_close_wait_required = handoff.final_close_wait_required,
            .clears_port_initialized_on_final_close = handoff.clears_port_initialized_on_final_close,
            .keeps_console_binding = handoff.keeps_console_binding,
            .tty_registration_pending = handoff.tty_registration_pending,
            .khvcd_polling_pending = handoff.khvcd_polling_pending,
            .notifier_driven_wakeup = notifier_driven_wakeup,
            .poll_driven_wakeup = poll_driven_wakeup,
            .khvcd_wakeup_required = handoff.khvcd_kick_on_open or
                handoff.khvcd_kick_on_unthrottle or
                notifier_driven_wakeup or
                poll_driven_wakeup,
            .reschedule_required = poll_driven_wakeup,
            .notifier_add_pending = request.notifier_add_pending,
            .notifier_del_pending = request.notifier_del_pending,
            .notifier_hangup_pending = request.notifier_hangup_pending,
            .read_poll_pending = request.read_poll_pending,
            .write_poll_pending = request.write_poll_pending,
            .teardown_host_io_pending = handoff.host_io_pending or poll_driven_wakeup,
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

pub fn headerParitySnapshot() HeaderParitySnapshot {
    return .{
        .anchor = "drivers/tty/hvc/hvc_console.h",
        .max_nr_hvc_consoles = max_nr_hvc_consoles,
        .alloc_tty_adapters = alloc_tty_adapters,
        .exports_instantiate = true,
        .exports_alloc = true,
        .exports_remove = true,
        .exports_poll = true,
        .exports_resize = true,
        .hv_ops = .{
            .has_get_chars = true,
            .has_put_chars = true,
            .has_flush = true,
            .has_notifier_add = true,
            .has_notifier_del = true,
            .has_notifier_hangup = true,
            .has_tiocmget = true,
            .has_tiocmset = true,
            .has_dtr_rts = true,
        },
        .keeps_tty_registration_out_of_scope = true,
        .keeps_live_hypervisor_io_out_of_scope = true,
    };
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
    var donecr = false;

    for (input) |char| {
        if (char == '\n' and !donecr) {
            output[index] = '\r';
            index += 1;
            output[index] = '\n';
            index += 1;
            donecr = true;
        } else {
            output[index] = char;
            index += 1;
            donecr = false;
        }
    }

    return index;
}
