import socket
import sys

def send_archive(apply_fix=False):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if apply_fix:
        try:
            # FIX: Clamp the Layer 4 Maximum Segment Size (MSS) to 1300 bytes.
            # This forces the OS network stack to slice the packet at the transport layer.
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG, 1300)
            print("[+] Layer 4 Optimization: Clamped TCP_MAXSEG to 1300 bytes.")
        except Exception as e:
            print(f"[-] Note: Setting TCP_MAXSEG might require admin rights or OS support: {e}")

    try:
        client.connect(('127.0.0.1', 9999))
        
        # Create a 5KB payload
        large_payload = b"A" * 5120 
        print(f"[*] Attempting to transmit log archive ({len(large_payload)} bytes)...")
        
        if apply_fix:
            # When fixed, we use sendall so the OS slices it into our 1300-byte clamped blocks
            client.sendall(large_payload)
        else:
            # FORCE FAILURE: We force a single massive write to trigger the server's MTU simulation drop rule
            client.send(large_payload)
            
        print("[========= SUCCESS =========] Archive fully uploaded successfully!")
        
    except Exception as e:
        print(f"\n[========= FAILED =========] Connection froze or was cut short: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Change this to True to test your Layer 4 TCP clamping fix!
    send_archive(apply_fix=False)
