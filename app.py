#!/usr/bin/env python3
"""
Real-Time Network Monitoring Tool with Live Dashboard Updates
Updates browser within 25 seconds of any CSV changes
"""

import subprocess
import time
import platform
import csv
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, request

# Global variable to track CSV file changes
csv_last_modified = 0

# ============================================================================
# MONITORING FUNCTIONS
# ============================================================================

def ping_device(ip_address):
    """
    Ping a device and return True if it responds, False if it doesn't
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip_address]
    
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def initialize_log(filename):
    """
    Initialize CSV log file with headers if it doesn't exist
    """
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Device Name", "IP Address", "Status"])

def log_status(filename, timestamp, device_name, ip_address, status):
    """
    Log ping result to CSV file with device name
    """
    global csv_last_modified
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, device_name, ip_address, status])
    
    # Update the modification time tracker
    csv_last_modified = time.time()

def monitor_device_background(device_name, ip_address, check_interval=30, log_file="network_log.csv"):
    """
    Background monitoring function for a single device
    """
    print(f"🔍 Starting monitoring of {device_name} ({ip_address}) every {check_interval} seconds...")

    try:
        while True:
            is_up = ping_device(ip_address)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = "UP" if is_up else "DOWN"
            
            # Log to console
            status_emoji = "✅" if is_up else "❌"
            print(f"[{timestamp}] {status_emoji} {device_name} ({ip_address}) is {status}")
            
            # Log to CSV
            log_status(log_file, timestamp, device_name, ip_address, status)
            
            time.sleep(check_interval)
            
    except Exception as e:
        print(f"⚠️  Monitoring error for {device_name}: {e}")

# ============================================================================
# FLASK WEB DASHBOARD WITH REAL-TIME UPDATES
# ============================================================================

app = Flask(__name__)

@app.route('/check_updates')
def check_updates():
    """
    API endpoint to check if CSV has been updated since last check
    Returns JSON indicating if browser should refresh
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'network_log.csv')
    
    if os.path.exists(csv_path):
        current_modified = os.path.getmtime(csv_path)
        
        # Check if file was modified since last request
        last_check = float(request.args.get('last_check', 0))
        
        if current_modified > last_check:
            return jsonify({
                "updated": True, 
                "last_modified": current_modified,
                "message": "New data available"
            })
    
    return jsonify({
        "updated": False,
        "last_modified": time.time(),
        "message": "No updates"
    })

@app.route('/')
def dashboard():
    """
    Main dashboard page with real-time update capability
    """
    data = []

    # Check if file exists
    csv_path = os.path.join(os.path.dirname(__file__), 'network_log.csv')
    if os.path.exists(csv_path):
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(row)
    else:
        return """
        <html>
        <head>
            <meta http-equiv="refresh" content="5">
            <title>Network Monitoring - Starting Up</title>
        </head>
        <body>
            <h1>🔍 Network Monitoring Dashboard</h1>
            <p>⏳ Monitoring system starting up... Please wait.</p>
            <p>🔄 This page will auto-refresh when data is available.</p>
        </body>
        </html>
        """

    # Show only last 20 entries, newest first
    recent_data = data[-20:] if len(data) > 20 else data
    if len(recent_data) > 1:  # Keep headers at top
        headers = recent_data[0]  # Save headers
        data_rows = recent_data[1:]  # Get data rows
        data_rows.reverse()  # Reverse the order (newest first)
        recent_data = [headers] + data_rows  # Combine back together

    # Get current status from most recent entry (now it's the first data row!)
    current_status = "Starting..."
    if len(recent_data) > 1:
        last_row = recent_data[1]  # First data row = newest entry
        current_status = last_row[3] if len(last_row) > 3 else "Unknown"  # Status is now column 3

    # Count UP and DOWN (updated for new CSV format)
    up_count = 0
    down_count = 0
    for row in recent_data[1:]:  # skip header
        if len(row) > 3:  # Now we have 4 columns: Timestamp, Device, IP, Status
            if row[3].upper() == "UP":  # Status is now column 3 (was column 2)
                up_count += 1
            elif row[3].upper() == "DOWN":
                down_count += 1

    # Calculate uptime percentage
    total = up_count + down_count
    uptime_percent = round((up_count / total) * 100, 2) if total > 0 else 0

    # Determine status color
    status_color = "green" if current_status.upper() == "UP" else "red" if current_status.upper() == "DOWN" else "orange"

    # Get current time and file modification time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_modified = os.path.getmtime(csv_path) if os.path.exists(csv_path) else time.time()

    # HTML with real-time JavaScript and enhanced styling
    html = f"""
    <html>
    <head>
        <title>Real-Time Network Monitor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }}
            h1 {{ 
                color: #333; 
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }}
            .realtime-indicator {{
                position: fixed;
                top: 10px;
                right: 10px;
                background: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 12px;
                z-index: 1000;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
                100% {{ opacity: 1; }}
            }}
            .summary {{ 
                margin: 20px 0; 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 25px;
                border-radius: 12px;
                border-left: 5px solid #007bff;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .current-status {{
                font-size: 24px;
                margin-bottom: 20px;
                text-align: center;
                padding: 15px;
                background: rgba(255,255,255,0.8);
                border-radius: 8px;
            }}
            .stats-row {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-item {{
                text-align: center;
                padding: 15px;
                background: rgba(255,255,255,0.9);
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .stat-value {{
                font-size: 28px;
                font-weight: bold;
                margin-top: 8px;
            }}
            .controls {{
                text-align: center;
                margin: 20px 0;
            }}
            .refresh-btn {{
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                margin: 0 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,123,255,0.3);
            }}
            .refresh-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,123,255,0.4);
            }}
            .auto-refresh-status {{
                display: inline-block;
                margin-left: 15px;
                padding: 8px 15px;
                background: #28a745;
                color: white;
                border-radius: 15px;
                font-size: 14px;
            }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin-top: 25px;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            th, td {{ 
                padding: 15px; 
                text-align: left; 
                border-bottom: 1px solid #eee;
            }}
            th {{ 
                background: linear-gradient(135deg, #495057, #6c757d);
                color: white;
                font-weight: bold;
                text-align: center;
                font-size: 16px;
            }}
            .status-up {{ 
                color: #28a745; 
                font-weight: bold; 
                font-size: 16px;
            }}
            .status-down {{ 
                color: #dc3545; 
                font-weight: bold; 
                font-size: 16px;
            }}
            tr:nth-child(even) {{ 
                background-color: #f8f9fa; 
            }}
            tr:hover {{
                background-color: #e3f2fd;
                transition: background-color 0.3s ease;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #666;
                font-size: 14px;
                padding: 20px;
                background: rgba(248,249,250,0.8);
                border-radius: 8px;
            }}
            .new-entry {{
                animation: highlightNew 3s ease-in-out;
            }}
            @keyframes highlightNew {{
                0% {{ background-color: #fff3cd; }}
                100% {{ background-color: transparent; }}
            }}
        </style>
    </head>
    <body>
        <div class="realtime-indicator" id="realtimeStatus">
            🔴 Real-Time Updates
        </div>
        
        <div class="container">
            <h1>🚀 Multi-Device Network Monitor</h1>
            
            <div class="summary">
                <div class="current-status">
                    <strong>Network Status:</strong> 
                    <span style="color: {status_color}; font-weight: bold; font-size: 28px;">
                        {current_status}
                    </span>
                </div>
                
                <div class="stats-row">
                    <div class="stat-item">
                        <div><strong>Successful Pings</strong></div>
                        <div class="stat-value" style="color: #28a745;">{up_count}</div>
                    </div>
                    <div class="stat-item">
                        <div><strong>Failed Pings</strong></div>
                        <div class="stat-value" style="color: #dc3545;">{down_count}</div>
                    </div>
                    <div class="stat-item">
                        <div><strong>Uptime</strong></div>
                        <div class="stat-value" style="color: #007bff;">{uptime_percent}%</div>
                    </div>
                    <div class="stat-item">
                        <div><strong>Total Checks</strong></div>
                        <div class="stat-value">{total}</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 15px; font-size: 14px; color: #666;">
                    <strong>Dashboard Updated:</strong> {last_updated}
                </div>
            </div>
            
            <div class="controls">
                <button class="refresh-btn" onclick="location.reload()">🔄 Manual Refresh</button>
                <span class="auto-refresh-status" id="autoStatus">🟢 Live Updates Active</span>
            </div>
            
            <table>
    """

    # Build table rows
    for i, row in enumerate(recent_data):
        if i == 0:  # Header row
            html += "<tr>" + "".join([f"<th>{cell}</th>" for cell in row]) + "</tr>"
        else:
            # Add class for potential new entry animation
            row_class = "new-entry" if i == 1 else ""  # First data row is newest
            html += f"<tr class='{row_class}'>"
            for j, cell in enumerate(row):
                if j == 3 and cell.upper() == "UP":  # Status is column 3
                    html += f"<td class='status-up' style='text-align: center;'>✅ {cell}</td>"
                elif j == 3 and cell.upper() == "DOWN":  # Status is column 3
                    html += f"<td class='status-down' style='text-align: center;'>❌ {cell}</td>"
                elif j == 1:  # Device Name column - make it bold
                    html += f"<td style='font-weight: bold; color: #007bff;'>{cell}</td>"
                else:
                    html += f"<td>{cell}</td>"
            html += "</tr>"

    html += f"""
            </table>
            
            <div class="footer">
                <p>🚀 Multi-Device Network Monitoring System</p>
                <p>⚡ Monitoring: Home Router, Google DNS, Cloudflare DNS, OpenDNS</p>
                <p>🔄 Updates automatically within 25 seconds of network changes</p>
                <p>📊 Showing last 20 monitoring results (newest first)</p>
            </div>
        </div>

        <script>
            let lastModified = {file_modified};
            let checkInterval;
            
            function startRealTimeUpdates() {{
                // Check for updates every 25 seconds
                checkInterval = setInterval(function() {{
                    fetch('/check_updates?last_check=' + lastModified)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.updated) {{
                                console.log('New data detected - refreshing dashboard');
                                
                                // Update status indicator
                                const indicator = document.getElementById('realtimeStatus');
                                indicator.style.backgroundColor = '#ffc107';
                                indicator.innerHTML = '🔄 Updating...';
                                
                                // Refresh the page
                                setTimeout(() => {{
                                    location.reload();
                                }}, 500);
                            }}
                            lastModified = data.last_modified;
                        }})
                        .catch(error => {{
                            console.log('Update check failed:', error);
                            const indicator = document.getElementById('realtimeStatus');
                            indicator.style.backgroundColor = '#dc3545';
                            indicator.innerHTML = '🔴 Connection Error';
                        }});
                }}, 25000);
            }}
            
            // Start real-time updates when page loads
            window.onload = function() {{
                startRealTimeUpdates();
                console.log('Real-time monitoring started');
                
                // Update the status indicator
                const indicator = document.getElementById('realtimeStatus');
                indicator.style.backgroundColor = '#28a745';
                indicator.innerHTML = '🟢 Live Updates';
            }};
            
            // Stop checking when page unloads
            window.onbeforeunload = function() {{
                if (checkInterval) {{
                    clearInterval(checkInterval);
                }}
            }};
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/status')
def api_status():
    """
    API endpoint for current status
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'network_log.csv')
    if os.path.exists(csv_path):
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
            if len(data) > 1:
                last_row = data[-1]
                return jsonify({
                    "status": last_row[3] if len(last_row) > 3 else "Unknown",
                    "timestamp": last_row[0] if len(last_row) > 0 else "Unknown",
                    "device": last_row[1] if len(last_row) > 1 else "Unknown",
                    "ip": last_row[2] if len(last_row) > 2 else "Unknown",
                    "realtime": True
                })
    return jsonify({"status": "No data", "timestamp": "Unknown", "device": "Unknown", "ip": "Unknown", "realtime": False})

# ============================================================================
# THREADING AND MAIN FUNCTIONS
# ============================================================================

def start_monitoring_thread(device_name, ip_address, interval=30):
    """
    Start monitoring in background thread for a single device
    """
    monitor_thread = threading.Thread(
        target=monitor_device_background, 
        args=(device_name, ip_address, interval),
        daemon=True
    )
    monitor_thread.start()
    print(f"✅ Monitoring thread started for {device_name} ({ip_address})")
    return monitor_thread

def main():
    """
    Main function - starts both monitoring and web dashboard
    """
    print("🚀 Multi-Device Network Monitoring System")
    print("=" * 55)
    print("⚡ Features: Real-time monitoring of multiple devices")
    print("🔧 Starting up...")
    
    # Configuration - Multiple Devices
    monitored_devices = {
        "Home Router": "10.0.0.1",
        "Google DNS": "8.8.8.8", 
        "Cloudflare DNS": "1.1.1.1",
        "OpenDNS": "208.67.222.222"
    }
    ping_interval = 30
    
    # Initialize CSV log file
    initialize_log("network_log.csv")
    
    # Start background monitoring for all devices
    print(f"🔍 Initializing monitoring for {len(monitored_devices)} devices...")
    monitoring_threads = []

    for device_name, ip_address in monitored_devices.items():
        thread = start_monitoring_thread(device_name, ip_address, ping_interval)
        monitoring_threads.append(thread)
        time.sleep(1)  # Small delay between starting threads

    print(f"✅ All {len(monitored_devices)} monitoring threads started")
    
    # Give monitoring a moment to start
    time.sleep(2)
    
    # Start web dashboard
    print("🌐 Starting real-time web dashboard...")
    print(f"📊 Dashboard: http://127.0.0.1:5000")
    print(f"⚡ Real-time updates: 25-second polling")
    print(f"🔄 Auto-refresh: When CSV changes detected")
    print(f"⏹️  Press Ctrl+C to stop all monitoring")
    print("=" * 55)
    
    try:
        app.run(
            debug=False,
            host='127.0.0.1', 
            port=5000,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutdown signal received...")
        print("💾 Monitoring data saved to network_log.csv")
        print("👋 Multi-device monitoring system stopped")

if __name__ == "__main__":
    main()