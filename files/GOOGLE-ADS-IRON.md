# Google Ads: IV iron founding waitlist (Search), Oct 28, 2026

A build sheet for whoever pushes this live. It's rewritten from the Oct 19 version in the same shape as the Cycle & Hormone Care sheet.

The campaign has four ad groups: two for searchers who already know they want iron (IRG1 IV iron, IRG3 iron pills not working) and two for searchers who don't know it's iron yet (IRG2 low ferritin, IRG4 tired all the time).

- **Character limits:** every headline ≤30 characters, every description ≤90 (ours are kept to about 70), every sitelink ≤25 with lines ≤35, every path ≤15. All checked by `gen/r9/check_google.py GOOGLE-ADS-IRON.md`.
- **Hormozi, kept simple:**
  - **Dream outcome:** iron stores refilled.
  - **Likelihood:** bloodwork before and after, an NP on site.
  - **Time:** often just one infusion, opening in November.
  - **Effort:** no referral, it skips the gut, free to join.
  - **One offer:** the free founding waitlist, with first access and founding pricing.
- **Guardrails, the same as the Meta set (`COPY-IRON-R2.md`):**
  - waitlist only, no price;
  - no drug or brand names;
  - no feel-better timelines;
  - no comparisons with other providers or hospitals.
- **Claims** come from the live page (beoptimal.ca/services/iron, checked Oct 28): "Restore it in as little as one visit", "1–2 infusions, often just one", "No referral needed", "We order your bloodwork", "An NP on site for every infusion", "Recheck bloodwork at 6–8 weeks", "Iron often covered by drug plans", "Opening November 2026".

## Before launch

1. **Final URL:** use `https://www.beoptimal.ca/services/iron`. `/iron` redirects to it, and Google flags redirecting final URLs.
2. **Conversion tracking:** fire a Google Ads conversion on a successful "Save my founding spot" submit (or import GA4 `generate_lead`). Start on Maximize clicks, then switch to Maximize conversions after about 30 signups.
3. **Lead form asset (optional):** lets people join from the results page. Download the leads every few days, because founding access goes in signup order.

## Campaign settings

| Setting | Value |
|---|---|
| Campaign name | `IV Iron · Barrie · Founding waitlist · Search` |
| Type / goal | Search · Leads |
| Networks | Search only. Turn **off** Search partners and the Display Network. |
| Locations | Barrie + 40 km radius, **"Presence: people in or regularly in"** |
| Language | English |
| Budget | $15–25/day to start |
| Bidding | Maximize clicks with a $4.00 max CPC cap, then Maximize conversions once tracking has data |
| Ad schedule | All days, 6 AM–11 PM |
| Final URL | `https://www.beoptimal.ca/services/iron` |
| Display path | `beoptimal.ca/iv-iron/barrie` |
| Final URL suffix | `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}&utm_content={creative}` |
| Ad names | `IRG1-RSA` … `IRG4-RSA` (one responsive search ad per ad group) |

## IRG1 · IV iron (people looking for it)

**Display path:** `beoptimal.ca/iv-iron/barrie`

**Keywords** (phrase match unless the brackets mean exact):
- `[iv iron barrie]`
- `[iron infusion barrie]`
- `"iv iron infusion"`
- `"iron infusion clinic"`
- `"iron infusion near me"`
- `"iv iron near me"`
- `"iron iv therapy"`
- `"iron infusion simcoe"`
- `"iron infusion orillia"`
- `"iron infusion innisfil"`

**Headlines (15):**
1. IV Iron in Barrie, NP-Led *(pin to position 1)*
2. Often Just One Infusion
3. No Referral Needed
4. Free Founding Waitlist
5. Opens in Barrie, November
6. IV Iron Skips the Gut
7. We Order Your Bloodwork
8. NP On Site Every Infusion
9. Bloodwork Rechecked at 6–8 Wk
10. First Access, Founding Price
11. Join Free, No Payment Today
12. Iron Often Covered by Plans
13. Measured, Not Guessed
14. A Calm, Comfortable Clinic
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Restore iron in as little as one visit. Join the free founding waitlist.
2. No referral. We order your bloodwork, and an NP assesses you first.
3. An NP is on site for every infusion, and we recheck iron at 6–8 weeks.
4. Founding members get first access and founding pricing. Free to join.

## IRG2 · Low ferritin / iron deficiency

**Display path:** `beoptimal.ca/low-ferritin/barrie`

**Keywords:**
- `"low ferritin treatment"`
- `"low ferritin barrie"`
- `"iron deficiency treatment barrie"`
- `"iron deficiency clinic"`
- `"low iron treatment"`
- `"ferritin test barrie"`
- `"iron levels low what to do"`

**Headlines (15):**
1. Low Ferritin? Talk to an NP *(pin to position 1)*
2. Low Iron, Even If Not Anemic
3. Ferritin Checked Properly
4. No Referral Needed
5. We Order Your Bloodwork
6. NP Reviews Your Labs First
7. Often Just One Infusion
8. Rechecked at 6–8 Weeks
9. Measured, Not Guessed
10. Free Founding Waitlist
11. Opens in Barrie, November
12. First Access, Founding Price
13. Join Free, No Payment Today
14. NP On Site Every Infusion
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Ferritin shows your iron stores. An NP reviews your bloodwork first.
2. Low iron doesn't always look like anemia. Get it measured properly.
3. No referral. We order the labs, assess you, and recheck at 6–8 weeks.
4. IV iron opens in Barrie in November. Join the free founding waitlist.

## IRG3 · Iron pills not working

**Display path:** `beoptimal.ca/iv-iron/pills`

**Keywords:**
- `"iron pills not working"`
- `"alternative to iron pills"`
- `"iron supplements upset stomach"`
- `"cant tolerate iron pills"`
- `"oral iron not working"`
- `"iron pills side effects"`

**Headlines (15):**
1. Iron Pills Not Working? *(pin to position 1)*
2. IV Iron Skips the Gut
3. An Option Beyond Pills
4. Often Just One Infusion
5. No Referral Needed
6. NP Decides the Right Route
7. We Order Your Bloodwork
8. Bloodwork Before and After
9. NP On Site Every Infusion
10. Free Founding Waitlist
11. First Access, Founding Price
12. Opens in Barrie, November
13. Iron Often Covered by Plans
14. Rechecked at 6–8 Weeks
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Pills refill iron a little at a time. IV iron skips the gut.
2. Pills suit many people. An NP decides the right route, after bloodwork.
3. Often just one monitored visit, with an NP on site the whole time.
4. No referral needed. Join the free founding waitlist for first access.

## IRG4 · Tired all the time (symptom searches)

**Display path:** `beoptimal.ca/iron-check/barrie`

**Keywords:**
- `"always tired low iron"`
- `"tired all the time iron"`
- `"fatigue iron deficiency"`
- `"hair loss low ferritin"`
- `"low iron symptoms women"`
- `"iron blood test barrie"`
- `"heavy periods low iron"`

**Headlines (15):**
1. Exhausted by Low Iron? *(pin to position 1)*
2. Tired All the Time?
3. Check Your Iron Stores
4. Hair Shedding? Check Ferritin
5. Heavy Periods Drain Iron
6. No Referral Needed
7. We Order Your Bloodwork
8. NP Reviews Your Labs First
9. Measured, Not Guessed
10. Often Just One Infusion
11. Free Founding Waitlist
12. Opens in Barrie, November
13. First Access, Founding Price
14. Rechecked at 6–8 Weeks
15. Local Clinic in Barrie, ON

**Descriptions (4):**
1. Tiredness, hair shedding and breathlessness can be low iron. Check it.
2. No referral. We order your bloodwork, and an NP reviews it with you.
3. If iron is low, IV iron can refill stores in as little as one visit.
4. IV iron opens in Barrie in November. Join the free founding waitlist.

## Assets (campaign level)

**Sitelinks:**

| Text | Line 1 | Line 2 |
|---|---|---|
| Save My Founding Spot | Free to join, no payment | First access in signup order |
| How It Works | NP assessment, labs, infusion | Recheck at 6–8 weeks |
| Check Your Symptoms | A 10-second quick check | See if iron could be the cause |
| For Doctors: Refer | One-page referral form | Fax it with recent labs |

**Callouts:** No Referral Needed · NP On Site · Bloodwork Ordered for You · Founding Waitlist Open · Free to Join · 6–8 Week Recheck · Local in Barrie

**Structured snippet** (header: Services): IV Iron Infusions · NP Assessment · Bloodwork Review · 6–8 Week Recheck

Also add a **call asset** ((437) 370-0291, clinic hours only) and a **location asset** (the Google Business Profile, 630 Huronia Rd, Unit 5).

## Negative keywords (campaign level, phrase match)

- **Jobs and training:** free, jobs, job, career, salary, course, training, certification, nurse jobs, how to start an iv business
- **Other kinds of "iron":** iron man, ironman, golf, steam iron, cast iron, iron supplement brand, iron rich foods, recipe
- **IV-therapy seekers who aren't the target:** hangover, vitamin drip, myers cocktail, nad, glutathione, hydration, drip bar, mobile iv, at home, house call
- **Out of scope:** pregnant, pregnancy, prenatal (not currently offered in pregnancy, per the referral form), kids, child, pediatric, baby, dog, cat, pet
- **Not our pathway:** hospital, emergency, er, wikipedia, reddit, side effects of iv iron, ferric, monoferric, venofer, feraheme
  - Drug names stay negative. We don't advertise against prescription brands, and those searchers want drug info, not a clinic.

## Policy notes for the person launching

- Google classes IV iron under **Healthcare and medicines**. Service ads for a clinic are allowed. **Don't name the drug** (it's a prescription product), and don't use "cure", "guaranteed" or before/after claims.
- If an ad shows **"Eligible (limited)"**, that's normal for health topics. If it's **"Disapproved: Unapproved substances" or "Prescription drugs"**, check for a drug name in the keywords or on the landing page.
- The landing page must match the ad: waitlist, NP-led, no referral, Barrie. Don't run these ads to the homepage.
- **First-week checks:**
  - search terms report (add negatives daily)
  - CTR by ad group
  - cost per waitlist signup against Meta's cost per lead
