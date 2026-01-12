#!/bin/bash

echo "🚀 Starting Quant Oracle Servers..."
echo ""

# Kill any existing processes
echo "Stopping existing servers..."
pkill -f "python api/server.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 2

# Start backend
echo "Starting backend API on port 8000..."
cd /workspaces/workspaces/backend
python api/server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Test backend
echo "Testing backend..."
curl -s http://localhost:8000/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start. Check /tmp/backend.log"
fi

# Start web
echo ""
echo "Starting web app on port 3000..."
cd /workspaces/workspaces/frontend/web
npm run dev > /tmp/web.log 2>&1 &
WEB_PID=$!
echo "Web PID: $WEB_PID"

echo ""
echo "⏳ Waiting for servers to be ready (30 seconds)..."
sleep 30

echo ""
echo "📊 Server Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Backend API:"
echo "  Local:  http://localhost:8000"
echo "  Public: https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev"
echo "  Docs:   https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev/docs"
echo ""
echo "Web Application:"
echo "  Local:  http://localhost:3000"
echo "  Public: https://3000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Logs:"
echo "  Backend: tail -f /tmp/backend.log"
echo "  Web:     tail -f /tmp/web.log"
echo ""
echo "🎉 Servers are starting! Open the Public URLs above in your browser."
echo ""
