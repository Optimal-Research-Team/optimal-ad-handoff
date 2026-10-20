# Google Ads: IV iron founding waitlist (Search), Oct 19, 2026

A build sheet for whoever on the team pushes this live. Every headline is ≤30 characters and every description ≤90 (checked). Copy follows the same guardrails as the Meta ads (`COPY-IRON-R2.md`): waitlist only, no price, no drug brand names, no feel-better timelines, no provider comparisons.

## Before launch: the landing page is live (Oct 20)

**`https://www.beoptimal.ca/iron` is live.** It redirects to `https://www.beoptimal.ca/services/iron` ("Save my founding spot" email form, symptom quick-check, pills vs hospital vs Optimal table, both referral paths, the real clinic photos). Peter confirmed it on Oct 20, and I checked the rendered page the same day.

1. **Final URL.** Use the canonical `https://www.beoptimal.ca/services/iron`, not the `/iron` redirect. Google flags redirecting final URLs, and the redirect can drop the UTM suffix.
2. **Conversion tracking (still to do, ~15 min).** The page loads GA4 (`G-FP790P5JK8`) and the Meta pixel, but no Google Ads conversion tag. Two options:
   - fire a Google Ads conversion on a successful "Save my founding spot" submit, or
   - mark the GA4 `generate_lead` (or the form-submit event) as a key event and import it into Ads.

   Start on **Maximize clicks**, then switch to **Maximize conversions** after about 30 signups.
3. **Landing-page review.** The page has the hospital-infusion comparison table and the "1 in 4 women" line. The Clinical Director signed off all clinical claims (Oct 20), so they're not a blocker. Google reviews the page against its healthcare policy, so if an ad is limited, check the policy note first.
4. **Lead form asset (optional).** Add a Google lead form asset (name, email, phone) so people can join from the results page. Download the leads every few days, because founding access goes in signup order.

## Campaign settings

| Setting | Value |
|---|---|
| Campaign name | `IV Iron · Barrie · Founding waitlist · Search` |
| Type / goal | Search · Leads |
| Networks | Search only. Turn **off** Search partners and the Display Network. |
| Locations | Barrie + 40 km radius, **"Presence: people in or regularly in"** (not "interest in") |
| Language | English |
| Budget | $15–25/day to start |
| Bidding | Maximize clicks with a $4.00 max CPC cap, then Maximize conversions once tracking has data |
| Ad schedule | All days, 6 AM–11 PM |
| Final URL | `https://www.beoptimal.ca/services/iron` (canonical; `/iron` redirects here) |
| Display path | `beoptimal.ca/iv-iron/barrie` |
| Final URL suffix | `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}&utm_content={creative}` |

## Ad group 1: IV iron (core)

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
1. IV Iron Infusions in Barrie *(pin to position 1)*
2. No Referral Needed
3. Join the Founding Waitlist
4. NP-Led IV Iron Program
5. As Little as One Visit
6. We Order Your Bloodwork
7. An NP On Site Every Infusion
8. Skips the Gut, Refills Stores
9. First Access in Signup Order
10. Founding Pricing for Members
11. Free to Join, No Payment
12. Bloodwork Rechecked at 6–8 Wks
13. Local Clinic in Barrie, ON
14. Coming Soon to Optimal
15. A Calm, Comfortable Clinic

**Descriptions (4):**
1. IV iron is coming to Optimal in Barrie. Join the free founding waitlist for first access.
2. No referral needed. We order your bloodwork and a Nurse Practitioner assesses you first.
3. IV iron skips the gut and can refill iron stores in as little as one monitored visit.
4. Founding members get first access in signup order and founding pricing. Free to join.

## Ad group 2: Low ferritin / iron deficiency

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
2. Iron Stores Measured Properly
3. IV Iron Coming to Barrie
4. No Referral Needed
5. Join the Founding Waitlist
6. Bloodwork Ordered for You
7. NP Reviews Your Labs First
8. As Little as One Visit
9. Recheck at 6–8 Weeks
10. First Access in Signup Order
11. Founding Pricing for Members
12. Free to Join, No Payment
13. An NP On Site Every Infusion
14. Local Clinic in Barrie, ON
15. Measured, Not Guessed

**Descriptions (4):**
1. Ferritin measures iron stores. Our Nurse Practitioner reviews your bloodwork first.
2. No referral needed: we order the labs, assess you, and recheck at 6–8 weeks.
3. IV iron is coming to Optimal in Barrie. Join the free founding waitlist for first access.
4. Founding members get first access in signup order and founding pricing. Free to join.

## Ad group 3: Iron pills not working

**Keywords:**
- `"iron pills not working"`
- `"alternative to iron pills"`
- `"iron supplements upset stomach"`
- `"cant tolerate iron pills"`
- `"oral iron not working"`
- `"iron pills side effects"`

**Headlines (15):**
1. An Option Beyond Iron Pills *(pin to position 1)*
2. IV Iron Skips the Gut
3. As Little as One Visit
4. No Referral Needed
5. Join the Founding Waitlist
6. IV Iron Coming to Barrie
7. NP Decides the Right Route
8. We Order Your Bloodwork
9. An NP On Site Every Infusion
10. First Access in Signup Order
11. Founding Pricing for Members
12. Free to Join, No Payment
13. Recheck at 6–8 Weeks
14. Local Clinic in Barrie, ON
15. Monitored, NP-Led Visits

**Descriptions (4):**
1. Iron pills work a little at a time. IV iron skips the gut, often in one visit.
2. Pills suit many people. Our Nurse Practitioner decides which route fits, after bloodwork.
3. IV iron is coming to Optimal in Barrie. Join the free founding waitlist for first access.
4. No referral needed. An NP is on site for every infusion. Free to join the waitlist.

## Negative keywords (campaign level, phrase match)

- **Jobs and training:** free, jobs, job, career, salary, course, training, certification, nurse jobs, how to start an iv business
- **Other kinds of "iron":** iron man, ironman, golf, steam iron, cast iron, iron supplement brand, iron rich foods, recipe
- **IV-therapy seekers who aren't the target:** hangover, vitamin drip, myers cocktail, nad, glutathione, hydration, drip bar, mobile iv, at home, house call
- **Out of scope:** pregnant, pregnancy, prenatal (not currently offered in pregnancy, per the referral form), kids, child, pediatric, baby, dog, cat, pet
- **Not our pathway:** hospital, emergency, er, wikipedia, reddit, side effects of iv iron, ferric, monoferric, venofer, feraheme
  - Drug names stay negative. We don't advertise against prescription brands, and those searchers want drug info, not a clinic.

## Assets (account or campaign level)

- **Sitelinks** (each with two description lines):
  1. **How It Works** → `/iron#how-it-works`
     - "No referral needed. NP assessment, bloodwork, then one visit."
     - "Recheck at 6–8 weeks."
  2. **Founding Waitlist** → `/iron#waitlist`
     - "Free to join, no payment."
     - "First access in signup order."
  3. **NP Assessment First** → `/iron#how-it-works`
     - "A Nurse Practitioner reviews your labs."
     - "We decide the right route together."
  4. **For Doctors: Refer** → `/iron#refer`
     - "One-page referral form."
     - "Fax it with recent labs to 833-370-0320."
- **Callouts:** No Referral Needed · NP On Site · Bloodwork Ordered for You · Founding Waitlist Open · Local in Barrie · 6–8 Week Recheck · Free to Join
- **Structured snippet (Services):** IV Iron Infusions, NP Assessment, Bloodwork Review, 6–8 Week Recheck
- **Call asset:** (437) 370-0291, during clinic hours only
- **Location asset:** link the Optimal Google Business Profile (630 Huronia Rd, Unit 5)
- **Image assets:** the 1:1 and 1.91:1 crops of IR4 (calendar) and IR5 (lakeshore) from `out/r5/iron/`. Leave "AI-generated" in the asset name.

## Policy notes for the person launching

- Google classes IV iron under **Healthcare and medicines**. Service ads for a clinic are allowed. **Don't name the drug** (it's a prescription product), and don't use "cure", "guaranteed" or before/after claims.
- If an ad shows **"Eligible (limited)"**, that's normal for health topics. If it's **"Disapproved: Unapproved substances" or "Prescription drugs"**, check for a drug name in the keywords or on the landing page.
- The landing page must match the ad: waitlist, NP-led, no referral, Barrie. Don't run these ads to the homepage.
- **First-week checks:**
  - search terms report (add negatives daily)
  - CTR by ad group
  - cost per waitlist signup against Meta's cost per lead
