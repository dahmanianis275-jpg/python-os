# Python OS 3.4

Hybrid Linux + Windows style operating system written in pure Python.

**Features**
- Full file extension support
- Unlimited Python script execution
- Linux + Windows command compatibility
- Games
- Virtual filesystem, processes, users, networking simulation

---

## Run

```bash
git clone https://github.com/dahmanianis275-jpg/python-os.git
cd python-os
python python_os.py
```

---

## File Extensions

| Extension | Behavior |
|-----------|----------|
| `.py` / `.pyw` | Runs with full unlimited Python |
| `.txt` `.md` `.log` `.csv` `.cfg` `.ini` `.html` | Opens as text |
| `.json` | Pretty-prints |
| `.sh` `.bash` | Simulated shell |
| Unknown | Refused cleanly |

### Commands for extensions
```bash
assoc              # list all extensions
file <path>        # inspect a file
open <file>        # open by type
run <file>         # execute
python <file.py>   # run Python file
./script.py        # same as run
```

---

## Main Commands

**Linux style:** `ls` `cd` `pwd` `cat` `mkdir` `rm` `ps` `top` `kill` `apt` ...  
**Windows style:** `dir` `cls` `ipconfig` `tasklist` `systeminfo` `ver` `type` `del` `md` `rd`

**Games:** `games` `guess` `rps` `hangman` `snake` `dice` `fortune`

---

## License

MIT

**https://github.com/dahmanianis275-jpg/python-os**
