"""
Embedded Python Block: File Source to Tagged Stream
"""

import numpy as np
from gnuradio import gr
import time
import pmt
import os.path
import sys
import base64

"""
State definitions
    0   idle
    1   send preamble
    2   send file data
    3   send file name
    4   send post filler
"""
class blk(gr.sync_block):
    def __init__(self, FileName='None', Pkt_len=52):
        gr.sync_block.__init__(
            self,
            name='EPB: File Source to Tagged Stream',
            in_sig=None,
            out_sig=[np.uint8])
        self.FileName = FileName
        self.Pkt_len = Pkt_len
        self.state = 0      # idle state
        self.pre_count = 0
        self.indx = 0
        self._debug = 0     
        self.data = ""
        self.transmission_complete = False  # New flag to track completion

        if (os.path.exists(self.FileName)):
            self.f_in = open(self.FileName, 'rb')
            self._eof = False
            if (self._debug):
                print("File name:", self.FileName)
            self.state = 1  # Start with preamble
        else:
            print(self.FileName, 'does not exist')
            self._eof = True
            self.state = 0

        # Preamble and filler definitions (unchanged)
        self.char_list = [37,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        self.c_len = len(self.char_list)
        self.filler = [37,85,85,85, 35,69,79,70, 85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        self.f_len = len(self.filler)

    def work(self, input_items, output_items):
        if self.transmission_complete:
            return 0  # Stay idle after transmission

        if (self.state == 0):
            return 0  # Idle

        elif (self.state == 1):
            # Send preamble (ONCE)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.c_len)
            self.add_item_tag(0, self.indx, key1, val1)
            self.indx += self.c_len
            for i in range(self.c_len):
                output_items[0][i] = self.char_list[i]
            self.state = 2  # Move to file data
            return self.c_len

        elif (self.state == 2):
            # Send file data (ONCE per chunk)
            buff = self.f_in.read(self.Pkt_len)
            b_len = len(buff)
            if b_len == 0:
                self._eof = True
                self.f_in.close()
                self.state = 3  # Send filename
                return 0
            encoded = base64.b64encode(buff)
            e_len = len(encoded)
            key0 = pmt.intern("packet_len")
            val0 = pmt.from_long(e_len)
            self.add_item_tag(0, self.indx, key0, val0)
            self.indx += e_len
            for i in range(e_len):
                output_items[0][i] = encoded[i]
            return e_len

        elif (self.state == 3):
            # Send filename (ONCE)
            fn_len = len(self.FileName)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(fn_len + 8)
            self.add_item_tag(0, self.indx, key1, val1)
            self.indx += (fn_len + 8)
            # Fill first 8 bytes with filler
            for i in range(8):
                output_items[0][i] = self.filler[i]
            # Append filename
            for j, char in enumerate(self.FileName):
                output_items[0][8 + j] = ord(char)
            self.state = 4
            return fn_len + 8

        elif (self.state == 4):
            # Send post-filler (ONCE)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.f_len)
            self.add_item_tag(0, self.indx, key1, val1)
            self.indx += self.f_len
            for i in range(self.f_len):
                output_items[0][i] = self.filler[i]
            self.transmission_complete = True  # Mark transmission as complete
            return self.f_len

        return 0
