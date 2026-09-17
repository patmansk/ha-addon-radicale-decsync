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
  4. check_and_sanitize_items() requires max_vevent_rrule_occurrence (Radicale 3.8.0).
  5. Storage.create_collection() now returns a 3-tuple
     (collection, replaced_items, new_item_hrefs) (Radicale 3.8.0).
  6. resources_listener() wraps per-entry processing in try/except so a
     single malformed vCard/VEVENT does not abort the entire collection import.

NOTE: class Storage(storage.Storage) is CORRECT - multifilesystem.Storage
      exists in Radicale 3.8.0 and provides all needed implementations.
NOTE: The passthrough call `return super().create_collection(href, items, props)`
      in Storage.create_collection() is intentionally NOT patched - it must
      forward the 3-tuple to the Radicale core.
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
    if new_ret in content:
        print("  [SKIP]    upload() return: already patched")
    elif old_ret in content:
        content = content.replace(old_ret, new_ret)
        print("  [PATCHED] upload(): return item, old_item (Tuple)")
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

    # --- 6) Add logging import and logger (for Bug 3 error handling) ---
    if "import logging" not in content:
        content = content.replace("import vobject\n", "import vobject\nimport logging\n", 1)
        content = content.replace(
            "from libdecsync import Decsync\n",
            "from libdecsync import Decsync\n\n_logger = logging.getLogger(\"radicale_storage_decsync\")\n",
            1,
        )
        print("  [PATCHED] Added logging import + module logger")
    else:
        print("  [SKIP]    logging import: already present")

    # --- 7) BUG 1: check_and_sanitize_items() requires max_vevent_rrule_occurrence ---
    old_sanitize = "radicale_item.check_and_sanitize_items([vobject_item], tag=tag)"
    new_sanitize = "radicale_item.check_and_sanitize_items([vobject_item], tag=tag, max_vevent_rrule_occurrence=10000)"
    if old_sanitize in content:
        content = content.replace(old_sanitize, new_sanitize)
        print("  [PATCHED] check_and_sanitize_items(): +max_vevent_rrule_occurrence=10000")
    elif new_sanitize in content:
        print("  [SKIP]    check_and_sanitize_items(): already patched")
    else:
        print("  [WARN]    check_and_sanitize_items(): pattern not found")

    # --- 8) BUG 2A: discover() create_collection() now returns 3-tuple ---
    old_disc_create = "child = super().create_collection(child_path, props=props)"
    new_disc_create = "child = super().create_collection(child_path, props=props)[0]"
    if new_disc_create in content:
        print("  [SKIP]    discover(): create_collection() already unpacked")
    elif old_disc_create in content:
        content = content.replace(old_disc_create, new_disc_create)
        print("  [PATCHED] discover(): create_collection() -> [0] (unpack 3-tuple)")
    else:
        print("  [WARN]    discover(): create_collection() pattern not found")

    # --- 9) BUG 2B: create_collection() create_collection() now returns 3-tuple ---
    old_cc_create = "col = super().create_collection(path, None, props)"
    new_cc_create = "col = super().create_collection(path, None, props)[0]"
    if new_cc_create in content:
        print("  [SKIP]    create_collection(): already unpacked")
    elif old_cc_create in content:
        content = content.replace(old_cc_create, new_cc_create)
        print("  [PATCHED] create_collection(): super().create_collection(...) -> [0]")
    else:
        print("  [WARN]    create_collection(): pattern not found")

    # --- 10) BUG 3: Wrap resources_listener body in try/except ---
    old_listener_body = (
        "                uid = path[0]\n"
        "                href = extra.get_href(uid)\n"
        "                if value is None:\n"
        "                    if extra._get(href) is not None:\n"
        "                        extra.delete(href, update_decsync=False)\n"
        "                else:\n"
        "                    vobject_item = vobject.readOne(value)\n"
        "                    if sync_type == \"contacts\":\n"
        "                        tag = \"VADDRESSBOOK\"\n"
        "                    else:\n"
        "                        tag = \"VCALENDAR\"\n"
        "                    radicale_item.check_and_sanitize_items([vobject_item], tag=tag, max_vevent_rrule_occurrence=10000)\n"
        "                    item = radicale_item.Item(collection=extra, vobject_item=vobject_item, uid=uid)\n"
        "                    item.prepare()\n"
        "                    extra.upload(href, item, update_decsync=False)"
    )
    new_listener_body = (
        "                try:\n"
        "                    uid = path[0]\n"
        "                    href = extra.get_href(uid)\n"
        "                    if value is None:\n"
        "                        if extra._get(href) is not None:\n"
        "                            extra.delete(href, update_decsync=False)\n"
        "                    else:\n"
        "                        vobject_item = vobject.readOne(value)\n"
        "                        if sync_type == \"contacts\":\n"
        "                            tag = \"VADDRESSBOOK\"\n"
        "                        else:\n"
        "                            tag = \"VCALENDAR\"\n"
        "                        radicale_item.check_and_sanitize_items([vobject_item], tag=tag, max_vevent_rrule_occurrence=10000)\n"
        "                        item = radicale_item.Item(collection=extra, vobject_item=vobject_item, uid=uid)\n"
        "                        item.prepare()\n"
        "                        extra.upload(href, item, update_decsync=False)\n"
        "                except Exception as e:\n"
        "                    _logger.warning(\"DecSync: failed to process entry %%s: %%s\", path, e, exc_info=True)"
    )
    if old_listener_body in content:
        content = content.replace(old_listener_body, new_listener_body)
        print("  [PATCHED] resources_listener(): wrapped in try/except")
    elif new_listener_body in content:
        print("  [SKIP]    resources_listener(): already wrapped")
    else:
        # Fallback: try matching without the max_vevent_rrule_occurrence (in case patch 7 didn't apply)
        old_listener_body_v2 = old_listener_body.replace(
            "radicale_item.check_and_sanitize_items([vobject_item], tag=tag, max_vevent_rrule_occurrence=10000)",
            "radicale_item.check_and_sanitize_items([vobject_item], tag=tag)"
        )
        new_listener_body_v2 = new_listener_body.replace(
            "radicale_item.check_and_sanitize_items([vobject_item], tag=tag, max_vevent_rrule_occurrence=10000)",
            "radicale_item.check_and_sanitize_items([vobject_item], tag=tag, max_vevent_rrule_occurrence=10000)"
        )
        if old_listener_body_v2 in content:
            content = content.replace(old_listener_body_v2, new_listener_body_v2)
            print("  [PATCHED] resources_listener(): wrapped in try/except (variant B)")
        else:
            print("  [WARN]    resources_listener(): body pattern not found (check manually)")

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


def patch_radicale_utils(filepath):
    """Patch radicale/utils.py: fix vobject_supports_vcard4() version check.

    Radicale 3.8.0 checks major >= 1, but vobject never reached 1.0.0 on PyPI
    (latest is 0.9.9). vobject >= 0.9.6 supports vCard 4.0. Without this fix,
    PROPFIND responses only advertise version="3.0" for supported-address-data,
    causing CardDAV clients to reject vCard 4.0 contacts.
    """
    if filepath is None or not os.path.isfile(filepath):
        print("  [SKIP]    radicale/utils.py not found")
        return

    with open(filepath, "r") as f:
        content = f.read()

    old_func = (
        "def vobject_supports_vcard4() -> bool:\n"
        '    """Check if vobject supports vCard 4.0 (requires version >= 1.0.0)."""\n'
        "    try:\n"
        '        version = package_version("vobject")\n'
        '        parts = version.split(".")\n'
        "        major = int(parts[0])\n"
        "        return major >= 1\n"
        "    except Exception:\n"
        "        return False"
    )

    new_func = (
        "def vobject_supports_vcard4() -> bool:\n"
        '    """Check if vobject supports vCard 4.0 (requires version >= 0.9.6)."""\n'
        "    try:\n"
        '        version = package_version("vobject")\n'
        '        parts = [int(x) for x in version.split(".")[:3]]\n'
        "        while len(parts) < 3:\n"
        "            parts.append(0)\n"
        "        return parts >= [0, 9, 6]\n"
        "    except Exception:\n"
        "        return False"
    )

    if new_func in content:
        print("  [SKIP]    vobject_supports_vcard4(): already patched")
    elif old_func in content:
        content = content.replace(old_func, new_func)
        print("  [PATCHED] vobject_supports_vcard4(): major>=1 -> parts>=[0,9,6]")
    else:
        print("  [WARN]    vobject_supports_vcard4(): pattern not found (check manually)")

    with open(filepath, "w") as f:
        f.write(content)


def find_radicale_utils():
    """Find radicale/utils.py in site-packages."""
    patterns = [
        os.path.expanduser("~/.local/lib/python*/site-packages/radicale/utils.py"),
        "/usr/local/lib/python*/site-packages/radicale/utils.py",
        "/usr/lib/python*/site-packages/radicale/utils.py",
    ]
    for pat in patterns:
        for fp in glob.glob(pat):
            if os.path.isfile(fp):
                return fp
    try:
        import importlib.util
        spec = importlib.util.find_spec("radicale.utils")
        if spec and spec.origin:
            return spec.origin
    except Exception:
        pass
    return None


def main():
    print("=== Radicale DecSync Compatibility Patch ===")
    print()

    # --- 0) Patch radicale/utils.py vcard4 check ---
    fp_utils = find_radicale_utils()
    if fp_utils:
        print(f"[0] Patching radicale/utils.py (vcard4 fix)")
        patch_radicale_utils(fp_utils)
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
