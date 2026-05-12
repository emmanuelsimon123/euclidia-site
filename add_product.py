#!/usr/bin/env python3
"""
Euclidia — Add Product Script
==============================
Run this in GitHub Codespaces to add a new product to the shop.

Usage:
    python add_product.py

It will ask you questions, create the product file, copy your thumbnail,
and push everything to GitHub automatically.
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

# ── COLORS FOR TERMINAL OUTPUT ──
GREEN  = "\033[92m"
GOLD   = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def print_header():
    print(f"\n{GOLD}{BOLD}{'='*50}{RESET}")
    print(f"{GOLD}{BOLD}   EUCLIDIA — Add New Product{RESET}")
    print(f"{GOLD}{BOLD}{'='*50}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}→ {msg}{RESET}")

def slugify(text):
    """Convert title to a URL-friendly filename."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text

def ask(question, required=True, default=None):
    """Ask a question and return the answer."""
    if default:
        prompt = f"{BOLD}{question}{RESET} [{default}]: "
    else:
        prompt = f"{BOLD}{question}{RESET}: "
    
    while True:
        answer = input(prompt).strip()
        if not answer and default:
            return default
        if answer or not required:
            return answer
        print_error("This field is required. Please enter a value.")

def ask_yes_no(question, default="n"):
    """Ask a yes/no question."""
    prompt = f"{BOLD}{question}{RESET} (y/n) [{default}]: "
    while True:
        answer = input(prompt).strip().lower()
        if not answer:
            answer = default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print_error("Please enter y or n.")

def find_thumbnail():
    """
    Look for image files the user might want to use as thumbnail.
    Checks common locations.
    """
    # Look for images in current directory and common locations
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    found = []
    
    search_dirs = ['.', 'images', os.path.expanduser('~/Downloads')]
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if os.path.splitext(f)[1].lower() in image_extensions:
                    found.append(os.path.join(d, f))
    
    return found

def get_thumbnail(slug):
    """
    Handle thumbnail selection and copying.
    Returns the relative path to use in the markdown, or empty string.
    """
    print(f"\n{BOLD}Thumbnail Image{RESET}")
    print_info("Looking for image files...")
    
    found = find_thumbnail()
    
    if found:
        print(f"\nFound these image files:")
        for i, f in enumerate(found[:10], 1):
            print(f"  {i}. {f}")
        print(f"  0. Enter a different path")
        print(f"  s. Skip thumbnail for now")
        
        while True:
            choice = input(f"\n{BOLD}Select image (number, 0 for custom path, s to skip){RESET}: ").strip().lower()
            
            if choice == 's':
                return ''
            
            if choice == '0':
                custom = input(f"{BOLD}Enter full path to image{RESET}: ").strip()
                if os.path.exists(custom):
                    return copy_thumbnail(custom, slug)
                else:
                    print_error(f"File not found: {custom}")
                    continue
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(found[:10]):
                    return copy_thumbnail(found[idx], slug)
                else:
                    print_error("Invalid selection.")
            except ValueError:
                print_error("Please enter a number, 0, or s.")
    else:
        print_info("No image files found automatically.")
        custom = input(f"{BOLD}Enter path to thumbnail image (or press Enter to skip){RESET}: ").strip()
        if custom and os.path.exists(custom):
            return copy_thumbnail(custom, slug)
        elif custom:
            print_error(f"File not found: {custom}")
        return ''

def copy_thumbnail(src_path, slug):
    """Copy thumbnail to images folder with a clean name."""
    ext = os.path.splitext(src_path)[1].lower()
    dest_filename = f"{slug}{ext}"
    dest_path = os.path.join('images', dest_filename)
    
    # Make sure images folder exists
    os.makedirs('images', exist_ok=True)
    
    shutil.copy2(src_path, dest_path)
    print_success(f"Thumbnail copied to images/{dest_filename}")
    return f"images/{dest_filename}"

def create_product_file(data):
    """Create the markdown product file in _products folder."""
    os.makedirs('_products', exist_ok=True)
    
    slug = slugify(data['title'])
    filename = f"{slug}.md"
    filepath = os.path.join('_products', filename)
    
    # Build the markdown content
    is_free = 'true' if data['is_free'] else 'false'
    thumbnail = data.get('thumbnail', '')
    
    content = f"""---
title: "{data['title']}"
standard: "{data['standard']}"
grade: "{data['grade']}"
price: "{data['price']}"
tpt_price: "{data['tpt_price']}"
description: "{data['description']}"
gumroad_url: "{data['gumroad_url']}"
thumbnail: "{thumbnail}"
tags: "{data['tags']}"
is_free: {is_free}
date: "{datetime.now().strftime('%Y-%m-%d')}"
---
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Product file created: _products/{filename}")
    return filepath, slug

def git_push(files, commit_message):
    """Add files and push to GitHub."""
    try:
        # Configure git if needed (for Codespaces)
        subprocess.run(['git', 'config', '--global', 'user.email', 'euclidiamath@gmail.com'], 
                      capture_output=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'Euclidia'], 
                      capture_output=True)
        
        # Add the specific files
        for f in files:
            result = subprocess.run(['git', 'add', f], capture_output=True, text=True)
            if result.returncode != 0:
                print_error(f"Failed to add {f}: {result.stderr}")
                return False
        
        # Commit
        result = subprocess.run(
            ['git', 'commit', '-m', commit_message],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print_error(f"Commit failed: {result.stderr}")
            return False
        
        # Push
        print_info("Pushing to GitHub...")
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Push failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Git error: {e}")
        return False

def main():
    print_header()
    
    # Check we're in the right directory
    if not os.path.exists('index.html') and not os.path.exists('shop.html'):
        print_error("This script must be run from your euclidia-site folder.")
        print_info("Make sure you're in the root of your euclidia-site repository.")
        sys.exit(1)
    
    print(f"{BLUE}Answer the questions below to add a new product to your shop.{RESET}")
    print(f"{BLUE}Press Enter to skip optional fields.{RESET}\n")
    
    # Collect product details
    data = {}
    
    data['title'] = ask("Product title", required=True)
    data['standard'] = ask("CCSS Standard (e.g. 8.EE.C.7b)", required=True)
    data['grade'] = ask("Grade range (e.g. 6-8)", required=True)
    
    data['is_free'] = ask_yes_no("Is this product free?", default="n")
    
    if data['is_free']:
        data['price'] = "FREE"
        data['tpt_price'] = ""
        data['gumroad_url'] = ask("Gumroad download link", required=True)
    else:
        data['price'] = ask("Your website price (e.g. $2.25)", required=True)
        data['tpt_price'] = ask("TPT price (e.g. $3.25 on TPT)", required=False, default="")
        data['gumroad_url'] = ask("Gumroad buy link", required=True)
    
    data['description'] = ask("Short description (1-2 sentences)", required=True)
    data['tags'] = ask("Tags for filtering (e.g. 6-8 equations 8-ee)", required=False, default="")
    
    # Handle thumbnail
    slug = slugify(data['title'])
    data['thumbnail'] = get_thumbnail(slug)
    
    # Preview
    print(f"\n{GOLD}{BOLD}{'='*50}{RESET}")
    print(f"{GOLD}{BOLD}   Product Preview{RESET}")
    print(f"{GOLD}{BOLD}{'='*50}{RESET}")
    print(f"  Title:       {data['title']}")
    print(f"  Standard:    {data['standard']}")
    print(f"  Grade:       {data['grade']}")
    print(f"  Price:       {data['price']}")
    print(f"  Free:        {'Yes' if data['is_free'] else 'No'}")
    print(f"  Thumbnail:   {data['thumbnail'] or 'None (can add later)'}")
    print(f"  Tags:        {data['tags']}")
    print()
    
    if not ask_yes_no("Everything look correct? Add this product?", default="y"):
        print_info("Cancelled. No changes made.")
        sys.exit(0)
    
    # Create the product file
    print()
    filepath, slug = create_product_file(data)
    
    # Collect files to push
    files_to_push = [filepath]
    if data['thumbnail']:
        files_to_push.append(data['thumbnail'])
    
    # Push to GitHub
    commit_msg = f"Add product: {data['title']}"
    print_info("Pushing to GitHub...")
    
    if git_push(files_to_push, commit_msg):
        print()
        print(f"{GREEN}{BOLD}{'='*50}{RESET}")
        print(f"{GREEN}{BOLD}   Product Added Successfully!{RESET}")
        print(f"{GREEN}{BOLD}{'='*50}{RESET}")
        print(f"{GREEN}✓ Product file created{RESET}")
        if data['thumbnail']:
            print(f"{GREEN}✓ Thumbnail uploaded{RESET}")
        print(f"{GREEN}✓ Pushed to GitHub{RESET}")
        print(f"\n{GOLD}Your product will be live at euclidiamath.com/shop{RESET}")
        print(f"{GOLD}in about 60 seconds.{RESET}\n")
    else:
        print()
        print_error("Push to GitHub failed.")
        print_info("Your product file was created locally but not pushed.")
        print_info("Try running 'git push' manually in the terminal.")

if __name__ == '__main__':
    main()
