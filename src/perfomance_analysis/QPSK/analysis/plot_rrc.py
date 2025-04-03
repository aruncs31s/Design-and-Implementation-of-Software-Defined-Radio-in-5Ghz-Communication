import matplotlib.pyplot as plt
import numpy as np


def root_raised_cosine(t, alpha):
    """Calculate Root Raised Cosine impulse response"""
    numerator = np.sin(np.pi*t*(1-alpha)) + 4*alpha*t*np.cos(np.pi*t*(1+alpha))
    denominator = np.pi*t*(1-(4*alpha*t)**2)
    
    # Handle special cases (t=0 and t=±1/(4α))
    h = np.zeros_like(t)
    mask = np.abs(t) != 1/(4*alpha)
    h[mask] = numerator[mask]/denominator[mask]
    
    # t=0 case
    h[np.abs(t) < 1e-10] = (1 + alpha*(4/np.pi - 1))
    
    # t=±1/(4α) case
    idx = np.where(np.abs(np.abs(t) - 1/(4*alpha)) < 1e-10)
    h[idx] = (alpha/np.sqrt(2)) * ((1+2/np.pi)*np.sin(np.pi/(4*alpha)) + (1-2/np.pi)*np.cos(np.pi/(4*alpha)))
    
    return h

# Parameters
alpha = 0.35  # Roll-off factor
span = 10     # Number of symbol durations to plot
sps = 32      # Samples per symbol (for smooth plotting)

# Time vector
t = np.linspace(-span/2, span/2, span*sps)
t_symbols = t  # Time in symbol durations

# Calculate impulse response
h = root_raised_cosine(t_symbols, alpha)

# Normalize energy
h /= np.sqrt(np.sum(h**2))

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(t_symbols, h, 'b-', linewidth=2, label=f'RRC (α={alpha})')
plt.title('Root Raised Cosine Impulse Response')
plt.xlabel('Time (Symbol Durations)')
plt.ylabel('Amplitude')
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.legend()
plt.tight_layout()

# Add markers for special points
plt.scatter([0], [h[np.argmin(np.abs(t_symbols))]], color='red', zorder=5)
plt.scatter([1/(4*alpha)], [h[np.argmin(np.abs(t_symbols - 1/(4*alpha)))]], color='green', zorder=5)
plt.scatter([-1/(4*alpha)], [h[np.argmin(np.abs(t_symbols + 1/(4*alpha)))]], color='green', zorder=5)

plt.show()
