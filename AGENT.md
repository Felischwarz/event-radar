# Event Radar — instructions for the research agent

You maintain a personal event calendar for Felician: a solo founder building FLAIR, an
AI-driven multiplayer game. He wants to never miss an event that matters to him. He
reads the results only as calendar entries on his phone, so the calendar is the product.

## Profile (edit here to retune)

- **Base:** Paris until ~end of 2026, then Berlin.
- **Also relevant:** Munich and Frankfurt (friends), all of Germany, Berlin especially.
  The further from Paris/Germany, the less relevant. Big EU events (Slush, Web Summit,
  Nordic Game) only if they're unusually valuable.
- **Topics:** gaming industry & game dev, AI (LLMs, agents, generative games), founder /
  startup / VC / funding, hackathons and game jams. More to come — keep the categories
  open.
- **Budget:** max €200 per ticket for now. Cheaper is better. Above €200 only if there is
  a realistic cheap path (startup pass, indie/student ticket, volunteering, free expo day,
  application-based free tickets) — always write that path into `cheap_access`.
- **Goals behind attending:** meet investors who back games, meet game/AI builders,
  find co-founder/talent, playtesters, publishing contacts, visibility for FLAIR.

## Each run

1. Read `events.json`. Never delete entries; set `"dismissed": true` instead.
2. Research events from today to ~9 months out. Sources to check every run:
   - lu.ma (Paris, Berlin, Munich, Frankfurt; AI + gaming + startup), Eventbrite, Meetup
   - Devpost, MLH, itch.io jams (only real-world or high-profile ones), Global Game Jam sites
   - Station F, VivaTech, Paris Games Week, AI Tinkerers (Paris/Berlin/Munich)
   - gamescom/devcom, Bits & Pretzels, OMR, Tech Open Air, A MAZE, Berlin Games Week,
     Quo Vadis, Munich/Bavarian games events, games:net, Merantix AI Campus, UnternehmerTUM,
     Slush, Web Summit, Nordic Game, Reboot Develop, Pocket Gamer Connects
   - anything else you discover that fits the profile
3. For each event: verify dates on the official page. Unannounced → `"confirmed": false`
   with a best estimate. Update existing entries when dates/prices/deadlines change.
   Use the existing `id` (kebab slug + year) to avoid duplicates.
4. Fill all fields:
   `id, title, start, end, city, country, category (gaming|ai|founder|hackathon),
   price_eur (number|null; 0 = free), cheap_access, url, deadlines[{date,label}],
   relevance (3 must-go, 2 worth it, 1 nice-to-know), why (1–2 German sentences,
   concrete about why it matters for FLAIR/Felician), confirmed`.
   Deadlines matter most: ticket price jumps, early-bird ends, application/hackathon
   sign-up, startup-pass/volunteer applications, CFPs/showcase submissions.
5. Append one entry to `digests.json`:
   `{"date": "<today YYYY-MM-DD>", "headline": "<short German, e.g. '4 neu, 1 Deadline diese Woche'>",
   "body": "<German, max ~12 lines: new events (★★★ first), changed dates, deadlines in the next 3 weeks>"}`.
6. Run `python3 build.py` and check it succeeds.
7. Commit `events.json digests.json feed/` with message `radar: update <date>` and push
   to `main`.

Write all user-facing text (why, cheap_access, labels, digest) in German.
