#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_idr_slot_summary summary)
{
	printf("{\"scanned_count\":%u,\"present_count\":%u,\"value_count\":%u,\"error_count\":%u,\"plain_count\":%u,\"first_present_id\":%u,\"next_free_id\":%u,\"flags\":%u}",
	       summary.scanned_count,
	       summary.present_count,
	       summary.value_count,
	       summary.error_count,
	       summary.plain_count,
	       summary.first_present_id,
	       summary.next_free_id,
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
	struct zigux_idr_slot_view truncated = zigux_idr_slot_view_from_entries(slots, 64, 6, 5);
	struct zigux_idr_slot_view full = zigux_idr_slot_view_from_entries(slots, 64, 6, 6);
	struct zigux_idr_slot_view empty = { .slots_addr = 0, .base_id = 32, .slot_count = 0, .max_scan = 0, .reserved = 0 };

	printf("{\"constants\":{\"idr_slot_flag_truncated\":%u},", ZIGUX_IDR_SLOT_FLAG_TRUNCATED);
	printf("\"truncated\":{\"entry_2\":%lu,\"summary\":", zigux_idr_slot_entry_at(&truncated, 2));
	print_summary(zigux_idr_slot_summarize(&truncated));
	printf("},\"full\":{\"entry_5\":%lu,\"summary\":", zigux_idr_slot_entry_at(&full, 5));
	print_summary(zigux_idr_slot_summarize(&full));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_idr_slot_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_idr_slot_summarize(&empty));
	printf("}}\n");
	return 0;
}
