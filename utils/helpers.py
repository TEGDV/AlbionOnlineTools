import os
import base64


def get_base64_image(file_path):
    # Check if path is a file and not a directory before opening
    if os.path.isfile(file_path):
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    return None


def encode_item_icon(item):
    """Helper to safely encode a single item icon."""
    if not isinstance(item, dict):
        return

    icon_val = item.get("icon")

    # CRITICAL: Skip if already base64 or doesn't look like a file path
    if not icon_val or icon_val.startswith("data:") or not icon_val.endswith(".png"):
        return

    # Extract clean filename
    filename = icon_val.split("/")[-1]
    path = os.path.join("static", "items", filename)

    # Encode
    b64 = get_base64_image(path)
    if b64:
        item["icon"] = f"data:image/png;base64,{b64}"
    else:
        # If file not found, you might want to keep the original or set to empty
        print(f"Warning: File not found at {path}")
