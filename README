# Python OS 3.2 – Hybrid Linux / Windows Simulation

**A pure-Python educational operating system simulation** that feels close to real Linux while also supporting many Windows-style commands.

It is **not** a real kernel. It runs entirely inside Python on top of your actual operating system.

---

## What’s new in 3.2

- **File extension support** – the OS now understands `.py`, `.txt`, `.sh`, `.md`, `.json`, etc.
- **Safe open / run** – before opening or executing a file the system **checks the extension** and refuses dangerous or unknown types with a clear message (no more sudden crashes).
- **Restricted real Python execution** – `.py` files can be run with a limited `exec()` so the simulation can “connect” to the real Python interpreter without giving full host access.
- **File association table** – like a real OS, different extensions are handled by different “programs”.
- **Shebang support** – `#!/usr/bin/env python3` style lines are respected for scripts.
- **More commands & better error handling** so the simulation feels less limited.

---

## Quick Start

```bash
git clone https://github.com/dahmanianis275-jpg/python-os.git
cd python-os
python python_os.py
```

Or just:

```bash
python python_os.py
```

---

## File Extensions & Safe Opening

| Extension | How it is handled                          | Command examples              |
|-----------|--------------------------------------------|-------------------------------|
| `.txt`    | Text file → shown with `cat` / `type`      | `cat notes.txt`               |
| `.py`     | Python script → run in **restricted** mode | `run script.py` or `./script.py` |
| `.sh`     | Shell script → simulated                   | `run script.sh`               |
| `.md`     | Markdown → shown as text                   | `cat readme.md`               |
| `.json`   | JSON → shown / validated                   | `cat data.json`               |
| unknown   | Refused with clear error                   | “Unsupported file type”       |

**Important safety rule**  
Before any file is opened or executed the OS checks its extension.  
If the type is not registered, you get a clear message instead of a Python traceback.

---

## New / Improved Commands

```bash
run <file>          # Safe run (checks extension first)
./file.py           # Same as run (for scripts)
open <file>         # Open according to extension
file <file>         # Show file type / extension info
assoc               # List file associations
python <file.py>    # Explicit restricted Python execution
```

---

## Hybrid Linux + Windows commands

Linux: `ls`, `cd`, `pwd`, `cat`, `mkdir`, `rm`, `ps`, `top`, `kill`, `apt`, …  
Windows: `dir`, `cls`, `ipconfig`, `tasklist`, `systeminfo`, `ver`, `type`, `del`, `md`, `rd`

Games: `games`, `guess`, `rps`, `hangman`, `snake`, `dice`, `fortune`

---

## Why “connect extensions” matters

A plain Python script has no idea what a `.docx`, `.exe` or unknown binary is.  
By registering extensions and checking them **before** opening, the simulation stays stable and can safely use the real Python interpreter for `.py` files without letting a bad file crash the whole OS.

---

## Requirements

- Python 3.8+
- No external packages required

---

## License

MIT – see [LICENSE](LICENSE)

**https://github.com/dahmanianis275-jpg/python-os**
