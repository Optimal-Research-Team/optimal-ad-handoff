# IV iron round 2: seven test ads (Oct 19, 2026)

IV iron still isn't live. Like round 1 (`COPY-IRON.md`), every ad sells **one free offer: the founding waitlist**. These ads add the three Hormozi levers round 1 didn't pull:

- **Time:** as little as one visit.
- **Effort:** no referral needed, and we order your bloodwork.
- **Likelihood:** bloodwork before and after, with an NP on site.

The formats differ, so Meta treats each as a separate creative.

| Ad | Lever | Format | On screen | Length |
|---|---|---|---|---|
| **IR4** | Time | Static, calendar engraving | IV iron can refill iron stores in *as little as one visit*. | n/a |
| **IR5** | Effort | Static, lakeshore engraving | IV iron in Barrie, with *no referral needed*. | n/a |
| **IR6** | Likelihood | Static, blood-tube engraving on forest | Bloodwork before and after, so your iron is *measured, not guessed*. | n/a |
| **IRM1** | Time + effort | HyperFrames motion, silent | 12 weeks of daily pills fill a calendar, then collapse to one circled visit; three effort-cutters; end card | 16 s |
| **IRM2** | Offer | HyperFrames motion, silent | The founding waitlist is *free*, plus what founding members get, line by line; end card | 13.4 s |
| **IRV2** | Likelihood + effort | Film, voiceover | Our **real** waiting lounge and reception, then bloodwork and the drip as still lifes; "No referral needed… an NP is on site for every infusion." | 19.4 s |
| **IRV3** | Time | Film, voiceover | Pills and an hourglass at home → the drip and bloodwork (still lifes) → our **real** waiting lounge; "a little at a time, often over months… as little as one visit" | 22.6 s |

Every ad comes in **Meta's three ratios: 1:1, 9:16 and 1.91:1**, full-bleed (Peter, Oct 19; 4:5 is retired). Every video is under 30 s. The films are voiceover-only (Maeve, the voice from the menopause film): no music. Captions are burned in, so muted autoplay still works.

Files (all in `out/r5/iron/`):
- **Statics:** `IR4–IR6` as `_1x1.png`, `_9x16.png` and `_1-91x1.png`.
- **Videos:** `IRM1`, `IRM2`, `IRV2` and `IRV3` as `_9x16.mp4`, `_1x1.mp4` and `_1-91x1.mp4`, each with a `_thumb.jpg`. Rebuild with `python3 gen/prep5.py`, then `python3 render.py --page iron2`.
- **Video sources:** `optimal-content-library/series/iron-motion` and `iron-irv1/2/3`, rendered with the shapes reel = 9:16, square = 1:1 and wide = 1.91:1.
  - Rebuild with `node scripts/render.mjs <series> --shapes reel,square,wide`.

## Setup (same campaign as round 1)

- **Objective and destination:** Leads → the existing Instant Form, "Join the IV iron founding waitlist" (`COPY-IRON.md` has the form). Nothing on beoptimal.ca is live yet; `/iron` still serves the homepage.
- **CTA button:** Sign up.
- **AI label:** on for every ad. The engravings, still lifes and the motion of the clinic clips are AI-generated. The clinic itself is the **real** waiting lounge and reception, animated from photos: we never show a room that doesn't exist (Peter, Oct 19). **No people appear anywhere.**
- **Ad sets:** run two, so statics and video don't share one learning pool.
  - **Statics:** IR1, IR3, IR4, IR5, IR6. IR2 stays on hold for the Clinical Director's sign-off.
  - **Video:** IRV1, IRM1, IRM2, IRV2, IRV3.
- **Budget:** $15–20 a day each, for 7 days, hands off. Adults 25–64, about 40 km around Barrie, broad targeting.
- **Placement asset customization:**
  - 1:1 for Feed
  - 9:16 for Stories and Reels
  - 1.91:1 for the right column, search and in-stream
- **Judge on:**
  - cost per waitlist signup
  - the share of signups answering "Yes" on drug coverage
  - for video: 3-second hold rate and ThruPlay
- **After the test:** keep the winning lever, and make the next round variations of it.
- **Opening date:** once it's confirmed (the landing page says November 2026, still pending), add "Opening November 2026." after the first sentence of each primary text. It is the only urgency these ads may use.

## Copy (Hormozi shape: hook → what you get and how fast → the one free offer)

Use the short primary text by default. The long one is for the second ad in each set.

### IR4 · "IV iron can refill iron stores in as little as one visit."
**Primary text (short):** IV iron can refill iron stores in as little as one monitored visit. It's coming to Optimal in Barrie: join the founding waitlist free for first access.
**Primary text (long):** Iron pills refill iron stores a little at a time. IV iron skips the gut and can do it in as little as one monitored visit. It's coming to Optimal in Barrie: no referral needed, and a Nurse Practitioner reviews your bloodwork first. Join the founding waitlist free for first access, in signup order, and founding pricing.
**Headline:** As little as one visit · **Description:** Free founding waitlist · Barrie

### IR5 · "IV iron in Barrie, with no referral needed."
**Primary text (short):** IV iron is coming to Barrie, and you don't need a referral. Join the founding waitlist free for first access, in signup order.
**Primary text (long):** IV iron is coming to Optimal in Barrie, and you don't need a referral. We order your bloodwork, a Nurse Practitioner assesses you first, and an NP is on site for every infusion. Join the founding waitlist free: first access goes in signup order, with founding pricing on your first treatment.
**Headline:** IV iron in Barrie, no referral · **Description:** Free founding waitlist

### IR6 · "Bloodwork before and after, so your iron is measured, not guessed."
**Primary text (short):** Every IV iron patient starts with bloodwork, and we recheck it at 6–8 weeks. Join the free founding waitlist for first access in Barrie.
**Primary text (long):** Every patient starts with bloodwork, and a Nurse Practitioner reviews it before anything else. If IV iron is right for you, we recheck your iron stores at 6–8 weeks, so they're measured, not guessed. IV iron is coming to Optimal in Barrie, no referral needed. Join the founding waitlist free for first access and founding pricing.
**Headline:** Measured, not guessed · **Description:** IV iron · Barrie · Free waitlist

### IRM1 · "A little at a time, or as little as one visit" (motion, 16 s)
**Primary text (short):** Iron pills work a little at a time. IV iron can refill iron stores in as little as one visit, and the founding waitlist in Barrie is free to join.
**Primary text (long):** Iron pills refill iron stores a little at a time, often over months. IV iron skips the gut and can do it in as little as one monitored visit. Pills are the right first step for many people: your Nurse Practitioner decides which route fits, after bloodwork. No referral needed. Join the founding waitlist free for first access in Barrie.
**Headline:** As little as one visit · **Description:** Free founding waitlist · Barrie

### IRM2 · "The founding waitlist is free." (motion, 13.4 s)
**Primary text (short):** Founding members get first access to IV iron in Barrie, in signup order, plus founding pricing on their first treatment. Joining is free and takes about 10 seconds.
**Primary text (long):** IV iron is coming to Optimal in Barrie, and the founding waitlist is open. Founding members get first access, in signup order, and founding pricing on their first treatment. No referral needed: we order your bloodwork, and a Nurse Practitioner assesses you before anything else. Joining is free and takes about 10 seconds.
**Headline:** Founding spots go in signup order · **Description:** Free · No payment · Barrie

### IRV2 · "Our clinic" (film, 19.4 s)
**Primary text (short):** No referral needed, and a Nurse Practitioner on site for every infusion. IV iron is coming to Optimal in Barrie: join the founding waitlist free.
**Primary text (long):** IV iron is coming to Optimal in Barrie. No referral needed: we order your bloodwork, a Nurse Practitioner assesses you first, and an NP is on site for every infusion. Join the founding waitlist free for first access, in signup order, and founding pricing.
**Headline:** Founding waitlist now open · **Description:** IV iron · Barrie · No referral

### IRV3 · "A little at a time" (film, 22.6 s)
**Primary text (short):** Iron pills work a little at a time. IV iron skips the gut and can refill iron stores in as little as one visit. Join the free founding waitlist in Barrie.
**Primary text (long):** Iron pills refill iron stores a little at a time, often over months. IV iron skips the gut and can do it in as little as one visit. A Nurse Practitioner checks your bloodwork first, and again at 6–8 weeks. IV iron is coming to Optimal in Barrie, no referral needed. Join the founding waitlist free for first access and founding pricing.
**Headline:** Skip the gut, not the bloodwork · **Description:** Free founding waitlist

**Voiceover scripts (as recorded, Maeve):**
- **IRV2:** "IV iron is coming to Optimal, right here in Barrie. No referral needed. We order your bloodwork, a nurse practitioner assesses you first, and an NP is on site for every infusion. Join the founding waitlist for first access."
- **IRV3:** "Iron pills refill your iron stores a little at a time, often over months. IV iron skips the gut, and can refill them in as little as one visit. A nurse practitioner checks your bloodwork first, and again at six to eight weeks. IV iron is coming to Barrie. Join the founding waitlist."

## Guardrails used (unchanged from round 1)

- **Waitlist only, and no price numbers.** The design canvas now shows "$495 founding / $595": that's fine on a review page, but not in ads. A reference price for a service that has never sold at it is a Competition Act risk, and "final prices are set at launch".
- **Kept out, though the landing-page canvas uses them:**
  - "Exhausted by low iron?" (Meta's personal-attributes rule)
  - "1 in 4 women"
  - "energy back in 1–2 weeks" (a feel-better timeline)
  - drug brand names
  - the hospital-clinic comparison table (CNO: no comparisons)
- **Pills vs IV is neutral.** "A little at a time" is how oral iron works, not a knock on it. IRM1 says outright that pills are the right first step for many people and that the NP decides the route after bloodwork.
- **Accuracy checks:**
  - "As little as one visit": the landing page says 1–2 infusions, often just one.
  - The 6–8 week recheck and "NP on site for every infusion" both match the landing page and the referral form.
  - "Takes about 10 seconds": the Instant Form's prefilled name, email and phone.
  - "First access in signup order" and "founding pricing on your first treatment": both come from the waitlist terms on the landing page.
- **No people.** That's the content library's house rule for AI imagery, and it sidesteps the employees' objection to AI staff.
- **No invented rooms.** Clinic spaces come only from real photos or footage, and IR3 and IRV1 (round 1) were re-cut onto the real lounge. The AI imagery stays in home and neutral settings.
