# OSI-SECURITY-DEEP-DIVE
In depth security hardening layout for the OSI model focusing on the understanding of vulnerabilities and proper security measures on all layers. 
---

##  Project Roadmap & Architecture

###  Layer 1: Physical Layer (Completed)
* **Vulnerability Context:** Fiber optic lines rely on Total Internal Reflection (TIR). Attackers can physically tap cables using macro-bending or high-refractive-index prisms to leak photon signals, converting them back into raw network frames.
* **Cryptographic Mitigation:** Implementing an isolated, encrypted virtual tunnel over the untrusted physical network link.
* **Tooling Used:** 
  * **WireGuard (`wg0`):** Handles mutual authentication and enforces ChaCha20-Poly1305 encryption on all data passing through the interface.
  * **Netcat (`nc`):** Simulates an application injection payload (`"SECRET_TUNNEL_DATA_PULSE"`) on listening port `9000`.
  * **Tcpdump:** Used to sniff the physical interface on port `51820` to verify that payload text is completely masked as high-entropy ciphertext.

<img width="1919" height="1077" alt="Screenshot 2026-06-21 102456" src="https://github.com/user-attachments/assets/7d2b5b2a-f434-478a-a394-9683205d5de5" />


# Layer 3 (Network Layer) Simulation: PMTUD & Black Hole Failure

This lab uses a decoupled client-server architecture to simulate an unfragmented path boundary restriction across a network.

##  Simulation Component Files
* **`server.py`**: Initializes a listener on port `9999`. It models an endpoint situated behind a restrictive MTU network boundary and drops connections when the payload threshold is breached.
* **`client.py`**: Interacts with the server by attempting to stream a `5120 bytes` log archive payload.

##  How to Run the Simulation
To replicate the Black Hole router drop, execute the server first, followed by the client in a separate terminal window:

```bash
# Terminal 1 (Start the listener)
python server.py

# Terminal 2 (Execute the payload transmission)
python client.py
```
