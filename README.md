# The DIY VAWT Book

A complete, self-contained static website/manual that teaches hobbyists how to design, source parts for, build, wire, and maintain a small vertical axis wind turbine (VAWT).

## Live site (GitHub Pages)

Published URL (placeholder):

- https://keithevin722-cell.github.io/keithevinwindturbineai/

## Repository layout

- `/docs` - GitHub Pages-ready multi-page book website (no build step required)
- `/docs/chapters` - all chapter pages
- `/docs/assets/diagrams` - standalone SVG wiring diagrams
- `/docs/data/parts-list.csv` and `/docs/data/parts-list.json` - machine-readable bill of materials

## Enable GitHub Pages from `/docs`

If Pages is not enabled yet:

1. Open repository **Settings** → **Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select your branch and set folder to **`/docs`**.
4. Save and wait for publication.

## Optional: GitHub Actions Pages workflow

This repo includes `.github/workflows/pages.yml` to deploy static content from `/docs` using GitHub Actions Pages.

## Safety and legal disclaimer

This content is educational and not professional engineering, electrical, or legal advice. Always follow local electrical/building codes, obtain required permits, and verify designs for your site conditions. Wind turbines, batteries, and power electronics can cause severe injury, fire, and property damage if built or operated incorrectly.
