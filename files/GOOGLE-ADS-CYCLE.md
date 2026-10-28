# Google Ads: Cycle & Hormone Care (Search), Oct 28, 2026

A build sheet for whoever on the team pushes this live. The landing page is live (checked Oct 28).

The campaign has five ad groups in two sets, matching the Meta ads:

| Set | Ad groups |
|---|---|
| **General** | CG1 cycle & hormone care · CG2 period problems |
| **By condition** | CG3 PMOS (formerly PCOS) · CG4 PMDD · CG5 endometriosis & adenomyosis |

- **Character limits:** every headline is ≤30 characters, every description ≤90 (ours are kept to about 70 so two fit on two lines), every callout and sitelink ≤25, every sitelink line ≤35, and every path ≤15. All are checked by `gen/r9/check_google.py`.
- **Approach:** Hormozi-style and simple.
  - Lead with the searcher's problem.
  - Make the outcome concrete ("real answers in 12 weeks", "a plan you understand").
  - Cut effort and wait ("no referral", "free 3-minute Cycle Check", "start within days").
  - Add proof of thoroughness ("bloodwork timed to your cycle", "same NP every visit").
- **Guardrails, the same as the Meta set:**
  - no drug names (Google restricts prescription drugs in ad text);
  - no "specialist" or "cure";
  - no testimonials or provider comparisons;
  - no outcome promises beyond the landing page;
  - "pain with intimacy", not "pain with sex".

## Before launch

1. **Conversion tracking.** Fire a Google Ads conversion (or a GA4 key event imported into Ads) on a completed **Cycle Check** (primary) and on a **Book intro** submit (secondary). Start on **Maximize clicks**, then switch to **Maximize conversions** after about 30 conversions.
2. **Price.** The page shows $895, or 3 × $325. Confirm whether HST applies before adding the price asset or the "Pricing" sitelink below.

## Campaign settings

| Setting | Value |
|---|---|
| Campaign name | `CHC · Cycle & Hormone Care · Barrie · Search` |
| Type / goal | Search · Leads |
| Networks | Search only. Turn **off** Search partners and the Display Network. |
| Locations | Barrie + 40 km radius, **"Presence: people in or regularly in"** |
| Language | English |
| Budget | $20–30/day to start, shared across the five ad groups |
| Bidding | Maximize clicks with a $4.00 max CPC cap, then Maximize conversions once tracking has data |
| Ad schedule | All days, 6 AM–11 PM |
| Final URL | `https://www.beoptimal.ca/services/cycle-and-hormone-care` |
| Display path | `beoptimal.ca/cycle-care/barrie` |
| Final URL suffix | `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}&utm_content={creative}` |
| Ad names | `CG1-RSA` … `CG5-RSA` (one responsive search ad per ad group) |

## CG1 · Cycle & hormone care (general)

**Display path:** `beoptimal.ca/cycle-care/barrie`

**Keywords** (phrase match unless the brackets mean exact):
- `[hormone doctor barrie]`
- `[womens hormone clinic barrie]`
- `"hormone testing for women"`
- `"hormone imbalance treatment women"`
- `"female hormone specialist near me"`
- `"womens health clinic barrie"`
- `"hormonal acne treatment barrie"`
- `"nurse practitioner barrie women"`

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
12. PMOS, PMDD & Endometriosis
13. Periods, Skin & Mood Assessed
14. Hormonal Acne & Hair Changes
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Free 3-minute Cycle Check, then 60 minutes with a Nurse Practitioner.
2. No referral. Bloodwork timed to your cycle, covered by OHIP.
3. In 12 weeks, know what's behind your symptoms, with a clear plan.
4. For women 18–45 with PMOS, PMDD, endometriosis or irregular cycles.
## CG2 · Period problems (irregular, heavy or painful)

**Display path:** `beoptimal.ca/periods/barrie`

**Keywords:**
- `[irregular periods doctor barrie]`
- `"irregular periods treatment"`
- `"missed periods not pregnant"`
- `"no period for months"`
- `"heavy periods treatment"`
- `"heavy menstrual bleeding treatment"`
- `"painful periods doctor"`
- `"period pain clinic"`

**Headlines (15):**
1. Irregular or Painful Periods? *(pin to position 1)*
2. Missed Periods, Not Pregnant?
3. Heavy Periods Can Drain Iron
4. Periods Deserve a Proper Look
5. Take the Free Cycle Check
6. No Referral Needed
7. 60-Minute Visit With an NP
8. Bloodwork Timed to Your Cycle
9. Ferritin and CBC Checked
10. Imaging & Referral if Needed
11. A Plan You Understand
12. Same NP Every Visit
13. OHIP-Covered Bloodwork
14. Real Answers in 12 Weeks
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Irregular, heavy or painful periods deserve a proper look.
2. We check iron, time your bloodwork to your cycle, and image if needed.
3. No referral. Free 3-minute Cycle Check, then 60 minutes with an NP.
4. In 12 weeks, know what's behind your symptoms, with a clear plan.
## CG3 · PMOS (formerly PCOS)

**Display path:** `beoptimal.ca/pmos-pcos/barrie`

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
1. PMOS (PCOS) Care in Barrie *(pin to position 1)*
2. PCOS, Now Called PMOS
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
13. No Referral Needed
14. 12-Week Foundation Program
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. PMOS, formerly PCOS: cycles, skin, hair and metabolism, together.
2. Androgen, insulin and thyroid bloodwork, timed to your cycle.
3. No referral. Free 3-minute Cycle Check, then 60 minutes with an NP.
4. Options chosen with you: cycle, skin, hair and metabolic care.
## CG4 · PMDD and severe PMS

**Display path:** `beoptimal.ca/pmdd/barrie`

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
3. More Than Bad PMS
4. There Are Options for PMDD
5. We Track the Pattern With You
6. Take the Free Cycle Check
7. No Referral Needed
8. 60-Minute Visit With an NP
9. Same NP Every Visit
10. Virtual Follow-Ups Available
11. A Plan You Understand
12. OHIP-Covered Bloodwork
13. Your Symptoms Are Real
14. 12-Week Foundation Program
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Mood that crashes before a period and lifts after? There are options.
2. We confirm the pattern with daily tracking, then plan with your NP.
3. No referral. Free 3-minute Cycle Check, then 60 minutes with an NP.
4. From sleep and stress support to medication when it helps.
## CG5 · Endometriosis and adenomyosis

**Display path:** `beoptimal.ca/endometriosis/barrie`

**Keywords:**
- `[endometriosis doctor barrie]`
- `"endometriosis treatment barrie"`
- `"endometriosis clinic near me"`
- `"suspected endometriosis"`
- `"adenomyosis treatment"`
- `"endometriosis pain help"`
- `"pelvic pain clinic women"`

**Headlines (15):**
1. Endometriosis Care in Barrie *(pin to position 1)*
2. Pain That Cancels Plans?
3. Pelvic Pain Deserves Answers
4. Suspected Endometriosis?
5. Adenomyosis Assessed Too
6. Imaging & Referral if Needed
7. Heavy Periods Can Drain Iron
8. No Referral Needed
9. Take the Free Cycle Check
10. 60-Minute Visit With an NP
11. Same NP Every Visit
12. A Plan You Understand
13. OHIP-Covered Bloodwork
14. Real Answers in 12 Weeks
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Painful periods, pelvic pain or pain with intimacy deserve answers.
2. We assess pain and bleeding, check iron, and refer or image if needed.
3. No referral. Free 3-minute Cycle Check, then 60 minutes with an NP.
4. Suspected or diagnosed: one NP, every visit, and a plan you understand.
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

`jobs` · `job` · `career` · `salary` · `course` · `training` · `school` · `nursing care plan` · `icd 10` · `pdf` · `wiki` · `reddit` · `menopause` · `perimenopause` · `hot flashes` · `pregnancy` · `pregnancy test` · `am i pregnant` · `early pregnancy` · `ivf` · `egg freezing` · `fertility clinic` · `men` · `male` · `trt` · `testosterone for men` · `birth control online` · `diet plan`

Menopause has its own campaign, so negating it here keeps the two from bidding against each other. Fertility searches go to fertility clinics, and the program refers out when that's the right next step.

There's no plain `pregnant` negative on purpose: it would block CG2's `"missed periods not pregnant"`. The pregnancy negatives above catch the searches we don't want instead.
