import socket
import threading
import json
import random
import string
import time

class NetworkManager:
    def __init__(self):
        self.server = None
        self.client = None
        self.is_host = False
        self.game_code = None
        self.connected = False
        self.other_player = None
        self.lock = threading.Lock()
        self.connection_error = None
        self.port = 5555

    def generate_game_code(self):
        """Generate a 6-character alphanumeric game code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=6))

    def get_local_ip(self):
        """Get the local IP address of the host"""
        try:
            # Create a temporary socket to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "localhost"

    def start_server(self, port=5555):
        """Start a server and return the game code"""
        try:
            self.port = port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('0.0.0.0', port))
            self.server.listen(1)
            self.is_host = True
            self.game_code = self.generate_game_code()
            self.connection_error = None
            
            # Start listening for connections in a separate thread
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return self.game_code
        except Exception as e:
            self.connection_error = f"Failed to start server: {str(e)}"
            print(self.connection_error)
            return None

    def _accept_connections(self):
        """Accept incoming connections"""
        try:
            while self.is_host:
                client, addr = self.server.accept()
                print(f"Connection from {addr}")
                self.client = client
                self.connected = True
                self.connection_error = None
                # Start receiving data in a separate thread
                threading.Thread(target=self._receive_data, daemon=True).start()
        except Exception as e:
            self.connection_error = f"Error accepting connections: {str(e)}"
            print(self.connection_error)

    def join_game(self, host, port=5555):
        """Join an existing game"""
        try:
            self.port = port
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5)  # 5 second timeout for connection
            self.client.connect((host, port))
            self.connected = True
            self.connection_error = None
            # Start receiving data in a separate thread
            threading.Thread(target=self._receive_data, daemon=True).start()
            return True
        except socket.timeout:
            self.connection_error = "Connection timed out. Check if the host is online and on the same network."
            print(self.connection_error)
            return False
        except ConnectionRefusedError:
            self.connection_error = "Connection refused. Check if the host is online and on the same network."
            print(self.connection_error)
            return False
        except Exception as e:
            self.connection_error = f"Error joining game: {str(e)}"
            print(self.connection_error)
            return False

    def send_data(self, data):
        """Send data to the other player"""
        if self.connected and self.client:
            try:
                self.client.send(json.dumps(data).encode())
            except Exception as e:
                print(f"Error sending data: {e}")
                self.connected = False
                self.connection_error = "Connection lost"

    def _receive_data(self):
        """Receive data from the other player"""
        while self.connected:
            try:
                data = self.client.recv(1024).decode()
                if data:
                    with self.lock:
                        self.other_player = json.loads(data)
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.connected = False
                self.connection_error = "Connection lost"
                break

    def get_other_player(self):
        """Get the other player's data"""
        with self.lock:
            return self.other_player

    def get_connection_info(self):
        """Get connection information for the host"""
        if self.is_host:
            return {
                "ip": self.get_local_ip(),
                "port": self.port,
                "game_code": self.game_code
            }
        return None

    def get_connection_error(self):
        """Get the last connection error"""
        return self.connection_error

    def disconnect(self):
        """Disconnect from the game"""
        self.connected = False
        if self.client:
            try:
                self.client.close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
        self.client = None
        self.server = None
        self.is_host = False
        self.game_code = None
        self.other_player = None
        self.connection_error = None 