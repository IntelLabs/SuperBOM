#!/bin/bash
# Local fuzzing script for SuperBOM

set -e

echo "🔍 SuperBOM Fuzzing Runner"
echo "=========================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run 'uv sync' first."
    exit 1
fi

# Install fuzzing dependencies if not already installed
echo "📦 Installing fuzzing dependencies..."
uv sync --group fuzzing

# Function to run random fuzzing
run_random() {
    local iterations=${1:-200}  # Default 200 iterations
    echo "🎲 Running random fuzzing with ${iterations} iterations per function..."
    echo "   This tests parsers with malformed input data"
    
    uv run python fuzz/fuzz_parsers.py ${iterations}
}

# Function to run Hypothesis fuzzing
run_hypothesis() {
    echo "🔬 Running Hypothesis property-based testing..."
    uv run python -m pytest fuzz/fuzz_hypothesis.py -v
}

# Function to run both approaches
run_both() {
    local iterations=${1:-200}
    run_hypothesis
    echo ""
    run_random ${iterations}
}

# Function to check for Atheris and run if available
run_atheris() {
    echo "🚀 Checking for Atheris availability..."
    if uv run python -c "import atheris" 2>/dev/null; then
        echo "✅ Atheris is available!"
        local duration=${1:-60}
        echo "   Running Atheris fuzzing for ${duration} seconds..."
        
        # Create a simple Atheris fuzzer on the fly
        cat > temp_atheris_fuzz.py << 'EOF'
import sys
import atheris
import tempfile
from pathlib import Path
sys.path.insert(0, 'src')
from superbom.utils.parsers import parse_requirements

@atheris.instrument_func
def TestOneInput(data):
    try:
        content = data.decode('utf-8', errors='ignore')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()
            parse_requirements(f.name)
            Path(f.name).unlink()
    except:
        pass

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
EOF
        timeout ${duration}s uv run python temp_atheris_fuzz.py -max_total_time=${duration} || {
            local exit_code=$?
            if [ $exit_code -eq 124 ]; then
                echo "⏰ Atheris fuzzing completed (timeout reached)"
            elif [ $exit_code -eq 130 ]; then
                echo "⏹️  Atheris fuzzing stopped by user"  
            else
                echo "💥 Atheris found an issue! Exit code: $exit_code"
            fi
        }
        rm -f temp_atheris_fuzz.py
    else
        echo "⚠️  Atheris not available on this platform"
        echo "   Install with: pip install atheris (requires clang on some systems)"
        echo "   Falling back to random fuzzing..."
        run_random ${1:-200}
    fi
}

# Main menu
case "${1:-interactive}" in
    "random")
        run_random ${2:-200}
        ;;
    "hypothesis")
        run_hypothesis
        ;;
    "atheris")
        run_atheris ${2:-60}
        ;;
    "both")
        run_both ${2:-200}
        ;;
    "all")
        echo "🎯 Running all fuzzing approaches..."
        run_hypothesis
        echo ""
        run_random ${2:-200}
        echo ""
        run_atheris ${3:-60}
        ;;
    "interactive"|*)
        echo ""
        echo "Choose fuzzing method:"
        echo "1) Random fuzzing (cross-platform)"
        echo "2) Hypothesis property-based testing"  
        echo "3) Atheris coverage-guided fuzzing (if available)"
        echo "4) Both random + hypothesis"
        echo "5) All approaches"
        echo ""
        read -p "Enter choice (1-5): " choice
        
        case $choice in
            1)
                read -p "Iterations per function (default 200): " iterations
                run_random ${iterations:-200}
                ;;
            2)
                run_hypothesis
                ;;
            3)
                read -p "Duration in seconds (default 60): " duration
                run_atheris ${duration:-60}
                ;;
            4)
                read -p "Iterations for random fuzzing (default 200): " iterations
                run_both ${iterations:-200}
                ;;
            5)
                read -p "Iterations for random fuzzing (default 200): " iterations
                read -p "Duration for Atheris in seconds (default 60): " duration
                echo "🎯 Running all fuzzing approaches..."
                run_hypothesis
                echo ""
                run_random ${iterations:-200}
                echo ""
                run_atheris ${duration:-60}
                ;;
            *)
                echo "❌ Invalid choice"
                exit 1
                ;;
        esac
        ;;
esac

echo ""
echo "✅ Fuzzing completed!"
echo "📁 Check for any crash-*, leak-*, or timeout-* files in the current directory"
echo "🔍 Look for potential issues reported in the output above"