# 🔧 Fix "Failed to fetch" Error

## ❌ Problem
You're seeing a "Failed to fetch" error in the browser when trying to use the Quotex Predictor.

## ✅ Solution

### **Step 1: Start the Django Server**
The most common cause is that the Django server is not running.

**Option A: Use the batch file (Windows)**
```bash
# Double-click this file:
start_quotex_server.bat
```

**Option B: Use command line**
```bash
# Navigate to project directory
cd quotex_predictor

# Start the server
python manage.py runserver 127.0.0.1:8000
```

**Option C: Use the startup script**
```bash
python start_server.py
```

### **Step 2: Verify Server is Running**
You should see output like:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### **Step 3: Access the Application**
Open your browser and go to:
```
http://127.0.0.1:8000
```

## 🔍 Troubleshooting

### If you still see "Failed to fetch":

1. **Check Browser Console (F12)**
   - Look for detailed error messages
   - Check the Network tab for failed requests

2. **Verify URL**
   - Make sure the frontend is accessing `http://127.0.0.1:8000`
   - Not `localhost:3000` or any other port

3. **Check Firewall**
   - Windows Firewall might be blocking port 8000
   - Allow Python through the firewall

4. **Try Different Browser**
   - Test in Chrome, Firefox, or Edge
   - Clear browser cache (Ctrl+F5)

### Common Error Messages:

| Error | Cause | Solution |
|-------|-------|----------|
| "Failed to fetch" | Server not running | Start Django server |
| "Connection refused" | Wrong port/URL | Use http://127.0.0.1:8000 |
| "CORS error" | Cross-origin issue | Server has CORS enabled |
| "404 Not Found" | Wrong endpoint | Check API URLs |

## 🧪 Test API Endpoints

Once server is running, test these URLs in your browser:

1. **Trading Pairs**: http://127.0.0.1:8000/api/trading-pairs/
2. **Homepage**: http://127.0.0.1:8000/
3. **Current Price**: http://127.0.0.1:8000/api/current-price/?symbol=EURUSD

## 📊 System Status

Run the health check to verify everything is working:
```bash
python system_health_check.py
```

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies (if needed)
pip install -r requirements.txt

# 2. Run migrations (if needed)
cd quotex_predictor
python manage.py migrate

# 3. Start server
python manage.py runserver 127.0.0.1:8000

# 4. Open browser to http://127.0.0.1:8000
```

## ✅ Success Indicators

You'll know it's working when:
- ✅ Server shows "Starting development server at http://127.0.0.1:8000/"
- ✅ Browser loads the Quotex Predictor interface
- ✅ No "Failed to fetch" errors in browser console
- ✅ API endpoints return JSON data

## 🆘 Still Having Issues?

1. **Check Python Version**: `python --version` (should be 3.8+)
2. **Check Dependencies**: `pip list | findstr Django`
3. **Check Port**: Make sure port 8000 is not used by another application
4. **Restart Computer**: Sometimes helps with port/firewall issues

---

**🎯 The key point**: The Django server MUST be running for the frontend to work. The "Failed to fetch" error almost always means the server is not running or not accessible.