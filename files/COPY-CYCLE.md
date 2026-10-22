# Cycle & Hormone Care: Meta statics, 4 singles (CS3–CS6) + 1 carousel (CC1–CC5), Oct 22, 2026

There are three rounds, all on Oct 22:
- **Round 1:** six one-sentence singles, one Hormozi lever each.
- **Round 2:** the program badge, two dark frames, a quote poster.
- **Round 3:** Peter said "CS1, CS2, CS6, CS7 literally don't make sense in isolation". They were written as one funnel sequence and shipped as singles. Now the lines that lean on each other are **one 5-card carousel**, and **every single stands alone**: it says what it is, who provides it and why it matters, plus the CYCLE & HORMONE CARE badge.

**Singles (each makes sense on its own):**

| Ad | Lever | On the image | Art |
|---|---|---|---|
| CS3 | Problem, specific | Painful, heavy or missing periods deserve *a proper look*. | Engraving: uterus and ovaries (AI) |
| CS4 | Dream outcome + time | 12 weeks to *a plan you understand*. | The program in 3 big steps: Free Cycle Check → bloodwork + 60-min NP visit → your plan |
| CS5 | Likelihood + cost | Bloodwork *timed to your cycle*, covered by OHIP. | Engraving: blood tubes and a calendar with two dates circled (AI) |
| CS6 | Effort: no referral | Nurse practitioner care for PCOS, PMDD and endometriosis, *no referral needed*. | **Real** front desk under the Optimal logo wall |

**Carousel CC1 → CC5 (one ad, swipe order, 1:1 cards).** The order runs hook → problem → mechanism → outcome → offer:

| Card | On the image | Card headline |
|---|---|---|
| CC1 | “It's just part of being a woman.” *Not always.* | Common isn't the same as normal |
| CC2 | Acne, irregular periods and sugar crashes *can be connected*. | Symptoms can share a cause |
| CC3 | So we look at them together, with bloodwork *timed to your cycle*. | Bloodwork timed to your cycle |
| CC4 | In 12 weeks, *a plan you understand*. | 12 weeks to a clear plan |
| CC5 | No referral needed: start with a free *3‑minute Cycle Check*. | Take the free 3-min Cycle Check |

**Carousel primary text:** “It's just part of being a woman.” Not always. Painful, heavy or irregular periods, acne, sugar crashes and mood that crashes before a period can be connected, and they deserve a proper look. Swipe to see how Optimal's Cycle & Hormone Care program in Barrie works, then start with the free 3-minute Cycle Check. No referral needed.

**Retired as singles:** CS1 (became CC1), CS2 (became CC2) and CS7 (became CC5).

```
python3 gen/r9/art.py && python3 render.py --page cycle   # art -> assets/r9, ads -> out/r9/cycle/CS3–CS6 + out/r9/cycle-carousel/CC1–CC5 _1x1 _9x16 _1-91x1, QA
```

**Guardrails.** These apply to the images and to the copy below.
- **Meta personal-attributes policy:** no "you have…", "your PCOS" or "Do you suffer from…".
- **CNO:** no testimonials, and no comparisons with other providers. The landing page's "standard referral clinics" table stays off the ads.
- **Claims:** no outcome promises beyond the landing page's own words, and no drug names.
- **Price:** none on the images. The page shows $895; confirm whether HST applies before any price goes in an ad.

## Setup

| | Cycle & Hormone Care |
|---|---|
| Campaign objective | Traffic → landing page views to start; switch to Leads once the Cycle Check completion fires as a conversion |
| Website URL | `https://www.beoptimal.ca/services/cycle-and-hormone-care`. **It 404s on Oct 22** (Jeremy's preview branch only), so don't launch until it's live |
| URL parameters | `utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}` |
| Audience | Women 18–45, about 40 km around Barrie, broad (no interests) |
| Ads | Singles CS3–CS6 + the carousel CC + the videos CV1–CV3 in one ad set. Singles use placement asset customization (1:1 Feed, 9:16 Stories/Reels, 1.91:1 right column); the carousel is five 1:1 cards |
| CTA button | Learn more |
| AI label | **On** for CS3, CS5 and the carousel CC (card 3 is the AI tube engraving). **Off** for CS4 (drawn) and CS6 (real photo) |

## Singles: copy

### CS3 · "Painful, heavy or missing periods deserve a proper look." (problem, specific)
**Primary text:** Painful, heavy or missing periods are common, but they deserve a proper look. Our nurse practitioner assesses pain, bleeding and iron, and arranges imaging or a referral when it's needed. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Periods deserve a proper look · **Description:** Free 3-min Cycle Check · Barrie

### CS4 · "12 weeks to a plan you understand." (dream outcome + time)
**Primary text:** In 12 weeks, find out what's driving cycle and hormone symptoms and leave with a plan you understand: a 60-minute nurse practitioner visit, bloodwork timed to your cycle, two InBody scans and two follow-ups. Start with the free 3-minute Cycle Check.
**Headline:** 12 weeks to a clear plan · **Description:** NP-led · Barrie · No referral

### CS5 · "Bloodwork timed to your cycle, covered by OHIP." (likelihood + cost)
**Primary text:** Some hormone tests only make sense on certain days of the cycle, so we time the bloodwork to it. OHIP covers the bloodwork, and our nurse practitioner walks through every result with you in a 60-minute visit. Start with the free 3-minute Cycle Check.
**Headline:** Bloodwork timed to your cycle · **Description:** OHIP-covered · NP-reviewed · Barrie

### CS6 · "Nurse practitioner care for PCOS, PMDD and endometriosis, no referral needed." (effort)
**Primary text:** Cycle & Hormone Care in Barrie for PCOS/PMOS, PMS/PMDD, endometriosis and adenomyosis, irregular periods, and hormonal acne or hair changes. The same nurse practitioner every visit. No referral needed. Start with the free 3-minute Cycle Check.
**Headline:** No referral needed · **Description:** PCOS · PMDD · Endometriosis · Barrie

