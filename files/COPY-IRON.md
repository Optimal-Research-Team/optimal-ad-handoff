# IV iron ads: three ideas for a pre-launch test (Oct 14, 2026)

IV iron isn't live yet, so these ads sell **only the founding waitlist**: there's nothing to book yet, and no price is set. There are three ideas, each a different format so Meta treats them as separate creatives. The third also has the one AI video.

| Ad | Idea | Format | On the image |
|---|---|---|---|
| IR1 | Pills not working | One big engraved IV bag of amber iron solution on cream (Oct 20 rework) | Iron pills not working? IV iron skips the gut. |
| IR2 | Hidden deficiency | The IV iron page's hero close-up, never extended (Oct 20) | Low iron doesn't always look like anemia. |
| ~~IR3~~ | **Removed Oct 20** (Peter: delete IR3) | | |
| IRV1 | The hero, animated | 6.5 s: the page hero close-up animated (she turns a page) + end card, silent (Oct 20) | IV iron is coming to Barrie this November. Then "Join the founding waitlist." |

```
python3 gen/r6/compose.py && python3 render.py --page iron   # art, then out/r4/iron/IR1–IR3 _1x1 + _9x16 + _1-91x1, QA
```

Backgrounds (Oct 20 rework, Peter: "IR2 image should be the hero from the website", "IR1 punchier and clearer", "IR3 much clearer", "a CLOSE-UP JUST LIKE THE HERO, no fake room background"):
- **IR1:** one big IV bag of amber iron solution, a copperplate engraving made with gpt_image_2_5 (2d97dd9d) from the page's own engravings. Only its paper is outpainted (16:9, d768af90). The 9:16 hangs the plate under a band of its own paper.
- **IR2:** the IV iron page's hero (`beoptimal.ca/images/iron/hero-infusion.jpg`, AI imagery) as the close-up only. The square is a crop. The 9:16 and 1.91:1 put the close-up on cream panels. Nothing is outpainted: an extended version invented a room (window, IV pole, rug) and a face, so it was rejected.
- **IR3:** the REAL front desk under the Optimal logo wall (`optimal-promo-videos/_project/ref/clinic_2`), crop only, on cream. The waiting-lounge version (Oct 19) read as confusing. The AI "infusion room" before that was pulled for good.
- Art script: `gen/r6/compose.py` → `assets/r4/IR1v_*`, `IR2h_*`, `IR3r_*`. The previous art stays in `assets/r4/IR1_*`, `IR2_*`, `IR3_*`.

IRV1 lives at `out/r4/iron/IRV1_{9x16,1x1,1-91x1}.mp4`, with thumbnails. It's rebuilt from `optimal-content-library/series/iron-irv1` (HyperFrames). Since Oct 20 its clip is the page hero animated (Kling 3.0 pro, ebbf538a, from a square crop of the hero: she turns a page, the IV line stays still, her face stays out of frame). The reel puts it under a cream band, the square runs it full bleed, and the wide sets it on the right. The lounge cut is retired.

## Setup

**There's no live landing page yet.** `beoptimal.ca/iv-iron` returns the 404 page. The waitlist page exists only as a review build ([iron-infusions-waitlist](https://optimal-research-team.github.io/iron-infusions-waitlist/), noindex, forms not wired). So the test runs on a **Meta Instant Form**: the waitlist form opens inside Facebook and Instagram, and nothing on the website is needed. When the page ships on beoptimal.ca with its forms wired, switch the destination to it and add the URL parameters below.

**Launch order (Oct 20):** IR1, IR2 and IRV1 can run (IR3 was removed Oct 20). The Clinical Director cleared every clinical claim on Oct 20, including IR2's "low iron without anemia". The page `beoptimal.ca/iron` (redirects to `/services/iron`) is live too, so a second ad set can test it as a website destination. Keep the Instant Form as the default.
- **Historical note:** IR2 was held until the Clinical Director signed off on "low iron without anemia". In Canada the infusion product's indication is iron-deficiency *anemia* in adults who can't tolerate oral iron or didn't respond to it. The landing-page handoff (Oct 14) already parks the same claim (the athletes card, the "Low iron, no anemia" referral option) for that sign-off, so the ad waits on the same call.

| | IV iron (pre-launch) |
|---|---|
| Campaign objective | Leads → Instant Form |
| Audience | Adults 25–64, about 40 km around Barrie, broad (no interests) |
| Ads | IR1, IR2 and IRV1 in one ad set; placement asset customization (1:1 Feed, 9:16 Stories/Reels, 1.91:1 right column) |
| CTA button | Sign up |
| AI label | **On** for IR1 (AI engraving), IR2 and IRV1 (AI hero image / its animation). **Off** for IR3 (a real photo of our front desk) |
| URL parameters (only once a website destination exists) | `utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}` |

**Instant Form ("Join the IV iron founding waitlist")**

1. **Intro:** IV iron is coming to Optimal in Barrie. Join the founding waitlist for first access, in signup order, and founding pricing. No referral needed.
2. **Questions:**
   - First name, email, phone number (prefilled).
   - One custom question: "Do you have private or workplace drug coverage?" (Yes / No / Not sure). The iron itself is a pharmacy prescription, so this sorts out likely buyers.
   - Don't ask health questions (ferritin, symptoms, diagnoses). Meta's lead-ad rules restrict them, and the NP covers this at assessment.
3. **Privacy policy:** https://www.beoptimal.ca/privacy
4. **Thank-you screen:** "You're on the list. We'll email you when booking opens. Questions? Call (437) 370-0291."

**Budget and reading the test:**
- Run $20–30 a day for 7 days and leave the ads alone.
- Judge on cost per waitlist signup and on the share of signups who answer "Yes" on drug coverage.
- Keep the winning idea, and replace the weakest with a new variation of the winner.
- Download the leads every few days. Founding access is in signup order.

## Copy

**Once the opening date is confirmed** (the landing page says November 2026, still pending), add "Opening November 2026." after the first sentence of each primary text. A real date is the only urgency these ads should use.

### IR1 · "Iron pills not working? IV iron skips the gut."
**Primary text:** Iron pills not working? IV iron skips the gut and goes straight into a vein, refilling iron stores in one or two monitored visits. It opens at Optimal in Barrie this November: no referral needed, and we order your bloodwork first. Join the founding waitlist free for first access and founding pricing.
**Headline:** Iron pills not working? · **Description:** IV iron · Opening November · Barrie

### IR2 · "Low iron doesn't always look like anemia." (cleared by the Clinical Director, Oct 20)
**Primary text:** Low iron doesn't always look like anemia. Hemoglobin can sit in range while iron stores, measured as ferritin, run low. IV iron opens at Optimal in Barrie this November, led by a Nurse Practitioner who reviews your bloodwork before anything else. No referral needed. Join the founding waitlist for first access and founding pricing.
**Headline:** Iron stores, checked properly · **Description:** Founding waitlist · Barrie

### ~~IR3~~ (removed Oct 20, Peter) · was "IV iron opens in Barrie this November: join the founding waitlist."
**Primary text:** IV iron opens at Optimal in Barrie this November. No referral needed: we order your bloodwork, a Nurse Practitioner assesses you first, and an NP is on site for every infusion. Join the founding waitlist free: first access goes in signup order, with founding pricing.
**Headline:** Opening November in Barrie · **Description:** Founding waitlist · Free to join

### IRV1 · "IV iron is coming to Barrie this November." (video)
**Primary text:** IV iron is coming to Optimal in Barrie this November: a calm, monitored infusion with a Nurse Practitioner on site, and no referral needed. Join the founding waitlist free for first access and founding pricing.
**Headline:** Join the founding waitlist · **Description:** IV iron · Barrie · November

## Guardrails used

- **Waitlist only.** No booking language, because the service isn't live.
- **No price numbers.** The founding rate is set at launch. There's no "regular $595" either: a reference price for a service that has never sold at that price is a Competition Act risk.
- **No drug brand names** (the iron is a separate prescription). No feel-better timelines. No "1 in 4 women".
- **Third person only.** No "Exhausted by low iron?" or "you have…" phrasing (Meta's personal-attributes policy).
- **No provider comparisons** (CNO): no drip bars, no other clinics. **Pills vs IV is described neutrally**, since pills are the right first step for many people. The NP decides whether IV iron fits, after bloodwork.
- **AI label on.** The engraving is AI-generated, and the lounge clip is animated from a real photo. Ads never show a clinic room that doesn't exist.
