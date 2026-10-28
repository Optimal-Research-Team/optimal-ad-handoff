# Cycle & Hormone Care: Meta statics, round 4 (Oct 28, 2026)

**Oct 28 edits (Peter):** CA5 now says "menstrual cycle" for context; the carousel's card 1 names the symptoms (Hormozi: problem → answers); "pain with intimacy" replaces "pain with sex" in CE2 and CC5; never turn on Meta's AI label; the landing page is live, so nothing is on hold.

Peter's brief: "re-do static ads. Set 1: GENERAL ads that catch ALL potential symptoms of the various conditions this program addresses. Set 2: disease-state specific ads, e.g. PMOS (formerly PCOS), PMDD, endometriosis (do you think you have this?)".

**Set 1: general (catches every symptom the program covers).** Five single-image ads, plus a 6-card carousel that walks through one symptom cluster per card.

| Ad | Format | On the image | Art |
|---|---|---|---|
| CA1 | Single | Common cycle symptoms still deserve *a proper look*. | A wall of 12 symptom tags (drawn) |
| CA2 | Single | Irregular, heavy, painful or missing periods deserve *a proper look*. | Engraving: uterus and ovaries (AI) |
| CA3 | Single | Jawline acne, thinning hair or unwanted hair growth can be *hormonal*. | Engraving: hairbrush with shed hair, hand mirror (AI) |
| CA4 | Single | Mood swings, sugar crashes and exhaustion can share *a hormonal cause*. | Three linked symptoms (drawn) |
| CA5 | Single | A free 3-minute check of your menstrual cycle shows *which care fits*. | The Cycle Check's first screen on deep forest (drawn) |
| CC1–CC6 | Carousel, 1 ad | Hook → periods → skin & hair → mood & energy → pain → free Cycle Check | Progress bar on every card, "Swipe" on card 1 |

**Set 2: by condition.** Peter asked "do you think you have this?". The answer is the *signs*, so a woman can recognize herself, worded "…can be a sign of…". The ads never ask "Do you have…?", because Meta's personal-attributes policy rejects ads that assert or ask about a viewer's health condition.

| Ad | Condition | On the image | Art |
|---|---|---|---|
| CP1 | PMOS (formerly PCOS) | PMOS, formerly called PCOS, can mean irregular periods, acne and *unwanted hair*. | Engraving: ovary, whole and in cross-section (AI) |
| CP2 | PMOS | PMOS care that looks at cycles, skin, hair and *metabolism together*. | Four linked parts: cycles, skin, hair, metabolism (drawn) |
| CD1 | PMDD | Mood that crashes the week before a period and lifts once it starts can be *PMDD*. | Mood across one cycle, dipping the week before (drawn) |
| CD2 | PMDD | PMDD is more than bad PMS, *and there are options*. | A tracked month: period days and the week before (drawn) |
| CE1 | Endometriosis | Periods so painful they cancel plans can be a sign of *endometriosis*. | Engraving: uterus close-up, endometriosis spots (AI) |
| CE2 | Endometriosis / adenomyosis | Pelvic pain, heavy periods or pain with intimacy can point to *endometriosis or adenomyosis*. | Engraving: hot-water bottle in a knitted cover (AI) |

```
python3 gen/r9/art.py && python3 render.py --page cycle   # art -> assets/r9, ads -> out/r9/cycle/ + out/r9/cycle-carousel/, QA
```

**Retired:** rounds 1–3 (CS1–CS7, the 5-card CC). These are replaced by the sets above.

**Guardrails.**
- **Meta's personal-attributes policy:** no "you have…", no "your PMOS", no condition questions.
- **CNO:** no testimonials, and no comparisons with other providers.
- **Claims:** no outcome promises beyond the landing page's own words.
- **No drug names and no price.** The page shows $895; confirm whether HST applies first.
- **Naming:** PMOS is written "PMOS, formerly called PCOS" wherever it first appears, so people who know the old name find it.

## Setup

| | Cycle & Hormone Care |
|---|---|
| Campaign objective | Traffic → landing page views to start; switch to Leads once the Cycle Check completion fires as a conversion |
| Website URL | `https://www.beoptimal.ca/services/cycle-and-hormone-care` (live, checked Oct 28) |
| URL parameters | `utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}` |
| Ad sets | **Set 1 (general):** CA1–CA5 + the CC carousel + the videos CV1–CV3. **Set 2 (by condition):** CP, CD and CE. Each condition can get its own ad set once there's spend data. |
| Audience | Women 18–45, about 40 km around Barrie, broad (no interests) |
| Formats | Singles: placement asset customization (1:1 Feed, 9:16 Stories/Reels, 1.91:1 right column). Carousel: six 1:1 cards in order |
| CTA button | Learn more |
| Meta AI label | **Off for every ad.** Never turn it on (Peter, Oct 28) |

## Set 1 carousel (CC1 → CC6)

| Card | On the image | Card headline |
|---|---|---|
| CC1 | Irregular periods, acne and mood swings *deserve real answers*. | Cycle symptoms deserve answers |
| CC2 | Irregular, heavy or missing periods *are worth a proper look*. | Periods deserve a proper look |
| CC3 | Jawline acne, thinning hair or unwanted hair *can be hormonal*. | Skin and hair can be hormonal |
| CC4 | Mood swings, sugar crashes and exhaustion *can share a cause*. | Symptoms can share a cause |
| CC5 | Painful periods, pelvic pain or pain with intimacy *deserve answers*. | Pain deserves answers |
| CC6 | No referral needed: start with a free *3‑minute Cycle Check*. | Take the free 3-min Cycle Check |

**Carousel primary text:** Irregular periods, acne and mood swings deserve real answers. Swipe through the symptoms Optimal's Cycle & Hormone Care program in Barrie looks at, from irregular, heavy or painful periods to jawline acne, mood crashes and pelvic pain. Start with the free 3-minute Cycle Check. No referral needed.

## Singles: copy

### CA1 · "Common cycle symptoms still deserve a proper look." (Set 1 · general)
**Primary text:** Irregular, heavy or painful periods, pelvic pain, jawline acne, thinning or unwanted hair, mood that crashes before a period, sugar cravings and exhaustion are common, and they still deserve a proper look. Optimal's Cycle & Hormone Care program in Barrie looks at them together. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Common doesn't mean normal · **Description:** Free 3-min Cycle Check · Barrie

### CA2 · "Irregular, heavy, painful or missing periods deserve a proper look." (Set 1 · periods)
**Primary text:** Irregular, heavy, painful or missing periods deserve a proper look. Our nurse practitioner reviews the cycle, orders bloodwork timed to it (covered by OHIP), and arranges imaging or a referral when it's needed. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Periods deserve a proper look · **Description:** Free 3-min Cycle Check · Barrie

### CA3 · "Jawline acne, thinning hair or unwanted hair growth can be hormonal." (Set 1 · skin & hair)
**Primary text:** Jawline acne, thinning hair and unwanted hair growth can be driven by hormones such as androgens. Our nurse practitioner checks the hormones behind them, with bloodwork timed to the cycle, and builds a plan with you. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Skin and hair can be hormonal · **Description:** Free 3-min Cycle Check · Barrie

### CA4 · "Mood swings, sugar crashes and exhaustion can share a hormonal cause." (Set 1 · mood & energy)
**Primary text:** Mood swings, sugar crashes and exhaustion often get treated as separate problems. They can share a hormonal cause, from insulin and thyroid to iron and the cycle hormones, so we look at them together. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** Looked at together, in Barrie · **Description:** Cycle & Hormone Care · No referral

### CA5 · "A free 3-minute check of your menstrual cycle shows which care fits." (Set 1 · the free offer)
**Primary text:** You don't have to diagnose yourself before asking for help. The free 3-minute Cycle Check looks at your menstrual cycle and symptoms and shows which care fits, then our care coordinator calls to talk it through. No referral needed.
**Headline:** Take the free menstrual cycle check · **Description:** 3 minutes · No referral · Barrie

### CP1 · "PMOS, formerly called PCOS, can mean irregular periods, acne and unwanted hair." (Set 2 · PMOS)
**Primary text:** PMOS, formerly called PCOS, can show up as irregular or missed periods, acne, thinning hair or unwanted hair growth, and changes in weight or energy. Our nurse practitioner checks the hormones and metabolism behind it, with bloodwork timed to the cycle. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** PMOS (formerly PCOS) care in Barrie · **Description:** No referral · Free Cycle Check

### CP2 · "PMOS care that looks at cycles, skin, hair and metabolism together." (Set 2 · PMOS)
**Primary text:** PMOS care that looks at the whole picture with one nurse practitioner: your cycles, skin, hair and metabolism, with androgen, insulin and thyroid bloodwork and an InBody scan at the start and the end. A plan you understand in 12 weeks. Start with the free 3-minute Cycle Check.
**Headline:** PMOS care, the whole picture · **Description:** NP-led · Barrie · No referral

### CD1 · "Mood that crashes the week before a period and lifts once it starts can be PMDD." (Set 2 · PMDD)
**Primary text:** Mood that crashes in the week before a period and lifts once bleeding starts can be PMDD, a recognized condition that's more than bad PMS. Our nurse practitioner tracks the pattern with you over 2–3 cycles and talks through the options. Start with the free 3-minute Cycle Check. No referral needed.
**Headline:** When PMS is more than PMS · **Description:** Free 3-min Cycle Check · Barrie

### CD2 · "PMDD is more than bad PMS, and there are options." (Set 2 · PMDD)
**Primary text:** PMDD is more than bad PMS, and there are options. We confirm the pattern with daily tracking, then your nurse practitioner builds a plan with you, from sleep and stress support to hormonal options or medication when it helps. Start with the free 3-minute Cycle Check.
**Headline:** There are options for PMDD · **Description:** NP-led · Barrie · No referral

### CE1 · "Periods so painful they cancel plans can be a sign of endometriosis." (Set 2 · endometriosis)
**Primary text:** Periods so painful they cancel plans are common, but they can be a sign of endometriosis or adenomyosis, and they deserve a proper look. Our nurse practitioner assesses pain and bleeding, checks iron, and arranges imaging or a gynecology referral when it's needed. Start with the free 3-minute Cycle Check.
**Headline:** Painful periods deserve answers · **Description:** Free 3-min Cycle Check · Barrie

### CE2 · "Pelvic pain, heavy periods or pain with intimacy can point to endometriosis or adenomyosis." (Set 2 · endometriosis)
**Primary text:** Pelvic pain, heavy periods or pain with intimacy can point to endometriosis or adenomyosis. Getting it looked at starts here: a 60-minute nurse practitioner visit, bloodwork including iron, and imaging or a referral when it's needed. No referral needed to start. Take the free 3-minute Cycle Check.
**Headline:** Pelvic pain deserves a proper look · **Description:** No referral · Barrie
