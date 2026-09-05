# Super Sweet Art — giveaway wheel

A weighted spin wheel for drawing giveaway winners in public, on camera.

**Live:** https://supersweetart.github.io/giveaway-wheel/

Built for the [@supersweetbyqiao](https://www.instagram.com/supersweetbyqiao/) 2K-followers
giveaway (September Sweet Mail subscriptions). One slice per entrant, sized by how many
entries that account earned — so the wheel is a picture of the odds, not just decoration.

## Running the draw

| | |
|---|---|
| **Spin** | Click **Spin the wheel**, or press the **space bar** (cleaner on camera — no cursor in frame) |
| **Length** | ~7 seconds, with a slowing tick and a chime on landing |
| **Landing** | The winning wedge lifts and brightens, the rest dim, the handle appears above the wheel and a postmark drops onto the stamp slot |
| **Next** | The winner leaves the pool; spin again. Three winners total |
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

## This draw

- **267 entries** from **83 accounts**, commented 25–31 August 2026, all inside the
  31 August 11:59 PM PT deadline.
- Entry rule as published: *tag one friend in the comments; each comment is one entry;
  enter again by tagging a different friend.*
- **Replies excluded** — top-level comments only.
- Nothing else was thrown out: no account tagged the same friend twice, tagged themselves,
  or tagged the host, so all 267 comments counted.
- The top 10 entrants hold about 41.5% of the entries. That follows the published rule,
  and the wheel shows it plainly.

## Data

| File | What's in it |
|---|---|
| `data/entrants.csv` | One row per entrant: handle, entry count, share of the drum. This is what the wheel is built from. |
| `data/entries-redacted.csv` | One row per comment: type, handle, tag count, timestamp. |

Both are **redacted**. Comment text and the handles of *tagged* accounts are deliberately
absent — those people were named by someone else and never chose to be listed here. The raw
export stays local and is git-ignored (see `.gitignore`).

## Reusing this for the next giveaway

Everything lives in `index.html`. Replace the `RAW` array near the top of the `<script>` —
`[["handle", entryCount], …]`, sorted highest first — and update the three numbers in the
masthead, the deadline sentence at the foot of the page, and `TOTAL_WINNERS` if you are
drawing a different number. No build step, no dependencies; Google Fonts is the only
external request.

## Taking it down again

This repo is public because GitHub Pages needs it to be on a free account.

- **Unpublish the site, keep the code:** repo → Settings → Pages → *Unpublish site*.
- **Make everything private:** `gh repo edit supersweetart/giveaway-wheel --visibility private`
  (this also switches Pages off, unless the account is on a paid plan).
- Anything already pushed to a public repo may have been cloned, forked or cached by third
  parties. Going private hides the repo from here on; it cannot recall what was already
  public. That is why the raw export was never committed in the first place.
