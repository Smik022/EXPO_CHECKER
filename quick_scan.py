from scanner import ExpoScanner
import sys
import re

# DEBUG: Test the regex against the known key from screenshot
test_key = "AIzaSy0-NTAE830nB74cIawFAndI_caVxLTzFsY"
# Note: Copied pattern from patterns.py manually for test
test_pattern = r"AIza[0-9A-Za-z\\-_]{35}"
print(f"\n[DEBUG] Regex Check: '{test_key}' matches? {bool(re.search(test_pattern, test_key))}")

# Target path provided by user
REPO_PATH = r"C:\Users\smik0\Desktop\Resume Analyzer\Resume-Analyzer"

print(f"--- STARTING SCAN ON: {REPO_PATH} ---")

try:
    scanner = ExpoScanner(REPO_PATH)
    count = 0
    for update in scanner.scan_history():
        if update["status"] == "progress":
            # Print status every 10 commits to show life
            if update["current"] % 10 == 0 or update["current"] == 1:
                print(f"[PROGRESS] {update['message']}")
                
        if update["status"] == "finding":
            count += 1
            f = update["data"]
            print(f"\n[!] VIOLATION FOUND!")
            print(f"    Type:   {f['secret_type']}")
            print(f"    Commit: {f['commit_hash'][:7]} by {f['author']}")
            print(f"    Date:   {f['date']}")
            print(f"    File:   {f['file_path']}")
            print(f"    Secret: {f['secret_value']}")
            print(f"    Line:   {f['line_content']}")

    if count == 0:
        print("\nNo secrets found (checked all commits).")
    else:
        print(f"\nScan complete. Found {count} secrets.")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
