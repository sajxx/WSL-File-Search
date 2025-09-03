import subprocess
import os
import json
import threading
import re
import sys

# Add bundled dependencies to Python path BEFORE importing flowlauncher
parent_folder_path = os.path.abspath(os.path.dirname(__file__))
lib_folder_path = os.path.join(parent_folder_path, "lib")
sys.path.insert(0, lib_folder_path)

# import flowlauncher from bundled dependencies
try:
    from flowlauncher import FlowLauncher
except ImportError as e:
    # Fallback error handling
    print(f"Error importing flowlauncher: {e}")
    print(f"Looking for flowlauncher in: {lib_folder_path}")
    sys.exit(1)

class WSLSearch(FlowLauncher):
    def left_truncate_path(self, path, max_length=50, keep_dirs=3):
        """
        Truncate the path to always show the last directory, and as many of the first `keep_dirs` directories as fit,
        with ellipsis in between if truncated, ensuring the total length does not exceed max_length.
        """
        if len(path) <= max_length:
            return path
        parts = path.strip('/').split('/')
        if len(parts) <= keep_dirs + 1:
            # Not enough dirs to truncate, fallback to old method
            return '...' + path[-(max_length-3):]
        last = parts[-1]
        sep = '/'
        ellipsis = '/.../'
        # Try to fit as many of the first keep_dirs as possible
        for n in range(keep_dirs, 0, -1):
            start = sep.join(parts[:n])
            candidate = f"{start}{ellipsis}{last}"
            if len(candidate) <= max_length:
                return candidate
        # If even one dir + ellipsis + last doesn't fit, just show .../last
        candidate = f".../{last}"
        if len(candidate) <= max_length:
            return candidate
        # If still too long, truncate last dir
        truncated_last = last[-(max_length-4):]
        return f".../{truncated_last}"
    
    def __init__(self):
        super().__init__()
        # Warm up WSL in background on plugin load
        threading.Thread(target=self._warmup_wsl, daemon=True).start()
    
    def _warmup_wsl(self):
        """Warm up WSL to reduce first-search latency"""
        try:
            subprocess.run("wsl echo warmup", shell=True, capture_output=True, timeout=3)
        except:
            pass  # Ignore warmup failures

    def get_distro(self):
        """Return WSL distro from Settings.json, fallback to 'Ubuntu'"""
        settings = self.load_settings()
        distro = settings.get("distro", "Ubuntu")
        if distro not in ("Ubuntu", "Debian"):
            distro = "Ubuntu"
        return distro
    
    DEFAULT_MAX_RESULTS = 20

    def load_settings(self):
        """Load Settings.json from Flow Launcher global settings directory"""
        try:
            settings_dir = os.path.join(
                os.getenv("APPDATA"),
                "FlowLauncher",
                "Settings",
                "Plugins",
                "WSL File Search"
            )
            settings_path = os.path.join(settings_dir, "Settings.json")

            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print("Error loading settings:", e)
        return {}

    def get_shell(self):
        """Return shell from Settings.json, fallback to 'zsh'"""
        settings = self.load_settings()
        shell = settings.get("shell", "zsh")
        if shell not in ("zsh", "bash"):
            shell = "zsh"
        return shell

    def get_max_results(self):
        """Return max_results from Settings.json, fallback to default"""
        settings = self.load_settings()
        return int(settings.get("max_results", self.DEFAULT_MAX_RESULTS))

    def query(self, query: str):
        max_results = self.get_max_results()
        parsed = self._parse_query(query)
        pattern = parsed["pattern"]
        exts = parsed["extensions"]

        if not any([pattern, exts]):
            return [{
                "Title": "Search WSL Files",
                "SubTitle": "Type keywords and optionally extensions like: report .py .js  OR  ext:py ext:md",
                "IcoPath": "icon.png"
            }]

        cmd = self._build_fd_command(pattern, exts, max_results)

        try:
            # Use timeout to prevent hanging
            output = subprocess.check_output(cmd, shell=True, text=True, timeout=10)
            lines = output.splitlines()

            if lines and lines[0] == 'FD_NOT_INSTALLED':
                return [{
                    "Title": "fd-find is not installed in WSL",
                    "SubTitle": "Please install fd-find in your WSL distribution (e.g., sudo apt install fd-find) and create the symlink as per README instructions.",
                    "IcoPath": "icon.png"
                }]

            results = []

            for line in lines:
                if not line.strip():
                    continue
                # Simplified directory detection - avoid extra subprocess calls
                if line.endswith('/') or '.' not in os.path.basename(line):
                    directory = line
                else:
                    directory = os.path.dirname(line) or line

                display_path = self.left_truncate_path(line, 55)

                results.append({
                    "Title": display_path,
                    "SubTitle": "Open in Explorer • Right Arrow + Enter to open in Terminal",
                    "IcoPath": "icon.png",
                    "JsonRPCAction": {
                        "method": "open_path",
                        "parameters": [line],
                        "dontHideAfterAction": False
                    },
                    "ContextData": [directory]
                })

            if not results:
                return [{
                    "Title": "No results",
                    "SubTitle": f"No matches for '{query}'",
                    "IcoPath": "icon.png"
                }]

            return results

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return [{
                "Title": "No results",
                "SubTitle": f"No matches for '{query}'",
                "IcoPath": "icon.png"
            }]

    # ---------------------- Query Parsing & Command Building ----------------------
    def _parse_query(self, raw: str):
        """Parse the user query into (pattern regex, list of extensions).

        Rules:
        - Tokens starting with "." followed by letters/numbers (_) are treated as extensions (.py)
        - Tokens starting with ext:EXTNAME also count (ext:py)
        - Remaining tokens become a fuzzy-ish regex: each token escaped then joined by '.*'
        - If only extensions given, pattern becomes '.' (match anything)
        - Duplicate extensions removed, order preserved
        """
        exts = []
        pattern_tokens = []
        for tok in raw.strip().split():
            if tok.startswith('ext:') and len(tok) > 4:
                ext = tok[4:].strip('.').lower()
                if ext and ext not in exts:
                    exts.append(ext)
            elif tok.startswith('.') and len(tok) > 1 and tok[1:].replace('_', '').isalnum():
                ext = tok[1:].lower()
                if ext and ext not in exts:
                    exts.append(ext)
            else:
                pattern_tokens.append(tok)
        if pattern_tokens:
            # Build a simple regex that ensures tokens appear in order (case-insensitive handled by fd by default)
            escaped = [re.escape(t) for t in pattern_tokens]
            pattern = '.*'.join(escaped)
        else:
            pattern = ''  # Will be replaced with '.' later if still empty
        return {"pattern": pattern, "extensions": exts}

    def _shell_escape_single(self, s: str) -> str:
        """Escape a string for safe inclusion inside single quotes in a bash command."""
        return "'" + s.replace("'", "'" + '"' + "'" + "'") + "'"  # conservative; rarely hit

    def _build_fd_command(self, pattern: str, exts, max_results: int):
        # Base inside the bash -c string
        if not pattern:
            pattern = '.'  # match anything
        pattern_quoted = self._shell_escape_single(pattern)
        ext_flags = ' '.join(f"-e {self._shell_escape_single(e)}" for e in exts)
        
        # Get the configured distro and shell
        distro = self.get_distro()
        shell = self.get_shell()
        
        # Compose command executed inside the specified distro
        inner = (
            f"if command -v fdfind >/dev/null 2>&1; then "
            f"  fdfind --threads 4 --max-results {max_results} "
            f"  {ext_flags} {pattern_quoted} ~ 2>/dev/null; "
            f"else "
            f"  echo 'FD_NOT_INSTALLED'; "
            f"fi"
        ).strip()
        
        # Use the configured distro instead of default
        return f"wsl -d {distro} {shell} -c \"{inner}\""

    def context_menu(self, data):
        """Provide context menu with only Windows Terminal option"""
        if not data:
            return []
        
        directory = data[0]
        
        return [
            {
                "Title": "Open in Windows Terminal",
                "SubTitle": f"Windows Terminal with WSL profile at {directory}",
                "IcoPath": "icon.png",
                "JsonRPCAction": {
                    "method": "open_windows_terminal",
                    "parameters": [directory],
                    "dontHideAfterAction": False
                }
            }
        ]

    def open_path(self, path: str):
        """Convert WSL path to Windows path and open it"""
        try:
            cmd = f"wsl wslpath -w '{path}'"
            win_path = subprocess.check_output(cmd, shell=True, text=True).strip()
            os.startfile(win_path)
        except Exception as e:
            return [{
                "Title": "Error opening file",
                "SubTitle": str(e),
                "IcoPath": "icon.png"
            }]

    def open_windows_terminal(self, directory: str):
        """Launch user-selected WSL distro/profile in Windows Terminal, starting user-selected shell in the given directory"""
        try:
            shell = self.get_shell()
            distro = self.get_distro()
            safe_directory = directory.replace("'", "'\\''")
            cmd = (
                f'wt.exe -p "{distro}" '
                f'wsl -d {distro} '
                f'{shell} -c "cd \'{safe_directory}\' && exec {shell}"'
            )
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            return [{
                "Title": "Error opening Windows Terminal",
                "SubTitle": str(e),
                "IcoPath": "icon.png"
            }]


if __name__ == "__main__":
    WSLSearch()