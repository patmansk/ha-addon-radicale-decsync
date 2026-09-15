#!/usr/bin/env python3
"""
Post-install compatibility patch for radicale_storage_decsync 2.1.0
with Radicale >= 3.6.0 (tested against 3.8.0).

Fixes:
  1. BaseStorage.discover() gained a 'user_groups' parameter (Radicale 3.6+).
  2. BaseCollection.upload() now returns Tuple[Item, Optional[Item]]
     instead of a bare Item (Radicale 3.6+).
  3. libdecsync uses pkg_resources.resource_filename - replaced with
     importlib.resources shim (safety net for Python 3.13 / setuptools>=81).

NOTE: class Storage(storage.Storage) is CORRECT - multifilesystem.Storage
      exists in Radicale 3.8.0 and provides all needed implementations.
"""
import os
import glob


def patch_decsync_plugin(filepath):
    """Patch radicale_storage_decsync/__init__.py"""
    with open(filepath, "r") as f:
        content = f.read()

    # --- 1) Add user_groups=None to discover() signature ---
    old_tail = "contextlib.ExitStack())):"
    new_tail = "contextlib.ExitStack()), user_groups=None):"
    if old_tail in content:
        content = content.replace(old_tail, new_tail)
        print("  [PATCHED] discover() signature: +user_groups=None")
    elif new_tail in content:
        print("  [SKIP]    discover() signature: already patched")
    else:
        print("  [WARN]    discover() signature: pattern not found")

    # --- 2) Forward user_groups to super().discover() ---
    old_call = "super().discover(path, depth, child_context_manager)"
    new_call = "super().discover(path, depth, child_context_manager, user_groups or set())"
    if old_call in content:
        content = content.replace(old_call, new_call)
        print("  [PATCHED] super().discover(): forwards user_groups")
    elif new_call in content:
        print("  [SKIP]    super().discover() call: already patched")
    else:
        print("  [WARN]    super().discover() call: pattern not found")

    # --- 3) Fix upload(): unpack Tuple[Item, Optional[Item]] return ---
    old_upload = "        item = super().upload(href, orig_item)"
    new_upload = "        item, old_item = super().upload(href, orig_item)"
    if old_upload in content:
        content = content.replace(old_upload, new_upload)
        print("  [PATCHED] upload(): unpack Tuple return value")
    elif new_upload in content:
        print("  [SKIP]    upload() unpack: already patched")
    else:
        print("  [WARN]    upload() unpack: pattern not found")

    # --- 4) Fix upload(): return Tuple instead of bare Item ---
    old_ret = '            self.decsync.set_entry(["resources", item.uid], None, item.serialize())\n        return item'
    new_ret = '            self.decsync.set_entry(["resources", item.uid], None, item.serialize())\n        return item, old_item'
    if old_ret in content:
        content = content.replace(old_ret, new_ret)
        print("  [PATCHED] upload(): return item, old_item (Tuple)")
    elif new_ret in content:
        print("  [SKIP]    upload() return: already patched")
    else:
        print("  [WARN]    upload() return: pattern not found")

    # --- 5) FIX: Revert incorrect BaseStorage patch (if previously applied) ---
    if "class Storage(BaseStorage):" in content:
        content = content.replace("class Storage(BaseStorage):", "class Storage(storage.Storage):")
        content = content.replace("\nfrom radicale.storage import BaseStorage", "")
        print("  [FIXED]   Reverted class Storage(BaseStorage) -> class Storage(storage.Storage)")
    elif "class Storage(storage.Storage):" in content:
        print("  [OK]      class Storage(storage.Storage): correct")
    else:
        print("  [WARN]    class Storage line not found - check manually")

    with open(filepath, "w") as f:
        f.write(content)


def patch_libdecsync(filepath):
    """Patch libdecsync/__init__.py - replace pkg_resources with importlib.resources"""
    with open(filepath, "r") as f:
        content = f.read()

    old_import = "from pkg_resources import resource_filename"
    if old_import in content:
        shim = (
            "from importlib.resources import files as _ir_files\n"
            "def resource_filename(package_name, resource_path):\n"
            "    return str(_ir_files(package_name).joinpath(resource_path))"
        )
        content = content.replace(old_import, shim)
        print("  [PATCHED] libdecsync: pkg_resources -> importlib.resources shim")
        with open(filepath, "w") as f:
            f.write(content)
    else:
        print("  [SKIP]    libdecsync: pkg_resources not found (already patched or not needed)")


def find_in_site_packages(module_name):
    """Find a module's __init__.py in site-packages."""
    patterns = [
        os.path.expanduser("~/.local/lib/python*/site-packages/" + module_name + "/__init__.py"),
        "/usr/local/lib/python*/site-packages/" + module_name + "/__init__.py",
        "/usr/lib/python*/site-packages/" + module_name + "/__init__.py",
    ]
    for pat in patterns:
        for fp in glob.glob(pat):
            if os.path.isfile(fp):
                return fp
    try:
        import importlib.util
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            return spec.origin
    except Exception:
        pass
    return None


def main():
    print("=== Radicale DecSync Compatibility Patch ===")
    print()

    fp = find_in_site_packages("radicale_storage_decsync")
    if fp is None:
        print("[FAIL] radicale_storage_decsync not found - cannot patch.")
        return 1
    print(f"[1/2] Patching: {fp}")
    patch_decsync_plugin(fp)

    fp2 = find_in_site_packages("libdecsync")
    if fp2 is None:
        print("[SKIP]  libdecsync not found - skipping.")
    else:
        print(f"[2/2] Patching: {fp2}")
        patch_libdecsync(fp2)

    print()
    try:
        import py_compile
        py_compile.compile(fp, doraise=True)
        if fp2:
            py_compile.compile(fp2, doraise=True)
        print("[OK]  Both files compile successfully.")
    except py_compile.PyCompileError as e:
        print(f"[FAIL] Compile check: {e}")
        return 1

    print()
    try:
        import radicale_storage_decsync
        print(f"[OK]  Import successful!")
        print(f"      Storage:    {radicale_storage_decsync.Storage}")
        for cls in radicale_storage_decsync.Storage.__mro__:
            print(f"        - {cls.__module__}.{cls.__name__}")
    except Exception as e:
        print(f"[FAIL] Import test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print()
    print("=== Patch complete - all checks passed. ===")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
