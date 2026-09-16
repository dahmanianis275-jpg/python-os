#!/usr/bin/env python3
"""
Python OS 3.1 – Hybrid Linux / Windows Simulation
=================================================
Educational toy operating system written in pure Python.
Feels close to real Linux while also supporting many Windows commands.

Not a real kernel. Runs on top of your actual OS.
"""

import os
import sys
import time
import random
import shlex
import textwrap
from datetime import datetime
from typing import Dict, List, Optional

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

        # /bin
        bin_dir = r.add(VFSNode("bin", True, owner="root", mode="755"))
        cmds = [
            "bash", "ls", "cat", "echo", "pwd", "cd", "mkdir", "rm", "cp", "mv",
            "chmod", "ps", "kill", "top", "nano", "apt", "ping", "ifconfig",
            "curl", "uname", "whoami", "sudo", "guess", "rps", "hangman",
            "snake", "dice", "fortune", "neofetch", "cowsay", "free", "df",
            "uptime", "dir", "cls", "ipconfig", "tasklist", "systeminfo",
            "ver", "type", "del", "md", "rd"
        ]
        for cmd in cmds:
            bin_dir.add(VFSNode(cmd, content=f"#!/bin/sh\n# {cmd}\n", owner="root", mode="755"))

        # /etc
        etc = r.add(VFSNode("etc", True, owner="root", mode="755"))
        etc.add(VFSNode("passwd", content=(
            "root:x:0:0:root:/root:/bin/bash\n"
            "user:x:1000:1000:User:/home/user:/bin/bash\n"
            "guest:x:1001:1001:Guest:/home/guest:/bin/bash\n"
        ), owner="root", mode="644"))
        etc.add(VFSNode("hostname", content="python-os\n", owner="root", mode="644"))
        etc.add(VFSNode("os-release", content=(
            'NAME="Python OS"\n'
            'VERSION="3.1 (Hybrid Linux/Windows)"\n'
            'ID=pythonos\n'
            'PRETTY_NAME="Python OS 3.1"\n'
        ), owner="root", mode="644"))
        etc.add(VFSNode("motd", content=(
            "Python OS 3.1 – Hybrid Linux + Windows simulation\n"
            "Type 'help' or 'games' to get started.\n"
        ), owner="root", mode="644"))

        # /home
        home = r.add(VFSNode("home", True, owner="root", mode="755"))
        user_home = home.add(VFSNode("user", True, owner="user", mode="755"))
        user_home.add(VFSNode(".bashrc", content="# .bashrc\n", owner="user", mode="644"))
        user_home.add(VFSNode("readme.txt", content=(
            "Welcome to Python OS 3.1\n"
            "This is a hybrid Linux/Windows style simulation.\n"
            "Type 'games' for games or 'help' for commands.\n"
        ), owner="user", mode="644"))

        home.add(VFSNode("guest", True, owner="guest", mode="755"))
        r.add(VFSNode("root", True, owner="root", mode="700"))

        # /usr
        usr = r.add(VFSNode("usr", True, owner="root", mode="755"))
        usr.add(VFSNode("bin", True, owner="root", mode="755"))
        usr.add(VFSNode("games", True, owner="root", mode="755"))

        # /var + /tmp
        var = r.add(VFSNode("var", True, owner="root", mode="755"))
        var.add(VFSNode("log", True, owner="root", mode="755"))
        r.add(VFSNode("tmp", True, owner="root", mode="1777"))

        # /proc
        proc = r.add(VFSNode("proc", True, owner="root", mode="555"))
        proc.add(VFSNode("version", content="Python OS 3.1 (Hybrid)\n", owner="root", mode="444"))
        proc.add(VFSNode("cpuinfo", content=(
            "processor\t: 0\nmodel name\t: Python Virtual CPU @ 3.4GHz\n"
        ), owner="root", mode="444"))
        proc.add(VFSNode("meminfo", content=(
            "MemTotal:       16384000 kB\nMemFree:         8192000 kB\n"
        ), owner="root", mode="444"))

        # /dev
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
# Games
# ============================================================

class Games:
    @staticmethod
    def guess():
        print("\n=== Number Guessing Game ===")
        print("I'm thinking of a number between 1 and 100.")
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
                    print(f"Correct! You got it in {attempts} attempts.")
                    break
            except ValueError:
                print("Please enter a number.")
            except (KeyboardInterrupt, EOFError):
                print("\nGame aborted.")
                break

    @staticmethod
    def rps():
        print("\n=== Rock Paper Scissors ===")
        options = ["rock", "paper", "scissors"]
        wins = losses = 0
        while True:
            user = input("rock / paper / scissors (or 'quit'): ").strip().lower()
            if user in ("quit", "exit", "q"):
                break
            if user not in options:
                print("Invalid choice.")
                continue
            comp = random.choice(options)
            print(f"Computer: {comp}")
            if user == comp:
                print("Draw!")
            elif (user == "rock" and comp == "scissors") or \
                 (user == "paper" and comp == "rock") or \
                 (user == "scissors" and comp == "paper"):
                print("You win!")
                wins += 1
            else:
                print("You lose!")
                losses += 1
            print(f"Score → You: {wins}  Computer: {losses}\n")

    @staticmethod
    def hangman():
        words = ["python", "linux", "kernel", "terminal", "filesystem",
                 "process", "memory", "network", "compiler", "virtual",
                 "simulation", "hangman", "windows", "hybrid"]
        word = random.choice(words)
        guessed = set()
        lives = 7
        print("\n=== Hangman ===")
        while lives > 0:
            display = " ".join(c if c in guessed else "_" for c in word)
            print(f"\nWord: {display}")
            print(f"Lives: {lives}  Guessed: {' '.join(sorted(guessed))}")
            if all(c in guessed for c in word):
                print(f"\nYou won! The word was: {word}")
                return
            try:
                letter = input("Letter: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nAborted.")
                return
            if not letter or len(letter) != 1 or not letter.isalpha():
                print("Enter a single letter.")
                continue
            if letter in guessed:
                print("Already guessed.")
                continue
            guessed.add(letter)
            if letter not in word:
                lives -= 1
                print("Wrong!")
        print(f"\nGame over. The word was: {word}")

    @staticmethod
    def snake():
        print("\n=== Snake (simple text version) ===")
        print("Controls: w/a/s/d   |   q to quit\n")
        width, height = 20, 10
        snake = [(5, 5), (5, 4), (5, 3)]
        direction = (0, 1)
        food = (random.randint(0, height-1), random.randint(0, width-1))
        score = 0

        def render():
            os.system("cls" if os.name == "nt" else "clear")
            print(f"Score: {score}   (q = quit)")
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

        try:
            while True:
                render()
                move = input("Move (w/a/s/d): ").strip().lower()
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

                head_y, head_x = snake[0]
                new_head = ((head_y + direction[0]) % height,
                            (head_x + direction[1]) % width)

                if new_head in snake:
                    print("You hit yourself! Game over.")
                    break

                snake.insert(0, new_head)
                if new_head == food:
                    score += 10
                    food = (random.randint(0, height-1),
                            random.randint(0, width-1))
                else:
                    snake.pop()
        except (KeyboardInterrupt, EOFError):
            pass
        print(f"Final score: {score}")

    @staticmethod
    def dice():
        print("\n=== Dice Roller ===")
        while True:
            try:
                n = input("How many dice? (1-10, or q): ").strip()
                if n.lower() in ("q", "quit", "exit"):
                    break
                n = int(n)
                if not 1 <= n <= 10:
                    print("Choose 1-10")
                    continue
                results = [random.randint(1, 6) for _ in range(n)]
                print("Results:", results, "  Total:", sum(results))
            except ValueError:
                print("Enter a number.")
            except (KeyboardInterrupt, EOFError):
                break

    @staticmethod
    def fortune():
        fortunes = [
            "You will find a bug today. It will be your own.",
            "A clean /tmp is a happy /tmp.",
            "sudo make me a sandwich.",
            "There is no cloud, just someone else's computer.",
            "It's not a bug, it's an undocumented feature.",
            "rm -rf / is the ultimate trust exercise.",
            "The best code is no code at all.",
            "You will compile successfully on the first try. (Just kidding.)",
            "A watched process never exits.",
            "Kernel panic? More like kernel party.",
            "Your next commit will break production. Have fun.",
            "Windows and Linux can live in peace... inside Python.",
        ]
        print("\n" + random.choice(fortunes) + "\n")


# ============================================================
# Main OS / Shell
# ============================================================

class PythonOS:
    def __init__(self):
        self.fs = FileSystem()
        self.pm = ProcessManager()
        self.users = {
            "root":  {"password": "root",  "uid": 0,    "home": "/root"},
            "user":  {"password": "user",  "uid": 1000, "home": "/home/user"},
            "guest": {"password": "guest", "uid": 1001, "home": "/home/guest"},
        }
        self.current_user = "user"
        self.hostname = "python-os"
        self.env = {
            "PATH": "/bin:/usr/bin:/usr/local/bin:/usr/games",
            "HOME": "/home/user",
            "USER": "user",
            "SHELL": "/bin/bash",
            "TERM": "xterm-256color",
            "OS": "PythonOS_Hybrid",
        }
        self.history: List[str] = []
        self.aliases = {
            "ll": "ls -l",
            "la": "ls -la",
            "cls": "clear",
            "dir": "ls -l",
            "md": "mkdir",
            "rd": "rm -r",
            "del": "rm",
            "type": "cat",
            "ipconfig": "ifconfig",
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
        print("\n[  0.000000] Linux version 6.6.0-pythonos (Hybrid Edition)")
        time.sleep(0.15)
        print("[  0.412000] Command line: BOOT_IMAGE=/vmlinuz root=UUID=pythonos")
        time.sleep(0.2)
        print("[  1.102000] Loading hybrid Linux/Windows compatibility layer...")
        time.sleep(0.25)
        print("[  1.890000] Multi-user target reached.")
        print()
        print(self.fs.cat("/etc/motd"), end="")
        print(f"Python OS 3.1  {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}")
        print("Type 'help' or 'games'. Windows commands (dir, cls, ipconfig...) also work.\n")

        while self.running:
            try:
                line = input(self.prompt())
                self.execute(line)
            except KeyboardInterrupt:
                print("\n^C")
            except EOFError:
                print("\nlogout")
                break

    def execute(self, line: str):
        line = line.strip()
        if not line:
            return
        self.history.append(line)

        # Alias expansion
        first = line.split()[0]
        if first in self.aliases:
            line = self.aliases[first] + line[len(first):]

        try:
            tokens = shlex.split(line)
        except ValueError:
            print("syntax error")
            return
        if not tokens:
            return

        cmd = tokens[0].lower()
        args = tokens[1:]

        # ---- Exit / users ----
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

        # ---- File system ----
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
                print(f"ls: cannot access '{path}': No such file or directory")
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

        # ---- Process / system ----
        if cmd in ("ps", "tasklist"):
            print(f"{'PID':>6} {'USER':<8} {'%CPU':>5} {'%MEM':>5} COMMAND")
            for p in self.pm.list():
                print(f"{p.pid:>6} {p.user:<8} {p.cpu:>5.1f} {p.mem:>5.1f} {p.cmd}")
            return

        if cmd == "top":
            print("top - Python OS  (Ctrl+C to stop)")
            try:
                while True:
                    os.system("cls" if os.name == "nt" else "clear")
                    print(f"top - {datetime.now().strftime('%H:%M:%S')}  up {int(time.time()-self.boot_time)}s")
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
                    print(f"kill: ({pid}) - No such process or permission denied")
            except ValueError:
                print("kill: invalid argument")
            return

        if cmd == "free":
            print("              total        used        free")
            print("Mem:       16384000     8192000     8192000")
            print("Swap:             0           0           0")
            return

        if cmd == "df":
            print("Filesystem     1K-blocks    Used Available Use% Mounted on")
            print("/dev/pythonos   10485760  3145728   7340032  30% /")
            print("tmpfs            2097152        0   2097152   0% /tmp")
            return

        if cmd == "uptime":
            secs = int(time.time() - self.boot_time)
            print(f" {datetime.now().strftime('%H:%M:%S')} up {secs//60} min,  1 user,  load average: 0.42, 0.35, 0.28")
            return

        if cmd in ("neofetch", "screenfetch", "systeminfo"):
            print(textwrap.dedent(f"""
                {self.current_user}@{self.hostname}
                OS: Python OS 3.1 (Hybrid Linux/Windows)
                Host: Virtual Machine
                Kernel: 6.6.0-pythonos
                Uptime: {int(time.time()-self.boot_time)} s
                Shell: bash (simulated)
                CPU: Python Virtual CPU
                Memory: 8192 MiB / 16384 MiB
            """))
            return

        if cmd in ("uname", "ver"):
            if "-a" in args or cmd == "ver":
                print(f"PythonOS {self.hostname} 3.1.0-pythonos #1 SMP Hybrid x86_64 GNU/Linux")
            else:
                print("PythonOS")
            return

        if cmd == "hostname":
            print(self.hostname)
            return

        if cmd == "date":
            print(datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y"))
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

        # ---- Network ----
        if cmd in ("ifconfig", "ipconfig"):
            print("eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500")
            print("        inet 10.0.2.15  netmask 255.255.255.0")
            print("        ether 08:00:27:aa:bb:cc")
            return

        if cmd == "ping":
            host = args[0] if args else "127.0.0.1"
            print(f"PING {host} (93.184.216.34) 56(84) bytes of data.")
            for i in range(4):
                time.sleep(0.3)
                print(f"64 bytes from {host}: icmp_seq={i+1} ttl=54 time={random.uniform(8, 40):.1f} ms")
            print(f"--- {host} ping statistics ---")
            print("4 packets transmitted, 4 received, 0% packet loss")
            return

        if cmd in ("curl", "wget"):
            url = args[0] if args else "http://example.com"
            print(f"* Connected to {url}")
            time.sleep(0.3)
            print("HTTP/1.1 200 OK")
            print("<html><body><h1>Python OS simulated page</h1></body></html>")
            return

        if cmd == "apt":
            if not args:
                print("apt 2.7 (pythonos)")
                return
            sub = args[0]
            if sub == "update":
                print("Hit:1 http://archive.pythonos.org stable InRelease")
                print("Reading package lists... Done")
            elif sub == "upgrade":
                print("0 upgraded, 0 newly installed, 0 to remove.")
            elif sub == "install":
                for p in args[1:]:
                    print(f"Installing {p}... done (simulated)")
            elif sub == "search":
                print("pythonos-games/stable")
                print("pythonos-core/stable")
            else:
                print(f"E: Invalid operation {sub}")
            return

        # ---- Games ----
        if cmd == "games":
            print("""
Available games:
  guess     - Number guessing (1-100)
  rps       - Rock Paper Scissors
  hangman   - Hangman
  snake     - Simple text snake
  dice      - Dice roller
  fortune   - Random fortune
""")
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
            msg = " ".join(args) if args else "Moo from hybrid OS"
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
            print(f"--- Simple {cmd} --- (end with a line containing only . )")
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
Python OS 3.1 – Hybrid Linux + Windows command summary

Linux style : ls  cd  pwd  cat  mkdir  touch  rm  echo  ps  top  kill
Windows style: dir  cls  ipconfig  tasklist  systeminfo  ver  type  del  md  rd
System       : uname  hostname  date  free  df  uptime  neofetch  env
Users        : whoami  id  su  sudo
Network      : ifconfig / ipconfig  ping  curl
Packages     : apt update|upgrade|install|search
Games        : games  guess  rps  hangman  snake  dice  fortune
Fun          : cowsay  fortune
Other        : history  clear/cls  alias  help  exit
""")
            return

        print(f"{cmd}: command not found")


if __name__ == "__main__":
    PythonOS().boot()
