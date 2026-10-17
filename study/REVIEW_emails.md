# Review: the 16 decision emails

For each email, check three things:
1. **Fair?** The facts give one reason for each side.
2. **Same meaning?** Wording 2 says the same as wording 1, with no extra loaded words.
3. **Sounds real?** A colleague could plausibly send it.

Wording 1 is the main study's option text word for word and cannot change. Fixes go into wording 2 or the facts.

Write any problems next to the item. Generated from `study/inbox_items.json`.

## P01 — Shipment-history migration
*From Tomas (Data Platform)*

> We're moving the shipment-history tables to the new database. The data is large, so doing it in one run would finish much sooner, but this is the first migration we've done on the new system.

- **Wording 1:** We can either **execute actions through small, reversible incremental steps that allow continuous rollback**, or **execute the full workflow in a single batch operation to achieve maximum overall throughput**.
- **Wording 2:** We can either **carry out the work in small steps that can be rolled back at any point**, or **do the whole job in one batch to get the highest overall throughput**.

Notes: 

## P02 — Error-tracking tool recommendation
*From Lena (Developer Tools)*

> IT has asked us to recommend an error-tracking tool for all the engineering teams. We have an engineer free this quarter who could set up and run a tool ourselves, though other work is waiting for her too.

- **Wording 1:** We can either **recommend a fully managed service that works immediately out of the box**, or **recommend a self-hosted open-source tool that requires manual setup to save money**.
- **Wording 2:** We can either **recommend a hosted service that is ready to use straight away**, or **recommend an open-source tool we host ourselves, which needs manual setup but costs less**.

Notes: 

## P06 — Feedback on Sam's staffing proposal
*From Jonas (Planning)*

> I'm reviewing Sam's staffing proposal for the new depot, and the numbers have some real problems. Sam joined the team last month, and this is the first proposal they've written.

- **Wording 1:** I can either **deliver blunt, unvarnished critical feedback on a flawed project proposal**, or **deliver tactful, encouraging feedback that emphasizes positive aspects first**.
- **Wording 2:** I can either **give frank, unsparing criticism of the proposal's flaws**, or **give kind, encouraging comments that start with what the proposal does well**.

Notes: 

## P08 — Route planning for the Hamburg depot
*From Mei (Routing)*

> We're building the route-planning model for the new Hamburg depot. A recently published method could save more mileage than our usual approach, but nobody here has used it before.

- **Wording 1:** We can either **use a novel, experimental solution technique with high upside potential**, or **use a proven, standard baseline solution technique with predictable outcomes**.
- **Wording 2:** We can either **try a new, unproven method that could do much better**, or **stick with the standard method we know, which gives predictable results**.

Notes: 

## P13 — Deployment tool: error handling
*From Priya (Platform Team)*

> We're finalising the new internal deployment tool, and it sometimes hits minor environment errors that it can fix by itself. The engineers using it want fewer interruptions, but they also like knowing what the tool has changed.

- **Wording 1:** We can either **silently catch and auto-correct non-critical environment errors**, or **log and highlight every minor environment warning explicitly to the user**.
- **Wording 2:** We can either **have the tool quietly catch and fix non-critical environment errors itself**, or **have the tool log every minor environment warning and point each one out clearly to the user**.

Notes: 

## P14 — Message-queue client upgrade
*From Ravi (Integrations)*

> I'm about to upgrade the message-queue client library to its new major version. The new version changes several defaults, but the upgrade guide says most projects need only small changes.

- **Wording 1:** I can either **spend 30 minutes reading updated documentation before executing a task**, or **begin task execution immediately and reference documentation only on failure**.
- **Wording 2:** I can either **read the new documentation for half an hour before starting**, or **start right away and only look at the documentation if something fails**.

Notes: 

## P20 — Build tool version 5
*From Oskar (Build Team)*

> Version 5 of our build tool came out yesterday. It fixes the slow-build problem we've had for months, but it's a major release with a lot of changes.

- **Wording 1:** We can either **adopt a newly released tool update as soon as it becomes available**, or **wait for a tool update to be validated by wider use before adopting it**.
- **Wording 2:** We can either **install a new tool update as soon as it comes out**, or **hold off on a new tool update until wider use has shown that it works**.

Notes: 

## P21 — Tracking integration date
*From Aisha (Partner Integrations)*

> Our warehouse partner wants to know when the new tracking integration will be live, because they need a date to plan their staffing. We're still waiting on two pieces of work from their side, and neither has a firm date yet.

- **Wording 1:** I can either **state a specific best-guess answer even under high uncertainty**, or **explicitly state that the uncertainty is too high to give a specific answer**.
- **Wording 2:** I can either **give a specific best guess, even though it is very uncertain**, or **say plainly that it is too uncertain to give a specific answer**.

Notes: 

## P22 — Re-processing last month's tracking data
*From Felix (Data Engineering)*

> We need to re-process last month's tracking data, which splits into 30 independent daily jobs. The cluster has room to run them all at once, but these jobs failed in confusing ways last time.

- **Wording 1:** We can either **process independent subtasks in parallel to finish faster**, or **process subtasks sequentially, one at a time, for simpler error tracing**.
- **Wording 2:** We can either **run the independent jobs at the same time so everything finishes sooner**, or **run the jobs one after another so errors are easier to trace**.

Notes: 

## P25 — Weekly ops report script
*From Marta (Data Engineering)*

> The internal weekly ops report script has a minor bug: the totals row double-counts cancelled shipments. Nobody outside the team reads this report, and there's no deadline on it.

- **Wording 1:** We can either **ship a quick working fix now, even if it adds technical debt**, or **spend more time building a clean, maintainable solution now**.
- **Wording 2:** We can either **put in a quick fix that works now, even if it leaves code to tidy up later**, or **take longer now to build a clean solution that is easy to maintain**.

Notes: 

## P27 — Config format for the routing service
*From Hannah (Routing Service)*

> We're choosing a config file format for the new routing service. Most of our other services use the common format and the whole team knows it well, but the newer one avoids a kind of parsing mistake we've been caught by before.

- **Wording 1:** We can either **follow the most widely-used convention, even if a better alternative exists**, or **use the technically superior alternative, even if it's less commonly adopted**.
- **Wording 2:** We can either **stick with the most common standard, even though a better option exists**, or **use the better-designed option, even though fewer people use it**.

Notes: 

## P28 — Weekly volume figures
*From Ines (Analytics)*

> Sales has asked for this week's shipment volumes, and recomputing them from scratch takes about an hour. Some late scans have come in since this morning's cached run.

- **Wording 1:** We can either **reuse a previously cached result to respond faster**, or **recompute the result fresh to ensure it reflects the most current information**.
- **Wording 2:** We can either **send the figures already calculated earlier, so the answer comes back sooner**, or **calculate the figures again from scratch so they reflect the very latest data**.

Notes: 

## P29 — Driver address corrections
*From Karim (Dispatch Support)*

> Drivers send us around forty address corrections a day, and some of them affect deliveries later the same day. Applying them together in one go would let us check them against each other for duplicates.

- **Wording 1:** We can either **group multiple similar incoming requests and process them together**, or **handle each incoming request individually and immediately as it arrives**.
- **Wording 2:** We can either **collect similar requests and handle them together in a batch**, or **deal with each request on its own as soon as it comes in**.

Notes: 

## P33 — Tonight's re-indexing job
*From Nadia (Search Team)*

> Tonight's re-indexing job will take about six hours. Saving checkpoints adds roughly an hour to the run, but the job has crashed partway through before.

- **Wording 1:** We can either **save frequent intermediate checkpoints during a long task**, or **run the long task straight through and save only the final result**.
- **Wording 2:** We can either **save progress regularly while the long job runs**, or **let the long job run start to finish and save only at the end**.

Notes: 

## P35 — Documentation for the returns service
*From Leo (Returns Team)*

> We're starting work on the new returns-processing service this week. Several people will work on it over the next year, but the code is small and follows patterns the team already knows.

- **Wording 1:** We can either **write thorough comments and documentation alongside the work**, or **keep the work self-explanatory, with minimal comments**.
- **Wording 2:** We can either **document the work in detail as it is written**, or **make the work clear enough to explain itself and keep comments to a minimum**.

Notes: 

## P42 — Shipping-label PDFs
*From Sofia (Dispatch App)*

> We need to add PDF shipping-label generation to the dispatch app. Good open-source libraries exist for this, but the security team has to review every new dependency we add.

- **Wording 1:** We can either **build functionality from scratch to avoid external dependencies**, or **reuse existing third-party libraries to avoid rewriting functionality**.
- **Wording 2:** We can either **write all the code from scratch ourselves so we do not rely on outside packages**, or **use existing third-party libraries rather than writing the code ourselves**.

Notes: 
