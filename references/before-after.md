# Before / after — the same finding, two formats

Six examples. All fictional. Each "before" is a real failure mode of default AI output; each "after" is what the rules produce.

---

## 1. A tool verdict

### ❌ Before

> Great question! When it comes to choosing a scheduler for your Python pipeline, there are a few things to consider. It's worth noting that Apache Airflow is generally regarded as the industry standard, and it should be noted that it has a very large community, whereas Prefect is a more modern alternative that takes a different approach to the same problem, and Dagster also exists and focuses on the data asset model, so ultimately the choice depends on your specific requirements and team context.

*(123 words. No verdict. The reader still doesn't know what to install.)*

### ✅ After

> **Pick Prefect. Don't pick Airflow for this.**
>
> - **Airflow** — 2,800 config keys, one cron daemon you now operate forever
> - **Prefect** — retries in Python, deploy in 20 minutes
> - **Dagster** — best asset model, worst learning curve
>
> **The exception:** if you already run Airflow for another team, add this to it. Switching costs beat tool quality.
>
> **Next:** scaffold `flows/` on the Prefect 3 template.

---

## 2. Admitting the research was wrong

### ❌ Before

> I have to give you this straight, because the picture is worse than I said. I named four competitors earlier from search snippets. I've now read their actual sites, and I was underselling them badly. Their headline is literally "one-stop partner for everything you asked me to design," and their menu covers the entire service list I spent today drafting for you, including the training component, which is also grant-claimable, so we should probably revisit the positioning before we talk to anyone.

### ✅ After

> **I was wrong. They already sell the whole suite.**
>
> Competitor A, read in full:
>
> - The three services I called "open gaps"
> - The certification course — grant-claimable
> - The measurement add-on
>
> **Consequence:** "nobody does this" is dead as a pitch.
>
> **Next:** reposition onto the two accounts they don't serve. Do not book the demo until that's written.

**Pattern:** the bad version buries the correction under narrative. The good version leads with the admission, then shows evidence.

---

## 3. Ranked recommendations

### ❌ Before

> The openings that we found during the research seem to be in a few places. Firstly, nobody really serves the smaller firms who rent space rather than own it, which could be a couple hundred companies who now have a live legal requirement, and secondly nobody owns the performance data even though every job legally generates a year of it, and thirdly there seem to be bigger penalties elsewhere that dwarf the problem we started with.

### ✅ After

> **Three gaps, ranked:**
>
> 1. **Renters** — ~200 firms, live legal duty, zero vendors serving them
> 2. **The data** — every job produces 12 months of readings. Nobody owns it.
> 3. **The penalty regime** — bigger than the problem we started with.
>
> **Cheapest test:** 2 phone calls. Not a deck.

**Pattern:** ordinal words ("firstly… secondly") are bullets that failed.

---

## 4. Status update

### ❌ Before

> Sure! Here is a summary of where things stand. The migration project has been progressing well over the last couple of weeks. The schema work was completed on Tuesday, and afterwards we discovered that there were some considerations around the legacy indexes which needed to be addressed, so that took a bit longer than anticipated, but we are hopeful that we will be able to finish the remaining data work by the end of the week, subject to review.

### ✅ After

> **Migration: 80% done. Blocked on index rebuilds.**
>
> - **Schema** — merged Tuesday
> - **Data copy** — 3 of 15 tables, ~2 days left
> - **Risk** — legacy indexes rebuild 6x slower than estimated
>
> **Needed from you:** approve the downtime window. Friday 22:00 or Saturday 02:00.

---

## 5. Price comparison

### ❌ Before

> Looking at the pricing, it should be noted that Provider One charges $49 per month for the starter tier, while Provider Two comes in a bit cheaper at $39, although you should probably be aware that the cheaper option limits you to five seats and charges extra for each API call, so when it comes to total cost of ownership the numbers can actually end up being quite different from the headline price, and it may be worth modeling both scenarios.

### ✅ After

> **$39 beats $49 until you pass 30k calls/month.**
>
> - **Provider One** — $49/mo, 10 seats, unlimited calls
> - **Provider Two** — $39/mo, 5 seats, $0.004/call after 30k
>
> **At our usage (~50k calls):** One = $49 · Two = **$239**
>
> **Buy One.** The sticker price is the least useful number on the page.

---

## 6. Bug investigation

### ❌ Before

> I've been looking into the login issue and I think the reason it's happening is probably related to the way the session token is being handled after the timeout occurs. Basically what seems to be happening is that the middleware is checking the token but at that point the token has already been rotated, so the validation fails, and then the user gets bounced back to the login screen even though they were still technically active, which would explain the reports we've been seeing.

### ✅ After

> **Cause: token rotates before the middleware validates it.**
>
> The race:
>
> 1. Session hits timeout — token rotates
> 2. Middleware validates the **old** token
> 3. Validation fails → user bounced to login, still active
