import os

# FIX: Explicitly set git path for Windows if not found
# (Handling this here so it works for both server.py and standalone scripts)
if os.name == 'nt' and "GIT_PYTHON_GIT_EXECUTABLE" not in os.environ:
    possible_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe",
    ]
    for path in possible_paths:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = expanded_path
            break

import git
import sys
from patterns import scan_text
from dataclasses import dataclass
from typing import List, Generator

@dataclass
class Finding:
    commit_hash: str
    author: str
    date: str
    file_path: str
    secret_type: str
    secret_value: str
    line_content: str

class ExpoScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
            if self.repo.bare:
                raise ValueError("Bare repositories are not supported")
        except git.exc.InvalidGitRepositoryError:
            raise ValueError(f"Not a valid git repository: {repo_path}")

    def scan_history(self) -> Generator[dict, None, None]:
        """
        Yields progress updates and findings.
        Format: {"status": "progress"|"finding"|"complete", "data": ...}
        """
        
        # Get all commits in reverse chronological order
        commits = list(self.repo.iter_commits())
        total_commits = len(commits)
        
        yield {"status": "start", "total": total_commits}

        # We keep track of file hashes we've already scanned to avoid rescanning identical blobs?
        # Actually for history scanning, we want to check the *diff* or the *content at that point*.
        # The best approach for "leaked in history" is checking the patch introduced by each commit.
        
        for i, commit in enumerate(commits):
            progress = int((i / total_commits) * 100)
            yield {
                "status": "progress", 
                "current": i + 1, 
                "total": total_commits, 
                "percent": progress,
                "message": f"Scanning {commit.hexsha[:7]} by {commit.author.name}"
            }

            # Check the diff of this commit against its parent(s)
            # If it's the first commit, compare against empty tree
            parents = commit.parents
            if not parents:
                # First commit
                diffs = commit.diff(git.NULL_TREE, create_patch=True)
            else:
                # Compare against first parent (ignoring merge complexity for now)
                diffs = parents[0].diff(commit, create_patch=True)

            for diff in diffs:
                # Skip binary files and deleted files
                if diff.deleted_file:
                    continue
                    
                path = diff.b_path if diff.b_path else diff.a_path
                
                # Simple ignore list
                if any(x in path for x in ['package-lock.json', 'yarn.lock', '.png', '.jpg', '.exe', '.dll']):
                    continue

                # Get the patch content (the unified diff)
                # We decode bytes to string
                try:
                    patch_text = diff.diff.decode('utf-8', errors='replace')
                except Exception:
                    continue # Skip if undecodable

                # Scan only the added lines in the patch (lines starting with +)
                # This ensures we only catch *new* secrets introduced in this commit
                # and don't re-flag them in every subsequent commit diff if they weren't touched.
                
                # However, if a secret is present in the file but not modified, diff won't show it.
                # But our goal is to find *when it was committed*. So checking diffs is correct.
                # If we want to find *current* secrets, we would scan HEAD separately.
                # Let's stick to Diff scanning for history.

                for line in patch_text.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        clean_line = line[1:] # Remove the +
                        matches = scan_text(clean_line)
                        for match in matches:
                            yield {
                                "status": "finding",
                                "data": Finding(
                                    commit_hash=commit.hexsha,
                                    author=commit.author.name,
                                    date=commit.committed_datetime.isoformat(),
                                    file_path=path,
                                    secret_type=match['type'],
                                    secret_value=match['value'],
                                    line_content=clean_line.strip()
                                ).__dict__
                            }
        
        yield {"status": "complete"}
