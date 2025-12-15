# Troubleshooting Guide

## Issue: Frontend loads but doesn't show backend data

### Quick Checks:

1. **Open Browser Console** (F12) on your mobile and check for:
   - Look for the message: "🌐 API Base URL: ..." 
   - It should show: `http://192.168.5.12:8000/api/v1`
   - If it shows `localhost`, the fix didn't work

2. **Check Network Tab** in browser console:
   - Look for failed requests
   - Check if requests are going to correct IP

3. **CORS Errors**: If you see CORS errors in console, the backend needs to allow your mobile's request

### Solutions:

#### Solution 1: Hard Restart Frontend
```bash
# Stop frontend (Ctrl+C)
# Clear node cache
rm -rf node_modules/.cache
# Restart
npm start
```

#### Solution 2: Access via IP on Both Ends
Instead of using localhost on your computer, access from:
- Computer: `http://192.168.5.12:3000`
- Mobile: `http://192.168.5.12:3000`

The new config.js will automatically use the correct backend IP!

#### Solution 3: Check Backend Logs
Look at your backend terminal for incoming requests. You should see:
```
INFO: 192.168.5.X:XXXXX - "GET /api/v1/users/ HTTP/1.1" 200 OK
```

If you don't see requests from your mobile IP, the frontend isn't calling the backend.

### Current Config Status:
- ✅ Backend: Running on 0.0.0.0:8000 (accessible from network)
- ✅ Frontend: Running on 0.0.0.0:3000 (accessible from network)  
- ✅ Firewall: Ports 3000 and 8000 allowed
- ✅ CORS: Configured for 192.168.5.12
- 🔄 Config: Auto-detects localhost vs network access
