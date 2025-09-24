#!/usr/bin/env python3
"""
GitHub Word Drawer - Creates commit patterns to draw words on GitHub contribution graph.

This script takes a word as input and creates a new git branch with commits
that form the word pattern on the GitHub contribution graph (7 rows × N columns).
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from typing import List, Dict

# ASCII art patterns for letters (7 rows high, variable width)
LETTER_PATTERNS = {
    'A': [
        " ███ ",
        "█   █",
        "█   █",
        "█████",
        "█   █",
        "█   █",
        "     "
    ],
    'B': [
        "████ ",
        "█   █",
        "█   █",
        "████ ",
        "█   █",
        "█   █",
        "████ "
    ],
    'C': [
        " ███ ",
        "█   █",
        "█    ",
        "█    ",
        "█    ",
        "█   █",
        " ███ "
    ],
    'D': [
        "████ ",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "████ "
    ],
    'E': [
        "█████",
        "█    ",
        "█    ",
        "████ ",
        "█    ",
        "█    ",
        "█████"
    ],
    'F': [
        "█████",
        "█    ",
        "█    ",
        "████ ",
        "█    ",
        "█    ",
        "█    "
    ],
    'G': [
        " ███ ",
        "█   █",
        "█    ",
        "█ ███",
        "█   █",
        "█   █",
        " ███ "
    ],
    'H': [
        "█   █",
        "█   █",
        "█   █",
        "█████",
        "█   █",
        "█   █",
        "█   █"
    ],
    'I': [
        "█████",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  ",
        "█████"
    ],
    'J': [
        "█████",
        "    █",
        "    █",
        "    █",
        "    █",
        "█   █",
        " ███ "
    ],
    'K': [
        "█   █",
        "█  █ ",
        "█ █  ",
        "██   ",
        "█ █  ",
        "█  █ ",
        "█   █"
    ],
    'L': [
        "█    ",
        "█    ",
        "█    ",
        "█    ",
        "█    ",
        "█    ",
        "█████"
    ],
    'M': [
        "█   █",
        "██ ██",
        "█ █ █",
        "█   █",
        "█   █",
        "█   █",
        "█   █"
    ],
    'N': [
        "█   █",
        "██  █",
        "█ █ █",
        "█  ██",
        "█   █",
        "█   █",
        "█   █"
    ],
    'O': [
        " ███ ",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        " ███ "
    ],
    'P': [
        "████ ",
        "█   █",
        "█   █",
        "████ ",
        "█    ",
        "█    ",
        "█    "
    ],
    'Q': [
        " ███ ",
        "█   █",
        "█   █",
        "█   █",
        "█ █ █",
        "█  █ ",
        " ████"
    ],
    'R': [
        "████ ",
        "█   █",
        "█   █",
        "████ ",
        "█ █  ",
        "█  █ ",
        "█   █"
    ],
    'S': [
        " ███ ",
        "█   █",
        "█    ",
        " ███ ",
        "    █",
        "█   █",
        " ███ "
    ],
    'T': [
        "█████",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  "
    ],
    'U': [
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        " ███ "
    ],
    'V': [
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        " █ █ ",
        "  █  "
    ],
    'W': [
        "█   █",
        "█   █",
        "█   █",
        "█   █",
        "█ █ █",
        "██ ██",
        "█   █"
    ],
    'X': [
        "█   █",
        " █ █ ",
        "  █  ",
        "  █  ",
        "  █  ",
        " █ █ ",
        "█   █"
    ],
    'Y': [
        "█   █",
        "█   █",
        " █ █ ",
        "  █  ",
        "  █  ",
        "  █  ",
        "  █  "
    ],
    'Z': [
        "█████",
        "    █",
        "   █ ",
        "  █  ",
        " █   ",
        "█    ",
        "█████"
    ],
    ' ': [
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     "
    ]
}


class GitHubWordDrawer:
    def __init__(self, word: str, start_date: str = None):
        self.word = word.upper()
        self.start_date = self._parse_start_date(start_date)

    def _parse_start_date(self, start_date: str) -> datetime:
        """Parse start date or use a date from one year ago."""
        if start_date:
            return datetime.strptime(start_date, "%Y-%m-%d")
        else:
            # Start from a Sunday one year ago to align with GitHub's week start
            one_year_ago = datetime.now() - timedelta(days=365)
            days_since_sunday = one_year_ago.weekday() + 1
            if days_since_sunday == 7:
                days_since_sunday = 0
            return one_year_ago - timedelta(days=days_since_sunday)

    def _create_pattern_grid(self) -> List[List[bool]]:
        """Create a 2D grid representing the commit pattern."""
        if not self.word:
            return []

        # Get patterns for each letter
        letter_patterns = []
        for char in self.word:
            if char in LETTER_PATTERNS:
                letter_patterns.append(LETTER_PATTERNS[char])
            else:
                letter_patterns.append(LETTER_PATTERNS[' '])  # Default to space

        # Calculate total width
        total_width = sum(len(pattern[0]) for pattern in letter_patterns) + len(letter_patterns) - 1

        # Create the grid (7 rows for days of week)
        grid = [[False for _ in range(total_width)] for _ in range(7)]

        # Fill the grid
        col_offset = 0
        for pattern in letter_patterns:
            pattern_width = len(pattern[0])

            for row in range(7):
                for col in range(pattern_width):
                    if pattern[row][col] == '█':
                        grid[row][col_offset + col] = True

            col_offset += pattern_width + 1  # Add spacing between letters

        return grid

    def _get_commit_dates(self, grid: List[List[bool]]) -> List[datetime]:
        """Convert grid pattern to commit dates."""
        commit_dates = []

        if not grid or not grid[0]:
            return commit_dates

        num_weeks = len(grid[0])

        for week in range(num_weeks):
            for day in range(7):  # 0=Sunday, 1=Monday, ..., 6=Saturday
                if grid[day][week]:
                    commit_date = self.start_date + timedelta(weeks=week, days=day)
                    commit_dates.append(commit_date)

        return sorted(commit_dates)

    def create_branch(self, branch_name: str = None) -> str:
        """Create a new git branch."""
        if not branch_name:
            branch_name = f"word-{self.word.lower().replace(' ', '-')}"

        try:
            # Check if branch exists
            result = subprocess.run(['git', 'branch', '--list', branch_name],
                                  capture_output=True, text=True)
            if branch_name in result.stdout:
                print(f"Branch '{branch_name}' already exists. Switching to it.")
                subprocess.run(['git', 'checkout', branch_name], check=True)
            else:
                subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
                print(f"Created and switched to branch '{branch_name}'")

            return branch_name
        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {e}")
            sys.exit(1)

    def create_commits(self, commit_dates: List[datetime]):
        """Create commits for each date in the pattern."""
        if not commit_dates:
            print("No commit dates generated. Check your word pattern.")
            return

        print(f"Creating {len(commit_dates)} commits...")

        # Create a simple file to commit
        commit_file = "word_pattern.txt"

        for i, commit_date in enumerate(commit_dates):
            # Create/update file content
            with open(commit_file, 'w') as f:
                f.write(f"Commit {i+1}/{len(commit_dates)} for word: {self.word}\n")
                f.write(f"Date: {commit_date.strftime('%Y-%m-%d')}\n")
                f.write(f"Drawing pattern on GitHub contribution graph\n")

            # Stage the file
            subprocess.run(['git', 'add', commit_file], check=True)

            # Create commit with specific date
            commit_message = f"Draw '{self.word}' - commit {i+1}/{len(commit_dates)}"
            date_str = commit_date.strftime('%Y-%m-%d %H:%M:%S')

            env = {
                'GIT_AUTHOR_DATE': date_str,
                'GIT_COMMITTER_DATE': date_str
            }

            subprocess.run(['git', 'commit', '-m', commit_message],
                          env=env, check=True)

        print(f"Successfully created {len(commit_dates)} commits for '{self.word}'")

    def draw_preview(self):
        """Print a preview of how the word will look."""
        grid = self._create_pattern_grid()
        if not grid:
            print("No pattern to display")
            return

        print(f"\nPreview of '{self.word}' pattern:")
        print("=" * (len(grid[0]) + 2))

        for row in grid:
            line = "|"
            for cell in row:
                line += "█" if cell else " "
            line += "|"
            print(line)

        print("=" * (len(grid[0]) + 2))
        print(f"Pattern size: {len(grid)} rows × {len(grid[0])} columns")

    def run(self, branch_name: str = None, preview_only: bool = False):
        """Main execution method."""
        print(f"Drawing word: '{self.word}'")

        grid = self._create_pattern_grid()
        commit_dates = self._get_commit_dates(grid)

        self.draw_preview()

        if preview_only:
            print(f"Preview mode: Would create {len(commit_dates)} commits")
            return

        if not commit_dates:
            print("No commits to create. Exiting.")
            return

        print(f"\nWill create {len(commit_dates)} commits starting from {self.start_date.strftime('%Y-%m-%d')}")

        response = input("Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return

        branch_name = self.create_branch(branch_name)
        self.create_commits(commit_dates)

        print(f"\nDone! Your word '{self.word}' has been drawn on branch '{branch_name}'")
        print("Push to GitHub to see the contribution graph pattern.")


def main():
    parser = argparse.ArgumentParser(description="Draw words on GitHub contribution graph")
    parser.add_argument("word", help="Word to draw (letters and spaces only)")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD), defaults to one year ago")
    parser.add_argument("--branch", help="Branch name (auto-generated if not provided)")
    parser.add_argument("--preview", action="store_true", help="Show preview only, don't create commits")

    args = parser.parse_args()

    # Validate word contains only letters and spaces
    if not all(c.isalpha() or c.isspace() for c in args.word):
        print("Error: Word can only contain letters and spaces")
        sys.exit(1)

    drawer = GitHubWordDrawer(args.word, args.start_date)
    drawer.run(args.branch, args.preview)


if __name__ == "__main__":
    main()