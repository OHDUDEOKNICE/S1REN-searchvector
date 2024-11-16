# 🚨 SearchVector (SEARCH ATTACK VECTOR)

SearchVector is a powerful command-line tool designed to streamline your search through the HackTricks repository. With its synonym matching, fuzzy search, and modular content filtering, SearchVector is an invaluable resource for cybersecurity professionals, students, and enthusiasts.

Originally developed to be learned alongside S1REN at [Learn.Startup.Security](https://Learn.Startup.Security:443/), SearchVector is adaptable for use in any environment.

![Example Usage](s1ren-searchvector-demo-optimized.gif)

---

## ✨ Features

- 🔍 **Fuzzy Search**: Intelligent search functionality that accounts for partial matches and synonyms.
- 📖 **Content Filtering**: Extract and display specific content types—text, commands, or links.
- 🔑 **Synonym Support**: Manually configurable synonyms expand your search precision.
- 📋 **Command History Navigation**: Effortlessly scroll through and reuse previous commands.
- 🌐 **Browser Integration**: Open external links from articles directly in your browser.

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/OHDUDEOKNICE/S1REN-searchvector.git
cd S1REN-searchvector
```

### Install Dependencies

Ensure Python 3 is installed on your system, then install required dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Quick Search

Run a search directly from the command line:

```bash
./searchvector.py "<search term>"
```

### Interactive Mode

For an interactive shell experience, simply run:

```bash
./searchvector.py
```

---

## 🛠 Commands

### General

- `search <query>`  
  Search the HackTricks repository for a query, leveraging synonym matching and fuzzy search.

- `help`  
  Display a list of available commands with usage instructions.

- `clear`  
  Clear the console screen for a fresh view.

- `exit` or `quit`  
  Exit the interactive shell.

### Working with Results

- `use <index|module_name>`  
  Load a module by search result index or its name for further exploration.

- `use <index|module_name> show <text|commands|links>`  
  Display specific types of content from a loaded module:
  - `text`: View only the textual content.
  - `commands`: Display all code blocks from the module.
  - `links`: List external links.

- `use <index|module_name> search <keyword>`  
  Search within a loaded module for a specific keyword.

- `read <link_index>`  
  Open a link from the loaded module in your default web browser.

---

## 💡 Examples

### Search for a Term

```bash
searchvector:> search active directory
```

### Display All Commands in a Module

```bash
searchvector:> use 2 show commands
```

### Search Within a Module

```bash
searchvector:> use 3 search privilege escalation
```

### Open a Link from a Module

```bash
searchvector:> read 1
```

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 💻 About

SearchVector was developed with flexibility and speed in mind, enabling quick access to actionable information from HackTricks. Learn more and practice your skills at [Learn.Startup.Security](https://Learn.Startup.Security:443/).

**Happy Hacking!**
