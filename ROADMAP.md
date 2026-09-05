# Roadmap

Working notes for turning the giveaway wheel from one artist's tool into something
other artists can pick up. Last updated 4 September 2026.

Sizes are rough: **S** ≈ an hour, **M** ≈ a day, **L** ≈ several days or a real design decision.

---

## Where it stands

Shipped and live at https://supersweetart.github.io/giveaway-wheel/

- [x] Weighted wheel — one slice per entrant, sized by entry count
- [x] Cryptographic RNG draw, weighted; wheel animates to the result
- [x] Winners leave the pool between spins
- [x] CSV import in the browser — column detection, adjustable entry rules, live preview
- [x] Build-in animation — names fly from the hub and stick to their wedges
- [x] Peg-and-flapper sound, synthesised, velocity-tracking
- [x] Empty opening state; **Load the saved draw** restores the published one
- [x] Redacted export (download, with host-save and clipboard fallbacks)
- [x] `tools/publish-draw.py` — redact, rewrite, commit, push in one command
- [x] Published to GitHub Pages; raw exports git-ignored

**One thing still unverified in a real browser:** after the build animation completes, the
Spin button should return to its enabled pink state. Headless Chrome couldn't test this
(its virtual clock starves animation frames). The equivalent code path was verified on the
reduced-motion route. Click **Load the saved draw** once and confirm.

---

## Next up

The three that stand between this and "another artist can use it".

- [ ] **Brand logo in the hub when empty** — **S**
      Replace the "waiting for / CSV" text with the artist's mark. Needs a decision on how
      the logo gets in: an image the artist uploads (stored where?), or an SVG in the repo.
      Simplest first cut: an `img` in the repo referenced by a config value.

- [ ] **Import by pasting a post link** — **L**
      Paste an Instagram / YouTube / TikTok URL instead of exporting a CSV. This is the
      single biggest usability win and the single hardest item: none of those platforms
      let a static page read a post's comments. It needs either an official API with
      credentials (so, a server), or the artist keeps using their existing export tool and
      the page just accepts more formats. **Worth scoping properly before starting** —
      see *Open questions* below.

- [ ] **Make the branding configurable** — **M**
      Right now the artist's name, the host handle default (`supersweetbyqiao`), the
      masthead wording and the palette are baked into `index.html`. Pull them into one
      config object at the top of the file, then a small settings panel that writes to
      `localStorage`. Until this exists, every other artist has to fork and hand-edit.

---

## Backlog

### Making it shareable

- [ ] **Palette per artist** — **M**. The candy palette is Super Sweet Art's. Let an artist
      pick an accent and derive the wheel colours from it, or choose from a few sets.
- [ ] **A "your first draw" walkthrough** — **S**. First-time visitors see an empty wheel
      and two buttons with no explanation of what file to bring.
- [ ] **Draw history** — **M**. Every publish overwrites the saved draw. Past draws should
      stay linkable, so an artist builds a public record over time.
- [ ] **Hosted, not forked** — **L**. Forking a repo is a big ask for most artists. A single
      hosted page where the config lives in the URL or in local storage would remove it.

### Input

- [ ] **More export formats** — **S each**. The parser already sniffs columns by name; adding
      known headers from other comment-export tools is cheap and useful today.
- [ ] **Normalise handles by case** — **S**. Both the page and the script key entrants on the
      raw handle (`counts[user]`), so `Artist` and `artist` would count as two people.
      Harmless for Instagram, which is lowercase-only — but YouTube handles are not, so this
      becomes a real bug the moment link-import lands. Fix it before that, not after.
- [ ] **Paste rows directly** — **S**. A textarea for pasted spreadsheet rows, for artists who
      count entries by hand.

### The wheel itself

- [ ] **Unlabelled slices** — **M**. Names only render on wedges wider than 3.4°. In the
      September draw that hid **51 of 83 entrants (61%)**, holding 61 of 267 entries — most
      of the people on the wheel cannot find themselves. Options: hover/tap to read a slice,
      a zoom as the wheel slows, or an outer ring of tick labels.
- [ ] **Very large draws** — **M**. Untested above 83 entrants. At several hundred, slices go
      below a pixel and the wheel stops meaning anything. Needs either a cap, grouping, or a
      different visual for the long tail.
- [ ] **Mobile layout** — **M**. The grid stacks, but it has not been checked on a phone.
      Artists may well record on one.
- [ ] **Multiple winners in one spin** — **S**. Some giveaways draw all winners at once.

### Trust and proof

- [ ] **Verifiable draws** — **L**, and the most interesting item here.
      `crypto.getRandomValues` is genuinely random but leaves no way for anyone to check the
      draw afterwards — viewers are asked to take the artist's word for it. A commit–reveal
      scheme would fix that: publish a hash of a seed before the draw, draw deterministically
      from the seed, reveal it after. Anyone could then replay the draw and get the same
      winners. Fits the transparency the rest of the project already aims at.
- [ ] **A result card to post** — **S**. One-click image or text: winners, their entry counts,
      total entries, date. Right now the artist screenshots it themselves.
- [ ] **Screen-reader announcement** — **S**. The wheel is canvas; the banner is `aria-live`,
      but the winner announcement has not actually been tested with a screen reader.

### Robustness

- [ ] **Sound on iOS Safari** — **S**. WebAudio unlocking differs there; untested.
- [ ] **Malformed CSV handling** — **S**. Missing columns are handled; ragged rows, wrong
      delimiters and huge files are not.
- [ ] **Tests for the entry rules** — **M**. The rules live twice (page and script) and were
      only checked by both agreeing on one export. A shared fixture set would keep them
      honest as rules get added.

---

## Open questions

- **Link import — is a server acceptable?** A static page cannot read comments from
  Instagram or YouTube. Every real version of this needs credentials, which means a backend,
  which means hosting, secrets and a privacy story. If the answer is no, the honest version
  of this feature is "accept more export formats", not "paste a link".
- **Where do other artists' draws live?** If the tool stays a static page, each artist forks
  it and owns their data. If it becomes hosted, someone is storing other people's entrant
  lists — a real responsibility, not a technical detail.
- **Should the raw comment text ever be shown?** Currently never published, deliberately.
  Some artists may want to display the winning comment. That would put third-party handles
  back on a public page.

---

## Decisions already made

Kept here so they don't get re-argued.

- **Static page, no backend.** Nothing to run, nothing to pay for, nothing to breach.
- **The page never publishes to GitHub.** It would have to carry a write token, and the repo
  is public. `tools/publish-draw.py` does it locally instead.
- **Raw exports are never committed.** They contain comment text and the handles of tagged
  third parties who never opted in. `.gitignore` blocks them, so they stay out of history.
- **The RNG draws first, the wheel animates second.** Stated on the page. The alternative —
  pretending the animation decides — would be a lie about what the code does.
- **The page opens empty.** It reads as a tool rather than a fixed exhibit. The published
  draw stays one click away so the public record is not lost.
