from utils.helpers import encode_item_icon

from models.db_group_builds import (
    dehydrate_build,
)


def process_comp_icons(comp_data):
    for role in comp_data.get("roles", []):
        # 1. Main Build
        build = role.get("build", {})
        if isinstance(build, dict):
            for slot, item in build.items():
                encode_item_icon(item)

        # 2. Swaps
        for swap in role.get("swaps", []):
            if isinstance(swap, dict):
                for slot, item in swap.items():
                    encode_item_icon(item)


def process_composition_dehydration(comp: dict):
    """Helper to recursively dehydrate all builds and swaps in a composition."""
    if "roles" not in comp or not isinstance(comp["roles"], list):
        return

    for role in comp["roles"]:
        # Dehydrate main build
        if "build" in role and isinstance(role["build"], dict):
            dehydrate_build(role["build"])

        # Dehydrate swaps
        swaps = role.get("swaps", [])
        if isinstance(swaps, list):
            for swap in swaps:
                dehydrate_build(swap)
        else:
            role["swaps"] = []
