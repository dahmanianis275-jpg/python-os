# Python OS 3.1 – Hybrid Linux / Windows Simulation

**A pure-Python educational operating system simulation** that feels close to real Linux while also supporting many Windows-style commands.

It is **not** a real kernel. It runs entirely inside Python on top of your actual operating system (Windows, Linux, or macOS).

---

## Features

### Linux-style core
- Realistic directory tree (`/bin`, `/etc`, `/home`, `/usr`, `/var`, `/proc`, `/dev`, `/tmp`…)
- Multi-user system (`root`, `user`, `guest`)
- Process table (`ps`, `top`, `kill`)
- Permissions & ownership simulation
- Environment variables + `export`
- `sudo` / `su`
- Package manager simulation (`apt`)
- Networking commands (`ping`, `ifconfig`, `curl`)
- Classic tools: `ls`, `cd`, `pwd`, `cat`, `mkdir`, `rm`, `echo`, `nano`, `history`, `uname`, etc.

### Windows-style commands (hybrid)
| Windows command | Equivalent / What it does          |
|-----------------|------------------------------------|
| `dir`           | Same as `ls -l`                    |
| `cls`           | Clear screen                       |
| `ipconfig`      | Network info (same as `ifconfig`)  |
| `tasklist`      | Process list (same as `ps`)        |
| `systeminfo`    | System information                 |
| `ver`           | Version info                       |
| `type`          | Same as `cat`                      |
| `copy` / `move` | Basic file operations              |
| `del`           | Same as `rm`                       |
| `md` / `rd`     | `mkdir` / `rmdir`                  |

### Games
- `guess` – Number guessing
- `rps` – Rock Paper Scissors
- `hangman`
- `snake` – Simple text snake
- `dice`
- `fortune`

### Extra
- `neofetch` / `screenfetch`
- `cowsay`
- `free`, `df`, `uptime`
- Command aliases (`ll`, `la`, …)
- Simple text editor (`nano` / `vi`)

---

## Quick Start

```bash
git clone https://github.com/dahmanianis275-jpg/python-os.git
cd python-os
python python_os.py
```

Or just download `python_os.py` and run:

```bash
python python_os.py
```

### Default login
- User: `user` (no password needed on start)
- You can switch with `su root` or `su guest`
- `sudo` works (password is auto-accepted in this simulation)

---

## Example session

```bash
user@python-os:~$ neofetch
user@python-os:~$ games
user@python-os:~$ guess
user@python-os:~$ dir
user@python-os:~$ tasklist
user@python-os:~$ ipconfig
user@python-os:~$ sudo apt update
user@python-os:~$ cowsay "Hello from hybrid OS"
user@python-os:~$ top
```

---

## Project structure

```
python-os/
├── python_os.py      # Main simulator (single file)
├── README.md         # This file
├── LICENSE           # MIT License
└── .gitignore
```

---

## Requirements

- Python 3.8 or newer
- No external dependencies (pure standard library)

---

## Disclaimer

This is an **educational toy / simulation**.  
It cannot control real hardware, load kernel modules, or replace your host operating system.  
All filesystem, processes, networking and package management are completely virtual and live only in memory.

---

## License

MIT License – see [LICENSE](LICENSE)

---

**Made for fun and learning.**  
Feel free to fork, extend, and experiment.
