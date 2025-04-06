import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Custom Looping Number Source',
            in_sig=None,
            out_sig=[np.uint8]
        )
        self.state = 0       # 0: send preamble, 1: send numbers, 2: send EOF
        self.numbers = list(range(1, 11))  # Numbers 1 to 10
        self.preamble = [ord('%'), ord('U'), ord('U'), ord(']')]  # % U U ]
        self.eof_marker = [ord('#'), ord('E'), ord('O'), ord('F')]  # "#EOF"
        self.index = 0

    def work(self, input_items, output_items):
        out = output_items[0]
        produced = 0

        while produced < len(out):
            if self.state == 0:
                # Send preamble "UUUU" (state 0)
                remaining_preamble = min(len(self.preamble), len(out) - produced)
                if remaining_preamble > 0:
                    out[produced:produced+remaining_preamble] = self.preamble[:remaining_preamble]
                    # Add packet_len tag (total length of preamble + numbers + EOF)
                    key = pmt.intern("packet_len")
                    val = pmt.from_long(len(self.preamble) + len(self.numbers) + len(self.eof_marker))
                    self.add_item_tag(0, self.nitems_written(0) + produced, key, val)
                    produced += remaining_preamble
                    if remaining_preamble == len(self.preamble):
                        self.state = 1  # Transition to numbers state

            elif self.state == 1:
                # Send numbers 1-10 (state 1)
                if self.index < len(self.numbers):
                    out[produced] = self.numbers[self.index]
                    produced += 1
                    self.index += 1
                    if self.index == len(self.numbers):
                        self.state = 2  # Transition to EOF state

            elif self.state == 2:
                # Send EOF marker "#EOF" (state 2)
                remaining_eof = min(len(self.eof_marker), len(out) - produced)
                if remaining_eof > 0:
                    out[produced:produced+remaining_eof] = self.eof_marker[:remaining_eof]
                    produced += remaining_eof
                    if remaining_eof == len(self.eof_marker):
                        self.state = 0  # Reset to preamble state
                        self.index = 0  # Reset numbers index

        return produced
