import numpy as np
from gnuradio import gr
import pmt
import time
import os

class blk(gr.sync_block):
    """
    Stream-Based BER Calculator with Logging and Live Average
    """
    def __init__(self, reference_bits_path="tx_bits.bin", log_file_path="ber_log.csv"):
        gr.sync_block.__init__(
            self,
            name='Enhanced BER Calculator',
            in_sig=[np.uint8],
            out_sig=None
        )

        # Reference bits
        self.reference_bits_path = reference_bits_path
        self.ref_bits = self._load_reference_bits(reference_bits_path)
        self.offset = 0

        # Packet processing
        self.current_packet_len = None
        self.current_packet_data = []

        # Logging and stats
        self.log_file_path = log_file_path
        self.packet_count = 0
        self.total_errors = 0
        self.total_bits = 0

        # Output port for live BER
        self.message_port_register_out(pmt.intern("ber_out"))

        # Prepare CSV
        self._init_log_file()

    def _load_reference_bits(self, path):
        try:
            with open(path, "rb") as f:
                print(f"[+] Loading reference bits from: {path}")
                return np.unpackbits(np.frombuffer(f.read(), dtype=np.uint8))
        except FileNotFoundError:
            print(f"[!] Reference bits file not found: {path}")
            return np.array([], dtype=np.uint8)

    def _init_log_file(self):
        # Add header if file is new
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w") as f:
                f.write("timestamp,packet_number,packet_len,errors,ber,avg_ber\n")

    def work(self, input_items, output_items):
        inp = input_items[0]
        nread = self.nitems_read(0)

        for i in range(len(inp)):
            tags = self.get_tags_in_range(0, nread + i, nread + i + 1)
            for tag in tags:
                if pmt.symbol_to_string(tag.key) == "packet_len":
                    self.current_packet_len = pmt.to_long(tag.value)
                    self.current_packet_data = []

            if self.current_packet_len is not None:
                self.current_packet_data.append(inp[i])

                if len(self.current_packet_data) == self.current_packet_len:
                    rx_bits = np.array(self.current_packet_data, dtype=np.uint8)
                    ref_bits = self.ref_bits[self.offset:self.offset + self.current_packet_len]

                    if len(ref_bits) != self.current_packet_len:
                        print("[!] Reference bits mismatch, skipping")
                    else:
                        errors = np.sum(rx_bits != ref_bits)
                        ber = errors / self.current_packet_len
                        self.total_errors += errors
                        self.total_bits += self.current_packet_len
                        self.packet_count += 1
                        avg_ber = 1 - self.total_errors / self.total_bits

                        # Print to console
                        print(f"[BER] Packet #{self.packet_count} → Errors: {errors} / {self.current_packet_len} → BER: {ber:.6f}, Avg: {avg_ber:.6f}")

                        # Log to CSV
                        timestamp = time.time()
                        with open(self.log_file_path, "a") as f:
                            f.write(f"{timestamp},{self.packet_count},{self.current_packet_len},{errors},{ber:.6f},{avg_ber:.6f}\n")

                        # Send BER via message port
                        msg = pmt.from_double(ber)
                        self.message_port_pub(pmt.intern("ber_out"), msg)

                    self.offset += self.current_packet_len
                    self.current_packet_len = None
                    self.current_packet_data = []

        return len(inp)
