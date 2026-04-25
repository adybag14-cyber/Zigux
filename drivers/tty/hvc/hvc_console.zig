const std = @import("std");

pub const max_nr_hvc_consoles: usize = 16;
pub const outbuf_capacity: usize = 16;
pub const removed_vtermno: u32 = std.math.maxInt(u32);
pub const eagain: isize = -11;

pub const FlushIntent = enum {
    none,
    retry_after_eagain,
    final_drain,
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

pub const WriteSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    adapter_present: bool,
    framed_len: usize,
    framed: [outbuf_capacity * 2]u8,
    remaining_len: usize,
    remaining: [outbuf_capacity * 2]u8,
    flush_intent: FlushIntent,
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

    pub fn stageWrite(self: *const Self, input: []const u8, put_result: isize) !WriteSnapshot {
        if (!self.slotSnapshot().usable_for_console) return error.ConsoleUnavailable;

        var framed: [outbuf_capacity * 2]u8 = undefined;
        const framed_len = try frameConsoleWrite(input, &framed);

        var remaining: [outbuf_capacity * 2]u8 = undefined;
        @memset(&remaining, 0);

        var remaining_len: usize = 0;
        var flush_intent: FlushIntent = .none;
        var dropped_on_error = false;

        if (put_result <= 0) {
            if (put_result == eagain) {
                flush_intent = .retry_after_eagain;
                remaining_len = framed_len;
                std.mem.copyForwards(u8, remaining[0..remaining_len], framed[0..remaining_len]);
            } else {
                dropped_on_error = true;
            }
        } else {
            const written = @min(@as(usize, @intCast(put_result)), framed_len);
            remaining_len = framed_len - written;
            if (remaining_len > 0) {
                std.mem.copyForwards(u8, remaining[0..remaining_len], framed[written..framed_len]);
            }
            flush_intent = .final_drain;
        }

        return .{
            .anchor = descriptor().anchor,
            .slot_index = self.slot_index,
            .adapter_present = self.adapter_present,
            .framed_len = framed_len,
            .framed = framed,
            .remaining_len = remaining_len,
            .remaining = remaining,
            .flush_intent = flush_intent,
            .final_flush = true,
            .dropped_on_error = dropped_on_error,
        };
    }
};

pub fn validateConsoleSlot(slot_index: usize) !void {
    if (slot_index >= max_nr_hvc_consoles) return error.InvalidConsoleSlot;
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
