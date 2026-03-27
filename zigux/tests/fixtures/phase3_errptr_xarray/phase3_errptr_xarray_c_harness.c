#include <stdio.h>

#include <linux/zigux.h>

int main(void)
{
	unsigned long err_addr = zigux_err_addr_from_errno(-22);
	struct zigux_err_ptr_summary err_summary = zigux_err_addr_summarize(err_addr);
	struct zigux_err_ptr_summary null_summary = zigux_err_addr_summarize(0);
	unsigned long plain_addr = 0x1000UL;
	struct zigux_xa_value_summary plain_summary = zigux_xa_summarize(plain_addr);
	unsigned long encoded_addr = zigux_xa_mk_value(37);
	struct zigux_xa_value_summary encoded_summary = zigux_xa_summarize(encoded_addr);

	printf(
		"{\"constants\":{\"max_errno\":%u,\"err_flag_error\":%u,"
		"\"err_flag_null\":%u,\"xa_flag_value\":%u,\"xa_flag_plain\":%u},"
		"\"err_ptr\":{\"raw_addr\":%lu,\"is_err\":%s,\"errno_code\":%d,"
		"\"summary\":{\"errno_code\":%d,\"flags\":%u}},"
		"\"null_ptr\":{\"is_null\":%s,\"is_null_or_err\":%s,"
		"\"summary\":{\"errno_code\":%d,\"flags\":%u}},"
		"\"xa\":{\"plain\":{\"raw_addr\":%lu,\"is_value\":%s,"
		"\"summary\":{\"raw_addr\":%lu,\"decoded_value\":%u,\"flags\":%u}},"
		"\"encoded\":{\"raw_addr\":%lu,\"is_value\":%s,\"decoded_value\":%u,"
		"\"summary\":{\"raw_addr\":%lu,\"decoded_value\":%u,\"flags\":%u}}}}\n",
		ZIGUX_MAX_ERRNO,
		ZIGUX_ERR_PTR_FLAG_ERROR,
		ZIGUX_ERR_PTR_FLAG_NULL,
		ZIGUX_XA_VALUE_FLAG_VALUE,
		ZIGUX_XA_VALUE_FLAG_PLAIN,
		err_addr,
		zigux_err_addr_is_err(err_addr) ? "true" : "false",
		zigux_err_addr_to_errno(err_addr),
		err_summary.errno_code,
		err_summary.flags,
		zigux_err_addr_is_null(0) ? "true" : "false",
		zigux_err_addr_is_null_or_err(0) ? "true" : "false",
		null_summary.errno_code,
		null_summary.flags,
		plain_addr,
		zigux_xa_is_value(plain_addr) ? "true" : "false",
		plain_summary.raw_addr,
		plain_summary.decoded_value,
		plain_summary.flags,
		encoded_addr,
		zigux_xa_is_value(encoded_addr) ? "true" : "false",
		zigux_xa_to_value(encoded_addr),
		encoded_summary.raw_addr,
		encoded_summary.decoded_value,
		encoded_summary.flags);
	return 0;
}