# Super Sweet Art — giveaway wheel

A weighted spin wheel for drawing giveaway winners in public, on camera.

**Live:** https://supersweetart.github.io/giveaway-wheel/

Built for the [@supersweetbyqiao](https://www.instagram.com/supersweetbyqiao/) 2K-followers
giveaway (September Sweet Mail subscriptions). One slice per entrant, sized by how many
entries that account earned — so the wheel is a picture of the odds, not just decoration.

## Opening state

The page opens with an **empty wheel** — a ghost of the rim waiting for a file. Nothing is
loaded until you choose:

- **Import a CSV** (top right, or click the empty wheel) — read a comment export and build
  the wheel from it.
- **Load the saved draw** — bring back the draw published in this repo, so the September
  record stays one click away.

Either way the names fly out of the hub and stick to their wedges as the wheel fills.

## Running the draw

| | |
|---|---|
| **Spin** | Click **Spin the wheel**, or press the **space bar** (cleaner on camera — no cursor in frame). Both stay disabled until a draw is loaded |
| **Length** | ~7 seconds. The pointer sound is synthesised as a rubber flapper hitting wooden pegs: a filtered noise slap plus a short damped tone, randomised per peg and fading as the wheel loses speed |
| **Landing** | The winning wedge lifts and brightens, the rest dim, the handle appears above the wheel and a postmark drops onto the stamp slot |
| **Next** | The winner leaves the pool; spin again |
| **Reset** | **Reset draw** puts everyone back — do a practice spin or two before you hit record |
| **Sound** | Toggle off if you are recording a voiceover |

The page respects `prefers-reduced-motion`: a short spin, no confetti, no ticking.

## How a winner is picked

1. Each entrant's weight is their number of qualifying entries.
2. A winner is drawn with the browser's cryptographic RNG (`crypto.getRandomValues`),
   weighted by those counts.
3. **Then** the wheel spins to that result.

That order is stated on the page itself. It is the honest description of what the code does —
the animation follows the draw rather than producing it. Landing position inside the winning
wedge is randomised too, so repeat winners never stop in the same spot.

## Loading a new draw

Two routes. Both apply the same entry rules, so they produce the same wheel.

### In the browser — for trying one out

**Import a CSV** in the top right. Drop in a raw comment export and the page reports which
columns it recognised, lets you set the rules, previews the resulting entrant and entry
counts, and then rebuilds the wheel with the names flying out of the hub and sticking to
their wedges.

The file is read locally and never uploaded. **Download redacted CSV** gives you the
cleaned data (and copies it to your clipboard, since some embedded viewers block downloads).
This route does not change what is deployed — reload and the wheel is empty again.

### On your machine — for publishing

```bash
python3 tools/publish-draw.py my_export.csv --push
```

That one command redacts the export, writes both files in `data/`, rewrites the wheel's
saved dataset and masthead inside `index.html`, then commits and pushes. GitHub Pages
rebuilds a minute later. Drop `--push` to review the changes first.

The saved dataset is what **Load the saved draw** restores — the page still opens empty.
Publishing a draw therefore changes the public record, not the opening screen.

Useful flags: `--winners 5`, `--host someaccount`, `--deadline "Closes 30 Sept 11:59 PM PT"`,
`--eyebrow` / `--subline` / `--slots` for the masthead wording, and `--keep-replies`,
`--no-tag-required`, `--allow-repeat-tags`, `--one-per-person` to change the entry rules.

**Why the web page can't publish for you.** A page on GitHub Pages is static — for it to
write to this repo it would have to carry a GitHub token, and this repo is public, so that
token would be handed to everyone who opens the page. The script does the same work with
the credentials already on your machine.

## This draw

- **267 entries** from **83 accounts**, commented 25–31 August 2026, all inside the
  31 August 11:59 PM PT deadline.
- Entry rule as published: *tag one friend in the comments; each comment is one entry;
  enter again by tagging a different friend.*
- **Replies excluded** — top-level comments only. That removed 5 rows.
- Nothing else was thrown out: no account tagged the same friend twice, tagged themselves,
  or tagged the host, so all 267 remaining comments counted.
- The top 10 entrants hold about 41.5% of the entries. That follows the published rule,
  and the wheel shows it plainly.

## Data

| File | What's in it |
|---|---|
| `data/entrants.csv` | One row per entrant: handle, entry count, share of the drum. This is what the wheel is built from. |
| `data/entries-redacted.csv` | One row per qualifying entry: type, handle, tag count, timestamp. |

Both are **redacted**. Comment text and the handles of *tagged* accounts are deliberately
absent — those people were named by someone else and never chose to be listed here. The raw
export stays local and is git-ignored (see `.gitignore`), so it never enters this history.

## Taking it down again

This repo is public because GitHub Pages needs it to be on a free account.

- **Unpublish the site, keep the code:** repo → Settings → Pages → *Unpublish site*.
- **Make everything private:** `gh repo edit supersweetart/giveaway-wheel --visibility private`
  (this also switches Pages off, unless the account is on a paid plan).
- Anything already pushed to a public repo may have been cloned, forked or cached by third
  parties. Going private hides the repo from here on; it cannot recall what was already
  public. That is why the raw export was never committed in the first place.

## Building on it

No build step and no dependencies; Google Fonts is the only external request. Everything —
markup, styles, wheel rendering, CSV parsing, audio synthesis — is in `index.html`.

The page chrome is sampled from supersweetstudio.ca — butter yellow `#F8D05C`, brand orange
`#E15E2E`, cream ground. The wheel's own slice colours are separate from that on purpose:
they have to stay far enough apart in hue to read as distinct wedges.

The Super Sweet Art mark sits in the hub whenever the wheel is empty. It is embedded as a
base64 data URI in `index.html`, so the page carries its own artwork wherever it is served;
`assets/logo.png` keeps the web-sized source (440px, cropped from the 3000px original).

[`ROADMAP.md`](ROADMAP.md) tracks what is shipped, what is next, and the decisions already
made — including what it would take for other artists to use this.
