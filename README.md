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


# Layer 3 Network Layer (Completed): 

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
# Layer 4: Transport Layer (Completed)

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

# Layer 5: Session Layer (Completed)

###  The Objective
To analyze the mechanics of Layer 5, I investigated a complete Session Initiation Protocol (SIP) and Session Description Protocol (SDP) transaction using a target packet capture trace (`MagicJack+_short_test_call.pcap`). The goal was to trace how endpoints securely establish, manage, and gracefully terminate a logical dialogue independent of the underlying transport protocols.

###  Step 1: Packet Dissection & Dialogue Breakdown
Using Wireshark's display filters to isolate the `sip` protocol, I tracked the raw sequential state transitions of the session establishment phase.

<img width="1247" height="560" alt="Screenshot 2026-07-20 025641" src="https://github.com/user-attachments/assets/2067c6b5-a1d2-44d8-8c08-8363b437d5c8" />


#### **Technical Analysis**
* **The Security Challenge (Packets 46–49):** The client (`192.168.0.10`) initiated a session request via an `INVITE`. The server (`216.234.64.8`) responded with a `401 Unauthorized` challenge, demanding cryptographic credentials. The client cleanly acknowledged (`ACK`) the rejection, completing the first sub-dialogue thread.
* **The Authenticated Success (Packets 50–54 & 925):** The client dynamically adapted, immediately re-transmitting an updated `INVITE` containing the necessary authentication headers. The server validated the credentials, passing through provisional states (`100 Trying` and `183 Session Progress`) before issuing a definitive `200 OK` approval to officially establish the session.

---

###  Step 2: Visualizing the Complete Session Lifecycle
To abstract the raw data rows into a clear engineering storyline, I extracted Wireshark's **VoIP Flow Graph** (`Telephony > VoIP Calls > Flow Sequence`). This cleanly maps out the dialogue logic from initialization to teardown.

<img width="949" height="466" alt="Screenshot 2026-07-20 030722" src="https://github.com/user-attachments/assets/c332c1a2-161c-45a3-bdb1-8ae45954f310" />


### **Architectural Insights from the Flow Graph:**
1. **Payload Codec Negotiation:** During the second handshake phase, the data label transitions to **SIP/SDP**. The embedded **SDP (Session Description Protocol)** payload successfully negotiated the media parameters, locking in the `g711U` voice audio codec and specific UDP communication ports.
2. **Graceful Session Teardown:** The ladder diagram exposes the critical terminal phase of Layer 5. At time `178.84`, the client issues a **`BYE`** command to hang up. The server immediately returns a final **`200 OK`**. This clean exchange proves that the session successfully dismantled its communication channel, preventing orphan sockets, resource ties, or memory leaks on the server.

###  Key Engineering Skills Demonstrated
* **Stateful Dialogue Analysis:** Traced asynchronous client-server token verification states across failures and successes.
* **Metadata Manipulation:** Evaluated Layer 5 encapsulation mechanics (`Call-ID`, `CSeq` sequence trackers) to verify transaction synchronicity.
* **Lifecycle Mapping:** Documented complete connection lifetimes from initial handshake through payload negotiation to terminal teardown.
* **Lines 1-3 (TCP Handshake Lifecycle):** Demonstrates strict, connection-oriented state establishment via explicit `SYN` -> `SYN-ACK` -> `ACK` tracking loops before any upper-layer data transfers.
* **Line 4 (TCP Payload Data):** Secure transmission of state-tracked payload data utilizing automatic sequence numbering and explicit arrival confirmation.
* **Lines 6-7 (TCP Connection Teardown):** Clean closure of the socket pairing using the `FIN` flag to prevent resource leaking on the host OS.
* **Line 8 (UDP Transmission):** Direct, stateless injection of real-time voice data bypassing all handshake overhead, validating the ultra-low latency architecture required for non-blocking communication fields.

# Layer 6: Presentation Layer (Completed)

- **Vulnerability Context (Insecure Deserialization & Format-Level Infiltration):** The Presentation Layer handles data syntax translation, serialization, and text encoding transformations before applications process payloads. Flawed architectures accept complex serialization formats (such as programmable YAML or object streams) directly from untrusted inputs. If the backend processes this data without strict layout checks, an attacker can craft a payload with embedded formatting instructions. This tricks the parsing engine into jumping out of data parsing and executing arbitrary operating system commands during the data reconstruction phase.
- **Security Hardening Mitigation (Format & Syntax Validation):** Implemented strict schema-enforced syntax parsing. By stripping runtime object-instantiation tags and validating the text string letter-by-letter, the backend parser isolates raw inputs into inert literal values. If a payload violates the strict layout structure by including executable macros, the engine throws an immediate syntax error and safely drops the request before code execution can occur.
- **Tooling Used:**
  - **Custom Serialization Lab Framework:** Built using native socket and parsing handlers to simulate multi-layered backend translation engines directly within a sandbox environment.

### Presentation Translation Validation

#### **Vulnerable Parse Mode (Full Syntax Engine)**
When configured in **Vulnerable Parse** mode, the data translation engine executes both formatting rules and embedded macro logic strings.

* **Injected Formatting Payload:** Contains hidden system command instructions.
* **Resulting Action:** The engine processes the untrusted layout rules, allowing command infiltration directly into the underlying operating system environment as verified by the active session response:
![Uploading Screenshot 2026-08-09 140858.png…]()

```text
Object Reconstructed Successfully! Data: Executing system payload 'expr 7 * 7' -> Result: 49
```

#### **Secure Parse Mode (Strict Format Validation)**
Toggling the platform interface to **Secure Parse** mode deactivates the executable syntax engines and enforces text-only mapping criteria.

* **Incoming Malicious Payload:** Checked letter-by-letter against a rigid text layout template.
* **Resulting Output:** The application parser flags the formatting violation, safely strips execution capabilities, and drop-terminates the connection block:
<img width="628" height="504" alt="Screenshot 2026-08-09 140818" src="https://github.com/user-attachments/assets/365cc899-73e0-4f64-b084-e7d9f9c8cf1f" />

```text
Validation Failed: Syntax Validation Failed: Invalid format structure tags. Request Safely Dropped.
```



# Layer 7: Application Layer (Completed)

- **Vulnerability Context (SQL Injection Authentication Bypass):** Flawed web applications accept user inputs as raw strings and concatenate them directly into SQL statements before passing them to the database engine. Attackers can exploit this structural vulnerability by injecting malicious code containing SQL control characters (such as quotes `'` and comments `--` or `#`). This manipulates the backend logic to disregard critical query conditions—such as a password verification block—allowing unauthorized access to privileged accounts without credential validation.
- **Security Hardening Mitigation (Parameterized Queries & Prepared Statements):** Implemented a rigorous data-plane separation using Parameterized Queries (Prepared Statements). By pre-compiling the structural database blueprint first, the application engine enforces strict structural typing. When a user input payload containing characters like `admin' --` is received, the database engine reads the input letter-by-letter as a literal string value rather than executable logical code. The query evaluates against the literal username, safely matches 0 rows, and cleanly restricts access with a standardized application rejection.
- **Tooling Used:**
  - **SQLi Auth Bypass Lab Frontend:** Used to test and validate input mutations across divergent query handling frameworks.
  - **Backend Server Logs:** Inspected live query execution flows to audit the transformation of inputs from active logical operators to inert literal values.

### Defensive Validation Analysis

#### **Vulnerable Query Mode**
When the validation interface is configured in **Vulnerable Query** mode, input strings directly mutate the runtime database execution engine logic.

* **Injected User Payload:** `admin' --`
* **Resulting Runtime Statement:** `SELECT * FROM users WHERE username = 'admin' -- ' AND password = '...';`

Because the database engine reads the double dash (`--`) as a code control symbol, it strips out the entire password criteria segment. This forces a logical bypass, directly logging the attacker into the application as demonstrated by the session telemetry returning the explicit tuple fields:

```text
Welcome back, (1, 'admin', 'super_secret_2026')! (Logged in via vulnerable mode)
```

#### **Secure Query Mode**
When toggling the platform interface to **Secure Query** mode, the pre-compiled database structural blueprint prevents command injection entirely. 

* **Pre-compiled Structural Blueprint:** `SELECT * FROM users WHERE username = ? AND password = ?;`
* **Resulting Literal Evaluation:** The database searches for a literal username string matching `admin' --`. 

Because no user record possesses that exact string structure, the system returns 0 matching rows. The authentication logic securely fails closed, returning a safe, uniform interface exception:

```text
Login Failed!
```
