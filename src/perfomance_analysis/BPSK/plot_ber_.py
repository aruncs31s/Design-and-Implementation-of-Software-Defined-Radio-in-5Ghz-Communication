preamble =  [37,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]


def find_preamble_all(tx, preamble):
    preamble_len = len(preamble)
    indices = []  # List to store all indices where the preamble is found
    for i in range(len(tx) - preamble_len + 1):
        if tx[i:i + preamble_len] == preamble:
            # print(f"Preamble found at index {i} in tx stream.")
            indices.append(i)  # Add the index to the list
    # if not indices:
        # print("Preamble not found in tx stream.")
    return indices  # Return the list of indices

def remove_preamble_from_rx():
    with open("./output.tmp", "rb") as rx_file:
        rx_bits = list(rx_file.read())
        print("rx len: ", len(rx_bits))
        
        # Find all preamble occurrences
        preamble_indices = find_preamble_all(rx_bits, preamble)
        if preamble_indices:
            print(f"Preamble found at indices: {preamble_indices}")
            # Remove the first occurrence of the preamble
            start_index = preamble_indices[0]
            rx_bits = rx_bits[start_index + len(preamble):]
            print(f"rx len after removing preamble: {len(rx_bits)}")
        else:
            print("Preamble not found in rx_bits.")
    
    # Save the modified rx_bits back to a file
    with open("./rx_bits_no_preamble.bin", "wb") as rx_file_no_preamble:
        rx_file_no_preamble.write(bytearray(rx_bits))
    print("Preamble removed and saved to rx_bits_no_preamble.bin.")

def find_preamble_in_rx():
    with open("./output.tmp" , "rb") as rx_file:
        rx = list(rx_file.read())
        print("rx len: ", len(rx))
        find_preamble_all(rx, preamble)
def find_preamble_in_tx():
    with open("./tx_bits.bin" , "rb") as tx_file:
        tx = list(tx_file.read())
        print("tx len: ", len(tx))
        find_preamble_all(tx, preamble)
find_preamble_in_tx()
find_preamble_in_rx()


def remove_preamble(tx, preamble):
    preamble_len = len(preamble)
    indices = find_preamble_all(tx, preamble)
    if indices:
        start_index = indices[0] + preamble_len  # Start after the first preamble
        return tx[start_index:]  # Return the tx stream without the preamble
    else:
        print("Preamble not found in tx stream.")
        return tx  # Return the original tx stream if no preamble is found
def remove_preamble_from_tx():
    with open("./tx_bits.bin" , "rb") as tx_file:
        tx = list(tx_file.read())
        print("tx len: ", len(tx))
        tx_without_preamble = remove_preamble(tx, preamble)
        print("tx without preamble len: ", len(tx_without_preamble))
        with open("./tx_without_preamble.bin", "wb") as out_file:
            out_file.write(bytes(tx_without_preamble))
def calculate_ber(tx_bits, rx_bits):
    errors = 0
    for t, r in zip(tx_bits, rx_bits):
        if t != r:
            errors += 1
    total = len(tx_bits)
    ber = errors / total if total > 0 else 0
    print(f"Bit Errors: {errors} / {total}")
    print(f"BER: {ber:.6e}")
    return ber

if __name__ == "__main__":
    with open("./tx_bits.bin", "rb") as tx_file:
        tx_bits = list(tx_file.read())
        print("tx len: ", len(tx_bits))
    with open("./output.tmp", "rb") as rx_file:
        rx_bits = list(rx_file.read())
        print("rx len: ", len(rx_bits))
    calculate_ber(tx_bits, rx_bits)
    remove_preamble_from_rx()