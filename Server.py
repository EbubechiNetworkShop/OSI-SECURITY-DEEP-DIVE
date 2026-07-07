import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 9999))
    server.listen(1)
    print("[*] Storage Server listening on 127.0.0.1:9999")

    while True:
        conn, addr = server.accept()
        try:
            total_bytes = 0
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                
                total_bytes += len(data)
                print(f"[->] Received {len(data)} bytes. Total: {total_bytes}")

                # SIMULATION: If more than 2000 bytes come in as a bulk blast
                # without the client announcing a fixed max segment size, drop it!
                if total_bytes > 2000:
                    print("\n[!] CRITICAL: Stream payload total crossed unfragmented path limit!")
                    print("[!] Simulating intermediate router packet drop (Black Hole).")
                    conn.close()
                    break
        except Exception as e:
            pass
        finally:
            conn.close()

if __name__ == "__main__":
    start_server()
