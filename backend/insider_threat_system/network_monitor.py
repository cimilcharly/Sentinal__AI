
import psutil
import datetime
import pandas as pd
import socket

class SystemMonitor:
    def __init__(self):
        pass

    def get_running_services(self):
        """
        Retrieves a list of all running Windows services.
        """
        services = []
        for service in psutil.win_service_iter():
            try:
                # We fetch fields manually to avoid crashes on missing descriptions/configs
                name = service.name()
                display_name = service.display_name()
                status = service.status()
                
                if status == 'running':
                    services.append({
                        'name': name,
                        'display_name': display_name,
                        'status': status
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                continue
        return pd.DataFrame(services)

    def get_network_interfaces(self):
        """
        Retrieves hardware (MAC) addresses for all network interfaces.
        """
        interfaces = []
        addrs = psutil.net_if_addrs()
        for name, addr_list in addrs.items():
            mac = None
            ipv4 = None
            for addr in addr_list:
                # Family can vary by OS, but 2 is usually AF_INET (IPv4)
                # psutil.AF_LINK is for MAC addresses
                if hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                    mac = addr.address
                elif addr.family == 2: # AF_INET
                    ipv4 = addr.address
            
            if mac or ipv4:
                interfaces.append({
                    'interface': name,
                    'mac_address': mac or "N/A",
                    'ipv4_address': ipv4 or "N/A"
                })
        return pd.DataFrame(interfaces)

    def get_network_connections(self):
        """
        Retrieves active network connections.
        """
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            try:
                # laddr and raddr are naming tuples (ip, port)
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "LISTENING"
                
                connections.append({
                    'fd': conn.fd,
                    'family': 'IPv4' if conn.family == 2 else 'IPv6',
                    'type': 'TCP' if conn.type == 1 else 'UDP',
                    'local_address': laddr,
                    'remote_address': raddr,
                    'status': conn.status,
                    'pid': conn.pid
                })
            except Exception:
                continue
        return pd.DataFrame(connections)

    def get_wifi_details(self):
        """
        Retrieves the connected Wi-Fi Network Name (SSID) on Windows using netsh.
        """
        import subprocess
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for line in result.stdout.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
        except Exception:
            pass
        return "Unknown or Not Connected"

    def get_connected_devices(self, deep_scan=False):
        """
        Retrieves a list of devices connected to the local network using the ARP table.
        If deep_scan is True, performs a fast ping sweep to discover hidden devices.
        """
        import subprocess
        import concurrent.futures
        import socket
        
        if deep_scan:
            try:
                # Automatically find the local IPv4 subnet
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                parts = local_ip.split('.')
                if len(parts) == 4:
                    subnet = f"{parts[0]}.{parts[1]}.{parts[2]}"
                    ips = [f"{subnet}.{i}" for i in range(1, 255)]
                    
                    def _ping(ip):
                        subprocess.run(['ping', '-n', '1', '-w', '200', ip], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        
                    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                        executor.map(_ping, ips)
            except Exception:
                pass

        devices = []
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            lines = result.stdout.split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 3 and parts[0].count('.') == 3:
                    ip = parts[0]
                    mac = parts[1]
                    mac_type = parts[2]
                    
                    # Filter out static multicast/broadcast IPs
                    if mac_type == "dynamic" and not ip.startswith("224.") and not ip.startswith("239.") and not ip.endswith(".255"):
                        devices.append({'ip': ip, 'mac': mac})
        except Exception:
            pass
        return pd.DataFrame(devices)

    def get_live_summary(self, deep_scan=False):
        """
        Creates a natural language summary of the current live system state.
        """
        services = self.get_running_services()
        conns = self.get_network_connections()
        interfaces = self.get_network_interfaces()
        wifi_ssid = self.get_wifi_details()
        connected_devices = self.get_connected_devices(deep_scan=deep_scan)
        
        num_services = len(services)
        num_conns = len(conns)
        num_devices = len(connected_devices)
        
        mac_list = [m for m in interfaces['mac_address'].tolist() if m != "N/A"] if not interfaces.empty else []
        
        # Cybersecurity specific check: Search for suspicious hacking tools in running processes
        suspicious_procs = ['wireshark', 'nmap', 'zenmap', 'metasploit', 'hydra', 'john', 'putty', 'powershell_ise']
        found_procs = []
        try:
            for proc in psutil.process_iter(['name']):
                pname = proc.info['name'].lower()
                if any(s in pname for s in suspicious_procs):
                    found_procs.append(pname)
        except:
            pass

        # Check for suspicious things
        suspicious_ports = [4444, 6667, 8080, 1337, 31337, 8888] 
        found_ports = []
        
        for _, row in conns.iterrows():
            remote = str(row['remote_address'])
            local = str(row['local_address'])
            for port in suspicious_ports:
                if f":{port}" in remote or f":{port}" in local:
                    found_ports.append(port)

        summary = f"Live Cybersecurity Snapshot ({datetime.datetime.now().strftime('%H:%M:%S')}):\n"
        summary += f"- Hostname: {socket.gethostname()}\n"
        summary += f"- Connected Wi-Fi: {wifi_ssid}\n"
        summary += f"- Devices on Local Network: {num_devices}\n"
        summary += f"- Active Windows Services: {num_services}\n"
        summary += f"- Open Network Connections: {num_conns}\n"
        if mac_list:
            summary += f"- Primary Hardware (MAC) Addresses: {', '.join(mac_list[:3])}\n"
        
        if found_ports:
            summary += f"- ⚠️ CRITICAL: Detected active connections on suspicious ports: {list(set(found_ports))}\n"
        
        if found_procs:
            summary += f"- ⚠️ WARNING: Potential hacking/monitoring tools detected: {', '.join(list(set(found_procs[:3])))}\n"
            
        if not found_ports and not found_procs:
            summary += "- No immediate low-level cyber tool threats detected.\n"
            
        summary += "\nTop Services Running:\n"
        if not services.empty:
            summary += ", ".join(services['name'].head(5).tolist())
            
        return summary

if __name__ == "__main__":
    monitor = SystemMonitor()
    print(monitor.get_live_summary())
