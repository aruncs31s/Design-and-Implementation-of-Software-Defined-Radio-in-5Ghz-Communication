import numpy as np
from gnuradio import gr
import os
import pmt
import base64

class blk(gr.sync_block):
    def __init__(self, FileName='None', Pkt_len=52):
        gr.sync_block.__init__(
            self,
            name='EPB: File Source to Tagged Stream',
            in_sig=None,
            out_sig=[np.uint8])

        self.FileName = FileName
        self.Pkt_len = Pkt_len
        self.state = 0  # Start in idle state
        self.pre_count = 0
        self.indx = 0
        self._debug = 0
        self._eof = True  # Start with no file loaded
        self.char_list = [37] + [85] * 46 + [93]  # Preamble
        self.filler = [37, 85, 85, 85, 35, 69, 79, 70] + [85] * 40 + [93]  # Post filler
        self.c_len = len(self.char_list)
        self.f_len = len(self.filler)

        # Register message input port for receiving a new file name
        self.message_port_register_in(pmt.intern("file_cmd"))
        self.set_msg_handler(pmt.intern("file_cmd"), self.handle_msg)

        if FileName != 'None':
            self.load_file(FileName)

    def handle_msg(self, msg):
        """Handles new file input via message"""
        if pmt.is_symbol(msg):
            new_filename = pmt.symbol_to_string(msg)
            self.load_file(new_filename)

    def load_file(self, filename):
        """Loads a new file for transmission"""
        if os.path.exists(filename):
            self.FileName = filename
            self.f_in = open(self.FileName, 'rb')
            self._eof = False
            self.state = 1  # Start transmission
            print(f"Loaded file: {self.FileName}")
        else:
            print(f"File '{filename}' not found.")
            self._eof = True
            self.state = 0  # Stay idle if file is not found

    def work(self, input_items, output_items):
        if self.state == 0:
            return 0  # Stay idle

        elif self.state == 1:
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.c_len)
            self.add_item_tag(0, self.indx, key1, val1)
            self.indx += self.c_len
            output_items[0][:self.c_len] = self.char_list
            self.pre_count += 1
            if self.pre_count > 64:
                self.pre_count = 0
                self.state = 2  # Move to sending data
            return self.c_len

        elif self.state == 2:
            if not self._eof:
                buff = self.f_in.read(self.Pkt_len)
                if len(buff) == 0:
                    print("End of file")
                    self._eof = True
                    self.f_in.close()
                    self.state = 3  # Send file name
                    return 0

                encoded = base64.b64encode(buff)
                key0 = pmt.intern("packet_len")
                val0 = pmt.from_long(len(encoded))
                self.add_item_tag(0, self.indx, key0, val0)
                self.indx += len(encoded)
                output_items[0][:len(encoded)] = encoded
                return len(encoded)

        elif self.state == 3:
            fn_len = len(self.FileName)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(fn_len + 8)
            self.add_item_tag(0, self.indx, key1, val1)
            self.indx += fn_len + 8
            output_items[0][:8] = self.filler[:8]
            output_items[0][8:fn_len + 8] = [ord(c) for c in self.FileName]
            self.state = 4
            return fn_len + 8

        elif self.state == 4:
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.f_len)
            self.add_item_tag(0, self.indx, key1, val1)
            self.indx += self.f_len
            output_items[0][:self.f_len] = self.filler
            self.pre_count += 1
            if self.pre_count > 16:
                self.pre_count = 0
                self.state = 0  # Return to idle, wait for new file
            return self.f_len

        return 0
