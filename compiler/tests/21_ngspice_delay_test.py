#!/usr/bin/env python3
"""
Run a regression test on various srams
"""

import unittest
from testutils import header,openram_test
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
import globals
from globals import OPTS
import debug

class timing_sram_test(openram_test):

    def runTest(self):
        globals.init_openram("config_20_{0}".format(OPTS.tech_name))
        OPTS.spice_name="ngspice"
        OPTS.analytical_delay = False
        OPTS.trim_netlist = False

        # This is a hack to reload the characterizer __init__ with the spice version
        from importlib import reload
        import characterizer
        reload(characterizer)
        from characterizer import delay
        if not OPTS.spice_exe:
            debug.error("Could not find {} simulator.".format(OPTS.spice_name),-1)

        from sram import sram
        from sram_config import sram_config
        c = sram_config(word_size=1,
                        num_words=16,
                        num_banks=1)
        c.words_per_row=1
        debug.info(1, "Testing timing for sample 1bit, 16words SRAM with 1 bank")
        s = sram(c, name="sram1")

        tempspice = OPTS.openram_temp + "temp.sp"
        s.sp_write(tempspice)

        probe_address = "1" * s.s.addr_size
        probe_data = s.s.word_size - 1
        debug.info(1, "Probe address {0} probe data bit {1}".format(probe_address, probe_data))

        corner = (OPTS.process_corners[0], OPTS.supply_voltages[0], OPTS.temperatures[0])
        d = delay(s.s, tempspice, corner)
        import tech
        loads = [tech.spice["msflop_in_cap"]*4]
        slews = [tech.spice["rise_time"]*2]
        data = d.analyze(probe_address, probe_data, slews, loads)

        if OPTS.tech_name == "freepdk45":
            golden_data = {'delay_hl0': [2.584251],
                            'delay_lh0': [0.22870469999999998],
                            'leakage_power': 0.0009567935,
                            'min_period': 4.844,
                            'read0_power0': [0.0547588],
                            'read1_power0': [0.051159970000000006],
                            'slew_hl0': [0.08164099999999999],
                            'slew_lh0': [0.025474979999999998],
                            'write0_power0': [0.06513271999999999],
                            'write1_power0': [0.058057000000000004]}
        elif OPTS.tech_name == "scn4m_subm":
            golden_data = {'delay_hl0': [3.644147],
                            'delay_lh0': [1.629815],
                            'leakage_power': 0.0009299118999999999,
                            'min_period': 4.688,
                            'read0_power0': [16.28732],
                            'read1_power0': [15.75155],
                            'slew_hl0': [0.6722473],
                            'slew_lh0': [0.3386347],
                            'write0_power0': [18.545450000000002],
                            'write1_power0': [16.81084]}
        else:
            self.assertTrue(False) # other techs fail

        # Check if no too many or too few results
        self.assertTrue(len(data.keys())==len(golden_data.keys()))
        
        self.assertTrue(self.check_golden_data(data,golden_data,0.25))

        globals.end_openram()

# instantiate a copdsay of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
