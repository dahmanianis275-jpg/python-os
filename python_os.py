#!/usr/bin/env python3
"""
Python OS 3.3 – Hybrid Linux / Windows Simulation (Unlimited Edition)
=====================================================================
Educational toy OS. File extensions + safe checking still exist,
but .py files now run with FULL / UNLIMITED real Python power
(as requested by the user).

Not a real kernel.
"""

import os
import sys
import time
import random
import shlex
import textwrap
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# File Extension / Association System
# ============================================================

class FileAssociation:
    def __init__(self):
        self.assoc = {
            ".txt":  ("Plain text",        "text",    False),
            ".md":   ("Markdown text",     "text",    False),
            ".log":  ("Log file",          "text",    False),
            ".py":   ("Python script",     "python",  True),
            ".pyw":  ("Python script",     "python",  True),
            ".sh":   ("Shell script",      "shell",   True),
            ".bash": ("Bash script",       "shell",   True),
            ".json": ("JSON data",         "json",    False),
            ".csv":  ("CSV data",          "text",    False),
            ".cfg":  ("Config file",       "text",    False),
            ".ini":  ("INI config",        "text",    False),
            ".html": ("HTML document",     "text",    False),
            ".htm":  ("HTML document",     "text",    False),
            "":      ("Unknown / no extension", "unknown", False),
        }

    def get_ext(self, filename: str) -> str:
        if "." in filename:
            return "." + filename.rsplit(".", 1)[-1].lower()
        return ""

    def info(self, filename: str):
        ext = self.get_ext(filename)
        return self.assoc.get(ext, self.assoc[""])

    def can_execute(self, filename: str) -> bool:
        return self.info(filename)[2]

    def list_all(self) -> str:
        lines = ["Registered file associations:", ""]
        for ext, (desc, handler, exe) in sorted(self.assoc.items()):
            if not ext:
                continue
            flag = "executable" if exe else "data"
            lines.append(f"  {ext:<8} {desc:<20} handler={handler:<8} ({flag})")
        return "\n".join(lines)


# ============================================================
# Virtual Filesystem
# ============================================================

class VFSNode:
    def __init__(self, name: str, is_dir: bool = False, content: str = "",
                 owner: str = "root", mode: str = "755", size: int = 0):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.owner = owner
        self.mode = mode
        self.children: Dict[str, "VFSNode"] = {}
        self.size = size if not is_dir else 4096
        self.mtime = datetime.now()

    def add(self, node: "VFSNode"):
        self.children[node.name] = node
        return node


class FileSystem:
    def __init__(self):
        self.root = VFSNode("/", is_dir=True, owner="root", mode="755")
        self._build_standard_tree()
        self.cwd_path = ["/"]
        self.cwd = self.root

    def _build_standard_tree(self):
        r = self.root

        bin_dir = r.add(VFSNode("bin", True, owner="root", mode="755"))
        cmds = [
            "bash", "ls", "cat", "echo", "pwd", "cd", "mkdir", "rm", "cp", "mv",
            "chmod", "ps", "kill", "top", "nano", "apt", "ping", "ifconfig",
            "curl", "uname", "whoami", "sudo", "guess", "rps", "hangman",
            "snake", "dice", "fortune", "neofetch", "cowsay", "free", "df",
            "uptime", "dir", "cls", "ipconfig", "tasklist", "systeminfo",
            "ver", "type", "del", "md", "rd", "run", "open", "file", "assoc",
            "python"
        ]
        for cmd in cmds:
            bin_dir.add(VFSNode(cmd, content=f"#!/bin/sh\n# {cmd}\n", owner="root", mode="755"))

        etc = r.add(VFSNode("etc", True, owner="root", mode="755"))
        etc.add(VFSNode("passwd", content=(
            "root:x:0:0:root:/root:/bin/bash\n"
            "user:x:1000:1000:User:/home/user:/bin/bash\n"
            "guest:x:1001:1001:Guest:/home/guest:/bin/bash\n"
        ), owner="root", mode="644"))
        etc.add(VFSNode("hostname", content="python-os\n", owner="root", mode="644"))
        etc.add(VFSNode("os-release", content=(
            'NAME="Python OS"\nVERSION="3.3 (Unlimited Python)"\n'
            'ID=pythonos\nPRETTY_NAME="Python OS 3.3"\n'
        ), owner="root", mode="644"))
        etc.add(VFSNode("motd", content=(
            "Python OS 3.3 – Hybrid + File Extensions + UNLIMITED Python\n"
            "Type 'help', 'games' or 'assoc'.\n"
        ), owner="root", mode="644"))

        home = r.add(VFSNode("home", True, owner="root", mode="755"))
        user_home = home.add(VFSNode("user", True, owner="user", mode="755"))
        user_home.add(VFSNode(".bashrc", content="# .bashrc\n", owner="user", mode="644"))
        user_home.add(VFSNode("readme.txt", content=(
            "Welcome to Python OS 3.3 (Unlimited)\n"
            "File extensions are supported.\n"
            "Python scripts now run with FULL power.\n"
            "Try:  run hello.py\n"
        ), owner="user", mode="644"))

        # Example scripts
        user_home.add(VFSNode("hello.py", content=(
            "#!/usr/bin/env python3\n"
            "print('Hello from UNLIMITED Python inside the OS!')\n"
            "print('2 + 2 =', 2 + 2)\n"
            "import sys\n"
            "print('Python version:', sys.version.split()[0])\n"
            "for i in range(3):\n"
            "    print('  loop', i)\n"
        ), owner="user", mode="755"))

        user_home.add(VFSNode("data.json", content='{"os": "Python OS", "version": 3.3, "unlimited": true}\n',
                              owner="user", mode="644"))

        home.add(VFSNode("guest", True, owner="guest", mode="755"))
        r.add(VFSNode("root", True, owner="root", mode="700"))

        usr = r.add(VFSNode("usr", True, owner="root", mode="755"))
        usr.add(VFSNode("bin", True, owner="root", mode="755"))
        usr.add(VFSNode("games", True, owner="root", mode="755"))

        var = r.add(VFSNode("var", True, owner="root", mode="755"))
        var.add(VFSNode("log", True, owner="root", mode="755"))
        r.add(VFSNode("tmp", True, owner="root", mode="1777"))

        proc = r.add(VFSNode("proc", True, owner="root", mode="555"))
        proc.add(VFSNode("version", content="Python OS 3.3 (Unlimited)\n", owner="root", mode="444"))
        proc.add(VFSNode("cpuinfo", content="processor\t: 0\nmodel name\t: Python Virtual CPU\n", owner="root", mode="444"))
        proc.add(VFSNode("meminfo", content="MemTotal: 16384000 kB\nMemFree: 8192000 kB\n", owner="root", mode="444"))

        dev = r.add(VFSNode("dev", True, owner="root", mode="755"))
        for d in ["null", "zero", "tty", "random", "urandom"]:
            dev.add(VFSNode(d, content="", owner="root", mode="666"))

    def resolve(self, path: str) -> Optional[VFSNode]:
        if not path or path == ".":
            return self.cwd
        if path == "/":
            return self.root
        parts = [p for p in path.split("/") if p]
        node = self.root if path.startswith("/") else self.cwd
        for part in parts:
            if part == "..":
                continue
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def get_absolute_path(self) -> str:
        if self.cwd_path == ["/"]:
            return "/"
        return "/" + "/".join(p for p in self.cwd_path if p != "/")

    def cd(self, path: str) -> bool:
        if path == "/":
            self.cwd = self.root
            self.cwd_path = ["/"]
            return True
        if path == "..":
            if len(self.cwd_path) > 1:
                self.cwd_path.pop()
                self.cwd = self.root
                for p in self.cwd_path[1:]:
                    self.cwd = self.cwd.children[p]
            return True
        target = self.resolve(path)
        if target is None or not target.is_dir:
            return False
        if path.startswith("/"):
            self.cwd_path = ["/"] + [p for p in path.split("/") if p]
        else:
            self.cwd_path += [p for p in path.split("/") if p]
        self.cwd = target
        return True

    def ls(self, path: str = ".", long: bool = False) -> List[str]:
        node = self.resolve(path)
        if node is None:
            return []
        if not node.is_dir:
            return [node.name]
        lines = []
        for name, child in sorted(node.children.items()):
            if long:
                t = "d" if child.is_dir else "-"
                lines.append(
                    f"{t}{child.mode} 1 {child.owner} {child.owner} "
                    f"{child.size:>8} {child.mtime.strftime('%b %d %H:%M')} {name}"
                )
            else:
                lines.append(name + ("/" if child.is_dir else ""))
        return lines

    def cat(self, path: str) -> Optional[str]:
        node = self.resolve(path)
        if node is None or node.is_dir:
            return None
        return node.content

    def mkdir(self, path: str, owner: str = "user") -> bool:
        parts = [p for p in path.split("/") if p]
        if not parts:
            return False
        name = parts[-1]
        parent_path = "/".join(parts[:-1]) if len(parts) > 1 else "."
        parent = self.resolve(parent_path if parent_path else ".")
        if parent is None or not parent.is_dir or name in parent.children:
            return False
        parent.add(VFSNode(name, True, owner=owner, mode="755"))
        return True

    def touch(self, path: str, owner: str = "user") -> bool:
        parts = [p for p in path.split("/") if p]
        name = parts[-1]
        parent_path = "/".join(parts[:-1]) if len(parts) > 1 else "."
        parent = self.resolve(parent_path if parent_path else ".")
        if parent is None or not parent.is_dir:
            return False
        if name not in parent.children:
            parent.add(VFSNode(name, content="", owner=owner, mode="644"))
        return True

    def write(self, path: str, content: str, owner: str = "user") -> bool:
        parts = [p for p in path.split("/") if p]
        name = parts[-1]
        parent_path = "/".join(parts[:-1]) if len(parts) > 1 else "."
        parent = self.resolve(parent_path if parent_path else ".")
        if parent is None or not parent.is_dir:
            return False
        parent.children[name] = VFSNode(
            name, content=content, owner=owner, mode="644", size=len(content)
        )
        return True

    def rm(self, path: str, recursive: bool = False) -> bool:
        parts = [p for p in path.split("/") if p]
        if not parts:
            return False
        name = parts[-1]
        parent_path = "/".join(parts[:-1]) if len(parts) > 1 else "."
        parent = self.resolve(parent_path if parent_path else ".")
        if parent is None or name not in parent.children:
            return False
        target = parent.children[name]
        if target.is_dir and target.children and not recursive:
            return False
        del parent.children[name]
        return True


# ============================================================
# Process Manager
# ============================================================

class Process:
    def __init__(self, pid: int, name: str, user: str, cmd: str):
        self.pid = pid
        self.name = name
        self.user = user
        self.cmd = cmd
        self.cpu = random.uniform(0.1, 12.0)
        self.mem = random.uniform(0.4, 15.0)


class ProcessManager:
    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.next_pid = 300
        self._spawn(1, "systemd", "root", "/sbin/init")
        self._spawn(2, "kthreadd", "root", "[kthreadd]")
        self._spawn(100, "sshd", "root", "/usr/sbin/sshd -D")
        self._spawn(200, "bash", "user", "-bash")
        self._spawn(201, "python-os", "user", "python_os.py")

    def _spawn(self, pid, name, user, cmd):
        self.processes[pid] = Process(pid, name, user, cmd)

    def spawn(self, name, user, cmd) -> int:
        pid = self.next_pid
        self.next_pid += 1
        self.processes[pid] = Process(pid, name, user, cmd)
        return pid

    def kill(self, pid: int, user: str) -> bool:
        if pid not in self.processes or pid < 100:
            return False
        if user != "root" and self.processes[pid].user != user:
            return False
        del self.processes[pid]
        return True

    def list(self):
        return list(self.processes.values())


# ============================================================
# UNLIMITED Python Execution (as requested)
# ============================================================

def unlimited_exec(code: str, filename: str = "<script>") -> None:
    """
    Execute Python code with FULL power of the host interpreter.
    No restrictions. Imports, open(), os, sys, everything is allowed.
    """
    try:
        # Full globals = normal Python environment
        exec(compile(code, filename, "exec"), globals(), {})
    except Exception as e:
        print(f"[Python OS] Error while running {filename}:")
        print(f"  {type(e).__name__}: {e}")
        # Optional: uncomment next line if you want full traceback
        # traceback.print_exc()


# ============================================================
# Games
# ============================================================

class Games:
    @staticmethod
    def guess():
        print("\n=== Number Guessing Game ===")
        secret = random.randint(1, 100)
        attempts = 0
        while True:
            try:
                guess = int(input("Your guess: "))
                attempts += 1
                if guess < secret:
                    print("Too low.")
                elif guess > secret:
                    print("Too high.")
                else:
                    print(f"Correct! {attempts} attempts.")
                    break
            except ValueError:
                print("Enter a number.")
            except (KeyboardInterrupt, EOFError):
                print("\nAborted.")
                break

    @staticmethod
    def rps():
        print("\n=== Rock Paper Scissors ===")
        options = ["rock", "paper", "scissors"]
        wins = losses = 0
        while True:
            user = input("rock / paper / scissors (q=quit): ").strip().lower()
            if user in ("q", "quit", "exit"):
                break
            if user not in options:
                print("Invalid.")
                continue
            comp = random.choice(options)
            print(f"Computer: {comp}")
            if user == comp:
                print("Draw!")
            elif (user, comp) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
                print("You win!")
                wins += 1
            else:
                print("You lose!")
                losses += 1
            print(f"Score You:{wins}  PC:{losses}\n")

    @staticmethod
    def hangman():
        words = ["python", "linux", "kernel", "extension", "filesystem",
                 "process", "hybrid", "windows", "unlimited", "simulation"]
        word = random.choice(words)
        guessed = set()
        lives = 7
        print("\n=== Hangman ===")
        while lives > 0:
            display = " ".join(c if c in guessed else "_" for c in word)
            print(f"\nWord: {display}   Lives: {lives}")
            if all(c in guessed for c in word):
                print(f"You won! → {word}")
                return
            try:
                letter = input("Letter: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return
            if len(letter) != 1 or not letter.isalpha():
                continue
            if letter in guessed:
                continue
            guessed.add(letter)
            if letter not in word:
                lives -= 1
        print(f"Game over. Word was: {word}")

    @staticmethod
    def snake():
        print("\n=== Snake ===  (w/a/s/d, q=quit)")
        width, height = 18, 9
        snake = [(4, 4), (4, 3), (4, 2)]
        direction = (0, 1)
        food = (random.randint(0, height-1), random.randint(0, width-1))
        score = 0
        try:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print(f"Score: {score}")
                print("+" + "-" * width + "+")
                for y in range(height):
                    line = "|"
                    for x in range(width):
                        if (y, x) == snake[0]:
                            line += "O"
                        elif (y, x) in snake:
                            line += "o"
                        elif (y, x) == food:
                            line += "*"
                        else:
                            line += " "
                    print(line + "|")
                print("+" + "-" * width + "+")
                move = input("Move: ").strip().lower()
                if move == "q":
                    break
                if move == "w" and direction != (1, 0):
                    direction = (-1, 0)
                elif move == "s" and direction != (-1, 0):
                    direction = (1, 0)
                elif move == "a" and direction != (0, 1):
                    direction = (0, -1)
                elif move == "d" and direction != (0, -1):
                    direction = (0, 1)
                hy, hx = snake[0]
                new = ((hy + direction[0]) % height, (hx + direction[1]) % width)
                if new in snake:
                    print("Hit yourself!")
                    break
                snake.insert(0, new)
                if new == food:
                    score += 10
                    food = (random.randint(0, height-1), random.randint(0, width-1))
                else:
                    snake.pop()
        except (KeyboardInterrupt, EOFError):
            pass
        print(f"Final score: {score}")

    @staticmethod
    def dice():
        print("\n=== Dice ===")
        while True:
            try:
                n = input("Dice (1-10, q=quit): ").strip()
                if n.lower() in ("q", "quit"):
                    break
                n = int(n)
                if 1 <= n <= 10:
                    res = [random.randint(1, 6) for _ in range(n)]
                    print(res, "Total:", sum(res))
            except ValueError:
                pass
            except (KeyboardInterrupt, EOFError):
                break

    @staticmethod
    def fortune():
        fortunes = [
            "Unlimited power comes with unlimited responsibility.",
            "Your .py files now have full access.",
            "There is no sandbox anymore.",
            "sudo make me a sandwich.",
            "Windows and Linux living together in one Python process.",
            "Check the extension, then run wild.",
        ]
        print("\n" + random.choice(fortunes) + "\n")


# ============================================================
# Main OS
# ============================================================

class PythonOS:
    def __init__(self):
        self.fs = FileSystem()
        self.pm = ProcessManager()
        self.assoc = FileAssociation()
        self.users = {
            "root":  {"uid": 0,    "home": "/root"},
            "user":  {"uid": 1000, "home": "/home/user"},
            "guest": {"uid": 1001, "home": "/home/guest"},
        }
        self.current_user = "user"
        self.hostname = "python-os"
        self.env = {
            "PATH": "/bin:/usr/bin:/usr/local/bin:/usr/games",
            "HOME": "/home/user",
            "USER": "user",
            "SHELL": "/bin/bash",
            "TERM": "xterm-256color",
        }
        self.history: List[str] = []
        self.aliases = {
            "ll": "ls -l", "la": "ls -la", "cls": "clear",
            "dir": "ls -l", "md": "mkdir", "rd": "rm -r",
            "del": "rm", "type": "cat", "ipconfig": "ifconfig",
            "tasklist": "ps",
        }
        self.running = True
        self.sudo_mode = False
        self.boot_time = time.time()

    def is_root(self) -> bool:
        return self.current_user == "root" or self.sudo_mode

    def prompt(self) -> str:
        path = self.fs.get_absolute_path()
        if path.startswith(self.env["HOME"]):
            path = "~" + path[len(self.env["HOME"]):]
        symbol = "#" if self.is_root() else "$"
        return f"{self.current_user}@{self.hostname}:{path}{symbol} "

    def boot(self):
        print("\n[  0.000000] Linux version 6.6.0-pythonos (Unlimited Edition)")
        time.sleep(0.1)
        print("[  0.500000] Loading file associations + FULL Python runtime...")
        time.sleep(0.2)
        print("[  1.200000] Multi-user target reached. Python execution is UNLIMITED.")
        print()
        print(self.fs.cat("/etc/motd"), end="")
        print(f"Python OS 3.3  {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}")
        print("Try:  run hello.py   (full power)\n")

        while self.running:
            try:
                line = input(self.prompt())
                self.execute(line)
            except KeyboardInterrupt:
                print("\n^C")
            except EOFError:
                print("\nlogout")
                break

    def safe_open(self, path: str) -> None:
        node = self.fs.resolve(path)
        if node is None:
            print(f"open: {path}: No such file or directory")
            return
        if node.is_dir:
            print(f"open: {path}: Is a directory")
            return

        desc, handler, executable = self.assoc.info(path)

        if handler == "unknown":
            print(f"[Python OS] Refused to open '{path}' (unknown extension)")
            print("  Use 'assoc' to see supported types.")
            return

        content = node.content

        if handler == "text":
            print(content, end="" if content.endswith("\n") else "\n")
        elif handler == "json":
            try:
                data = json.loads(content)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
                print(content)
        elif handler == "python":
            print(f"[Python OS] '{path}' is a Python script (unlimited).")
            print(f"  Use:  run {path}   or   python {path}")
        elif handler == "shell":
            print(f"[Python OS] '{path}' is a shell script.")
            print(f"  Use:  run {path}")
        else:
            print(content)

    def safe_run(self, path: str) -> None:
        node = self.fs.resolve(path)
        if node is None:
            print(f"run: {path}: No such file or directory")
            return
        if node.is_dir:
            print(f"run: {path}: Is a directory")
            return

        desc, handler, executable = self.assoc.info(path)

        if not executable:
            print(f"[Python OS] Cannot execute '{path}' ({desc})")
            print(f"  Tip: use 'open {path}' instead.")
            return

        content = node.content

        # Shebang
        first_line = content.splitlines()[0] if content else ""
        if first_line.startswith("#!"):
            if "python" in first_line:
                handler = "python"
            elif "bash" in first_line or "sh" in first_line:
                handler = "shell"

        if handler == "python":
            print(f"[Python OS] Running {path} with UNLIMITED Python...")
            print("-" * 50)
            unlimited_exec(content, filename=path)
            print("-" * 50)
            print("[Python OS] Script finished.")
        elif handler == "shell":
            print(f"[Python OS] Simulating shell script {path}")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                print(f"+ {line}")
                if line.startswith("echo "):
                    print(line[5:])
        else:
            print(f"[Python OS] No runner for '{handler}'")

    def execute(self, line: str):
        line = line.strip()
        if not line:
            return
        self.history.append(line)

        first = line.split()[0]
        if first in self.aliases:
            line = self.aliases[first] + line[len(first):]

        if line.startswith("./"):
            line = "run " + line[2:]

        try:
            tokens = shlex.split(line)
        except ValueError:
            print("syntax error")
            return
        if not tokens:
            return

        cmd = tokens[0].lower()
        args = tokens[1:]

        if cmd in ("exit", "logout", "quit"):
            if self.sudo_mode:
                self.sudo_mode = False
                print("sudo session closed")
            else:
                print("logout")
                self.running = False
            return

        if cmd == "sudo":
            if not args:
                print("usage: sudo <command>")
                return
            print(f"[sudo] password for {self.current_user}: (accepted)")
            self.sudo_mode = True
            self.execute(" ".join(args))
            self.sudo_mode = False
            return

        if cmd == "su":
            target = args[0] if args else "root"
            if target not in self.users:
                print(f"su: user {target} does not exist")
                return
            print("Password: (accepted)")
            self.current_user = target
            self.env["USER"] = target
            self.env["HOME"] = self.users[target]["home"]
            self.fs.cd(self.env["HOME"])
            return

        if cmd == "whoami":
            print(self.current_user)
            return

        if cmd == "id":
            u = self.users[self.current_user]
            print(f"uid={u['uid']}({self.current_user}) gid={u['uid']}({self.current_user})")
            return

        if cmd == "file":
            if not args:
                print("usage: file <path>")
                return
            path = args[0]
            node = self.fs.resolve(path)
            if node is None:
                print(f"{path}: cannot open")
                return
            if node.is_dir:
                print(f"{path}: directory")
                return
            desc, handler, executable = self.assoc.info(path)
            print(f"{path}: {desc}")
            print(f"  handler   : {handler}")
            print(f"  executable: {'yes' if executable else 'no'}")
            return

        if cmd == "assoc":
            print(self.assoc.list_all())
            return

        if cmd == "open":
            if not args:
                print("usage: open <file>")
                return
            self.safe_open(args[0])
            return

        if cmd == "run":
            if not args:
                print("usage: run <file>")
                return
            self.safe_run(args[0])
            return

        if cmd == "python":
            if not args:
                print("usage: python <file.py>")
                return
            self.safe_run(args[0])
            return

        if cmd == "pwd":
            print(self.fs.get_absolute_path())
            return

        if cmd == "cd":
            path = args[0] if args else self.env["HOME"]
            if not self.fs.cd(path):
                print(f"bash: cd: {path}: No such file or directory")
            return

        if cmd in ("ls", "dir"):
            path = "."
            long = cmd == "dir" or any("l" in a for a in args if a.startswith("-"))
            for a in args:
                if not a.startswith("-"):
                    path = a
            items = self.fs.ls(path, long=long)
            if not items and path != ".":
                print(f"ls: cannot access '{path}'")
            else:
                print("\n".join(items) if long else "  ".join(items))
            return

        if cmd in ("cat", "type"):
            if not args:
                print(f"{cmd}: missing file operand")
                return
            content = self.fs.cat(args[0])
            if content is None:
                print(f"{cmd}: {args[0]}: No such file or directory")
            else:
                print(content, end="" if content.endswith("\n") else "\n")
            return

        if cmd in ("mkdir", "md"):
            for p in args:
                if not self.fs.mkdir(p, owner=self.current_user):
                    print(f"mkdir: cannot create directory ‘{p}’")
            return

        if cmd == "touch":
            for p in args:
                self.fs.touch(p, owner=self.current_user)
            return

        if cmd in ("rm", "del", "rd"):
            recursive = any(a in ("-r", "-rf", "-fr") for a in args) or cmd == "rd"
            paths = [a for a in args if not a.startswith("-")]
            for p in paths:
                if not self.fs.rm(p, recursive=recursive):
                    print(f"rm: cannot remove '{p}'")
            return

        if cmd == "echo":
            if ">" in tokens:
                idx = tokens.index(">")
                text = " ".join(tokens[1:idx])
                filename = tokens[idx+1] if idx+1 < len(tokens) else None
                if filename:
                    self.fs.write(filename, text + "\n", owner=self.current_user)
                else:
                    print(text)
            else:
                print(" ".join(args))
            return

        if cmd in ("ps", "tasklist"):
            print(f"{'PID':>6} {'USER':<8} {'%CPU':>5} {'%MEM':>5} COMMAND")
            for p in self.pm.list():
                print(f"{p.pid:>6} {p.user:<8} {p.cpu:>5.1f} {p.mem:>5.1f} {p.cmd}")
            return

        if cmd == "top":
            print("top - Ctrl+C to stop")
            try:
                while True:
                    os.system("cls" if os.name == "nt" else "clear")
                    print(f"top - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"{'PID':>6} {'USER':<8} {'%CPU':>5} {'%MEM':>5} COMMAND")
                    for p in sorted(self.pm.list(), key=lambda x: x.cpu, reverse=True):
                        p.cpu = max(0.1, p.cpu + random.uniform(-1.5, 1.5))
                        print(f"{p.pid:>6} {p.user:<8} {p.cpu:>5.1f} {p.mem:>5.1f} {p.cmd}")
                    time.sleep(1.5)
            except KeyboardInterrupt:
                print()
            return

        if cmd == "kill":
            if not args:
                print("usage: kill <pid>")
                return
            try:
                pid = int(args[0])
                if self.pm.kill(pid, "root" if self.is_root() else self.current_user):
                    print(f"Killed {pid}")
                else:
                    print(f"kill: ({pid}) - No such process")
            except ValueError:
                print("kill: invalid argument")
            return

        if cmd == "free":
            print("              total        used        free")
            print("Mem:       16384000     8192000     8192000")
            return

        if cmd == "df":
            print("Filesystem     1K-blocks    Used Available Use% Mounted on")
            print("/dev/pythonos   10485760  3145728   7340032  30% /")
            return

        if cmd == "uptime":
            secs = int(time.time() - self.boot_time)
            print(f" up {secs//60} min")
            return

        if cmd in ("neofetch", "screenfetch", "systeminfo"):
            print(textwrap.dedent(f"""
                {self.current_user}@{self.hostname}
                OS: Python OS 3.3 (Unlimited Python)
                Kernel: 6.6.0-pythonos
                Uptime: {int(time.time()-self.boot_time)} s
                Features: file extensions + FULL Python power
            """))
            return

        if cmd in ("uname", "ver"):
            print(f"PythonOS {self.hostname} 3.3.0-pythonos Unlimited")
            return

        if cmd == "hostname":
            print(self.hostname)
            return

        if cmd == "date":
            print(datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
            return

        if cmd == "history":
            for i, h in enumerate(self.history[-40:], 1):
                print(f" {i:4d}  {h}")
            return

        if cmd in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            return

        if cmd == "env":
            for k, v in sorted(self.env.items()):
                print(f"{k}={v}")
            return

        if cmd == "export":
            for a in args:
                if "=" in a:
                    k, v = a.split("=", 1)
                    self.env[k] = v
            return

        if cmd == "alias":
            if not args:
                for k, v in self.aliases.items():
                    print(f"alias {k}='{v}'")
            return

        if cmd in ("ifconfig", "ipconfig"):
            print("eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500")
            print("        inet 10.0.2.15  netmask 255.255.255.0")
            return

        if cmd == "ping":
            host = args[0] if args else "127.0.0.1"
            print(f"PING {host}")
            for i in range(4):
                time.sleep(0.25)
                print(f"64 bytes from {host}: icmp_seq={i+1} time={random.uniform(8,35):.1f} ms")
            return

        if cmd in ("curl", "wget"):
            url = args[0] if args else "http://example.com"
            print(f"* Connected to {url}")
            print("<html><body><h1>Python OS page</h1></body></html>")
            return

        if cmd == "apt":
            if not args:
                print("apt (pythonos)")
                return
            sub = args[0]
            if sub == "update":
                print("Reading package lists... Done")
            elif sub == "install":
                for p in args[1:]:
                    print(f"Installing {p}... done")
            else:
                print(f"E: Invalid operation {sub}")
            return

        if cmd == "games":
            print("\nGames:  guess  rps  hangman  snake  dice  fortune\n")
            return

        if cmd == "guess":
            Games.guess()
            return
        if cmd == "rps":
            Games.rps()
            return
        if cmd == "hangman":
            Games.hangman()
            return
        if cmd == "snake":
            Games.snake()
            return
        if cmd == "dice":
            Games.dice()
            return
        if cmd == "fortune":
            Games.fortune()
            return

        if cmd == "cowsay":
            msg = " ".join(args) if args else "Unlimited mode activated"
            print(f"""
  ___________
< {msg} >
  -----------
         \\   ^__^
          \\  (oo)\\_______
             (__)\\       )\\/\\
                 ||----w |
                 ||     ||
""")
            return

        if cmd in ("nano", "vi", "vim"):
            if not args:
                print(f"{cmd}: missing filename")
                return
            print(f"--- {cmd} (end with .) ---")
            lines = []
            while True:
                try:
                    l = input()
                    if l == ".":
                        break
                    lines.append(l)
                except EOFError:
                    break
            self.fs.write(args[0], "\n".join(lines) + "\n", owner=self.current_user)
            print(f"Written {args[0]}")
            return

        if cmd == "help":
            print("""
Python OS 3.3 – Unlimited Edition

File extensions:
  file <path>     Show type
  assoc           List extensions
  open <file>     Open safely
  run <file>      Execute (UNLIMITED for .py)
  python <file>   Same as run for Python
  ./script.py     Same as run

Classic + hybrid commands still work
(ls/dir, ps/tasklist, ifconfig/ipconfig, etc.)

Games: games  guess  rps  hangman  snake  dice  fortune
""")
            return

        print(f"{cmd}: command not found")


if __name__ == "__main__":
    PythonOS().boot()
