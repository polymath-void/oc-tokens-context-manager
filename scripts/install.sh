#!/data/data/com.termux/files/usr/bin/bash
# OC Tokens Context Manager - Quick Installer

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  OC Tokens Context Manager - Quick Installer"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check OpenCode config
if [ ! -d "$HOME/.config/opencode" ]; then
    echo "❌ OpenCode config directory not found."
    echo "   Expected: $HOME/.config/opencode"
    echo "   Please ensure OpenCode is installed."
    exit 1
fi

echo "✅ OpenCode config found"

# Run deployment
echo ""
echo "🚀 Starting deployment..."
echo ""

python3 "$PROJECT_ROOT/src/deploy.py" --install

if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  ✅ Installation Complete!"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📊 Next Steps:"
    echo ""
    echo "  1. Check status:"
    echo "     python3 $PROJECT_ROOT/src/manager.py status"
    echo ""
    echo "  2. Enable ML preloading:"
    echo "     python3 $PROJECT_ROOT/src/manager.py enable ml-preload"
    echo ""
    echo "  3. View analytics:"
    echo "     python3 $PROJECT_ROOT/src/analytics.py dashboard"
    echo ""
    echo "  4. Start using OpenCode:"
    echo "     opencode"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Check errors above."
    exit 1
fi
