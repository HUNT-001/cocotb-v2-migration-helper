import cocotb
from cocotb.result import TestFailure


async def helper(dut):
    dut._log.info("helper running")


@cocotb.test()
async def test_legacy(dut):
    task = cocotb.fork(helper(dut))
    signal_handle = dut._id("data_valid", extended=False)
    raise TestFailure("legacy failure path")