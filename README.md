# 🚀 SearchVector

SearchVector is a command-line tool that lets you search HackTricks for relevant articles with ease. It integrates synonym matching and features fuzzy search, making it similar to `searchsploit` but optimized for HackTricks content.

Developed to be learned alongside S1REN at [Learn.Startup.Security](https://Learn.Startup.Security:443/), but can be used anywhere for quick and effective searches.

![Example Usage](s1ren-searchvector-demo-optimized.gif)

## ✨ Features
- 🔍 Fuzzy search with synonym support.
- 📋 Displays text, commands, or links based on your preference.
- ⬆️⬇️ Command history navigation.
- 🌐 Opens article links in your browser.

## ⚙️ Installation & Usage
```sh
git clone https://github.com/OHDUDEOKNICE/S1REN-searchvector.git
cd S1REN-searchvector
pip install -r requirements.txt
./searchvector.py <search term>
```

For interactive mode, simply run:
```sh
./searchvector.py
```
### Commands:
- `search <query>` - Find articles.
- `use <index>` - View a specific result.
- `use <index> show <text|commands|links>` - View specific content types.
- `use <index> search <keyword>` - Search within a selected article.
- `read <link_index>` - Open a link from an article.

## 📄 License
Licensed under the MIT License.
