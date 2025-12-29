#!/bin/bash
# Quick Connection Verification Script

echo "=========================================="
echo "Kwizy - Frontend/Backend/Database Check"
echo "=========================================="

# Check Backend
echo ""
echo "1. Checking Backend Configuration..."
if [ -f ".env" ]; then
    if grep -q "SUPABASE_URL" .env && grep -q "SUPABASE_KEY" .env; then
        echo "   ✓ .env configured with Supabase credentials"
    else
        echo "   ✗ .env missing Supabase credentials"
    fi
else
    echo "   ✗ .env file not found"
fi

# Check Python
echo ""
echo "2. Checking Python Environment..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo "   ✓ Python installed: $PYTHON_VERSION"
    
    if python -c "import flask" 2>/dev/null; then
        echo "   ✓ Flask installed"
    else
        echo "   ✗ Flask not installed"
    fi
    
    if python -c "from supabase import create_client" 2>/dev/null; then
        echo "   ✓ Supabase client installed"
    else
        echo "   ✗ Supabase client not installed"
    fi
else
    echo "   ✗ Python not installed"
fi

# Check Frontend
echo ""
echo "3. Checking Frontend Configuration..."
if [ -f "frontend/.env.local" ]; then
    echo "   ✓ frontend/.env.local exists"
    if grep -q "REACT_APP_API_URL" frontend/.env.local; then
        API_URL=$(grep "REACT_APP_API_URL" frontend/.env.local | cut -d= -f2)
        echo "   ✓ API URL configured: $API_URL"
    fi
else
    echo "   ✗ frontend/.env.local not found"
fi

if [ -f "frontend/.env.production" ]; then
    echo "   ✓ frontend/.env.production exists"
    if grep -q "REACT_APP_API_URL" frontend/.env.production; then
        API_URL=$(grep "REACT_APP_API_URL" frontend/.env.production | cut -d= -f2)
        echo "   ✓ Production API URL: $API_URL"
    fi
fi

if [ -d "frontend/node_modules" ]; then
    echo "   ✓ Frontend dependencies installed"
else
    echo "   ✗ Frontend dependencies not installed (run: cd frontend && npm install)"
fi

# Check Backend Connection
echo ""
echo "4. Checking Backend Connectivity..."
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "   ✓ Backend running at http://localhost:5000"
else
    echo "   ✗ Backend not responding (run: python app.py)"
fi

# Check Database
echo ""
echo "5. Checking Database Connection..."
if [ -f ".env" ] && grep -q "SUPABASE_URL" .env; then
    echo "   ✓ Supabase credentials found"
    echo "   (Database connectivity verified when backend is running)"
else
    echo "   ✗ Cannot check database without .env"
fi

echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Configure Backend:"
echo "   - Create .env file with Supabase credentials"
echo "   - Run: python app.py"
echo ""
echo "2. Configure Frontend:"
echo "   - Verify frontend/.env.local has correct API URL"
echo "   - Run: cd frontend && npm start"
echo ""
echo "3. Test Connection:"
echo "   - Open http://localhost:3000"
echo "   - Try signing up"
echo "   - Check browser console (F12) for errors"
echo ""
echo "4. Troubleshooting:"
echo "   - See CONNECTION_GUIDE.md for detailed steps"
echo "   - Use api-tester.html to test endpoints"
echo ""
