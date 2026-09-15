#!/usr/bin/env python3
"""
Post-install compatibility patch for radicale_storage_decsync 2.1.0
with Radicale >= 3.6.0 (user_groups param added to BaseStorage.discover).
"""
import os
import glob


def patch_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # 1) Add user_groups=None to discover() signature
    old_tail = "contextlib.ExitStack())):"
    new_tail = "contextlib.ExitStack()), user_groups=None):"
    if old_tail in content:
        content = content.replace(old_tail, new_tail)
        print("  [PATCHED] discover() signature: +user_groups=None")
    else:
        print("  [SKIP]  discover() signature: pattern not found (already patched?)")

    # 2) Forward user_groups to super().discover()
    old_call = "super().discover(path, depth, child_context_manager)"
    new_call = "super().discover(path, depth, child_context_manager, user_groups or set())"
    if old_call in content:
        content = content.replace(old_call, new_call)
        print("  [PATCHED] super().discover(): forwards user_groups")
    else:
        print("  [SKIP]  super().discover() call: pattern not found")

    with open(filepath, "w") as f:
        f.write(content)


def find_plugin():
    patterns = [
        os.path.expanduser("~/.local/lib/python*/site-packages/radicale_storage_decsync/__init__.py"),
        "/usr/local/lib/python*/site-packages/radicale_storage_decsync/__init__.py",
        "/usr/lib/python*/site-packages/radicale_storage_decsync/__init__.py",
    ]
    for pat in patterns:
        for fp in glob.glob(pat):
            if os.path.isfile(fp):
                return fp
    # fallback via importlib
    try:
        import importlib.util
        spec = importlib.util.find_spec("radicale_storage_decsync")
        if spec and spec.origin:
            return spec.origin
    except Exception:
        pass
    return None


def main():
    fp = find_plugin()
    if fp is None:
        print("[WARN] radicale_storage_decsync not found – skipping patch.")
        return
    print(f"Patching: {fp}")
    patch_file(fp)
    print("[OK] Compatibility patch applied.")


if __name__ == "__main__":
    main()
