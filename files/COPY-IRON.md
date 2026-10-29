# IV iron ads: three ideas (Oct 14, 2026) · Book now since Oct 29

**Oct 29 (Peter): the call to action is "Book now", not the founding waitlist.** The Meta button is **Book now**, the destination is the IV iron page, and the IRV1 end card says "Book your IV iron visit." Every waitlist, founding-price and sign-up line is gone. These ads launched as a pre-launch waitlist test on Oct 14; the history below is kept for the art. There are three ideas, each a different format so Meta treats them as separate creatives.

| Ad | Idea | Format | On the image |
|---|---|---|---|
| IR1 | Pills not working | One big engraved IV bag of amber iron solution on cream (Oct 20 rework) | Iron pills not working? IV iron skips the gut. |
| IR2 | Hidden deficiency | The IV iron page's hero close-up, never extended (Oct 20) | Low iron doesn't always look like anemia. |
| ~~IR3~~ | **Removed Oct 20** (Peter: delete IR3) | | |
| IRV1 | The hero, animated | 6.5 s: the page hero close-up animated (she turns a page) + end card, silent (Oct 20) | IV iron is coming to Barrie this November. Then "Book your IV iron visit." with a Book now button (Oct 29) |

```
python3 gen/r6/compose.py && python3 render.py --page iron   # art, then out/r4/iron/IR1–IR3 _1x1 + _9x16 + _1-91x1, QA
```

Backgrounds (Oct 20 rework, Peter: "IR2 image should be the hero from the website", "IR1 punchier and clearer", "IR3 much clearer", "a CLOSE-UP JUST LIKE THE HERO, no fake room background"):
- **IR1:** one big IV bag of amber iron solution, a copperplate engraving made with gpt_image_2_5 (2d97dd9d) from the page's own engravings. Only its paper is outpainted (16:9, d768af90). The 9:16 hangs the plate under a band of its own paper.
- **IR2:** the IV iron page's hero (`beoptimal.ca/images/iron/hero-infusion.jpg`, AI imagery) as the close-up only. The square is a crop. The 9:16 and 1.91:1 put the close-up on cream panels. Nothing is outpainted: an extended version invented a room (window, IV pole, rug) and a face, so it was rejected.
- **IR3:** the REAL front desk under the Optimal logo wall (`optimal-promo-videos/_project/ref/clinic_2`), crop only, on cream. The waiting-lounge version (Oct 19) read as confusing. The AI "infusion room" before that was pulled for good.
- Art script: `gen/r6/compose.py` → `assets/r4/IR1v_*`, `IR2h_*`, `IR3r_*`. The previous art stays in `assets/r4/IR1_*`, `IR2_*`, `IR3_*`.

IRV1 lives at `out/r4/iron/IRV1_{9x16,1x1,1-91x1}.mp4`, with thumbnails. It's rebuilt from `optimal-content-library/series/iron-irv1` (HyperFrames). Since Oct 20 its clip is the page hero animated (Kling 3.0 pro, ebbf538a, from a square crop of the hero: she turns a page, the IV line stays still, her face stays out of frame). The reel puts it under a cream band, the square runs it full bleed, and the wide sets it on the right. The lounge cut is retired.

## Setup (Oct 29: Book now)

| | IV iron |
|---|---|
| Campaign objective | Sales → website conversions, optimized for **BookAppointmentSuccess** (the same booking event as the menopause and longevity campaigns) |
| Destination | `https://www.beoptimal.ca/services/iron` (`/iron` redirects there) |
| Audience | Adults 25–64, about 40 km around Barrie, broad (no interests) |
| Ads | One ad set, images and videos together (Jeremy's Oct 19 rule). Start with IR1, IR2, IRV1 and IRT1. Placement asset customization: 1:1 Feed, 9:16 Stories/Reels, 1.91:1 right column |
| CTA button | **Book now** |
| Budget | As set by Peter in Slack (Oct 29): track it for a week, reassess in 2–3 weeks |
| Meta AI label | **Off** for every ad. Never turn it on (Peter, Oct 28) |
| URL parameters | `utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}` |

**Before launch:** on Oct 29 the IV iron page still showed "Save my founding spot" and an email-only waitlist form. Its buttons have to open booking before these ads go live, or the ad and the page will disagree. The Instant Form ("Join the IV iron founding waitlist") is retired.

**Reading the test:** judge on cost per booked consult. For video, also look at the 3-second hold rate and ThruPlay. Turn off an ad that has spent about 1.5× the cost per booking with no booking, and add the next one from the queue.

**IR2's clinical claim:** the Clinical Director cleared "low iron without anemia" on Oct 20. In Canada the infusion product's indication is iron-deficiency *anemia* in adults who can't tolerate oral iron or didn't respond to it, so the ad stays on the cleared wording.

## Copy

Every primary text ends on the one action: book. The first step people book is a consult with our Nurse Practitioner, virtual or in-clinic (the page's "Path B"). "Opening November" stays where it's true; swap it for "now open" once IV iron starts.

### IR1 · "Iron pills not working? IV iron skips the gut."
**Primary text:** Iron pills not working? IV iron skips the gut and goes straight into a vein, refilling iron stores in one or two monitored visits. It opens at Optimal in Barrie this November: no referral needed, and we order your bloodwork first. Book a consult with our Nurse Practitioner now, virtual or in-clinic.
**Headline:** Iron pills not working? · **Description:** IV iron · No referral · Barrie

### IR2 · "Low iron doesn't always look like anemia." (cleared by the Clinical Director, Oct 20)
**Primary text:** Low iron doesn't always look like anemia. Hemoglobin can sit in range while iron stores, measured as ferritin, run low. IV iron opens at Optimal in Barrie this November, led by a Nurse Practitioner who reviews your bloodwork before anything else. No referral needed. Book a consult with our NP now, virtual or in-clinic.
**Headline:** Iron stores, checked properly · **Description:** IV iron · No referral · Barrie

### ~~IR3~~ (removed Oct 20, Peter)

### IRV1 · "IV iron is coming to Barrie this November." (video)
**Primary text:** IV iron is coming to Optimal in Barrie this November: a calm, monitored infusion with a Nurse Practitioner on site, and no referral needed. Book a consult with our NP now, virtual or in-clinic.
**Headline:** Book IV iron in Barrie · **Description:** No referral · Opening November

## Guardrails used

- **Book now (Oct 29, Peter).** No waitlist, founding or sign-up language anywhere.
- **No price numbers.** Final prices are set at launch. There's no "regular $595" either: a reference price for a service that has never sold at that price is a Competition Act risk.
- **No drug brand names** (the iron is a separate prescription). No feel-better timelines. No "1 in 4 women".
- **Third person only.** No "Exhausted by low iron?" or "you have…" phrasing (Meta's personal-attributes policy).
- **No provider comparisons** (CNO): no drip bars, no other clinics. **Pills vs IV is described neutrally**, since pills are the right first step for many people. The NP decides whether IV iron fits, after bloodwork.
- **Meta AI label: off.** Never turn on Meta's AI label for any ad or post (Peter, Oct 28). The lounge clip is animated from a real photo. Ads never show a clinic room that doesn't exist.
