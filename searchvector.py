#!/usr/bin/env python3

import os
import subprocess
import sys
import re
from rich.console import Console
from rich.markdown import Markdown

# Supported commands
COMMANDS = ["back", "search", "use", "select", "help", "exit", "clear", "quit", "q"]

# Display help for the pseudo-shell
HELP_TEXT = """
Commands available:
  search <query>    - Search the HackTricks repository for a given query
  use <index>       - Select a file to view by specifying its index number from the last search
  select <index>    - Alias for 'use', behaves identically
  back              - Go back to the initial prompt to perform another action
  clear             - Clear the console screen
  help              - Display this help message
  exit, quit, q     - Exit the pseudo-shell
"""

console = Console()

def search_hacktricks(search_query, hacktricks_dir):
    results = []
    for root, dirs, files in os.walk(hacktricks_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(search_query, content, re.IGNORECASE):
                            results.append(file_path)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return results

def display_file(file_path):
    console.rule(f"[bold blue]Content of {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            md = Markdown(content)
            console.print(md)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

def main(search_query=None):
    home_dir = os.path.expanduser("~")
    hacktricks_dir = os.path.join(home_dir, "hacktricks")

    if not os.path.exists(hacktricks_dir):
        # Clone the repository
        print("HackTricks content not found. Downloading...")
        clone_url = "https://github.com/carlospolop/hacktricks.git"
        try:
            subprocess.run(["git", "clone", clone_url, hacktricks_dir], check=True)
        except subprocess.CalledProcessError:
            print("Error: Could not clone HackTricks repository.")
            sys.exit(1)

    search_results = []

    if search_query:
        # Perform initial search if query is provided via command line
        print(f"Searching for: {search_query}\n")
        search_results = search_hacktricks(search_query, hacktricks_dir)
        if search_results:
            print(f"\nFound {len(search_results)} result(s):\n")
            for idx, file_path in enumerate(search_results):
                print(f"{idx+1}. {file_path}")
        else:
            print("No results found.")

    while True:
        command = input("searchvector:> ").strip()
        if not command:
            continue

        parts = command.split(" ", 1)
        action = parts[0].lower()

        if action == "search" and len(parts) > 1:
            search_query = parts[1]
            print(f"Searching for: {search_query}\n")
            search_results = search_hacktricks(search_query, hacktricks_dir)
            if search_results:
                print(f"\nFound {len(search_results)} result(s):\n")
                for idx, file_path in enumerate(search_results):
                    print(f"{idx+1}. {file_path}")
            else:
                print("No results found.")

        elif action in ["use", "select"] and len(parts) > 1:
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(search_results):
                    display_file(search_results[idx])
                else:
                    print("Invalid index. Please select a valid number from the search results.")
            except ValueError:
                print("Please provide a valid number after the command.")

        elif action == "back":
            search_results = []
            print("Going back to the main prompt.")

        elif action in ["help", "?"]:
            print(HELP_TEXT)

        elif action in ["exit", "quit", "q"]:
            print("Exiting searchvector.")
            break

        elif action == "clear":
            console.clear()

        elif action.isdigit():
            try:
                idx = int(action) - 1
                if 0 <= idx < len(search_results):
                    display_file(search_results[idx])
                else:
                    print("Invalid index. Please select a valid number from the search results.")
            except ValueError:
                print("Please provide a valid number.")

        else:
            print(f"Unknown command: {action}. Type 'help' to see the list of available commands.")

if __name__ == "__main__":
    try:
        from rich import print
    except ImportError:
        print("The 'rich' library is required to run this script.")
        print("Install it using: pip install rich")
        sys.exit(1)

    # Check if a search query is provided via command line arguments
    if len(sys.argv) > 1:
        search_query = ' '.join(sys.argv[1:])
        main(search_query)
    else:
        main()
