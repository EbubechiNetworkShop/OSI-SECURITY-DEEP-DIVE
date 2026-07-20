# OSI-SECURITY-DEEP-DIVE
In depth security hardening layout for the OSI model focusing on the understanding of vulnerabilities and proper security measures on all layers. 
---

##  Project Roadmap & Architecture

#  Layer 1: Physical Layer (Completed)
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
## Layer 4: Transport Layer (Completed)

* **Vulnerability Context (Port Spoofing & Traffic Interception):** Attackers targeting application ports try to cause stateful denial of service (like SYN floods) or sniff unencrypted streams. Additionally, deploying standard applications over identical port boundaries can introduce processing bottlenecks or traffic leaking if the host operating system cannot cleanly segregate the data planes.

* **Security Hardening Mitigation:** Implemented a dual-protocol multiplexing layer that isolates traffic using strict 4-tuple evaluation (`Protocol` field differentiation). By splitting the corporate data planes at Layer 4, high-integrity assets are locked into standard connection-state tracking, while low-overhead assets are directed to standard stateless pipelines over the exact same structural listening port.

* **Tooling Used:**
    * **Windows PowerShell:** Used native net framework sockets (`System.Net.Sockets`) to open concurrent, collision-free listeners on TCP and UDP across a single host interface.
    * **Wireshark:** Captured live loopback telemetry to visually analyze and audit connection state flags (`SYN`, `ACK`, `FIN`) and contrast transport-layer header overhead.

### How to Run the Simulation

To replicate the simultaneous multi-protocol capture, execute the following commands in separate PowerShell windows:

```powershell
# Terminal 1: Initialize the Secure File Server (TCP Listener)
\(Listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, 8443)\)Listener.Start()

# Terminal 2: Initialize the Real-Time Communications Stream (UDP Listener)
\$UdpClient = [System.Net.Sockets.UdpClient]::new(8443)

# Terminal 3: Audit Live Socket Map Coexistence
netstat -an | Select-String "8443"

# Terminal 3 (Continued): Execute Payload Transmissions
# Send Reliable File Data via TCP
\$ClientTCP = [System.Net.Sockets.TcpClient]::new("127.0.0.1", 8443)
\$Stream = \(ClientTCP.GetStream()\)DataTCP = [System.Text.Encoding]::ASCII.GetBytes("Sending Corporate Financial Spreadsheet Backup")
Stream.Write(DataTCP, 0, \(DataTCP.Length)\)ClientTCP.Close()

# Send Low-Latency Streams via UDP
\(ClientUDP = [System.Net.Sockets.UdpClient]::new()\)DataUDP = [System.Text.Encoding]::ASCII.GetBytes("Real-time VoIP Voice Stream Payload")
\$ClientUDP.Send(DataUDP, DataUDP.Length, "127.0.0.1", 8443)
\$ClientUDP.Close()
```

### Protocol Telemetry Verification

<img width="952" height="877" alt="Screenshot 2026-07-11 084548" src="https://github.com/user-attachments/assets/72891a46-35e3-4f07-bec8-01c6fe8f5da1" />

# Comprehensive OSI Model Network Analysis Project

This repository documents a deep-dive investigation into the 7 layers of the OSI model. By utilizing network simulation tools and packet analysis, I isolated, mapped, and analyzed real-world network mechanics unique to each layer of the network stack.

---

## 📁 Layer 5: Session Layer (Dialogue Control & Session Lifecycle)

### 🔹 The Objective
To analyze the mechanics of Layer 5, I investigated a complete Session Initiation Protocol (SIP) and Session Description Protocol (SDP) transaction using a target packet capture trace (`MagicJack+_short_test_call.pcap`). The goal was to trace how endpoints securely establish, manage, and gracefully terminate a logical dialogue independent of the underlying transport protocols.

### 🔹 Step 1: Packet Dissection & Dialogue Breakdown
Using Wireshark's display filters to isolate the `sip` protocol, I tracked the raw sequential state transitions of the session establishment phase.

![Wireshark SIP Traffic Capture](./images/layer5_sip_packets.png)
*Figure 1: Analysis of the initial multi-stage SIP dialogue handshake rows.*

#### **Technical Analysis & Fluid Intelligence Discovery:**
* **The Security Challenge (Packets 46–49):** The client (`192.168.0.10`) initiated a session request via an `INVITE`. The server (`216.234.64.8`) responded with a `401 Unauthorized` challenge, demanding cryptographic credentials. The client cleanly acknowledged (`ACK`) the rejection, completing the first sub-dialogue thread.
* **The Authenticated Success (Packets 50–54 & 925):** The client dynamically adapted, immediately re-transmitting an updated `INVITE` containing the necessary authentication headers. The server validated the credentials, passing through provisional states (`100 Trying` and `183 Session Progress`) before issuing a definitive `200 OK` approval to officially establish the session.

---

### 🔹 Step 2: Visualizing the Complete Session Lifecycle
To abstract the raw data rows into a clear engineering storyline, I extracted Wireshark's **VoIP Flow Graph** (`Telephony > VoIP Calls > Flow Sequence`). This cleanly maps out the dialogue logic from initialization to teardown.

![Wireshark VoIP Flow Sequence Graph](./images/layer5_voip_flow.png)
*Figure 2: Fully mapped SIP ladder diagram displaying the entire session lifecycle.*

#### **Architectural Insights from the Flow Graph:**
1. **Payload Codec Negotiation:** During the second handshake phase, the data label transitions to **SIP/SDP**. The embedded **SDP (Session Description Protocol)** payload successfully negotiated the media parameters, locking in the `g711U` voice audio codec and specific UDP communication ports.
2. **Graceful Session Teardown:** The ladder diagram exposes the critical terminal phase of Layer 5. At time `178.84`, the client issues a **`BYE`** command to hang up. The server immediately returns a final **`200 OK`**. This clean exchange proves that the session successfully dismantled its communication channel, preventing orphan sockets, resource ties, or memory leaks on the server.

### 🔹 Key Engineering Skills Demonstrated
* **Stateful Dialogue Analysis:** Traced asynchronous client-server token verification states across failures and successes.
* **Metadata Manipulation:** Evaluated Layer 5 encapsulation mechanics (`Call-ID`, `CSeq` sequence trackers) to verify transaction synchronicity.
* **Lifecycle Mapping:** Documented complete connection lifetimes from initial handshake through payload negotiation to terminal teardown.
* **Lines 1-3 (TCP Handshake Lifecycle):** Demonstrates strict, connection-oriented state establishment via explicit `SYN` -> `SYN-ACK` -> `ACK` tracking loops before any upper-layer data transfers.
* **Line 4 (TCP Payload Data):** Secure transmission of state-tracked payload data utilizing automatic sequence numbering and explicit arrival confirmation.
* **Lines 6-7 (TCP Connection Teardown):** Clean closure of the socket pairing using the `FIN` flag to prevent resource leaking on the host OS.
* **Line 8 (UDP Transmission):** Direct, stateless injection of real-time voice data bypassing all handshake overhead, validating the ultra-low latency architecture required for non-blocking communication fields.
