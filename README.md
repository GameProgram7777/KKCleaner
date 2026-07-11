# KKCleaner

A GUI tool to detect and clean up **unused Koikatsu (KK) zipmods and BepInEx plugins**, based on card-usage data exported from [KKManager](https://github.com/IllusionMods/KKManager). It detects mods/plugins whose card-usage count is at or below a user-defined threshold, then lets you **Pack** (move aside), **Undo Pack** (restore), or **Remove** them.

> Renamed from `KKModsCleaner`, which was itself renamed from `KKUnusedModsRemoverPacker`. KKCleaner adds BepInEx **plugin** (`.dll` / `.dl_`) support on top of the original **zipmod** cleaning.

The interface supports 6 languages (in-app text is machine-translated): English, 繁體中文, 简体中文, 日本語, 한국어, Русский.

## Features

- **Zipmod cleaning** — reads a KKManager *Zipmod usage* CSV and finds low-usage `.zipmod` files.
- **Plugin cleaning** — reads a KKManager *Plugin usage* CSV and matches BepInEx `.dll` / `.dl_` files by their `BepInPlugin` GUID (read via Mono.Cecil).
- Three actions: **Pack**, **Undo Pack**, **Remove**.
- **Custom … Only** checkbox to restrict operations to the root folder (skip subfolders).
- Drag-and-drop or browse to load the CSV.

## Requirements

- Windows, Python 3.8+
- [.NET runtime](https://dotnet.microsoft.com/) (required by pythonnet / Mono.Cecil for reading plugin DLLs)
- Python packages:

  ```
  pip install -r requirements.txt
  ```

  (`tkinterdnd2`, `chardet`, `pythonnet`)

- `Mono.Cecil.dll` must sit next to `KKCleaner.py` (it is included in this repo and required at runtime).

## Usage

1. **Export a CSV from KKManager**
   - Open [KKManager](https://github.com/IllusionMods/KKManager) → select a folder → `Tools` → `Export to csv...`
   - For **mods**: choose *Zipmod usage (including unused)*.
   - For **plugins**: choose the plugin/usage export.
   - KKCleaner auto-detects whether the CSV is a mod or plugin export.

2. **Load the CSV** — drag it onto the window or click to browse.

3. **Set the threshold** (*Minimum Card Usages*, default `0`) and click **Detect**. The min/max usage range is shown next to the input. Items with usage **at or below** the threshold are selected.

4. **Enter the mod/plugin folder path** (type it or use **Browse**).

5. **Choose an action** and click **Run**:
   - **Pack** — move low-usage items into a `low_usage_mods` / `low_usage_plugins` folder (created automatically).
   - **Undo Pack** — move packed items back to their original locations.
   - **Remove** — delete detected low-usage items (asks for confirmation first).

6. **Custom … Only** (optional) — when checked, only files in the root of the given folder are affected; subfolders are skipped.

## Known Limitations

- **Undo Pack is in-memory only.** The original paths of packed files are kept only in the running process (`self.moved_files`). If you close KKCleaner after packing, those packs can no longer be undone on the next launch.
- **Remove cannot be undone.** Only Pack is reversible — use Remove with care.
- **Detection may be flagged by antivirus.** Reading DLL metadata via Mono.Cecil can trip heuristics; temporarily allow-list or disable AV if needed.
- KKManager exports a single GUID per mod (typically the lowest version), and disabled mods still report their real usage count.

## License

Licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome — open an issue or submit a pull request.
