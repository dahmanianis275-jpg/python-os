#!/usr/bin/env python3
"""
Python OS 3.4
Hybrid Linux + Windows operating system in pure Python.
Full file extension support + unlimited Python execution.
"""

import os
import sys
import time
import random
import shlex
import textwrap
import json
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# File Extensions
# ============================================================

class FileAssociation:
    def __init__(self):
        self.assoc = {
            ".txt":  ("Plain text",        "text",    False),
            ".md":   ("Markdown",          "text",    False),
            ".log":  ("Log file",          "text",    False),
            ".py":   ("Python script",     "python",  True),
            ".pyw":  ("Python script",     "python",  True),
            ".sh":   ("Shell script",      "shell",   True),
            ".bash": ("Bash script",       "shell",   True),
            ".json": ("JSON",              "json",    False),
            ".csv":  ("CSV",               "text",    False),
            ".cfg":  ("Config",            "text",    False),
            ".ini":  ("INI config",        "text",    False),
            ".html": ("HTML",              "text",    False),
            ".htm":  ("HTML",              "text",    False),
            "":      ("Unknown",           "unknown", False),
        }

    def get_ext(self, filename: str) -> str:
        if "." in filename:
            return "." + filename.rsplit(".", 1)[-1].lower()
        return ""

    def info(self, filename: str):
        return self.assoc.get(self.get_ext(filename), self.assoc[""])

    def can_execute(self, filename: str) -> bool:
        return self.info(filename)[2]

    def list_all(self) -> str:
        lines = ["File extensions:", ""]
        for ext, (desc, handler, exe) in sorted(self.assoc.items()):
            if not ext:
                continue
            flag = "executable" if exe else "data"
            lines.append(f"  {ext:<8} {desc:<18} {handler:<8} ({flag})")
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
        self._build()
        self.cwd_path = ["/"]
        self.cwd = self.root

    def _build(self):
        r = self.root

        bin_dir = r.add(VFSNode("bin", True, owner="root", mode="755"))
        for cmd in ["bash","ls","cat","echo","pwd","cd","mkdir","rm","ps","kill",
                    "top","nano","apt","ping","ifconfig","curl","uname","whoami",
                    "sudo","guess","rps","hangman","snake","dice","fortune",
                    "neofetch","cowsay","free","df","uptime","dir","cls",
                    "ipconfig","tasklist","systeminfo","ver","type","del",
                    "md","rd","run","open","file","assoc","python"]:
            bin_dir.add(VFSNode(cmd, content=f"#!/bin/sh\n# {cmd}\n", owner="root", mode="755"))

        etc = r.add(VFSNode("etc", True, owner="root", mode="755"))
        etc.add(VFSNode("passwd", content=(
            "root:x:0:0:root:/root:/bin/bash\n"
            "user:x:1000:1000:User:/home/user:/bin/bash\n"
            "guest:x:1001:1001:Guest:/home/guest:/bin/bash\n"
        ), owner="root", mode="644"))
        etc.add(VFSNode("hostname", content="python-os\n", owner="root", mode="644"))
        etc.add(VFSNode("os-release", content=(
            'NAME="Python OS"\nVERSION="3.4"\nID=pythonos\nPRETTY_NAME="Python OS 3.4"\n'
        ), owner="root", mode="644"))
        etc.add(VFSNode("motd", content="Python OS 3.4\nType 'help' or 'games'.\n", owner="root", mode="644"))

        home = r.add(VFSNode("home", True, owner="root", mode="755"))
        user_home = home.add(VFSNode("user", True, owner="user", mode="755"))
        user_home.add(VFSNode(".bashrc", content="# .bashrc\n", owner="user", mode="644"))
        user_home.add(VFSNode("readme.txt", content=(
            "Python OS 3.4\n"
            "Extensions are active.\n"
            "Try: run hello.py\n"
        ), owner="user", mode="644"))

        user_home.add(VFSNode("hello.py", content=(
            "#!/usr/bin/env python3\n"
            "print('Hello from Python OS')\n"
            "print('2 + 2 =', 2 + 2)\n"
            "import sys\n"
            "print('Python', sys.version.split()[0])\n"
        ), owner="user", mode="755"))

        user_home.add(VFSNode("data.json", content='{"name": "Python OS", "version": 3.4}\n',
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
        proc.add(VFSNode("version", content="Python OS 3.4\n", owner="root", mode="444"))
        proc.add(VFSNode("cpuinfo", content="processor : 0\nmodel name : Python CPU\n", owner="root", mode="444"))
        proc.add(VFSNode("meminfo", content="MemTotal: 16384000 kB\n", owner="root", mode="444"))

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
                lines.append(f"{t}{child.mode} 1 {child.owner} {child.owner} {child.size:>8} {child.mtime.strftime('%b %d %H:%M')} {name}")
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
        parent.children[name] = VFSNode(name, content=content, owner=owner, mode="644", size=len(content))
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
# Processes
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
        self._spawn(100, "sshd", "root", "/usr/sbin/sshd")
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
# Unlimited Python execution
# ============================================================

def unlimited_exec(code: str, filename: str = "<script>") -> None:
    try:
        exec(compile(code, filename, "exec"), globals(), {})
    except Exception as e:
        print(f"[Python OS] Error in {filename}: {type(e).__name__}: {e}")


# ============================================================
# Games
# ============================================================

class Games:
    @staticmethod
    def guess():
        print("\n=== Number Guessing ===")
        secret = random.randint(1, 100)
        attempts = 0
        while True:
            try:
                g = int(input("Guess: "))
                attempts += 1
                if g < secret: print("Too low")
                elif g > secret: print("Too high")
                else:
                    print(f"Correct in {attempts} tries")
                    break
            except ValueError:
                print("Number only")
            except (KeyboardInterrupt, EOFError):
                break

    @staticmethod
    def rps():
        print("\n=== Rock Paper Scissors ===")
        opts = ["rock", "paper", "scissors"]
        w = l = 0
        while True:
            u = input("rock/paper/scissors (q=quit): ").strip().lower()
            if u in ("q", "quit"): break
            if u not in opts: continue
            c = random.choice(opts)
            print("Computer:", c)
            if u == c: print("Draw")
            elif (u, c) in [("rock","scissors"),("paper","rock"),("scissors","paper")]:
                print("You win"); w += 1
            else:
                print("You lose"); l += 1
            print(f"You {w} - {l} PC\n")

    @staticmethod
    def hangman():
        words = ["python","linux","kernel","extension","hybrid","windows","filesystem"]
        word = random.choice(words)
        guessed = set()
        lives = 7
        print("\n=== Hangman ===")
        while lives > 0:
            disp = " ".join(c if c in guessed else "_" for c in word)
            print(f"\n{disp}  Lives:{lives}")
            if all(c in guessed for c in word):
                print("You won:", word)
                return
            try:
                letter = input("Letter: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return
            if len(letter) != 1 or not letter.isalpha() or letter in guessed:
                continue
            guessed.add(letter)
            if letter not in word:
                lives -= 1
        print("Word was:", word)

    @staticmethod
    def snake():
        print("\n=== Snake (w/a/s/d, q=quit) ===")
        w, h = 18, 9
        snake = [(4,4),(4,3),(4,2)]
        direction = (0,1)
        food = (random.randint(0,h-1), random.randint(0,w-1))
        score = 0
        try:
            while True:
                os.system("cls" if os.name=="nt" else "clear")
                print(f"Score: {score}")
                print("+" + "-"*w + "+")
                for y in range(h):
                    line = "|"
                    for x in range(w):
                        if (y,x) == snake[0]: line += "O"
                        elif (y,x) in snake: line += "o"
                        elif (y,x) == food: line += "*"
                        else: line += " "
                    print(line + "|")
                print("+" + "-"*w + "+")
                m = input("Move: ").strip().lower()
                if m == "q": break
                if m=="w" and direction!=(1,0): direction=(-1,0)
                elif m=="s" and direction!=(-1,0): direction=(1,0)
                elif m=="a" and direction!=(0,1): direction=(0,-1)
                elif m=="d" and direction!=(0,-1): direction=(0,1)
                hy,hx = snake[0]
                new = ((hy+direction[0])%h, (hx+direction[1])%w)
                if new in snake:
                    print("Game over")
                    break
                snake.insert(0, new)
                if new == food:
                    score += 10
                    food = (random.randint(0,h-1), random.randint(0,w-1))
                else:
                    snake.pop()
        except (KeyboardInterrupt, EOFError):
            pass
        print("Score:", score)

    @staticmethod
    def dice():
        print("\n=== Dice ===")
        while True:
            try:
                n = input("How many (1-10, q=quit): ").strip()
                if n.lower() in ("q","quit"): break
                n = int(n)
                if 1 <= n <= 10:
                    r = [random.randint(1,6) for _ in range(n)]
                    print(r, "Total:", sum(r))
            except ValueError:
                pass
            except (KeyboardInterrupt, EOFError):
                break

    @staticmethod
    def fortune():
        print("\n" + random.choice([
            "Extensions are online.",
            "Full Python power enabled.",
            "Hybrid mode active.",
            "Keep building.",
        ]) + "\n")


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
            "PATH": "/bin:/usr/bin:/usr/local/bin",
            "HOME": "/home/user",
            "USER": "user",
            "SHELL": "/bin/bash",
        }
        self.history = []
        self.aliases = {
            "ll": "ls -l", "la": "ls -la", "cls": "clear",
            "dir": "ls -l", "md": "mkdir", "rd": "rm -r",
            "del": "rm", "type": "cat", "ipconfig": "ifconfig",
            "tasklist": "ps",
        }
        self.running = True
        self.sudo_mode = False
        self.boot_time = time.time()

    def is_root(self):
        return self.current_user == "root" or self.sudo_mode

    def prompt(self):
        path = self.fs.get_absolute_path()
        if path.startswith(self.env["HOME"]):
            path = "~" + path[len(self.env["HOME"]):]
        symbol = "#" if self.is_root() else "$"
        return f"{self.current_user}@{self.hostname}:{path}{symbol} "

    def boot(self):
        print("\nPython OS 3.4")
        print(self.fs.cat("/etc/motd"), end="")
        print()

        while self.running:
            try:
                line = input(self.prompt())
                self.execute(line)
            except KeyboardInterrupt:
                print("\n^C")
            except EOFError:
                print("\nlogout")
                break

    def safe_open(self, path: str):
        node = self.fs.resolve(path)
        if node is None:
            print(f"open: {path}: No such file")
            return
        if node.is_dir:
            print(f"open: {path}: Is a directory")
            return

        desc, handler, _ = self.assoc.info(path)
        if handler == "unknown":
            print(f"[Python OS] Unknown extension for '{path}'")
            return

        content = node.content
        if handler == "text":
            print(content, end="" if content.endswith("\n") else "\n")
        elif handler == "json":
            try:
                print(json.dumps(json.loads(content), indent=2))
            except:
                print(content)
        elif handler == "python":
            print(f"'{path}' is a Python script. Use: run {path}")
        elif handler == "shell":
            print(f"'{path}' is a shell script. Use: run {path}")
        else:
            print(content)

    def safe_run(self, path: str):
        node = self.fs.resolve(path)
        if node is None:
            print(f"run: {path}: No such file")
            return
        if node.is_dir:
            print(f"run: {path}: Is a directory")
            return

        desc, handler, executable = self.assoc.info(path)
        if not executable:
            print(f"Cannot execute '{path}' ({desc})")
            return

        content = node.content
        first = content.splitlines()[0] if content else ""
        if first.startswith("#!") and "python" in first:
            handler = "python"
        elif first.startswith("#!") and ("bash" in first or "sh" in first):
            handler = "shell"

        if handler == "python":
            print(f"Running {path}...")
            print("-" * 40)
            unlimited_exec(content, path)
            print("-" * 40)
        elif handler == "shell":
            print(f"Simulating {path}")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    print("+", line)
                    if line.startswith("echo "):
                        print(line[5:])
        else:
            print("No runner for this type")

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
                print("sudo ended")
            else:
                print("logout")
                self.running = False
            return

        if cmd == "sudo":
            if not args:
                print("usage: sudo <cmd>")
                return
            print("[sudo] password: (accepted)")
            self.sudo_mode = True
            self.execute(" ".join(args))
            self.sudo_mode = False
            return

        if cmd == "su":
            target = args[0] if args else "root"
            if target not in self.users:
                print("user does not exist")
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
            print(f"uid={u['uid']}({self.current_user})")
            return

        if cmd == "file":
            if not args:
                print("usage: file <path>")
                return
            node = self.fs.resolve(args[0])
            if node is None:
                print("No such file")
                return
            if node.is_dir:
                print("directory")
                return
            desc, handler, exe = self.assoc.info(args[0])
            print(f"{args[0]}: {desc}")
            print(f"  handler: {handler}")
            print(f"  executable: {'yes' if exe else 'no'}")
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
                print(f"cd: {path}: No such directory")
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
                print(f"{cmd}: missing file")
                return
            content = self.fs.cat(args[0])
            if content is None:
                print(f"{cmd}: {args[0]}: No such file")
            else:
                print(content, end="" if content.endswith("\n") else "\n")
            return

        if cmd in ("mkdir", "md"):
            for p in args:
                if not self.fs.mkdir(p, owner=self.current_user):
                    print(f"mkdir: cannot create '{p}'")
            return

        if cmd == "touch":
            for p in args:
                self.fs.touch(p, owner=self.current_user)
            return

        if cmd in ("rm", "del", "rd"):
            recursive = any(a in ("-r","-rf","-fr") for a in args) or cmd == "rd"
            for p in [a for a in args if not a.startswith("-")]:
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
            print("top (Ctrl+C to stop)")
            try:
                while True:
                    os.system("cls" if os.name=="nt" else "clear")
                    print(f"{'PID':>6} {'USER':<8} {'%CPU':>5} {'%MEM':>5} COMMAND")
                    for p in sorted(self.pm.list(), key=lambda x: x.cpu, reverse=True):
                        p.cpu = max(0.1, p.cpu + random.uniform(-1.5,1.5))
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
                    print("No such process")
            except ValueError:
                print("invalid pid")
            return

        if cmd == "free":
            print("              total        used        free")
            print("Mem:       16384000     8192000     8192000")
            return

        if cmd == "df":
            print("Filesystem     Size  Used Avail Use% Mounted on")
            print("/dev/pythonos   10G  3.0G  7.0G  30% /")
            return

        if cmd == "uptime":
            print(f" up {int(time.time()-self.boot_time)//60} min")
            return

        if cmd in ("neofetch", "screenfetch", "systeminfo"):
            print(f"""{self.current_user}@{self.hostname}
OS: Python OS 3.4
Kernel: 6.6.0-pythonos
Uptime: {int(time.time()-self.boot_time)}s
""")
            return

        if cmd in ("uname", "ver"):
            print("PythonOS 3.4")
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
            os.system("cls" if os.name=="nt" else "clear")
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
            print("eth0: inet 10.0.2.15  netmask 255.255.255.0")
            return

        if cmd == "ping":
            host = args[0] if args else "127.0.0.1"
            print(f"PING {host}")
            for i in range(4):
                time.sleep(0.2)
                print(f"64 bytes from {host}: icmp_seq={i+1} time={random.uniform(8,30):.1f} ms")
            return

        if cmd in ("curl", "wget"):
            print("* Connected")
            print("<html><body><h1>Python OS</h1></body></html>")
            return

        if cmd == "apt":
            if not args:
                print("apt")
                return
            if args[0] == "update":
                print("Reading package lists... Done")
            elif args[0] == "install":
                for p in args[1:]:
                    print(f"Installing {p}... done")
            else:
                print("Unknown apt command")
            return

        if cmd == "games":
            print("\nGames: guess  rps  hangman  snake  dice  fortune\n")
            return

        if cmd == "guess": Games.guess(); return
        if cmd == "rps": Games.rps(); return
        if cmd == "hangman": Games.hangman(); return
        if cmd == "snake": Games.snake(); return
        if cmd == "dice": Games.dice(); return
        if cmd == "fortune": Games.fortune(); return

        if cmd == "cowsay":
            msg = " ".join(args) if args else "Python OS"
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
                    if l == ".": break
                    lines.append(l)
                except EOFError:
                    break
            self.fs.write(args[0], "\n".join(lines)+"\n", owner=self.current_user)
            print(f"Written {args[0]}")
            return

        if cmd == "help":
            print("""
Python OS 3.4

Extensions:
  assoc          list extensions
  file <path>    inspect file
  open <file>    open by type
  run <file>     execute
  python <file>  run Python
  ./script.py    same as run

Commands:
  ls/dir  cd  pwd  cat/type  mkdir/md  rm/del
  ps/tasklist  top  kill  free  df  uptime
  neofetch  uname/ver  ifconfig/ipconfig  ping
  whoami  su  sudo  history  clear/cls
  games  guess  rps  hangman  snake  dice  fortune
""")
            return

        print(f"{cmd}: command not found")


if __name__ == "__main__":
    PythonOS().boot()
