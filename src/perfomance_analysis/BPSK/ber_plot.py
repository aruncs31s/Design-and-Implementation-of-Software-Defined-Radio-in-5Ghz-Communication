import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("ber_log.csv")
import datetime
df['time'] = df['timestamp'].apply(lambda ts: datetime.datetime.fromtimestamp(ts))
plt.figure(figsize=(10, 5))
plt.plot(df['packet_number'], df['ber'], label='BER per Packet', color='blue', marker='o', markersize=2)
plt.plot(df['packet_number'], df['avg_ber'], label='Running Average BER', color='red', linestyle='--')
plt.xlabel('Packet Number')
plt.ylabel('Bit Error Rate (BER)')
plt.title('BER vs Packet Number')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
