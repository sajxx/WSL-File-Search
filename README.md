# WSL File Search (Flow Launcher Plugin)

Search files inside your WSL distro’s home directory from Flow Launcher—fast, simple, and keyboard-friendly.  
Powered by [`fd`](https://github.com/sharkdp/fd) inside WSL for speed.

## ✨ Features

- 🔍 Super fast WSL file search in Flow Launcher using `wslf`
- ⛔ Stops after **N** results (configurable) to stay snappy
- 🗂️ Open matches directly in **Windows Explorer**
- ⌨️ (Context action) Open the containing folder in a WSL Ubuntu terminal
- ⚙️ Configure **Max Results** from Flow Launcher’s plugin settings UI

> NOTE: This plugin runs searches **inside WSL**. Make sure `fd` is installed in your WSL Ubuntu.

---

## 🧩 Prerequisites

- **Windows 10/11** with **WSL** enabled and Linux Ubuntu installed
- **Flow Launcher** v1.20+  
  Download: https://www.flowlauncher.com/
- **`fd` inside your WSL distro** (see install steps below).
- (Optional) **Windows Terminal** configured to open in Ubuntu for “Open in Terminal” context action.

---

## 📦 Installation

### 1) Install `fd` in WSL

**Ubuntu**
```bash
sudo apt update
sudo apt install fd-find
# On Ubuntu the binary is named 'fdfind'. Create a friendly 'fd' alias:
mkdir -p ~/.local/bin
ln -sf "$(command -v fdfind)" ~/.local/bin/fd
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
