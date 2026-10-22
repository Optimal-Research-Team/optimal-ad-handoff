# Cycle & Hormone Care: Meta static ads CS1–CS6 (Oct 22, 2026)

Peter asked for Hormozi-style concepts, and said "simple is good". There are six statics, one sentence each. Each one pulls a single lever from the value equation (dream outcome × likelihood ÷ time × effort), and they all lead to the same free offer, the 3-minute Cycle Check. They run beside Cheryl's three videos (CV1–CV3, `VIDEO-ADS.md`).

| Ad | Lever | On the image | Art |
|---|---|---|---|
| CS1 | Problem: validation | Real symptoms deserve *real answers*. | **Real** consult room (exam table, NP desk), on cream |
| CS2 | Dream outcome + time | 12 weeks to *a plan you understand*. | The program's 5 stops, drawn from the landing page (Day 1 → Week 12) |
| CS3 | Problem, specific | Painful, heavy or missing periods deserve *a proper look*. | Engraving: uterus and ovaries (AI) |
| CS4 | Effort: no referral, local | PCOS, PMDD and endometriosis care in Barrie, *no referral needed*. | **Real** front desk under the Optimal logo wall |
| CS5 | Likelihood + cost | Bloodwork *timed to your cycle*, covered by OHIP. | Engraving: blood tubes and a calendar with two dates circled (AI) |
| CS6 | The one free offer | Start with a free *3‑minute Cycle Check*. | The Cycle Check's first screen, drawn from the landing page |

```
python3 gen/r9/art.py && python3 render.py --page cycle   # art -> assets/r9, ads -> out/r9/cycle/CS1–CS6 _1x1 _9x16 _1-91x1, QA
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
| Ads | CS1–CS6 + CV1–CV3 in one ad set; placement asset customization (1:1 Feed, 9:16 Stories/Reels, 1.91:1 right column) |
| CTA button | Learn more |
| AI label | **On** for CS3 and CS5 (AI engravings). **Off** for CS1 and CS4 (real photos) and CS2 and CS6 (drawn graphics) |

## Copy

### CS1 · "Real symptoms deserve real answers." (problem)
**Primary text:** Cycle and hormone symptoms are real, and they deserve real answers. Optimal's Cycle & Hormone Care program in Barrie starts with a free 3-minute Cycle Check, then a 60-minute visit with our nurse practitioner. No referral needed.
**Headline:** Real answers, here in Barrie · **Description:** Free 3-min Cycle Check · No referral

### CS2 · "12 weeks to a plan you understand." (dream outcome + time)
**Primary text:** In 12 weeks, find out what's driving cycle and hormone symptoms and leave with a plan you understand: a 60-minute nurse practitioner visit, bloodwork timed to your cycle, two InBody scans and two follow-ups. Start with the free 3-minute Cycle Check.
**Headline:** 12 weeks to a clear plan · **Description:** NP-led · Barrie · No referral

### CS3 · "Painful, heavy or missing periods deserve a proper look." (problem, specific)
**Primary text:** Painful, heavy or missing periods are common, but they deserve a proper look. Our nurse practitioner assesses pain, bleeding and iron, and arranges imaging or a referral when it's needed. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Periods deserve a proper look · **Description:** Free 3-min Cycle Check · Barrie

### CS4 · "PCOS, PMDD and endometriosis care in Barrie, no referral needed." (effort)
**Primary text:** Cycle & Hormone Care in Barrie for PCOS/PMOS, PMS/PMDD, endometriosis and adenomyosis, irregular periods, and hormonal acne or hair changes. The same nurse practitioner every visit. No referral needed. Start with the free 3-minute Cycle Check.
**Headline:** No referral needed · **Description:** PCOS · PMDD · Endometriosis · Barrie

### CS5 · "Bloodwork timed to your cycle, covered by OHIP." (likelihood + cost)
**Primary text:** Some hormone tests only make sense on certain days of the cycle, so we time the bloodwork to it. OHIP covers the bloodwork, and our nurse practitioner walks through every result with you in a 60-minute visit. Start with the free 3-minute Cycle Check.
**Headline:** Bloodwork timed to your cycle · **Description:** OHIP-covered · NP-reviewed · Barrie

### CS6 · "Start with a free 3-minute Cycle Check." (the free offer)
**Primary text:** You don't have to diagnose yourself before asking for help. The free 3-minute Cycle Check shows which program fits, then our care coordinator calls to talk it through. No referral needed.
**Headline:** Take the free Cycle Check · **Description:** 3 minutes · No referral · Barrie
