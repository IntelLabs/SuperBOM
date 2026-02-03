#!/bin/bash
# 
# SuperBOM Fuzzing Test Runner
# This script provides an interactive menu to run different fuzzing approaches
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
echo -e "${BLUE}│      SuperBOM Fuzzing Suite        │${NC}"
echo -e "${BLUE}└─────────────────────────────────────┘${NC}"
echo ""

# Function to run fuzzing tests
run_random_fuzzing() {
    echo -e "${YELLOW}🎲 Running Random Fuzzing${NC}"
    echo "  Generates random input to test parser robustness"
    echo ""
    uv run python fuzz/fuzz_parsers.py 50
}

run_property_testing() {
    echo -e "${YELLOW}📊 Running Property-Based Testing${NC}"
    echo "  Uses Hypothesis to generate structured test cases"
    echo ""
    uv run python fuzz/fuzz_hypothesis.py
}

run_all_fuzzing() {
    echo -e "${YELLOW}🚀 Running All Fuzzing Tests${NC}"
    echo ""
    run_random_fuzzing
    echo ""
    run_property_testing
}

# Main menu
while true; do
    echo -e "${GREEN}Select fuzzing approach:${NC}"
    echo "  1) Random input fuzzing (quick)"
    echo "  2) Property-based testing with Hypothesis"
    echo "  3) Run all fuzzing tests"
    echo "  4) Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            run_random_fuzzing
            ;;
        2)
            run_property_testing
            ;;
        3)
            run_all_fuzzing
            ;;
        4)
            echo -e "${GREEN}✅ Fuzzing session completed!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid option. Please select 1-4.${NC}"
            echo ""
            ;;
    esac
    
    echo ""
    echo -e "${PURPLE}─────────────────────────────────────${NC}"
    echo ""
done