#!/usr/bin/env python3
"""
instagram-view — Fetch Instagram profile posts and generate HTML gallery.
Uses Instagram's public web API with rate limiting.
Always exits with code 0 for Aynite compatibility.
"""

import sys
import json
import os
import shutil
import re
import time
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import quote


# ── Argument parsing ──────────────────────────────────────────
def parse_args(argv):
    args = {}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith("--"):
            if "=" in arg:
                key, val = arg[2:].split("=", 1)
                args[key] = val
            else:
                key = arg[2:]
                if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                    i += 1
                    args[key] = argv[i]
                else:
                    args[key] = True
        i += 1
    return args


def usage():
    return {
        "status": "error",
        "error": "Missing required parameter: --file",
        "usage": {
            "description": "Fetch Instagram profile pictures and generate an HTML gallery. No login required.",
            "syntax": "> instagram-view --file <path/to/accounts.txt> [--count 12] [--output ./gallery]",
            "required": [
                {"name": "--file", "description": "Path to a text file listing Instagram usernames (one per line)"}
            ],
            "optional": [
                {"name": "--count", "description": "Number of recent posts to fetch per account (max available: ~12, default: 12)"},
                {"name": "--output", "description": "Output folder (default: same folder as input file)"}
            ],
            "input_format": {
                "description": "Create a simple text file with one Instagram username per line. Example:",
                "example": "natgeo\nnasa\n9gag\nbbcnews"
            }
        }
    }


# ── Instagram Web API (no login needed) ──────────────────────
INSTAGRAM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.instagram.com/",
    "X-IG-App-ID": "936619743392459",
    "X-Requested-With": "XMLHttpRequest",
}

DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
}


def api_request(url, retries=2):
    """Make a request to Instagram with proper headers and retry logic."""
    last_err = None
    for attempt in range(retries + 1):
        if attempt > 0:
            wait = attempt * 10  # Wait 10s, 20s between retries
            print(f"  Rate limited, waiting {wait}s before retry...", file=sys.stderr)
            time.sleep(wait)

        req = urllib.request.Request(url, headers=INSTAGRAM_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            last_err = e
            if e.code == 401:
                # Rate limited — retry
                if "wait a few minutes" in body:
                    if attempt < retries:
                        continue
                    return None, "Instagram rate limit hit. Try again in a few minutes."
                return None, f"Unauthorized (401). Instagram may be blocking this request."
            elif e.code == 404:
                return None, f"Profile not found (404)."
            else:
                return None, f"HTTP Error {e.code}: {e.reason}"
        except Exception as e:
            last_err = e
            if attempt < retries:
                continue
            return None, str(e)

    return None, str(last_err)


def fetch_profile(username):
    """Fetch profile data from Instagram's public web API."""
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={quote(username)}"
    data = api_request(url)
    if isinstance(data, tuple):
        return None, data[1]

    user = data.get("data", {}).get("user")
    if not user:
        return None, "Profile not found"

    # Extract user info
    profile_info = {
        "id": user.get("id"),
        "username": user.get("username"),
        "full_name": user.get("full_name"),
        "profile_pic_url": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
        "is_private": user.get("is_private", False),
        "is_verified": user.get("is_verified", False),
        "biography": user.get("biography", ""),
        "followers": user.get("edge_followed_by", {}).get("count", 0),
        "following": user.get("edge_follow", {}).get("count", 0),
    }

    # Extract posts
    posts = []
    edges = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
    for edge in edges:
        node = edge.get("node", {})
        img_url = node.get("display_url") or node.get("thumbnail_src", "")
        if not img_url:
            continue

        post = {
            "shortcode": node.get("shortcode", ""),
            "taken_at": node.get("taken_at_timestamp", 0),
            "likes": node.get("edge_liked_by", {}).get("count", 0),
            "comments": node.get("edge_media_to_comment", {}).get("count", 0),
            "is_video": node.get("is_video", False),
            "image_url": img_url,
            "caption": None,
        }

        caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
        if caption_edges:
            post["caption"] = caption_edges[0].get("node", {}).get("text", "")

        posts.append(post)

    return {"profile": profile_info, "posts": posts}, None


def download_image(url, filepath, retries=1):
    """Download an image to a local file with retry."""
    last_err = None
    for attempt in range(retries + 1):
        if attempt > 0:
            time.sleep(2)

        req = urllib.request.Request(url, headers=DOWNLOAD_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            return True
        except Exception as e:
            last_err = e
            continue
    return False


def sanitize_filename(name):
    """Sanitize a string for use in filenames."""
    return re.sub(r'[^\w\-]', '_', name)


# ── Asset copying ─────────────────────────────────────────────
def copy_assets(assets_dir, target_dir):
    """Copy asset files to target directory, skipping existing files."""
    copied = []
    for fname in os.listdir(assets_dir):
        if fname == 'template.html':
            continue
        src = os.path.join(assets_dir, fname)
        dst = os.path.join(target_dir, fname)
        if os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            copied.append(fname)
    return copied


# ── HTML generation ───────────────────────────────────────────
def generate_html(template_path, target_dir, input_filename, accounts_data):
    """Generate a view HTML file from the template."""
    with open(template_path) as f:
        html = f.read()

    viewer_data = {
        "title": f"Instagram Gallery — {input_filename}",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accounts": accounts_data,
    }

    html = html.replace("{{GALLERY_DATA}}", json.dumps(viewer_data, indent=2))
    html = html.replace("{{TITLE}}", f"Instagram Gallery — {input_filename}")

    today = datetime.now().strftime("%Y%m%d")
    base = os.path.splitext(input_filename)[0]
    out_name = f"{sanitize_filename(base)}.{today}.view.html"
    out_path = os.path.join(target_dir, out_name)
    with open(out_path, "w") as f:
        f.write(html)

    return out_path, out_name


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.get("help") or args.get("h"):
        print(json.dumps(usage(), indent=2))
        sys.exit(0)

    file_path = args.get("file", "")
    if not file_path:
        print(json.dumps(usage(), indent=2))
        sys.exit(0)

    file_path = os.path.expanduser(file_path)
    file_path = os.path.abspath(file_path)

    if not os.path.isfile(file_path):
        print(json.dumps({"status": "error", "error": f"File not found: {file_path}"}, indent=2))
        sys.exit(0)

    # Parse accounts from file
    try:
        with open(file_path) as f:
            usernames = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"Failed to read input file: {e}"}, indent=2))
        sys.exit(0)

    if not usernames:
        print(json.dumps({"status": "error", "error": "No usernames found in input file"}, indent=2))
        sys.exit(0)

    count = int(args.get("count", "12"))  # Default: fetch all available (max ~12 from API)
    output_dir = args.get("output", "") or os.path.dirname(file_path)
    output_dir = os.path.expanduser(output_dir)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(script_dir), "assets")

    if not os.path.isdir(assets_dir):
        print(json.dumps({"status": "error", "error": f"Assets directory not found: {assets_dir}"}, indent=2))
        sys.exit(0)

    # Fetch data for each account
    results = []
    errors = []
    for i, username in enumerate(usernames):
        if i > 0:
            # Rate limit: 1.5s delay between profile requests
            print(f"  (waiting 1.5s to avoid rate limiting...)", file=sys.stderr)
            time.sleep(1.5)

        print(f"Fetching @{username}...", file=sys.stderr)
        data, error = fetch_profile(username)
        if error:
            errors.append({"username": username, "error": error})
            print(f"  Error: {error}", file=sys.stderr)
            continue

        profile = data["profile"]
        posts = data["posts"][:count]

        # Download profile picture
        profile_pic_local = None
        if profile.get("profile_pic_url"):
            pp_name = f"{sanitize_filename(username)}_profile.jpg"
            pp_path = os.path.join(images_dir, pp_name)
            if download_image(profile["profile_pic_url"], pp_path, retries=1):
                profile_pic_local = f"images/{pp_name}"

        # Download post images
        downloaded_posts = []
        for j, post in enumerate(posts):
            img_name = f"{sanitize_filename(username)}_{j+1:02d}.jpg"
            img_path = os.path.join(images_dir, img_name)

            # Small delay between image downloads
            if j > 0:
                time.sleep(0.3)

            success = download_image(post["image_url"], img_path, retries=1)
            downloaded_posts.append({
                "shortcode": post["shortcode"],
                "taken_at": post["taken_at"],
                "likes": post["likes"],
                "comments": post["comments"],
                "is_video": post["is_video"],
                "caption": post["caption"],
                "local_path": f"images/{img_name}" if success else None,
                "remote_url": post["image_url"] if not success else None,
                "download_ok": success,
            })
            if success:
                print(f"  Downloaded post {j+1}", file=sys.stderr)
            else:
                print(f"  Failed to download post {j+1}", file=sys.stderr)

        results.append({
            "profile": {
                "username": profile["username"],
                "full_name": profile["full_name"],
                "is_verified": profile["is_verified"],
                "biography": profile.get("biography", ""),
                "followers": profile.get("followers", 0),
                "profile_pic_local": profile_pic_local,
            },
            "posts": downloaded_posts,
        })

    # Copy assets
    copied = copy_assets(assets_dir, output_dir)

    # Generate HTML
    input_basename = os.path.basename(file_path)
    template_path = os.path.join(assets_dir, "template.html")
    html_path, html_name = generate_html(template_path, output_dir, input_basename, results)

    result = {
        "status": "ok",
        "html_file": html_path,
        "accounts_fetched": len(results),
        "accounts_failed": len(errors),
        "errors": errors if errors else None,
        "assets_copied": copied,
        "images_saved_to": os.path.join(output_dir, "images"),
        "total_images": sum(len(a["posts"]) for a in results),
        "message": f"Fetched {len(results)}/{len(usernames)} accounts",
        "open_with": f"Open {html_name} in your browser to view the gallery."
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)
