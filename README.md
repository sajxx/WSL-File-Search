# WSL File Search - Flow Launcher Plugin

> 🚀 **Lightning-fast file search for your WSL Ubuntu environment, integrated seamlessly with Flow Launcher**

Search and open files from your WSL Ubuntu home directory directly within Flow Launcher. Powered by the blazing-fast `fd` command-line tool, this plugin brings WSL file discovery to your Windows desktop workflow.

![Plugin Demo](https://img.shields.io/badge/Flow_Launcher-Plugin-blue) ![WSL](https://img.shields.io/badge/WSL-Ubuntu-orange) ![Python](https://img.shields.io/badge/Python-3.7+-green)

---

## 🌟 Features

- **⚡ Ultra-Fast Search**: Leverages `fd` for sub-second file discovery across your entire WSL home directory
- **🎯 Intelligent Results**: Configurable result limits (5-50) to keep searches snappy and relevant  
- **🗂️ Seamless Integration**: Open files directly in Windows Explorer with a single keystroke
- **⌨️ Terminal Access**: Right-click context menu to open containing folders in Windows Terminal with WSL
- **⚙️ User-Friendly Settings**: Configure maximum results, WSL distro (Ubuntu/Debian), and shell (zsh/bash) through Flow Launcher's built-in settings UI
- **🔍 Smart Filtering**: Searches both filenames and directory names with fuzzy matching

---

## 📋 Prerequisites

Before installing this plugin, ensure you have the following components properly configured:

### Required Components

| Component | Version | Purpose |
|-----------|---------|---------|
| **Windows** | 10 (Build 19041+) or 11 | Host operating system |
| **WSL 2** | Latest | Windows Subsystem for Linux |
| **Ubuntu/Debian** | 20.04+ | WSL distribution (user-selectable) |
| **Flow Launcher** | v1.20+ | Plugin host application |
| **fd** | Latest | Fast file finder (installed in WSL) |

### Optional Components

- **Windows Terminal** - Enhanced terminal experience for WSL integration
- **Zsh** or **Bash** - Modern shells (user-selectable; plugin works with both)

---

## 🛠️ Installation Guide

### Step 1: Verify WSL Installation

First, ensure WSL is properly installed and your preferred distribution (Ubuntu or Debian) is installed:

```powershell
# Check WSL status
wsl --status

# List installed distributions
wsl --list --verbose

# Set Ubuntu as default (if needed)
wsl --set-default Ubuntu
```

### Step 2: Install fd in WSL Ubuntu

Open your WSL Ubuntu terminal and install the `fd` file finder:

```bash
# Update package lists
sudo apt update

# Install fd-find package
sudo apt install fd-find

# Create a symlink for easier access (Ubuntu names it 'fdfind')
mkdir -p ~/.local/bin
ln -sf "$(command -v fdfind)" ~/.local/bin/fd

# Add local bin to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# OR if using zsh:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

**Verify fd installation:**
```bash
# Test fd is working
fd --version
cd ~
fd "test" --type f --max-results 5
```

### Step 3: Install Flow Launcher

1. Download Flow Launcher from [https://www.flowlauncher.com/](https://www.flowlauncher.com/)
2. Install and run the application
3. Complete the initial setup wizard

### Step 4: Install WSL File Search Plugin

#### Method 1: From Flow Launcher Plugin Store (WILL NOT WORK AS OF NOW)
1. Open Flow Launcher (`Alt + Space`)
2. Type `pm install wsl file search`
3. Select the plugin and press Enter to install

#### Method 2: Manual Installation
1. Download the latest release from the [GitHub releases page](https://github.com/Sajxx/WSL-File-Search/releases)
2. Extract the plugin files to:
   ```
   %APPDATA%\FlowLauncher\Plugins\WSL File Search\
   ```
3. Restart Flow Launcher

### Step 5: Configure Plugin Settings

1. Open Flow Launcher settings (`Alt + Space`, then type `settings`)
2. Navigate to **Plugins** → **WSL File Search**
3. Configure your preferred **Max Results** (5, 10, 15, 20, 30, or 50)
4. Select your **WSL Distro** (Ubuntu or Debian)
5. Select your **Shell** (zsh or bash)
6. Click **Save**

---

## 🚀 Usage Guide

### Basic Search

1. Open Flow Launcher with `Alt + Space`
2. Type `wslf` followed by your search term
3. Example: `wslf config` to find configuration files

### Search Examples

```
wslf docker          # Find Docker-related files
wslf .env            # Find environment files  
wslf package.json    # Find Node.js package files
wslf *.py            # Find Python files
wslf src/            # Find directories named 'src'
```

### Available Actions

| Action | Shortcut | Description |
|--------|----------|-------------|
| **Open in Explorer** | `Enter` | Opens the file/folder in Windows File Explorer |
| **Open in Terminal** | `Right Arrow + Enter` | Opens containing directory in Windows Terminal (WSL) |
| **Context Menu** | `Right Click` or `Ctrl + Enter` | Shows additional actions |

### Advanced Usage

- **Fuzzy Search**: `wslf confg` will still find `config.txt`
- **Path Search**: `wslf home/user/docs` searches within specific paths
- **Extension Filter**: `wslf .js` finds all JavaScript files
- **Directory Search**: `wslf src/` specifically finds directories

---

## ⚙️ Configuration

### Plugin Settings

Access plugin settings through Flow Launcher's settings panel:

**Settings Location**: 
```
%APPDATA%\FlowLauncher\Settings\Plugins\WSL File Search\Settings.json
```

**Available Options**:


```json
{
   "max_results": "20",
   "distro": "Ubuntu",
   "shell": "zsh"
}
```

| Setting | Type | Options | Default | Description |
|---------|------|---------|---------|-------------|
| `max_results` | string | "5", "10", "15", "20", "30", "50" | "5" | Maximum search results displayed |
| `distro` | string | "Ubuntu", "Debian" | "Ubuntu" | WSL distribution to use for search and terminal |
| `shell` | string | "zsh", "bash" | "zsh" | Shell to use in Windows Terminal context menu |

### Advanced Configuration

For power users, you can modify the search behavior by editing the plugin's `main.py` file:

```python
# Modify the fd command parameters
cmd = (
    f"wsl bash -c \"command -v fd >/dev/null 2>&1 "
    f"&& fd '{query}' ~ --type f --hidden --no-ignore | head -n {max_results}\""
)
```

**Available fd flags**:
- `--type f` - Files only
- `--type d` - Directories only  
- `--hidden` - Include hidden files
- `--no-ignore` - Ignore .gitignore rules
- `--case-sensitive` - Case-sensitive search

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "No results" for valid files

**Problem**: Plugin returns no results despite files existing.

**Solutions**:
```bash
# Verify fd is installed and accessible
wsl bash -c "command -v fd"

# Test fd directly in WSL
wsl bash -c "fd 'test' ~"

# Check PATH includes ~/.local/bin
wsl bash -c "echo \$PATH"
```

#### 2. Windows Terminal doesn't open

**Problem**: Context menu "Open in Windows Terminal" fails.

**Solutions**:
1. Install Windows Terminal from Microsoft Store
2. Verify Ubuntu profile exists:
   ```json
   // In Windows Terminal settings.json
   {
     "guid": "{your-ubuntu-guid}",
     "name": "Ubuntu",
     "source": "Windows.Terminal.Wsl"
   }
   ```

#### 3. Plugin doesn't appear in Flow Launcher

**Problem**: Plugin isn't recognized after installation.

**Solutions**:
1. Verify plugin files are in correct directory:
   ```
   %APPDATA%\FlowLauncher\Plugins\WSL File Search\
   ├── main.py
   ├── plugin.json
   ├── icon.png
   └── Settings.json
   ```
2. Restart Flow Launcher completely
3. Check Flow Launcher logs for errors

#### 4. Slow search performance

**Problem**: Searches take too long to complete.

**Solutions**:
1. Reduce `max_results` in settings
2. Use more specific search terms
3. Ensure WSL 2 is being used (not WSL 1)
4. Consider excluding large directories:
   ```bash
   # Add to ~/.fdignore in WSL
   node_modules/
   .git/
   __pycache__/
   ```

### Debug Mode

To enable detailed logging:

1. Edit `main.py` and add debug prints
2. Run Flow Launcher from command line to see output:
   ```cmd
   "%APPDATA%\FlowLauncher\app\FlowLauncher.exe"
   ```

### Getting Help

If you encounter issues:

1. **Check the logs**: `%APPDATA%\FlowLauncher\Logs\`
2. **Verify prerequisites**: Ensure all components are properly installed
3. **Test WSL directly**: Run fd commands manually in WSL
4. **Report bugs**: [GitHub Issues](https://github.com/Sajxx/Flow.Launcher.Plugin.WSLSearch/issues)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sajxx/Flow.Launcher.Plugin.WSLSearch.git
   cd Flow.Launcher.Plugin.WSLSearch
   ```

2. **Install development dependencies**:
   ```bash
   pip install flowlauncher
   ```

3. **Link plugin for testing**:
   ```cmd
   mklink /D "%APPDATA%\FlowLauncher\Plugins\WSL File Search Dev" "C:\path\to\your\clone"
   ```

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add comments for complex logic
- Test on both WSL 1 and WSL 2

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Flow Launcher](https://www.flowlauncher.com/)** - Excellent launcher platform
- **[fd](https://github.com/sharkdp/fd)** - Lightning-fast file finder
- **Microsoft WSL Team** - Making Linux on Windows seamless
- **Contributors** - Thanks to everyone who has contributed to this project

---

## 📞 Support

- **Documentation**: This README and inline code comments
- **Issues**: [GitHub Issues Page](https://github.com/Sajxx/Flow.Launcher.Plugin.WSLSearch/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Sajxx/Flow.Launcher.Plugin.WSLSearch/discussions)
- **Flow Launcher Community**: [Flow Launcher Discord](https://discord.gg/flowlauncher)

---

**Made with ❤️ for the Flow Launcher and WSL communities**