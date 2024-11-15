# SearchVector

SearchVector is a command-line tool for searching through the HackTricks repository, providing a pseudo-shell interface to navigate through results. This tool is useful for penetration testers, red teamers, or anyone needing quick reference to hacking techniques and methodologies.

## Installation

### Prerequisites

Ensure you have Python 3 installed and the required Python modules. You can install the necessary dependencies using:

```bash
pip install rich
```

This script requires the `rich` library to provide formatted output in the terminal.

### Clone the HackTricks Repository

The script will automatically clone the HackTricks repository to your home directory if it's not already present:

```bash
git clone https://github.com/carlospolop/hacktricks.git ~/hacktricks
```

### Usage

Run the script using Python 3:

```bash
python3 searchvector.py <search_query>
```

If no query is provided, you can enter the pseudo-shell interface to run commands interactively.

### Setting Up an Alias

To simplify running the tool, you can set up a bash or zsh alias:

```bash
alias searchvector="<path_to_searchvector.py> $*"
```

Replace `<path_to_searchvector.py>` with the actual path to the `searchvector.py` script. For example, if the script is located in your projects directory, you could use:

```bash
alias searchvector="/home/kali/projects/searchvector/searchvector.py $*"
```

After adding this alias, you can use the `searchvector` command directly in your terminal:

```bash
searchvector kerberoasting
```

## Commands Available in Pseudo-Shell

- `search <query>`: Search the HackTricks repository for a given query.
- `use <index>` / `select <index>`: Select a file to view by specifying its index number from the last search.
- `back`: Go back to the initial prompt to perform another action.
- `clear`: Clear the console screen.
- `help` / `?`: Display the help message.
- `exit` / `quit` / `q`: Exit the pseudo-shell.

## Example Usage

```bash
kali@kali:~/projects/searchvector$ python3 searchvector.py kerberoasting
searchvector:> Found 5 result(s):
1. /home/kali/hacktricks/windows-hardening/active-directory-methodology/README.md
2. /home/kali/hacktricks/windows-hardening/active-directory-methodology/kerberoast.md
3. /home/kali/hacktricks/windows-hardening/active-directory-methodology/external-forest-domain-oneway-inbound.md
4. /home/kali/hacktricks/windows-hardening/active-directory-methodology/acl-persistence-abuse/README.md
5. /home/kali/hacktricks/macos-hardening/macos-red-teaming/README.md
```

## License

This project is licensed under the MIT License.
