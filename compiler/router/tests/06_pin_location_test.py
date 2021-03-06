#!/usr/bin/env python3
"Run a regresion test the library cells for DRC"

import unittest
from testutils import header,openram_test
import sys,os
sys.path.append(os.path.join(sys.path[0],"../.."))
sys.path.append(os.path.join(sys.path[0],".."))
import globals
import debug

OPTS = globals.OPTS

class pin_location_test(openram_test):
    """
    Simplest two pin route test with no blockages using the pin locations instead of labels.
    """

    def runTest(self):
        globals.init_openram("config_{0}".format(OPTS.tech_name))
        from gds_cell import gds_cell
        from design import design
        from signal_router import signal_router as router

        class routing(design, openram_test):
            """
            A generic GDS design that we can route on.
            """
            def __init__(self, name):
                design.__init__(self, "top")

                # Instantiate a GDS cell with the design
                gds_file = "{0}/{1}.gds".format(os.path.dirname(os.path.realpath(__file__)),name)
                cell = gds_cell(name, gds_file)
                self.add_inst(name=name,
                              mod=cell,
                              offset=[0,0])
                self.connect_inst([])
                
                r=router(gds_file)
                layer_stack =("metal1","via1","metal2")
                # these are user coordinates and layers
                src_pin = [[0.52, 4.099],11]
                tgt_pin = [[3.533, 1.087],11]
                #r.route(layer_stack,src="A",dest="B")
                self.assertTrue(r.route(self,layer_stack,src=src_pin,dest=tgt_pin))

        # This only works for freepdk45 since the coordinates are hard coded
        if OPTS.tech_name == "freepdk45":
            r = routing("06_pin_location_test_{0}".format(OPTS.tech_name))
            self.local_drc_check(r)
        else:
            debug.warning("This test does not support technology {0}".format(OPTS.tech_name))

        # fails if there are any DRC errors on any cells
        globals.end_openram()
                             


# instantiate a copy of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
