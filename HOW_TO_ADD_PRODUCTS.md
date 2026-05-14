# How to Add a New Product to the Shop

This guide walks you through adding a new product to euclidiamath.com/shop using the `add_product.py` script in GitHub Codespaces. No coding knowledge needed.

---

## What You Need Before Starting

Before running the script, make sure you have:

- [ ] Your lesson bundle uploaded to **Payhip** (see Payhip setup below)
- [ ] Your **Payhip product link** (looks like `https://payhip.com/b/XXXXX`)
- [ ] Your **Canva thumbnail** exported as a PNG file
- [ ] The **CCSS standard** for the lesson (e.g. 8.EE.C.7b)

---

## Step 1 — Open GitHub Codespaces

1. Go to **github.com/emmanuelsimon123/euclidia-site**
2. Click the green **Code** button
3. Click the **Codespaces** tab
4. Click **Create codespace on main** (or open an existing one if you have one)
5. Wait about 30 seconds for it to load — you'll see a VS Code editor in your browser

---

## Step 2 — Upload Your Thumbnail

Before running the script, upload your Canva thumbnail into Codespaces:

1. In the left sidebar of Codespaces you'll see your file list
2. Right-click on the **images** folder
3. Click **Upload**
4. Select your Canva PNG thumbnail from your computer
5. It will appear inside the images folder

---

## Step 3 — Run the Script

1. In Codespaces, look for the **Terminal** at the bottom of the screen
2. If you don't see it, click **Terminal → New Terminal** in the top menu
3. Type this and press Enter:

```
python add_product.py
```

---

## Step 4 — Answer the Questions

The script will ask you these questions one by one. Just type your answer and press Enter.

| Question | Example Answer |
|----------|---------------|
| Product title | Solving Multi-Step Equations |
| CCSS Standard | 8.EE.C.7b |
| Grade range | 6-8 |
| Is this product free? | n |
| Your website price | $2.25 |
| TPT price | $3.25 on TPT |
| Payhip buy link | https://payhip.com/b/XXXXX |
| Short description | No-prep lesson bundle covering combining like terms and inverse operations. |
| Tags for filtering | 6-8 equations 8-ee |

---

## Step 5 — Select Your Thumbnail

After answering the questions the script will look for image files and show you a list like this:

```
Found these image files:
  1. images/solving-multi-step-equations.png
  2. images/scientific-notation.png

Select image (number, 0 for custom path, s to skip):
```

Type the number next to your thumbnail and press Enter.

If your thumbnail isn't listed type **0** and enter the full path manually, or type **s** to skip and add it later.

---

## Step 6 — Confirm and Publish

The script shows you a preview of your product:

```
==================================================
   Product Preview
==================================================
  Title:       Solving Multi-Step Equations
  Standard:    8.EE.C.7b
  Grade:       6-8
  Price:       $2.25
  Free:        No
  Thumbnail:   images/solving-multi-step-equations.png
  Tags:        6-8 equations 8-ee
```

If everything looks correct type **y** and press Enter.

The script will:
1. Update products.json with your new product
2. Copy the thumbnail to the right place
3. Push everything to GitHub automatically

You'll see this when it's done:

```
==================================================
   Product Added Successfully!
==================================================
✓ products.json updated
✓ Thumbnail uploaded
✓ Pushed to GitHub

Your product will be live at euclidiamath.com/shop
in about 60 seconds.
```

---

## Step 7 — Check the Shop

1. Wait about 60 seconds
2. Go to **euclidiamath.com/shop**
3. Your new product should appear automatically

---

## Setting Up Payhip (One Time Only)

Payhip handles your payments and file delivery. You only need to set this up once.

1. Go to **payhip.com** and create a free account using euclidiamath@gmail.com
2. Click **Add a Product → Digital Download**
3. Upload your lesson bundle as a ZIP file (lesson plan + worksheet + answer key)
4. Set your price (e.g. $2.25)
5. Add a title and short description
6. Click **Publish**
7. Copy the product URL — this is your Payhip link (e.g. `https://payhip.com/b/XXXXX`)

Payhip handles payments, receipts, and file delivery to the buyer automatically.

---

## Adding a Free Product

If the product is free (like the Laws of Exponents freebie):

1. Run `python add_product.py` as normal
2. When asked "Is this product free?" type **y**
3. The script skips the price fields
4. Enter your Payhip link — on Payhip set the price to $0 so it's a free download

---

## Updating an Existing Product

To change the price, description, or buy link of an existing product:

1. Open Codespaces
2. In the left sidebar find **products.json**
3. Edit the value you want to change directly in the file
4. In the Terminal run:

```
git add products.json
git commit -m "Update product: Your Product Name"
git push
```

Changes are live in about 60 seconds.

---

## Replacing a Thumbnail

1. Upload the new image to the `images/` folder in Codespaces
2. Open `products.json` and find your product
3. Update the `thumbnail` field with the new filename
4. In the Terminal run:

```
git add images/new-thumbnail.png products.json
git commit -m "Update thumbnail: Your Product Name"
git push
```

---

## Troubleshooting

**Script says "must be run from your euclidia-site folder"**
Make sure your terminal is in the right place. In Codespaces the terminal should already be in the correct folder. If not type:
```
cd /workspaces/euclidia-site
```

**Push failed**
Try running this in the terminal:
```
git push
```
If it asks for credentials, Codespaces handles this automatically — just wait a moment and try again.

**Product not showing on shop after 2 minutes**
Go to your GitHub repo and check the **Actions** tab. Look for a green checkmark meaning the deployment succeeded. If there's a red X click it to see the error and send it to euclidiamath@gmail.com for help.

**Thumbnail not showing on shop**
Make sure the filename in `products.json` exactly matches the filename in the `images/` folder — including capitalization.

---

## Quick Reference

| Task | Command |
|------|---------|
| Add new product | `python add_product.py` |
| Push manual changes | `git add . && git commit -m "message" && git push` |
| Open Codespaces | github.com → Code → Codespaces |
| Check if live | euclidiamath.com/shop |
| Contact support | euclidiamath@gmail.com |
