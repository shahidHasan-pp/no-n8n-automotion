# Running the Application on Local Network (WiFi)

## Quick Start Guide

### Your Network Setup
- **Your Computer IP**: `192.168.5.12`
- **Backend URL**: `http://192.168.5.12:8000`
- **Frontend URL**: `http://192.168.5.12:3000`

---

## Step 1: Start the Backend

Open a terminal in the backend folder and run:

```bash
cd C:\LAB\DummyProjects\no-n8n-automotion\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Important**: 
- `--host 0.0.0.0` makes the backend accessible from any device on your network
- You should see: `Uvicorn running on http://0.0.0.0:8000`

---

## Step 2: Start the Frontend

Open a **NEW** terminal in the frontend folder and run:

```bash
cd C:\LAB\DummyProjects\no-n8n-automotion\frontend
set HOST=0.0.0.0
npm start
```

**Important**: 
- The `HOST=0.0.0.0` environment variable makes the frontend accessible from your network
- You should see: `On Your Network: http://192.168.5.12:3000`

---

## Step 3: Access from Your Lead's Computer

On your lead's computer (connected to the same WiFi):

### Option 1: Direct Browser Access
Open a browser and navigate to:
```
http://192.168.5.12:3000
```

### Option 2: If Your IP Changes
If your IP is different, check it with:
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter.

Then update the `.env.local` file in the frontend folder:
```
REACT_APP_API_BASE_URL=http://YOUR_NEW_IP:8000/api/v1
```

And restart the frontend.

---

## Troubleshooting

### Firewall Issues
If your lead cannot access the application:

1. **Windows Firewall**: Allow ports 3000 and 8000
   - Open Windows Defender Firewall → Advanced Settings
   - Inbound Rules → New Rule
   - Port → TCP → Specific ports: 3000, 8000
   - Allow the connection

2. **Quick Test**: Temporarily disable Windows Firewall to verify it's the issue

### Network Issues
- Ensure both computers are on the **same WiFi network**
- Try pinging from your lead's computer:
  ```bash
  ping 192.168.5.12
  ```
  
### CORS Issues
- Already configured in `backend/app/main.py` with your IP
- If IP changes, update the CORS origins list

---

## Production Tips

For a more professional demo:

1. **Use ngrok** (for remote access without same network):
   ```bash
   # Install ngrok first
   ngrok http 3000
   ```
   This gives you a public URL that works anywhere.

2. **Build the frontend** for better performance:
   ```bash
   cd frontend
   npm run build
   ```
   Then serve the build folder with a simple server.

---

## What's Already Done

✅ Backend configured to accept connections from `192.168.5.12`
✅ All frontend pages updated to use network IP instead of localhost
✅ Environment variable created for easy IP changes
✅ CORS properly configured

---

## Current Status

- Backend: Ready to run with `--host 0.0.0.0`
- Frontend: Configured to use `http://192.168.5.12:8000/api/v1`
- Both services: Can be accessed from any device on your network
