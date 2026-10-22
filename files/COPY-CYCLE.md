# Cycle & Hormone Care: Meta static ads CS1–CS7 (Oct 22, 2026)

Peter asked for Hormozi-style concepts and said "simple is good". Round 2 came the same day, after "iterate and think even more carefully". There are seven statics, one sentence each. Each one pulls a single lever, and they're ordered like a funnel (hooks first, the offer last). They all lead to the same free offer, the 3-minute Cycle Check, and they run beside Cheryl's three videos (CV1–CV3, `VIDEO-ADS.md`).

| Ad | Lever | On the image | Art |
|---|---|---|---|
| CS1 | Hook: the dismissal women hear | “It's just part of being a woman.” *Not always.* | Typographic poster on deep forest |
| CS2 | Curiosity: symptoms can share a cause | Acne, irregular periods and sugar crashes *can be connected*. | Three coloured nodes, linked |
| CS3 | Problem, specific | Painful, heavy or missing periods deserve *a proper look*. | Engraving: uterus and ovaries (AI) |
| CS4 | Dream outcome + time | 12 weeks to *a plan you understand*. | The program in 3 big steps: Day 1 → Then → Week 12 |
| CS5 | Likelihood + cost | Bloodwork *timed to your cycle*, covered by OHIP. | Engraving: blood tubes and a calendar with two dates circled (AI) |
| CS6 | Effort: no referral | PCOS, PMDD and endometriosis care, *no referral needed*. | **Real** front desk under the Optimal logo wall |
| CS7 | The one free offer | Start with a free *3‑minute Cycle Check*. | The Cycle Check's first screen, on deep forest |

**Round 2 changes.**
- **Program badge:** every ad now names the program with a CYCLE & HORMONE CARE pill beside the mark, as the videos do from frame 0.
- **Backgrounds:** two frames (CS1, CS7) are deep forest, so Meta doesn't read the set as one creative.
- **CS1:** the vague "Real symptoms deserve real answers." became the quote poster, the strongest hook from CV2.
- **New CS2:** a curiosity angle with specific symptoms.
- **CS4:** the 5-stop path is now 3 big steps, readable at feed size.
- **CS6:** the desk line dropped "in Barrie" (the logo wall already says local) and runs 3 lines instead of 4.
- **Retired:** CS1 v1 (the consult room).

```
python3 gen/r9/art.py && python3 render.py --page cycle   # art -> assets/r9, ads -> out/r9/cycle/CS1–CS7 _1x1 _9x16 _1-91x1, QA
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
| Ads | CS1–CS7 + CV1–CV3 in one ad set; placement asset customization (1:1 Feed, 9:16 Stories/Reels, 1.91:1 right column) |
| CTA button | Learn more |
| AI label | **On** for CS3 and CS5 (AI engravings). **Off** for CS6 (real photo) and CS1, CS2, CS4, CS7 (drawn graphics) |

## Copy

### CS1 · "It's just part of being a woman. Not always." (hook)
**Primary text:** "It's just part of being a woman." Painful, heavy or missing periods, mood that crashes before a period, acne and hair changes are common, but common doesn't mean they're something to push through. Optimal's Cycle & Hormone Care program in Barrie starts with a free 3-minute Cycle Check. No referral needed.
**Headline:** Common doesn't mean normal · **Description:** Free 3-min Cycle Check · Barrie

### CS2 · "Acne, irregular periods and sugar crashes can be connected." (curiosity)
**Primary text:** Acne along the jaw, irregular periods and sugar crashes often get treated as three separate problems. They can be connected, so androgens, insulin, thyroid and the cycle hormones are worth looking at together. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Looked at together, in Barrie · **Description:** Cycle & Hormone Care · No referral

### CS3 · "Painful, heavy or missing periods deserve a proper look." (problem, specific)
**Primary text:** Painful, heavy or missing periods are common, but they deserve a proper look. Our nurse practitioner assesses pain, bleeding and iron, and arranges imaging or a referral when it's needed. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Periods deserve a proper look · **Description:** Free 3-min Cycle Check · Barrie

### CS4 · "12 weeks to a plan you understand." (dream outcome + time)
**Primary text:** In 12 weeks, find out what's driving cycle and hormone symptoms and leave with a plan you understand: a 60-minute nurse practitioner visit, bloodwork timed to your cycle, two InBody scans and two follow-ups. Start with the free 3-minute Cycle Check.
**Headline:** 12 weeks to a clear plan · **Description:** NP-led · Barrie · No referral

### CS5 · "Bloodwork timed to your cycle, covered by OHIP." (likelihood + cost)
**Primary text:** Some hormone tests only make sense on certain days of the cycle, so we time the bloodwork to it. OHIP covers the bloodwork, and our nurse practitioner walks through every result with you in a 60-minute visit. Start with the free 3-minute Cycle Check.
**Headline:** Bloodwork timed to your cycle · **Description:** OHIP-covered · NP-reviewed · Barrie

### CS6 · "PCOS, PMDD and endometriosis care, no referral needed." (effort)
**Primary text:** Cycle & Hormone Care in Barrie for PCOS/PMOS, PMS/PMDD, endometriosis and adenomyosis, irregular periods, and hormonal acne or hair changes. The same nurse practitioner every visit. No referral needed. Start with the free 3-minute Cycle Check.
**Headline:** No referral needed · **Description:** PCOS · PMDD · Endometriosis · Barrie

### CS7 · "Start with a free 3-minute Cycle Check." (the free offer)
**Primary text:** You don't have to diagnose yourself before asking for help. The free 3-minute Cycle Check shows which program fits, then our care coordinator calls to talk it through. No referral needed.
**Headline:** Take the free Cycle Check · **Description:** 3 minutes · No referral · Barrie
