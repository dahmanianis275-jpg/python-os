# Python OS 3.3 – Hybrid Linux / Windows Simulation (Unlimited)

**A pure-Python educational operating system simulation** that feels close to real Linux while also supporting many Windows-style commands.

**Version 3.3 change:** Python script execution is now **unlimited**.  
`.py` files run with the full power of the host Python interpreter (imports, `open()`, etc. are allowed).

It is still **not** a real kernel. It runs on top of your actual operating system.

---

## Quick Start

```bash
git clone https://github.com/dahmanianis275-jpg/python-os.git
cd python-os
python python_os.py
```

---

## File Extensions & Execution

| Extension | Behavior                                      |
|-----------|-----------------------------------------------|
| `.py`     | Runs with **full / unlimited** Python power   |
| `.txt`    | Shown as text                                 |
| `.json`   | Pretty-printed                                |
| `.sh`     | Simulated shell                               |
| others    | Checked and handled or refused cleanly        |

### Important commands

```bash
file <path>        # show type & extension info
assoc              # list registered extensions
open <file>        # open according to type
run <file>         # execute (unlimited for .py)
python <file.py>   # same as run for Python files
./script.py        # same as run script.py
```

---

## Hybrid commands

Linux style + Windows style (`dir`, `cls`, `ipconfig`, `tasklist`, `systeminfo`, …) + games.

---

## Warning

Because execution is now unlimited, a `.py` file you run inside the simulation has the **same power** as any normal Python script on your machine.  
Only run code you trust.

---

## License

MIT License

**https://github.com/dahmanianis275-jpg/python-os**
