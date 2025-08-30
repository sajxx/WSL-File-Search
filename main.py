import subprocess
import os
import json
from flowlauncher import FlowLauncher

class WSLSearch(FlowLauncher):
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
            # Flow stores plugin settings globally, not in the plugin folder
            settings_dir = os.path.join(
                os.getenv("APPDATA"),
                "FlowLauncher",
                "Settings",
                "Plugins",
                "WSL File Search"  # must match "Name" in plugin.json
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

        if not query.strip():
            return [{
                "Title": "Search WSL Files",
                "SubTitle": "Type a filename or keyword to find inside your WSL home directory",
                "IcoPath": "icon.png"
            }]

        cmd = (
            f"wsl bash -c \"command -v fd >/dev/null 2>&1 "
            f"&& fd '{query}' ~ 2>/dev/null | head -n {max_results}\""
        )

        try:
            output = subprocess.check_output(cmd, shell=True, text=True)
            results = []

            for line in output.splitlines():
                dir_check_cmd = f"wsl bash -c \"if [ -d '{line}' ]; then echo '{line}'; else dirname '{line}'; fi\""
                try:
                    directory = subprocess.check_output(dir_check_cmd, shell=True, text=True).strip()
                except:
                    directory = line
                
                results.append({
                    "Title": line,
                    "SubTitle": "Open in Explorer • Right Arrow + Enter to open in Terminal",
                    "IcoPath": "icon.png",
                    "JsonRPCAction": {
                        "method": "open_path",
                        "parameters": [line],
                        "dontHideAfterAction": False
                    },
                    "ContextData": [directory]
                })

            return results

        except subprocess.CalledProcessError:
            return [{
                "Title": "No results",
                "SubTitle": f"No matches for '{query}'",
                "IcoPath": "icon.png"
            }]

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
