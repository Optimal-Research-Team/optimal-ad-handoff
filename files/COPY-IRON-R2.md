# IV iron round 2: seven test ads (Oct 19, 2026) · Book now since Oct 29

**Oct 29 (Peter): the call to action is "Book now", not the founding waitlist.** Every end card now reads "Book your IV iron visit." with a **Book now** button, the spoken "join the (founding) waitlist" lines are cut from IRV2, IRV3 and the talking heads, and IRM2, which used to sell the free waitlist, is now a what-you-get stack. Like round 1 (`COPY-IRON.md`), every ad has **one action: book**. These ads add the three Hormozi levers round 1 didn't pull:

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
| **IRM2** | Offer (what you get) | HyperFrames motion, silent | What you get, *start to finish*: an NP assessment, bloodwork, a monitored infusion, the 6–8 week recheck, line by line; end card (reworked Oct 29) | 13.4 s |
| **IRV2** | Likelihood + effort | Film, voiceover | Our **real** waiting lounge and reception, then bloodwork and the drip as still lifes; "No referral needed… an NP is on site for every infusion." | 18.7 s |
| **IRV3** | Time | Film, voiceover | Pills and an hourglass at home → the drip and bloodwork (still lifes) → our **real** waiting lounge; "a little at a time, often over months… as little as one visit" | 22.6 s |

Every ad comes in **Meta's three ratios: 1:1, 9:16 and 1.91:1**, full-bleed (Peter, Oct 19; 4:5 is retired). Every video is under 30 s. The films are voiceover-only (Maeve, the voice from the menopause film): no music. Captions are burned in, so muted autoplay still works.

Files (all in `out/r5/iron/`):
- **Statics:** `IR4–IR6` as `_1x1.png`, `_9x16.png` and `_1-91x1.png`.
- **Videos:** `IRM1`, `IRM2`, `IRV2` and `IRV3` as `_9x16.mp4`, `_1x1.mp4` and `_1-91x1.mp4`, each with a `_thumb.jpg`. Rebuild with `python3 gen/prep5.py`, then `python3 render.py --page iron2`.
- **Video sources:** `optimal-content-library/series/iron-motion` and `iron-irv1/2/3`, rendered with the shapes reel = 9:16, square = 1:1 and wide = 1.91:1.
  - Rebuild with `node scripts/render.mjs <series> --shapes reel,square,wide`.

## Setup (same campaign as round 1, Oct 29: Book now)

- **Objective and destination:** Sales → website conversions on `https://www.beoptimal.ca/services/iron`, optimized for **BookAppointmentSuccess**, with the URL parameters in `COPY-IRON.md`. The Instant Form is retired. The page still showed "Save my founding spot" on Oct 29: its buttons must open booking before launch.
- **CTA button:** Book now.
- **Meta AI label: off.** Never turn on Meta's AI label for any ad or post (Peter, Oct 28). The clinic itself is the **real** waiting lounge and reception, animated from photos: we never show a room that doesn't exist (Peter, Oct 19). **No people appear anywhere.**
- **Ad sets:** one, images and videos together (Jeremy's Oct 19 rule). At this budget, start with 4–5 distinct ideas (IR1, IR2, IRV1, IRT1) and add one or two from this round each week.
- **Budget:** as set by Peter in Slack (Oct 29). Adults 25–64, about 40 km around Barrie, broad targeting.
- **Placement asset customization:**
  - 1:1 for Feed
  - 9:16 for Stories and Reels
  - 1.91:1 for the right column, search and in-stream
- **Judge on:**
  - cost per booked consult
  - for video: 3-second hold rate and ThruPlay
- **After the test:** keep the winning lever, and make the next round variations of it.
- **Opening date:** the copy says IV iron opens in November. Once it's open, swap "opens this November" for "now open".

## Copy (Hormozi shape: hook → what you get and how fast → book)

Use the short primary text by default. The long one is for the second ad in each set.

### IR4 · "IV iron can refill iron stores in as little as one visit."
**Primary text (short):** IV iron can refill iron stores in as little as one monitored visit. It's coming to Optimal in Barrie this November, no referral needed. Book now.
**Primary text (long):** Iron pills refill iron stores a little at a time. IV iron skips the gut and can do it in as little as one monitored visit. It's coming to Optimal in Barrie: no referral needed, and a Nurse Practitioner reviews your bloodwork first. Book a consult with our NP now, virtual or in-clinic.
**Headline:** As little as one visit · **Description:** IV iron · No referral · Barrie

### IR5 · "IV iron in Barrie, with no referral needed."
**Primary text (short):** IV iron is coming to Barrie, and you don't need a referral. Book now and we'll order your bloodwork.
**Primary text (long):** IV iron is coming to Optimal in Barrie, and you don't need a referral. We order your bloodwork, a Nurse Practitioner assesses you first, and an NP is on site for every infusion. Book a consult with our NP now, virtual or in-clinic.
**Headline:** IV iron in Barrie, no referral · **Description:** NP-led · Book now

### IR6 · "Bloodwork before and after, so your iron is measured, not guessed."
**Primary text (short):** Every IV iron patient starts with bloodwork, and we recheck it at 6–8 weeks. Book now in Barrie, no referral needed.
**Primary text (long):** Every patient starts with bloodwork, and a Nurse Practitioner reviews it before anything else. If IV iron is right for you, we recheck your iron stores at 6–8 weeks, so they're measured, not guessed. IV iron is coming to Optimal in Barrie, no referral needed. Book a consult with our NP now, virtual or in-clinic.
**Headline:** Measured, not guessed · **Description:** IV iron · No referral · Barrie

### IRM1 · "A little at a time, or as little as one visit" (motion, 16 s)
**Primary text (short):** Iron pills work a little at a time. IV iron can refill iron stores in as little as one visit. Book now in Barrie, no referral needed.
**Primary text (long):** Iron pills refill iron stores a little at a time, often over months. IV iron skips the gut and can do it in as little as one monitored visit. Pills are the right first step for many people: your Nurse Practitioner decides which route fits, after bloodwork. No referral needed. Book a consult with our NP now, virtual or in-clinic.
**Headline:** As little as one visit · **Description:** IV iron · No referral · Barrie

### IRM2 · "What you get, start to finish." (motion, 13.4 s)
**Primary text (short):** Here's how IV iron at Optimal works, start to finish: an NP assessment, bloodwork ordered and reviewed for you, a monitored infusion with an NP on site, and a recheck at 6–8 weeks. Book now in Barrie, no referral needed.
**Primary text (long):** IV iron is coming to Optimal in Barrie, and here's how it works, start to finish. An NP assessment, virtual or in-clinic. Bloodwork ordered and reviewed for you. A monitored infusion with an NP on site the whole time. A recheck at 6–8 weeks to confirm your iron is back up. The iron itself is a pharmacy prescription, often covered by drug plans. No referral needed: book a consult with our NP now.
**Headline:** IV iron, start to finish · **Description:** No referral · Barrie

### IRV2 · "Our clinic" (film, 18.7 s)
**Primary text (short):** No referral needed, and a Nurse Practitioner on site for every infusion. IV iron is coming to Optimal in Barrie: book now.
**Primary text (long):** IV iron is coming to Optimal in Barrie. No referral needed: we order your bloodwork, a Nurse Practitioner assesses you first, and an NP is on site for every infusion. Book a consult with our NP now, virtual or in-clinic.
**Headline:** IV iron in Barrie, NP-led · **Description:** Book now · No referral

### IRV3 · "A little at a time" (film, 22.6 s)
**Primary text (short):** Iron pills work a little at a time. IV iron skips the gut and can refill iron stores in as little as one visit. Book now in Barrie.
**Primary text (long):** Iron pills refill iron stores a little at a time, often over months. IV iron skips the gut and can do it in as little as one visit. A Nurse Practitioner checks your bloodwork first, and again at 6–8 weeks. IV iron is coming to Optimal in Barrie, no referral needed. Book a consult with our NP now, virtual or in-clinic.
**Headline:** Skip the gut, not the bloodwork · **Description:** IV iron · No referral · Barrie

**Voiceover scripts (as recorded, Maeve):**
- **IRV2:** "IV iron is coming to Optimal, right here in Barrie. No referral needed. We order your bloodwork, a nurse practitioner assesses you first, and an NP is on site for every infusion." (Oct 29: the recorded last line, "Join the founding waitlist for first access.", is cut.)
- **IRV3:** "Iron pills refill your iron stores a little at a time, often over months. IV iron skips the gut, and can refill them in as little as one visit. A nurse practitioner checks your bloodwork first, and again at six to eight weeks. IV iron is coming to Barrie." (Oct 29: "Join the founding waitlist." is cut.)

## Guardrails used (unchanged from round 1)

- **Book now (Oct 29), and no price numbers.** The page shows "$495 founding / $595": that's fine on the page, but not in ads. A reference price for a service that has never sold at it is a Competition Act risk, and "final prices are set at launch".
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
  - IRM2's list (NP assessment, bloodwork ordered and reviewed, a monitored infusion with an NP on site, the 6–8 week recheck) is the page's own "Iron Restore package" list.
- **No people.** That's the content library's house rule for AI imagery, and it sidesteps the employees' objection to AI staff.
- **No invented rooms.** Clinic spaces come only from real photos or footage, and IR3 and IRV1 (round 1) were re-cut onto the real lounge. The AI imagery stays in home and neutral settings.

## IV iron talking heads: IRT1–IRT4 (Oct 20, 2026)

Cheryl (care coordinator) films four takes in our real lounge. Every ad comes in 1:1, 9:16 and 1.91:1 and runs 30 s or less, with burned-in captions, a hook and graphics: engraving cards above her head and numbered chips. There's no music.

- **Destination (Oct 29):** the IV iron page, with the **Book now** button, like the rest of the round. The spoken "Join the waitlist" is cut from every take (IRT4's step one is now "No referral needed", chip "Book directly, no referral"), and the end card says "Book your IV iron visit." Before Oct 29 these ran to the Instant Form and CTA **Sign up**. The takes also ended on "…at beoptimal.ca/iron", which stays cut.
- **November:** Peter recorded "opens in November", so IRT1 and IRT3 still say it out loud; the end card no longer does.
- **Clinical sign-off:** the Clinical Director has approved everything, which covers IRT2's "doesn't always look like anemia" (and IR2) (Oct 20).
- **Audio:** the DJI Mic Mini wasn't connected, so these were recorded on the iPhone's built-in mics. The voice is cleaned with DeepFilterNet (`tools/enhance_voice.py`), then EQ'd for presence.
- **Specs:** `ads/iron_pills_dont_work.py`, `iron_not_anemia.py`, `iron_three_things.py` and `iron_what_it_looks_like.py`.
- **Organic Instagram later:** each spec has an `ig` channel, a 9:16 cut ending on "Link in bio". IRT4's organic cut is the Full version, which keeps the spoken "Opening in November".

### IRT1 · "Iron pills don't work for everyone." (talking head, 29 s)
**Primary text (short):** Iron pills don't work for everyone. IV iron skips the gut, often in one monitored visit, and it opens in Barrie this November. Book now, no referral needed.
**Primary text (long):** Iron pills don't work for everyone: some people can't absorb enough through the gut, and others can't handle the side effects. IV iron skips the gut and goes straight into a vein, in a monitored 60–90 minute visit, and many people only need one. A Nurse Practitioner reviews your bloodwork first. IV iron opens at Optimal in Barrie this November. Book a consult with our NP now, virtual or in-clinic.
**Headline:** When iron pills don't work · **Description:** IV iron · Barrie · Opening November
**Instagram caption (organic, later):** Iron pills don't work for everyone. IV iron skips the gut, and many people only need one monitored visit. IV iron opens at Optimal in Barrie this November. Book through the link in our bio. #Barrie #BarrieOntario #ivtherapy #irondeficiency #womenshealth

### IRT2 · "Low iron doesn't always look like anemia." (talking head, 27 s)
**Primary text (short):** Low iron doesn't always show up as anemia: ferritin measures your iron stores. Our Nurse Practitioners can order the bloodwork, no referral needed. Book now.
**Primary text (long):** Low iron doesn't always show up as anemia. Hemoglobin can come back normal while iron stores, measured by ferritin, run low, and low ferritin is linked with fatigue, hair shedding, restless legs and getting winded on the stairs. When oral iron hasn't helped, IV iron may be an option. Our Nurse Practitioners order the bloodwork and walk you through it, no referral needed. IV iron opens at Optimal in Barrie this November: book a consult with our NP now.
**Headline:** Ferritin, checked properly · **Description:** No referral · Opening November
**Instagram caption (organic, later):** Low iron doesn't always show up as anemia. Hemoglobin can look normal while ferritin, your iron stores, runs low. Our Nurse Practitioners can order the bloodwork, no referral needed. IV iron opens at Optimal in Barrie this November. Book through the link in our bio. Educational content only. Not medical advice. #Barrie #BarrieOntario #ferritin #irondeficiency #womenshealth

### IRT3 · "Three things most people don't know about IV iron." (talking head, 27 s)
**Primary text (short):** Three things about IV iron: it's often a single visit, the iron is a pharmacy prescription often covered by drug plans, and you don't need a referral. It opens in Barrie this November. Book now.
**Primary text (long):** Three things most people don't know about IV iron. One: it's often a single visit, and some people need a second a week later. Two: the iron itself is a pharmacy prescription, often covered by drug plans. Three: you don't need a referral, because we order your bloodwork. IV iron opens at Optimal in Barrie this November. Book a consult with our NP now, virtual or in-clinic.
**Headline:** 3 things about IV iron · **Description:** Opening November · Barrie
**Instagram caption (organic, later):** Three things most people don't know about IV iron: it's often a single visit, the iron is a pharmacy prescription often covered by drug plans, and you don't need a referral. IV iron opens at Optimal in Barrie this November. Book through the link in our bio. #Barrie #BarrieOntario #ivtherapy #irondeficiency #preventivehealth

### IRT4 · "Here's what getting IV iron actually looks like." (talking head, 28 s)
**Primary text (short):** Here's what IV iron at Optimal looks like: book directly with no referral, an NP assesses you and orders your bloodwork, then one relaxed 60–90 minute infusion with an NP on site. Opening in Barrie this November. Book now.
**Primary text (long):** Here's what getting IV iron in Barrie actually looks like. One: book directly, no referral needed. Two: our Nurse Practitioner assesses you and orders your bloodwork. Three: if it's right for you, you fill the prescription at your pharmacy, often covered by drug plans. Four: you relax for a 60–90 minute infusion with an NP on site the whole time. Five: we recheck your bloodwork at 6–8 weeks. IV iron opens at Optimal this November. Book a consult with our NP now.
**Headline:** IV iron, step by step · **Description:** No referral · Opening November
**Instagram caption (organic, later):** Here's what getting IV iron in Barrie actually looks like, in five steps: book directly with no referral, an NP assessment and bloodwork, your prescription from the pharmacy, a relaxed 60–90 minute infusion with an NP on site, and a recheck at 6–8 weeks. Opening in November. Book through the link in our bio. #Barrie #BarrieOntario #ivtherapy #irondeficiency #womenshealth
