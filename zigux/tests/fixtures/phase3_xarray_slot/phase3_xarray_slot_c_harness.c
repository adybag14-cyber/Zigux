#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_xa_slot_summary summary)
{
	printf("{\"scanned_count\":%u,\"null_count\":%u,\"value_count\":%u,\"error_count\":%u,\"plain_count\":%u,\"flags\":%u}",
	       summary.scanned_count,
	       summary.null_count,
	       summary.value_count,
	       summary.error_count,
	       summary.plain_count,
	       summary.flags);
}

int main(void)
{
	unsigned long slots[] = {
		0,
		0x2000UL,
		zigux_xa_mk_value(11),
		zigux_err_addr_from_errno(-2),
		zigux_xa_mk_value(29),
		zigux_err_addr_from_errno(-12),
	};
	struct zigux_xa_slot_view truncated = zigux_xa_slot_view_from_entries(slots, 6, 5);
	struct zigux_xa_slot_view full = zigux_xa_slot_view_from_entries(slots, 6, 6);
	struct zigux_xa_slot_view empty = { .slots_addr = 0, .slot_count = 0, .max_scan = 0 };

	printf("{\"constants\":{\"xa_slot_flag_truncated\":%u},", ZIGUX_XA_SLOT_FLAG_TRUNCATED);
	printf("\"truncated\":{\"entry_3\":%lu,\"summary\":", zigux_xa_slot_entry_at(&truncated, 3));
	print_summary(zigux_xa_slot_summarize(&truncated));
	printf("},\"full\":{\"entry_5\":%lu,\"summary\":", zigux_xa_slot_entry_at(&full, 5));
	print_summary(zigux_xa_slot_summarize(&full));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_xa_slot_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_xa_slot_summarize(&empty));
	printf("}}\n");
	return 0;
}
