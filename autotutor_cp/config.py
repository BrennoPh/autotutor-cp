"""Central application limits. Secrets are supplied in memory or environment."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'seed_problems.json'
WORKSPACE = BASE_DIR / 'workspace'
TIME_LIMIT_SEC = 2.0
COMPILE_TIMEOUT_SEC = 25
MEMORY_LIMIT_MB = 256
OUTPUT_LIMIT_BYTES = 2 * 1024 * 1024
MAX_SOURCE_BYTES = 100_000
MAX_TESTS = 200
STARTER_CODE = '''#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    return 0;
}
'''
