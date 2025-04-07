import numpy as np
from gnuradio import gr
import pmt
import os

class blk(gr.sync_block):  # Embedded Python Block
    """
    SNR Estimator per Packet (logs to file)
    """
    def __init__(self, reference_bits_path="tx_bits.bin", log_file="snr_log.txt"):
        gr.sync_block.__init__(
            self,
            name='SNR Estimator',
            in_sig=[np.uint8],
            out_sig=None
        )

        self.ref_bits = self._load_reference_bits(reference_bits_path)
        self.offset = 0
        self.current_packet_len = None
        self.current_packet_data = []
        self.log_file = log_file

        with open(self.log_file, 'w') as f:
            f.write("packet,snr_db\n")

    def _load_reference_bits(self, path):
        try:
            with open(path, "rb") as f:
                print(f"[+] Loading reference bits from: {path}")
                return 2 * np.unpackbits(np.frombuffer(f.read(), dtype=np.uint8)) - 1
        except FileNotFoundError:
            print(f"[!] Reference bits file not found: {path}")
            return np.array([], dtype=np.int8)

    def work(self, input_items, output_items):
        inp = input_items[0]
        nread = self.nitems_read(0)

        for i in range(len(inp)):
            # Check for packet_len tag
            tags = self.get_tags_in_range(0, nread + i, nread + i + 1)
            for tag in tags:
                if pmt.symbol_to_string(tag.key) == "packet_len":
                    self.current_packet_len = pmt.to_long(tag.value)
                    self.current_packet_data = []

            if self.current_packet_len is not None:
                self.current_packet_data.append(inp[i])

                if len(self.current_packet_data) == self.current_packet_len:
                    # Estimate SNR
                    y = np.array(self.current_packet_data, dtype=np.float32)
                    x = self.ref_bits[self.offset:self.offset + self.current_packet_len]

                    if len(x) == self.current_packet_len:
                        noise = y - x
                        snr_linear = np.mean(x ** 2) / np.mean(noise ** 2)
                        snr_db = 10 * np.log10(snr_linear + 1e-10)

                        with open(self.log_file, 'a') as f:
                            f.write(f"{self.offset // self.current_packet_len},{snr_db:.4f}\n")

                        print(f"[SNR] Packet #{self.offset // self.current_packet_len} → SNR: {snr_db:.2f} dB")

                    self.offset += self.current_packet_len
                    self.current_packet_len = None
                    self.current_packet_data = []

        return len(inp)
