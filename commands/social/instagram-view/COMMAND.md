---
name: instagram-view
description: Fetch recent Instagram posts from public profiles and generate an HTML gallery.
parameters:
  - name: file
    description: Path to a text file listing Instagram usernames (one per line)
    required: true
  - name: output
    description: Folder to save the gallery HTML and images (defaults to the input file's folder)
    required: false
  - name: count
    description: "Number of posts to fetch per account (default: 12, fetches all available)"
    required: false
    default: "12"
---

# instagram-view

Fetches recent public Instagram posts for a list of accounts and generates an HTML gallery.
Uses Instagram's public web API — no login required.

## Input File Format

Create a simple text file with one Instagram username per line:

```
natgeo
nasa
9gag
bbcnews
davidgilmour
```

The command includes an example file at `example/my-fav-insta.txt`.

## Usage

```
> instagram-view --file my-accounts.txt
> instagram-view --file ./accounts.txt --output ./gallery
> instagram-view --file ./accounts.txt --count 5 --output ./gallery
```

## Output

- Copies shared assets (`viewer.js`, `style.css`) to the output folder
- Downloads profile pictures and post images to `images/` subfolder
- Generates `<filename>.<date>.view.html` in the output folder
- Open the HTML file in any browser to see an interactive gallery

## Gallery Features

- Per-account sections with profile info (avatar, name, followers)
- Image grid with captions, likes, and comment counts
- Lightbox viewer — click any image to view full-size
- Clickable account headers linking to Instagram profiles
- Dark theme matching Aynite's aesthetic
