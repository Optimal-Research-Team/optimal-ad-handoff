# Google Ads: Cycle & Hormone Care (Search), Oct 22, 2026

A build sheet for whoever on the team pushes this live.
- **Character limits:** every headline is ≤30 characters, every description ≤90, every callout and sitelink ≤25, and every sitelink line ≤35. All are checked by `gen/r9/check_google.py`.
- **Approach:** Hormozi-style and simple. Each ad group leads with the searcher's problem, makes the outcome concrete ("a plan you understand", "in 12 weeks"), cuts effort ("no referral", "free 3-minute Cycle Check") and adds proof of thoroughness ("bloodwork timed to your cycle", "same NP every visit").
- **Guardrails, same as the Meta set (`COPY-CYCLE.md`):** no drug names (Google restricts prescription drugs in ad text), no "specialist" or "cure", no testimonials, no provider comparisons, no outcome promises beyond the landing page.

## Before launch

1. **The landing page must be live.** `https://www.beoptimal.ca/services/cycle-and-hormone-care` showed "404 – Page Not Found" on Oct 22, because the page is only on Jeremy's preview branch. Google disapproves ads with broken final URLs.
2. **Conversion tracking.** Fire a Google Ads conversion (or a GA4 key event imported into Ads) on:
   - a completed **Cycle Check** (primary), and
   - a **Book intro** submit (secondary).
   Start on **Maximize clicks**, then switch to **Maximize conversions** after about 30 conversions.
3. **Price.** The page shows $895, or 3 × $325. Confirm whether HST applies before adding the price asset or the "Pricing" sitelink below.

## Campaign settings

| Setting | Value |
|---|---|
| Campaign name | `CHC · Cycle & Hormone Care · Barrie · Search` |
| Type / goal | Search · Leads |
| Networks | Search only. Turn **off** Search partners and the Display Network. |
| Locations | Barrie + 40 km radius, **"Presence: people in or regularly in"** |
| Language | English |
| Budget | $20–30/day to start |
| Bidding | Maximize clicks with a $4.00 max CPC cap, then Maximize conversions once tracking has data |
| Ad schedule | All days, 6 AM–11 PM |
| Final URL | `https://www.beoptimal.ca/services/cycle-and-hormone-care` |
| Display path | `beoptimal.ca/cycle-care/barrie` |
| Final URL suffix | `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}&utm_content={creative}` |
| Ad names | `CG1-RSA` … `CG4-RSA` (one responsive search ad per ad group) |

## CG1 · Cycle & hormone care (core)

**Keywords** (phrase match unless the brackets mean exact):
- `[hormone doctor barrie]`
- `[womens hormone clinic barrie]`
- `"hormone testing for women"`
- `"hormone imbalance treatment women"`
- `"irregular periods doctor"`
- `"missed periods not pregnant"`
- `"hormonal acne treatment barrie"`
- `"female hormone specialist near me"`
- `"womens health clinic barrie"`

**Headlines (15):**
1. Cycle & Hormone Care, Barrie *(pin to position 1)*
2. Your Symptoms Are Real
3. Real Answers in 12 Weeks
4. Take the Free Cycle Check
5. No Referral Needed
6. 60-Minute Visit With an NP
7. Bloodwork Timed to Your Cycle
8. OHIP-Covered Bloodwork
9. A Plan You Understand
10. Same NP Every Visit
11. Start Within Days
12. PCOS, PMDD & Endometriosis
13. Irregular or Missed Periods
14. Acne & Hair Changes Assessed
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Take the free 3-minute Cycle Check, then a 60-minute visit with our Nurse Practitioner.
2. No referral needed. We time your bloodwork to your cycle, and OHIP covers the bloodwork.
3. In 12 weeks, know what's driving your symptoms and leave with a plan you understand.
4. For premenopausal women 18+: PCOS, PMDD, endometriosis, adenomyosis, irregular cycles.

## CG2 · PCOS / PMOS

**Keywords:**
- `[pcos doctor barrie]`
- `[pcos treatment barrie]`
- `"pcos clinic near me"`
- `"pcos specialist barrie"`
- `"polycystic ovary syndrome treatment"`
- `"pcos nurse practitioner"`
- `"pmos treatment"`
- `"pcos testing"`

**Headlines (15):**
1. PCOS Care in Barrie *(pin to position 1)*
2. PCOS & PMOS, No Referral
3. Cycles, Skin, Hair: Together
4. Androgen + Insulin Bloodwork
5. Take the Free Cycle Check
6. 60-Minute Visit With an NP
7. Bloodwork Timed to Your Cycle
8. OHIP-Covered Bloodwork
9. InBody Scan at Start and End
10. A Plan You Understand
11. Same NP Every Visit
12. Options Chosen With You
13. Start Within Days
14. 12-Week Foundation Program
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. PCOS care that looks at cycles, skin, hair and metabolism together, with one NP.
2. We check androgens, insulin and thyroid, timed to your cycle. OHIP covers the bloodwork.
3. No referral needed. Free 3-minute Cycle Check, then a 60-minute visit with your NP.
4. Options are chosen with you: cycle regulation, skin and hair care, metabolic support.

## CG3 · PMS / PMDD

**Keywords:**
- `[pmdd treatment barrie]`
- `"pmdd treatment"`
- `"pmdd doctor"`
- `"pmdd help near me"`
- `"severe pms treatment"`
- `"premenstrual dysphoric disorder treatment"`
- `"pms mood swings help"`

**Headlines (15):**
1. PMDD & Severe PMS Care *(pin to position 1)*
2. Mood That Tanks Before Periods
3. There Are Options for PMDD
4. We Track the Pattern With You
5. Take the Free Cycle Check
6. No Referral Needed
7. 60-Minute Visit With an NP
8. Same NP Every Visit
9. Bloodwork Timed to Your Cycle
10. Virtual Follow-Ups Available
11. A Plan You Understand
12. OHIP-Covered Bloodwork
13. Your Symptoms Are Real
14. 12-Week Foundation Program
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. When mood shifts before a period affect work and relationships, there are options.
2. We confirm the pattern with daily tracking, then build a plan with your NP.
3. No referral needed. Free 3-minute Cycle Check, then a 60-minute visit with your NP.
4. Options are chosen with you, from sleep and stress support to medication when it helps.

## CG4 · Painful or heavy periods (endometriosis, adenomyosis)

**Keywords:**
- `[endometriosis doctor barrie]`
- `"endometriosis treatment barrie"`
- `"adenomyosis treatment"`
- `"painful periods doctor"`
- `"heavy periods treatment"`
- `"heavy menstrual bleeding treatment"`
- `"period pain clinic"`

**Headlines (15):**
1. Painful or Heavy Periods? *(pin to position 1)*
2. Pain That Cancels Plans?
3. Endometriosis Concerns?
4. Heavy Periods Can Drain Iron
5. Ferritin and CBC Checked
6. Imaging & Referral if Needed
7. No Referral Needed
8. Take the Free Cycle Check
9. 60-Minute Visit With an NP
10. Same NP Every Visit
11. A Plan You Understand
12. OHIP-Covered Bloodwork
13. Your Symptoms Are Real
14. 12-Week Foundation Program
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Periods that cancel plans or soak a pad every hour or two deserve a proper look.
2. We check iron, assess pain and bleeding, and arrange imaging or referral when needed.
3. No referral needed. Free 3-minute Cycle Check, then a 60-minute visit with your NP.
4. In 12 weeks, know what's driving your symptoms and leave with a plan you understand.

## Assets (campaign level)

**Sitelinks:**

| Text | Line 1 | Line 2 |
|---|---|---|
| Take the Cycle Check | Free, about 3 minutes | See which program fits |
| How the 12 Weeks Work | Six steps, Day 1 to Week 12 | One clinic visit, rest virtual |
| What We May Test | Tests timed to your cycle | Only when it changes the plan |
| Pricing *(after the HST check)* | $895 Foundation, 12 weeks | Or 3 monthly payments of $325 |

**Callouts:** No Referral Needed · OHIP-Covered Bloodwork · 60-Minute NP Visit · Same NP Every Visit · Free 3-Min Cycle Check · Virtual Follow-Ups · HSA-Eligible · Local in Barrie

**Structured snippet** (header: Services): PCOS / PMOS · PMS / PMDD · Endometriosis · Adenomyosis · Irregular Periods · Hormonal Acne

## Negative keywords (campaign level)

`jobs` · `job` · `career` · `salary` · `course` · `training` · `school` · `nursing care plan` · `icd 10` · `pdf` · `wiki` · `reddit` · `menopause` · `perimenopause` · `hot flashes` · `pregnancy` · `pregnant` · `ivf` · `egg freezing` · `fertility clinic` · `men` · `male` · `trt` · `testosterone for men` · `birth control online` · `diet plan`

Menopause has its own campaign, so negating it here keeps the two from bidding against each other. Fertility searches go to fertility clinics, and the program refers out when that's the right next step.
