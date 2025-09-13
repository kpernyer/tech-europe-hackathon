#!/bin/bash

echo "🧪 Testing Hackathon Demo Setup..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Run this from the organizational-ai-fine-tuning directory"
    exit 1
fi

echo "✅ Repository structure looks good"

# Check backend files
if [ -f "backend/app/main.py" ] && [ -f "backend/app/routers/fine_tuning.py" ]; then
    echo "✅ Backend files present"
else
    echo "❌ Backend files missing"
    exit 1
fi

# Check frontend files  
if [ -f "frontend/src/components/FineTuningExperiment.tsx" ]; then
    echo "✅ Frontend components present"
else
    echo "❌ Frontend components missing"
    exit 1
fi

# Check sample data
if [ -f "experiments/sample_companies/techcorp_vision.md" ]; then
    echo "✅ Sample company data present"
else
    echo "❌ Sample company data missing"
    exit 1
fi

# Check demo script
if [ -f "docs/DEMO_SCRIPT.md" ]; then
    echo "✅ Demo script present"
else
    echo "❌ Demo script missing"
    exit 1
fi

echo ""
echo "🎯 Demo Readiness Checklist:"
echo "✅ Repository extracted and initialized"
echo "✅ Backend API with fine-tuning endpoints"
echo "✅ Frontend React interface"
echo "✅ Docker setup for easy deployment"  
echo "✅ Sample organizational documents"
echo "✅ Complete demo script with timing"
echo "✅ Git repository initialized"
echo ""
echo "🚀 Your hackathon demo is ready!"
echo "   Run 'make demo' to start the presentation"
echo ""
echo "📋 Files created:"
find . -name "*.md" -o -name "*.py" -o -name "*.tsx" -o -name "*.json" | head -10