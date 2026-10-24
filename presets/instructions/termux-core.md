# Termux Core Environment

**Operating Environment:** Android Termux (`aarch64`, Bionic libc)

## Critical Path Rules

1. **Non-Standard FHS**: `/bin` and `/usr/bin` do NOT exist
   - Binaries: `$PREFIX/bin/` (`/data/data/com.termux/files/usr/bin/`)
   - Use: `$PREFIX/bin/bash`, `$PREFIX/bin/python3`, `$PREFIX/bin/node`

2. **Package Management**
   - System: `pkg install <package>`
   - Python: `pip install --break-system-packages <package>`

3. **Android Integration**
   - Clipboard: `termux-clipboard-get`, `termux-clipboard-set`
   - Open: `termux-open-url <url>`, `termux-open <file>`

4. **Memory Management**
   - Android LMK kills heavy processes
   - Avoid unbounded parallel execution
   - Keep builds and tests bounded

5. **Search Constraints**
   - NEVER: `find /`, `grep -r /`, scanning `/sdcard` or `node_modules`
   - USE: `fd` or `rg` with explicit paths and exclusions
   - Example: `fd -t f -e py --exclude .git --exclude node_modules . ./target`
