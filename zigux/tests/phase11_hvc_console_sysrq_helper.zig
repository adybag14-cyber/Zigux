const hvc_console = @import("hvc_console");

pub const SysrqHandoffRequest = struct {
    is_kernel_console: bool = false,
    sysrq_pressed_before: bool = false,
    input_char: u8 = 0,
};

pub const SysrqHandoffSnapshot = struct {
    anchor: []const u8,
    slot_index: usize,
    vtermno: u32,
    adapter_present: bool,
    is_kernel_console: bool,
    sysrq_pressed_before: bool,
    input_char: u8,
    toggles_sysrq_mode: bool,
    sysrq_pressed_after: bool,
    invokes_sysrq_handler: bool,
    clears_sysrq_after_handler: bool,
    emits_literal_char: bool,
    consumes_input_without_flip: bool,
    keeps_tty_registration_out_of_scope: bool,
    keeps_live_hypervisor_io_out_of_scope: bool,
    keeps_live_sysrq_execution_out_of_scope: bool,
};

pub fn summarizeSysrqHandoff(
    console: *const hvc_console.HvcConsoleLab,
    request: SysrqHandoffRequest,
) !SysrqHandoffSnapshot {
    const slot = console.slotSnapshot();
    if (!slot.usable_for_console) return error.ConsoleUnavailable;

    const is_toggle = request.is_kernel_console and request.input_char == 0x0f;
    const invokes_sysrq_handler = request.is_kernel_console and request.sysrq_pressed_before and !is_toggle;
    const clears_sysrq_after_handler = invokes_sysrq_handler;
    const sysrq_pressed_after = if (is_toggle)
        !request.sysrq_pressed_before
    else if (invokes_sysrq_handler)
        false
    else
        request.sysrq_pressed_before;
    const emits_literal_char = if (!request.is_kernel_console)
        true
    else if (is_toggle)
        request.sysrq_pressed_before
    else
        !request.sysrq_pressed_before;

    return .{
        .anchor = hvc_console.HvcConsoleLab.descriptor().anchor,
        .slot_index = slot.slot_index,
        .vtermno = slot.vtermno,
        .adapter_present = slot.adapter_present,
        .is_kernel_console = request.is_kernel_console,
        .sysrq_pressed_before = request.sysrq_pressed_before,
        .input_char = request.input_char,
        .toggles_sysrq_mode = is_toggle,
        .sysrq_pressed_after = sysrq_pressed_after,
        .invokes_sysrq_handler = invokes_sysrq_handler,
        .clears_sysrq_after_handler = clears_sysrq_after_handler,
        .emits_literal_char = emits_literal_char,
        .consumes_input_without_flip = !emits_literal_char,
        .keeps_tty_registration_out_of_scope = true,
        .keeps_live_hypervisor_io_out_of_scope = true,
        .keeps_live_sysrq_execution_out_of_scope = true,
    };
}
