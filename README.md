# 🚀 Live Network Monitor

A real-time network monitoring system with instant web dashboard updates. Monitor network devices with automatic ping-based health checks and view results through a beautiful, responsive web interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-brightgreen.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-red.svg)

## ✨ Features

- ⚡ **Real-time monitoring** - Continuous ping-based network health checks
- 🌐 **Live web dashboard** - Updates automatically within 25 seconds of network changes
- 📊 **Network statistics** - Uptime percentage, success/failure counts, current status
- 💾 **Data persistence** - CSV logging for historical analysis
- 📱 **Mobile responsive** - Works perfectly on desktop, tablet, and mobile
- 🎨 **Modern UI** - Beautiful gradient design with live status indicators
- 🔄 **Auto-refresh** - Smart polling that only updates when data actually changes
- 🚀 **Single command startup** - Combined monitoring and dashboard in one application

## 🖥️ Screenshots

### Dashboard Overview
*Real-time network monitoring dashboard with live statistics*

### Mobile View  
*Fully responsive design works on all devices*

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Network access for ping operations

### Installation & Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/marlon-netsecurity/live-network-monitor.git
   cd live-network-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

5. **Monitor your network**
   - The system automatically starts monitoring Google DNS (8.8.8.8)
   - Dashboard updates in real-time as ping results come in
   - Press `Ctrl+C` to stop the monitoring system

## 🔧 Configuration

### Monitoring Target
To monitor a different IP address, edit the `monitored_ip` variable in `app.py`:

```python
# Configuration
monitored_ip = "192.168.1.1"  # Change to your target IP
ping_interval = 30            # Ping interval in seconds
```

### Dashboard Settings
- **Update frequency**: Dashboard checks for new data every 25 seconds
- **Data retention**: Shows last 20 ping results in the web interface
- **CSV storage**: All results saved to `network_log.csv` for historical analysis

## 📊 How It Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Background    │    │   CSV File      │    │  Web Dashboard  │
│   Monitoring    │───▶│   Storage       │───▶│   Display       │
│   (Threading)   │    │   (Data Log)    │    │   (Flask App)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

1. **Background Thread**: Continuously pings the target device every 30 seconds
2. **Data Storage**: Results logged to CSV file with timestamp, IP, and status
3. **Web Interface**: Flask dashboard reads CSV and displays real-time statistics
4. **Live Updates**: JavaScript polls for file changes and refreshes automatically

## 🎯 Use Cases

- **Network Operations Centers**: Monitor critical network infrastructure
- **Home Lab Monitoring**: Keep track of servers and network devices
- **Internet Connectivity**: Monitor your internet connection stability  
- **Device Health Checks**: Continuous monitoring of network equipment
- **Learning Tool**: Understand network monitoring concepts and implementation

## 📁 Project Structure

```
live-network-monitor/
├── app.py              # Main application (monitoring + web dashboard)
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── LICENSE            # MIT license
├── .gitignore         # Git ignore file
├── network_log.csv    # Generated data file (created at runtime)
└── screenshots/       # Dashboard screenshots
    ├── dashboard.png
    └── mobile.png
```

## 🛠️ Technical Details

### Technologies Used
- **Python 3.7+** - Core application logic
- **Flask** - Web framework for dashboard
- **Threading** - Concurrent monitoring and web serving
- **CSV** - Data storage and persistence
- **HTML/CSS/JavaScript** - Frontend dashboard interface

### Architecture
- **Multi-threaded design** - Separate threads for monitoring and web interface
- **Real-time updates** - Efficient polling system with minimal resource usage  
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Lightweight** - Minimal dependencies and resource footprint

### Performance
- **CPU Usage**: < 1% during normal operation
- **Memory Usage**: < 50MB typical
- **Network Usage**: 1 ping packet every 30 seconds
- **Update Latency**: Dashboard updates within 25 seconds of network changes

## 🔍 API Endpoints

The application provides a simple REST API:

### GET `/`
Main dashboard interface

### GET `/check_updates`
Check for new monitoring data
```json
{
  "updated": true,
  "last_modified": 1640995200.0,
  "message": "New data available"
}
```

### GET `/status`
Current network status
```json
{
  "status": "UP",
  "timestamp": "2025-05-26 14:30:45",
  "ip": "8.8.8.8",
  "realtime": true
}
```

## 📈 Data Format

Monitoring data is stored in CSV format:

```csv
Timestamp,IP Address,Status
2025-05-26 14:30:15,8.8.8.8,UP
2025-05-26 14:30:45,8.8.8.8,UP
2025-05-26 14:31:15,8.8.8.8,DOWN
```

## 🚨 Troubleshooting

### Common Issues

**"Permission denied" when running**
- On some systems, ping requires elevated privileges
- Try running with `sudo python app.py` (Linux/macOS) or as Administrator (Windows)

**Dashboard shows "CSV file not found"**
- The monitoring thread takes a few seconds to create the first log entry
- Wait 30-60 seconds for the first ping result

**Browser doesn't auto-update**
- Check browser console for JavaScript errors
- Ensure the Flask server is running without errors
- Try manually refreshing the page

### Performance Issues

**High CPU usage**
- Check if multiple instances are running
- Verify ping interval isn't set too low (minimum recommended: 10 seconds)

**Slow dashboard loading**
- Large CSV files (>1000 entries) may slow loading
- Consider archiving old data or implementing data rotation

## 🤝 Contributing

Contributions are welcome! Here are some areas for improvement:

- [ ] **Multiple device monitoring** - Monitor several IPs simultaneously
- [ ] **Email/SMS alerts** - Notifications when devices go down
- [ ] **Historical charts** - Graphical uptime visualization  
- [ ] **Configuration file** - External config instead of code changes
- [ ] **Database storage** - Alternative to CSV for large deployments
- [ ] **Docker support** - Containerized deployment
- [ ] **Authentication** - Login system for security

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Marlon** - Network Security Consultant  
- GitHub: [@marlon-netsecurity](https://github.com/marlon-netsecurity)
- LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)

## 🙏 Acknowledgments

- Built as part of learning network monitoring and web development
- Inspired by enterprise network monitoring solutions
- Thanks to the open-source community for Flask and Python ecosystem

## ⭐ Support

If this project helped you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting issues or bugs
- 💡 Suggesting new features
- 📖 Improving documentation

---

**Made with ❤️ for network administrators and monitoring enthusiasts**