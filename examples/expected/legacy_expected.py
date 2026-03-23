import cocotb
from cocotb.result import TestFailure


async def helper(dut):
    dut._log.info("helper running")


@cocotb.test()
async def test_legacy(dut):
    task = cocotb.start_soon(helper(dut))
    signal_handle = dut["data_valid"]
    assert False, "legacy failure path"