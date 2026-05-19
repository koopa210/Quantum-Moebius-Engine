import os
import re

class SteamScanner:
    def __init__(self):
        self.default_paths = [
            "C:/Program Files (x86)/Steam",
            "C:/Program Files/Steam",
            "D:/SteamLibrary",
            "E:/SteamLibrary"
        ]

    def _parse_vdf(self, vdf_content):
        """Simple regex-based VDF parser to find library paths."""
        paths = []
        matches = re.findall(r'"path"\s+"(.*?)"', vdf_content)
        for m in matches:
            paths.append(m.replace("\\\\", "/"))
        return paths

    def _get_game_name(self, acf_path):
        """Extracts the 'name' field from a Steam .acf manifest file."""
        try:
            with open(acf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                name_match = re.search(r'"name"\s+"(.*?)"', content)
                if name_match:
                    return name_match.group(1)
        except:
            pass
        return None

    def scan(self):
        libraries = []
        # Find the primary Steam installation
        main_steam = None
        for p in self.default_paths:
            if os.path.exists(os.path.join(p, "steamapps/libraryfolders.vdf")):
                main_steam = p
                break
        
        if main_steam:
            vdf_path = os.path.join(main_steam, "steamapps/libraryfolders.vdf")
            with open(vdf_path, 'r', encoding='utf-8') as f:
                libraries = self._parse_vdf(f.read())
        else:
            # Fallback to checking default paths directly
            libraries = self.default_paths

        games = []
        for lib in libraries:
            apps_path = os.path.join(lib, "steamapps")
            if not os.path.exists(apps_path):
                continue
            
            # Find all appmanifest files
            for file in os.listdir(apps_path):
                if file.startswith("appmanifest_") and file.endswith(".acf"):
                    acf_full_path = os.path.join(apps_path, file)
                    game_name = self._get_game_name(acf_full_path)
                    if game_name:
                        # Find the actual folder in 'common'
                        game_folder = os.path.join(apps_path, "common", game_name)
                        if os.path.exists(game_folder):
                            # Calculate approximate size
                            size_bytes = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                                             for dirpath, dirnames, filenames in os.walk(game_folder) 
                                             for filename in filenames)
                            games.append({
                                "name": game_name,
                                "path": game_folder,
                                "size_gb": round(size_bytes / (1024**3), 2),
                                "id": file.split("_")[1].split(".")[0]
                            })
        return games

if __name__ == "__main__":
    scanner = SteamScanner()
    found_games = scanner.scan()
    print(f"Found {len(found_games)} Steam games.")
    for g in found_games:
        print(f"- {g['name']} ({g['size_gb']} GB) at {g['path']}")
