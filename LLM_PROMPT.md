# Prompt: Fill `blank.json` from URL and contract address

Use this prompt with an LLM when you have a canonical URL and an on-chain contract address and want a draft builder entry.

---

## Role

You are filling a **Hyperliquid builder list** entry. You receive:

1. **`url`** — Official or best canonical site for the product or project (may be marketing site, app link, or docs).
2. **`contract_address`** — EVM contract address (for example `0x…`) that identifies this builder in the repo; filenames and asset paths use this exact string (checksummed or lowercase as provided).

## Goal

Produce **one JSON object** that matches the schema below, with **as many fields filled as you can justify** from public sources (the given URL, linked pages, social profiles, repos, branding). Use **`null`** for optional social fields you cannot verify. Omit optional top-level keys only if your tooling or schema allows; if you must output the full template, use **`null`** for unknown optional fields.

**Also**, search for **official brand assets** the user can download (see [Brand assets for the user](#brand-assets-for-the-user)) and list them **outside** the JSON block.

**Finding assets is often tricky**; if you cannot fetch or name a direct file, still give **actionable URLs** and where to look so the user can finish manually. **Do not** pretend a logo exists when you only found a favicon or generic page.

### How this repo uses your output (read this)

- **`categories.json`** in the repo is the **canonical** list of allowed category strings. Your **`category`** must match **exactly one** of those values (same set as in [Hard rules](#hard-rules)).
- **`name`** must be human-readable and **does not need to be unique** across builders; **`id`** must be **unique** (slug).
- **`socials`**: When included, use **only** the keys from **`blank.json`** (see [Hard rules](#hard-rules)); use **`null`** for platforms you cannot verify. Prefer outputting the **full** object with **`null`**s so the file matches the standard template.
- **`description`**: Short, factual copy (see [Hard rules](#hard-rules)); required.
- **`brand_color`** is optional; when present it must be a **valid hex** color (see [Hard rules](#hard-rules)).
- After the JSON file and assets exist on disk, **running `aggregate.py`** regenerates **`builders.json`**. An entry is **only included** in `builders.json` when validation passes **and** there is **`assets/{contract_address}/logo.svg`** *or* **`assets/{contract_address}/logo.png`** (see [Contract address usage](#contract-address-usage)).

## Hard rules

- **`id`**: Short **unique** slug for this builder (for example `phantom`, `hyperliquid_xyz`). Use **lowercase**, **`a-z`**, **`0-9`**, and **`_`** only unless the product’s canonical handle clearly uses another safe pattern. Must be stable and unlikely to collide with other builders.
- **`category`**: MUST be **exactly one** of the strings in **`categories.json`** (also listed here for convenience):

  `wallet` | `exchange` | `dex` | `copytrading` | `bot` | `tools` | `analytics`

  Pick the **single best fit** from the product’s stated category, features, and positioning. If ambiguous, choose the closest match and keep the description accurate.
- **`name`**: Human-readable product or project name (title case as the brand uses).
- **`description`**: One to three sentences: what it is, who it’s for, and how it relates to trading or Hyperliquid if applicable. Factual; no hype unless quoted from official copy.
- **`url`**: Use the **canonical HTTPS URL** provided, normalized (no tracking query params unless required). If the input URL redirects to a better canonical homepage, prefer the official stable URL.
- **`socials`**: Object with **only** these keys (each value is a **full HTTPS URL string** or **`null`**):

  `x`, `discord`, `telegram`, `linkedin`, `youtube`, `instagram`, `facebook`, `reddit`, `github`

  - Prefer **official** links from the site’s footer, “Community,” or verified profiles.
  - **Discord**: use invite URLs that look official; if only a generic `discord.gg` link exists, include it.
  - **X (Twitter)**: `https://x.com/...` or `https://twitter.com/...` if that’s what the brand lists.
  - **GitHub**: organization or main repo URL when that’s the official presence.
  - Use **`null`** for any platform you cannot verify; do **not** invent URLs.
- **`brand_color`**: Optional. If you find a **primary brand color** (style guides, logo SVG, meta theme-color, CSS variables), output as **`#RRGGBB`** (or valid 3-digit hex `#RGB`). If you cannot confirm a hex from sources, use **`null`** or omit per schema. Do **not** guess a random hex.

## Contract address usage

- Treat **`contract_address`** as the **on-chain identity** for this list entry: the data file is the **flat path** **`data/{contract_address}.json`** (one JSON file per contract, not a nested folder). Assets live under **`assets/{contract_address}/`**.
- **Local asset layout** (the human placing files in the repo should follow this):
  - **`assets/{contract_address}/logo.svg`** *or* **`assets/{contract_address}/logo.png`** — At least **one** of these is **required** for the builder to be picked up by the aggregator. Prefer **official vector** SVG when available; if there is **no** suitable SVG, an **official** PNG (for example from app stores, press kits, or the site’s icon set) is acceptable as `logo.png`. If neither can be justified, **do not** invent a path; **tell the user** in **`Brand assets (downloads)`** what is missing.
  - **`assets/{contract_address}/brand/`** — Any **other** official logo or brand files (wordmarks, alternate marks, PNGs from the pack, icons, guideline PDFs, etc.) go **inside this folder** when the user downloads them. If there are no extra assets worth keeping beyond the main logo (or nothing official exists), **leave this folder empty or omit it** and **tell the user** explicitly that no additional files were identified for `brand/`.
- You **do not** need to paste the address inside the JSON unless the list’s convention requires it; focus on filling **`url`** and metadata from the **project behind** that address.
- If research ties the URL to a different name than the contract label, prefer **branding from the official site** and keep **`id`** consistent with that brand.

## Brand assets for the user

After (or while) drafting the JSON, **actively search** for **official** downloadable branding: logo packs, press kits, “Brand,” “Media,” “Assets,” “Logos,” developer or design resources, and organization repos named like `brand-resources` or `media-kit`. Prefer links **from** the canonical site, official docs, or verified GitHub organizations—not reuploads on random CDNs unless they are clearly the vendor’s own asset host.

**Provide to the user** (in prose **below** the JSON, not inside it):

1. **Full HTTPS URLs** to each useful download: ZIP packs, direct SVG/PNG/PDF links, GitHub **Release** assets or **raw** files from official repos when that is the published distribution method.
2. A **short label** per link (for example “Logo pack (ZIP),” “Wordmark SVG,” “Color palette PDF”) so the user knows what they are fetching.
3. **Where files should land in the repo** — Map downloads to the layout in [Contract address usage](#contract-address-usage):
   - The **best official SVG** for the primary mark → instruct saving as **`assets/{contract_address}/logo.svg`** when such a file exists.
   - If **no** official SVG exists but an **official PNG** is suitable as the primary logo → instruct saving as **`assets/{contract_address}/logo.png`** (still satisfies the list).
   - If **neither** SVG nor PNG can be sourced reliably, **state clearly** that **`logo.svg` / `logo.png`** are still needed before the entry appears in **`builders.json`**.
   - **All other** official logos and brand collateral → instruct placing them under **`assets/{contract_address}/brand/`** (suggest sensible filenames). If **nothing** qualifies beyond the main logo (or no extras exist), **say explicitly** that the **`brand/`** folder can stay **empty** or **absent**.
4. **Always** call out gaps: if the user cannot obtain official assets, say **what is missing** (logo file for aggregation, extras for `brand/`, or both) so they are not left guessing.

If **no** official public asset page exists, say so briefly and optionally mention **fallbacks** (for example favicon or GitHub org avatar URL) only as *unofficial substitutes*, not as primary brand sources.

## Research strategy

1. Open or reason about the **given URL**: about page, docs, footer, blog, “Community,” “Careers,” press kit.
2. Follow **official** links only; avoid third-party aggregators as primary sources for name and description.
3. Infer **`category`** from product type (for example wallet app → `wallet`; on-chain aggregator → often `dex` or `tools` depending on emphasis).
4. Extract **social URLs** explicitly listed; do not fabricate.
5. For **`brand_color`**, only fill if you can point to a concrete source (for example CSS `theme-color`, brand PDF, or obvious primary color from official design assets).
6. For **brand assets**, follow [Brand assets for the user](#brand-assets-for-the-user): locate official packs or files and prepare the download list for the prose section after the JSON.

## Output format

Return **valid JSON first** (no markdown fences unless asked), with this structure:

```json
{
  "id": "string",
  "category": "one_of_the_allowed_values",
  "name": "string",
  "description": "string",
  "url": "https://...",
  "socials": {
    "x": null,
    "discord": null,
    "telegram": null,
    "linkedin": null,
    "youtube": null,
    "instagram": null,
    "facebook": null,
    "reddit": null,
    "github": null
  },
  "brand_color": null
}
```

**Then**, after the JSON, output a short section (plain text or markdown is fine) titled **`Brand assets (downloads)`** containing the labeled URLs, **mapping to `assets/{contract_address}/logo.svg` or `logo.png`, and `assets/{contract_address}/brand/`**, and **explicit notes when either is unavailable**, as described in [Brand assets for the user](#brand-assets-for-the-user) and [Contract address usage](#contract-address-usage).

### Maintainer checklist (for the human)

After writing the files locally:

1. Save **`data/{contract_address}.json`** with the JSON object above.
2. Add **`assets/{contract_address}/logo.svg`** and/or **`logo.png`** (and optional **`brand/`** files).
3. Run **`aggregate.py`** from the repo root to refresh **`builders.json`**.

## Quality bar

- Prefer **empty or `null`** over wrong URLs or wrong category.
- **`description`** must remain accurate if someone verifies against the **`url`**.
- If the URL is dead, wrong, or unrelated to the contract, state that briefly **outside the JSON** (or in an extra field only if the user allows); still output the best-effort JSON with **`null`** where needed.
- **Brand asset links** must be **actionable** (direct download or official landing page with a clear download), not dead ends or generic homepages unless that page is the only official distribution point.

## Inputs for this run

Contributors typically **edit this section** with the builder’s URL and contract address before pasting the prompt to an LLM (see the repo **README**).

- **URL:** INSERT_YOUR_URL_HERE
- **Contract address:** INSERT_YOUR_CONTRACT_ADDRESS_HERE

If the URL and the contract address are not provided (they still show as INSERT_YOUR_URL_HERE and INSERT_YOUR_CONTRACT_ADDRESS_HERE), ask the user to provide them before continuing further.
  