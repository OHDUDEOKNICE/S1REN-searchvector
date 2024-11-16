#!/usr/bin/env python3

import os
import subprocess
import sys
import re
import readline
import webbrowser
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax
from concurrent.futures import ThreadPoolExecutor, as_completed
from rapidfuzz import fuzz  # For fuzzy search
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

# Constants
COMMAND_HISTORY_FILE = os.path.expanduser("~/.searchvector_history")
COMMANDS = ["back", "search", "use", "select", "help", "exit", "clear", "quit", "q", "read"]
LINK_PATTERN = r'(https?://[^\s\)\]]+)'
CODE_BLOCK_PATTERN = r'```(.*?)```'
INVALID_LINK_DOMAINS = ["discord.gg", "twitter.com", "t.me", "github.com/sponsors"]

# Synonyms dictionary for manual configuration
# Add synonyms for your search terms here
SYNONYMS = {
    "ad": ["active directory"],
    "privesc": ["privilege escalation"],
    "kerberoasting": ["kerberoast", "kerberos roasting"],
    "sql": ["sql injection", "structured query language"],
    "lsass": ["local security authority subsystem service"],
    "persistence": ["backdoor", "persistent access"],
    "pass the hash": ["pth", "passing the hash"],
    "rce": ["remote code execution"],
    "smb": ["server message block", "cifs"],
    "cmd": ["command prompt", "windows cmd"],
    "mimikatz": ["credential dumping tool"],
    "shell": ["reverse shell", "bind shell"],
    "privilege escalation": ["priv esc", "privesc"],
    "directory traversal": ["path traversal", "dot-dot-slash attack"],

}

HELP_TEXT = """
Commands available:
  search <query>    - Search the HackTricks repository for a given query (supports synonyms)
  use <index> [show <text|commands|links>] [search <keyword>] - View a file's content, optionally showing only text, commands, or links or searching within the file
  select <index>    - Alias for 'use', behaves identically
  read <link_index> - Open a link found in the article
  back              - Go back to the initial prompt to perform another action
  clear             - Clear the console screen
  help              - Display this help message
  exit, quit, q     - Exit the pseudo-shell
"""

console = Console()

# Set up command history using prompt_toolkit
history = FileHistory(COMMAND_HISTORY_FILE)

# Set up a style for the prompt
style = Style.from_dict({
    'prompt': '#00ff00 bold'
})

def clone_repository(clone_url, hacktricks_dir):
    console.print("[yellow]HackTricks content not found. Cloning repository...[/yellow]")
    try:
        subprocess.run(["git", "clone", clone_url, hacktricks_dir], check=True)
        console.print("[green]Repository cloned successfully.[/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Error: Could not clone HackTricks repository.[/red]")
        sys.exit(1)

def update_repository(hacktricks_dir):
    console.print("[yellow]Updating HackTricks repository...[/yellow]")
    try:
        subprocess.run(["git", "-C", hacktricks_dir, "pull"], check=True)
        console.print("[green]Repository updated successfully.[/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Error: Could not update HackTricks repository.[/red]")

def get_synonym_queries(query):
    """
    Get a list of synonyms for a given query.
    """
    if query in SYNONYMS:
        return SYNONYMS[query]
    return [query]

def search_hacktricks(search_query, hacktricks_dir, fuzzy=False):
    # Get the list of synonyms for the provided search query
    synonyms_list = get_synonym_queries(search_query)
    search_query_lower_list = [q.lower() for q in synonyms_list]

    results = []
    exact_matches = []
    partial_matches = []

    def search_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                title_match = re.search(r'^# (.+)', content, re.MULTILINE)
                title = title_match.group(1) if title_match else "No Title"

                for search_query_lower in search_query_lower_list:
                    if fuzzy:
                        score = fuzz.partial_ratio(search_query_lower, title.lower())
                        if score > 80:
                            return {'title': title, 'path': file_path, 'score': score, 'content': content}
                    else:
                        if re.search(search_query_lower, content, re.IGNORECASE):
                            return {'title': title, 'path': file_path, 'content': content}
        except Exception as e:
            console.print(f"[red]Error reading file {file_path}: {e}[/red]")
        return None

    file_paths = [os.path.join(root, file)
                 for root, dirs, files in os.walk(hacktricks_dir)
                 for file in files if file.endswith(".md")]

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_file = {executor.submit(search_file, fp): fp for fp in file_paths}
        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                # Prioritize exact matches first
                for search_query_lower in search_query_lower_list:
                    if search_query_lower in result['content'].lower():
                        if re.search(r'\b' + re.escape(search_query_lower) + r'\b', result['content'], re.IGNORECASE):
                            exact_matches.append(result)
                        else:
                            partial_matches.append(result)

    # Sort results: exact matches first, then partial matches by score if fuzzy matching
    results = exact_matches + sorted(partial_matches, key=lambda x: x['score'], reverse=True) if fuzzy else exact_matches + partial_matches

    return results

def truncate_middle(text, max_length):
    """
    Truncate a string in the middle with an ellipsis if it exceeds max_length.
    """
    if len(text) <= max_length:
        return text
    else:
        half_length = (max_length - 3) // 2
        return f"{text[:half_length]}...{text[-half_length:]}"

def highlight_terms(text, search_terms):
    """
    Highlight search terms in the provided text using rich-style markup.
    """
    for term in search_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(f"[bold red]{term}[/bold red]", text)
    return text

def display_search_results(results, search_query):
    """
    Display search results in a table format.
    """
    search_terms = get_synonym_queries(search_query)  # Get all synonyms for highlighting
    table = Table(title=f"Search Results for '{search_query}'", show_lines=True)
    table.add_column("No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Path", style="green")

    for idx, result in enumerate(results, start=1):
        relative_path = os.path.relpath(result['path'], os.path.expanduser("~"))
        truncated_path = truncate_middle(relative_path, 80)  # Set a max length for path
        highlighted_title = highlight_terms(result['title'], search_terms)
        table.add_row(str(idx), highlighted_title, truncated_path)

    console.print(table)

def extract_paragraph_and_code_block(content, keyword):
    """
    Extract paragraphs containing the keyword and the code block that follows each paragraph.
    """
    keyword_pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    lines = content.splitlines()
    matches = []
    capturing_paragraph = False
    paragraph = []
    code_block = []
    in_code_block = False

    for line in lines:
        # Start capturing paragraph if the keyword is found
        if keyword_pattern.search(line):
            capturing_paragraph = True

        if capturing_paragraph:
            if line.strip() == "" and not in_code_block:
                # Paragraph ends, add to matches and reset
                if paragraph:
                    highlighted_paragraph = highlight_terms("\n".join(paragraph), [keyword])
                    matches.append(highlighted_paragraph)
                    paragraph = []
                capturing_paragraph = False
            else:
                paragraph.append(line)

        # Handle code block extraction
        if line.strip().startswith("```"):
            if not in_code_block:
                # Start of code block
                in_code_block = True
                code_block = [line]
            else:
                # End of code block
                in_code_block = False
                code_block.append(line)
                matches.append("\n[bold cyan]Code Block:[/bold cyan]\n" + "\n".join(code_block))
                code_block = []
        elif in_code_block:
            code_block.append(line)

    # Add any remaining paragraph
    if paragraph:
        highlighted_paragraph = highlight_terms("\n".join(paragraph), [keyword])
        matches.append(highlighted_paragraph)

    return matches

def display_article(file_path, content_type="all", keyword=None):
    relative_path = os.path.relpath(file_path, os.path.expanduser("~"))
    console.rule(f"[bold blue]Content of {relative_path}[/bold blue]")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

            if keyword:
                # Extract paragraphs and code blocks related to the keyword
                matches = extract_paragraph_and_code_block(content, keyword)
                if matches:
                    console.print(f"[bold magenta]Showing occurrences of '{keyword}':[/bold magenta]\n")
                    for match in matches:
                        if "```" in match:  # If it's a code block, render with Syntax
                            code_content = re.search(r'```(.*?)```', match, re.DOTALL).group(1)
                            syntax = Syntax(code_content.strip(), "bash", theme="monokai", line_numbers=True)
                            console.print(syntax)
                        else:
                            console.print(match)
                else:
                    console.print(f"[yellow]No occurrences of '{keyword}' found in this article.[/yellow]")
                return

            if content_type == "commands":
                # Extract and display code blocks only
                code_blocks = re.findall(CODE_BLOCK_PATTERN, content, re.DOTALL)
                for idx, code in enumerate(code_blocks, start=1):
                    syntax = Syntax(code.strip(), "bash", theme="monokai", line_numbers=True)
                    console.print(f"[bold cyan]Code Block {idx}:[/bold cyan]")
                    console.print(syntax)

            elif content_type == "text":
                # Remove code blocks and display text only
                text_only = re.sub(CODE_BLOCK_PATTERN, '', content, flags=re.DOTALL)
                md = Markdown(text_only)
                console.print(md)

            elif content_type == "links":
                # Extract and display links only
                raw_links = re.findall(LINK_PATTERN, content)
                clean_links = clean_up_links(raw_links)
                if clean_links:
                    console.print("\n[bold magenta]Links found in the article:[/bold magenta]")
                    for idx, link in enumerate(clean_links, start=1):
                        console.print(f"{idx}. [blue underline]{link}[/blue underline]")

            else:
                # Default behavior: Display entire content with formatting
                md = Markdown(content)
                console.print(md)

    except Exception as e:
        console.print(f"[red]Error reading file {file_path}: {e}[/red]")

def clean_up_links(raw_links):
    """
    Clean up the extracted links to ensure they are unique, properly formatted,
    and filter out undesirable or invalid links.
    """
    clean_links_set = set()  # Use a set to remove duplicates
    for link in raw_links:
        # Remove trailing punctuation that is not part of the URL
        cleaned_link = re.sub(r'[)\]\.\"]+$', '', link)
        # Remove markdown remnants, keep only valid URLs
        if "](" in cleaned_link:
            cleaned_link = re.sub(r'\]\(.+?\)', '', cleaned_link)

        # Check if the link is valid and not an unwanted social media link
        if is_valid_link(cleaned_link):
            clean_links_set.add(cleaned_link)

    return list(clean_links_set)

def is_valid_link(link):
    """
    Check if a link is valid and not a social media or undesirable link.
    """
    # Filter out invalid or social media links
    for domain in INVALID_LINK_DOMAINS:
        if domain in link:
            return False
    # Ensure the link is not malformed
    if not re.match(r'^https?://', link):
        return False
    # Remove links that contain unintended characters or incomplete markdown
    if re.search(r'\(|\)', link):
        return False
    return True

def handle_search_command(command_parts, hacktricks_dir):
    if len(command_parts) < 2:
        console.print("[red]Error: 'search' command requires a query.[/red]")
        return []

    search_query = command_parts[1]
    console.clear()
    console.print(f"searchvector:> search {search_query}")
    results = search_hacktricks(search_query, hacktricks_dir, fuzzy=True)
    if results:
        console.print(f"\n[green]Found {len(results)} result(s):[/green]\n")
        display_search_results(results, search_query)
    else:
        console.print("[yellow]No results found.[/yellow]")
    return results

def handle_use_command(command_parts, search_results):
    if len(command_parts) < 2:
        console.print("[red]Error: 'use' command requires an index number.[/red]")
        return [], [], None

    try:
        params = command_parts[1].split()
        idx = int(params[0]) - 1
        content_type = "all"
        keyword = None

        # Handle additional 'show' or 'search' parameter if provided
        for i in range(1, len(params)):
            if params[i] == "show" and i + 1 < len(params):
                content_type = params[i + 1].strip().lower()
                if content_type not in ["text", "commands", "links"]:
                    console.print(f"[red]Invalid content type '{content_type}'. Valid options are: text, commands, links.[/red]")
                    return search_results, [], None
            elif params[i] == "search" and i + 1 < len(params):
                keyword = params[i + 1].strip()

        if 0 <= idx < len(search_results):
            file_path = search_results[idx]['path']
            module_path = os.path.relpath(file_path, os.path.expanduser("~")).replace(".md", "")
            console.clear()
            console.print(f"searchvector:> use {command_parts[1]}")
            display_article(file_path, content_type, keyword)
            return search_results, [], module_path

        else:
            console.print("[red]Invalid index. Please select a valid number from the search results.[/red]")

    except ValueError:
        console.print("[red]Please provide a valid number after the command.[/red]")

    return search_results, [], None


def handle_read_command(command_parts, links):
    if len(command_parts) < 2:
        console.print("[red]Error: 'read' command requires a link index number.[/red]")
        return

    try:
        idx = int(command_parts[1]) - 1
        if 0 <= idx < len(links):
            url = links[idx]
            console.print(f"[green]Opening: {url}[/green]")
            webbrowser.open(url)
        else:
            console.print("[red]Invalid link index. Please select a valid number from the list of links.[/red]")
    except ValueError:
        console.print("[red]Please provide a valid number after the command.[/red]")

def main():
    home_dir = os.path.expanduser("~")
    hacktricks_dir = os.path.join(home_dir, "hacktricks")
    clone_url = "https://github.com/carlospolop/hacktricks.git"

    # Initialize search results and links
    search_results = []
    links = []

    # Check if the repository exists
    if not os.path.exists(hacktricks_dir):
        clone_repository(clone_url, hacktricks_dir)
    else:
        console.print("[green]HackTricks repository already exists.[/green]")

    # Handle initial search query from command line arguments
    if len(sys.argv) > 1:
        initial_query = ' '.join(sys.argv[1:])
        search_results = search_hacktricks(initial_query, hacktricks_dir, fuzzy=True)
        console.clear()
        console.print(f"searchvector:> search {initial_query}")
        if search_results:
            console.print(f"\n[green]Found {len(search_results)} result(s):[/green]\n")
            display_search_results(search_results, initial_query)
        else:
            console.print("[yellow]No results found.[/yellow]")

# Start the interactive shell
    while True:
        try:
            prompt_prefix = f"searchvector:> "
            if 'module_path' in locals() and module_path:
                prompt_prefix = f"searchvector ({module_path}):> "

            command = prompt(prompt_prefix, history=history, style=style).strip()
            if not command:
                continue

            parts = command.split(" ", 1)
            action = parts[0].lower()

            if action == "search":
                search_results = handle_search_command(parts, hacktricks_dir)

            elif action in ["use", "select"]:
                if not search_results:
                    console.print("[yellow]No search results available. Please perform a search first.[/yellow]")
                else:
                    search_results, links, module_path = handle_use_command(parts, search_results)

            elif action == "read":
                if not links:
                    console.print("[yellow]No links available. Please select an article first.[/yellow]")
                else:
                    handle_read_command(parts, links)

            elif action == "back":
                search_results = []
                links = []
                module_path = None
                console.print("Cleared current search results. You can perform a new search.")

            elif action in ["help", "?"]:
                console.print(HELP_TEXT)

            elif action in ["exit", "quit", "q"]:
                console.print("Exiting searchvector.")
                break

            elif action == "clear":
                console.clear()

            elif action.isdigit():
                if not search_results:
                    console.print("[yellow]No search results available. Please perform a search first.[/yellow]")
                else:
                    try:
                        idx = int(command) - 1
                        if 0 <= idx < len(search_results):
                            search_results, links, module_path = handle_use_command(["use", command], search_results)
                        else:
                            console.print("[red]Invalid index. Please select a valid number from the search results.[/red]")
                    except ValueError:
                        console.print("[red]Please provide a valid number.[/red]")

            else:
                console.print(f"[red]Unknown command: {action}. Type 'help' to see the list of available commands.[/red]")

        except KeyboardInterrupt:
            console.print("\n[red]Exiting searchvector.[/red]")
            break


if __name__ == "__main__":
    try:
        from rich import print
    except ImportError:
        print("The 'rich' library is required to run this script.")
        print("Install it using: pip install rich")
        sys.exit(1)

    main()
