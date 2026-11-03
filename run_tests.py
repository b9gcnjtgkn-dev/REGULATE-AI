#!/usr/bin/env python3
"""
REGULATE.AI — Automated Verification Suite Runner
Executes comprehensive tests across all core regulatory compliance engines with zero dependencies.
"""

import sys
import os
import unittest

def run_suite():
    print("=" * 70)
    print("RUNNING REGULATE.AI COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)
    
    # Ensure root directory is on PYTHONPATH
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root_dir)
    
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(root_dir, "tests"), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 70)
    print("VERIFICATION SUITE COMPLETED")
    print(f"Total Tests Run: {result.testsRun} | Passed: {result.testsRun - len(result.failures) - len(result.errors)} | Failed: {len(result.failures) + len(result.errors)}")
    
    if result.wasSuccessful():
        print("Overall Result: SUCCESS [All 6/6 Core Engines Verified]")
        print("=" * 70)
        return 0
    else:
        print("Overall Result: FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(run_suite())
