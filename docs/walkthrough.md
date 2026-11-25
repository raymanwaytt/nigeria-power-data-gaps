# Working notes: Nigeria's electricity figures

These are the notes I would want in front of me before explaining this project. The short version is in the README. This file is the reason for each choice.

## The question I actually asked

I started from a broad brief: Nigeria's generation and demand do not match across Ember, the IEA, the EIA and Nigerian official sources, the time series has breaks, and grid statistics miss captive diesel and petrol. After looking at the files, that was three projects. I kept one.

The question is whether Ember's published generation series for Nigeria can be used as a measure of electricity output. The test has four parts. Does it match the EIA series Ember says it comes from? Does it match the capacity Ember prints in the same file? Does it match what NERC publishes for the grid? And what do all of those still leave out?

I chose generation in terawatt-hours, not peak demand in megawatts, and not "electricity access". Access is a household concept. Peak demand is a single hour. Generation is the quantity every one of these publishers prints, so it is the quantity I can actually line up. I still check Ember's demand column, because Ember defines demand as generation plus net imports, and that identity is a useful test of whether the file is internally coherent. It is. The problem is elsewhere.

## Why these sources

**Ember** is the series an energy data team would actually open. The yearly page is public, the CSV is CC BY 4.0, and the methodology PDF has a country note. I used the global yearly file and the global monthly file, not a republished extract.

**The EIA** is not a second opinion I went looking for after Ember. Ember's Nigeria note says annual generation and net imports are taken from the EIA. If I compare Ember with the EIA and they differ, I have found either a vintage problem or an adjustment, not two independent measurements. That is a stronger finding than "two agencies disagree", and it is the one I can defend.

**Our World in Data** is a third public compilation, and its codebook says electricity comes from Ember, with the Energy Institute and historical sources also in the chain. I pinned the 10 September 2026 release (`garden/energy/2026-09-10`), not the URL that always means "whatever is latest". A moving URL would make the project unreproducible next month.

**NERC** is the Nigerian regulator. The quarterly and annual reports are the official account of grid-connected plants. I did not treat them as a check on Ember's arithmetic. They are a different boundary: plants on the Nigerian Electricity Supply Industry grid, not a national energy balance.

**The IEA statistical database** is the source people expect in this comparison. I could not download it. The Energy Statistics Data Browser returned HTTP 403, and Electricity Information is not an open file. I say that in the README rather than borrowing IEA totals from a secondary website. What I could download was the free *Africa Energy Outlook 2019*, which has a direct sentence on Nigerian back-up generators. That is an IEA analytical estimate, not the IEA electricity balance, and I label it as such.

**The World Bank production series** `EG.ELC.PROD.KH` is gone from the live API. The response was that the indicator was not found and may have been deleted or archived. I did not fill the gap with an old copy from memory. Access to electricity, `EG.ELC.ACCS.ZS`, did download: 62.5 per cent in 2024.

**TCN and the Nigerian Electricity Hub.** I did not find a stable machine-readable daily file I could archive. Ember's methodology already says the monthly series is TCN, with all thermal generation assumed to be gas, and with distributed generation, including solar, not captured. I use that statement as a claim about Ember's monthly file. I do not pretend I re-extracted TCN's own workbook.

## What I downloaded, and the check I refuse to skip

The EIA electricity CSV is 108,255,548 bytes. Nigeria is not near the start of the file. A connection that dies halfway can leave a CSV that opens, parses, and simply has no Nigeria rows. EIA's own metadata, dated 19 November 2026, publishes the byte size and a SHA-256. I hashed the download and matched `d1830e20b062c8d67dc50c62117c5dc0fc73579ce57593c6bba77829a0b93b26` before using a single Nigeria value. The full file is not in the git history because of its size. The ECOWAS slice is, and `data/raw/slices/manifest.json` stores both hashes so the slice can be tied back to the file I checked.

Everything else used in the tables was downloaded on 25 November 2026. The Ember yearly page listed a last update of 17 November 2026.

## The comparison, in the order I did it

### 1. Line the annual totals up, and do not smooth them

I kept Ember, the EIA and Our World in Data as separate columns. I did not average them. For the years when NERC has published an annual total, or a complete set of quarters, I added that too.

From 2000 through 2018 the Ember and EIA totals sit on top of each other. In 2015 the figures are 33.170 and 33.167 TWh. The first year the absolute gap exceeds 0.05 TWh is 2019. By 2024 Ember is 39.306 and the EIA is 40.836. By 2025 Ember is 45.561 and the EIA is 42.702. The sign flips. A chart that stops at "they are both about 40" would miss the only interesting part of the series.

I also checked each publisher's own identity, because a broken sum is a different bug from a boundary difference.

- Ember: demand minus (generation + net imports) stays inside 0.02 TWh. In 2024, generation 39.306 plus net imports of −2.3 equals demand of 37.006. The negative net imports mean Ember has Nigeria as a net exporter, which is at least directionally consistent with supply to neighbouring utilities. I did not audit those export contracts.
- EIA: generation minus (consumption + distribution losses + exports − imports) stays inside 0.05 TWh. So the EIA "generation" activity, in billion kilowatthours, is the supply that balances the rest of that file. Ember's methodology says it aims to report gross generation and that "EIA data represents gross generation". I repeat that claim. I do not relabel the EIA column as net or gross beyond what the balance shows, because the file itself only says "generation".

### 2. Split the gap by fuel before believing the total

This is the step I would insist on in a review. In 2024 the total gap is −1.53 TWh, which looks modest. The fuel gaps are not modest:

- Gas: Ember 28.170, EIA 29.726, difference −1.556
- Hydro: Ember 9.200, EIA 10.782, difference −1.582
- Solar: Ember 1.876, EIA 0.268, difference +1.608

They cancel. A dashboard that tracks only "total generation, Ember versus EIA" would stay green while every major fuel was wrong by about one and a half terawatt-hours. In 2023 the pattern is cleaner: gas and hydro almost match, and almost the entire +0.91 TWh total gap is solar (+0.87 TWh). In 2025 solar is +2.81 TWh, hydro is +1.01 TWh and gas is −0.96 TWh.

Our World in Data makes the solar point sharper, with a caveat. In 2024 its gas (28.17) and hydro (9.20) match the Ember file I downloaded, and its solar is 0.13 against Ember's 1.876. The gap in the totals, 39.306 − 37.560 = 1.746, is the same as the solar gap, 1.876 − 0.130. The same is true in 2023. I do not call that proof that Ember revised solar after Our World in Data's 10 September build, because Our World in Data also draws on the Energy Institute. I do say that whatever else is going on, the extra terawatt-hours in this Ember vintage are sitting in the solar row.

### 3. Ask whether the solar row can be physical

Capacity factor is generation divided by what the stated capacity would produce if it ran flat out all year.

`capacity factor = generation_TWh / (capacity_GW × hours_in_year / 1000)`

A gigawatt running for an hour is a gigawatt-hour. Divide by 1,000 to get terawatt-hours. I use 8,784 hours in 2020 and 2024 and 8,760 otherwise.

For Nigeria solar in the Ember yearly file:

| Year | Generation (TWh) | Capacity (GW) | Capacity factor |
| --- | ---: | ---: | ---: |
| 2019 | 0.147 | 0.05 | 34% |
| 2021 | 0.514 | 0.10 | 59% |
| 2023 | 1.099 | 0.17 | 74% |
| 2024 | 1.876 | 0.23 | 93% |
| 2025 | 3.184 | 0.28 | 130% |

I drew two reference lines, and neither is a borrowed "typical Nigerian solar" statistic. I do not have a metered capacity-factor series, and I did not invent one. The 100 per cent line is arithmetic: you cannot get more energy out than nameplate running every hour. The 50 per cent line is the daylight argument. Nigeria is between about 4°N and 14°N, so night is about half the year. A solar fleet with no storage produces nothing in those hours. If the capacity column is that fleet's nameplate, the capacity factor cannot exceed the daylight share, and in practice it will be well below it because nameplate is a laboratory irradiance, not an all-afternoon average. I do not need the tighter point to make the finding. 93 per cent and 130 per cent are already impossible on the night argument, and 130 per cent is impossible on the arithmetic.

So I flag the pair. I do not "correct" solar by applying a 20 per cent capacity factor to 0.23 GW and replacing Ember's generation. That would be me manufacturing a series. The honest output is: these two columns cannot be used together, and the generation figure should not be used as metered output of the published capacity until Ember or the underlying source explains it.

I then computed the same factor for the other ECOWAS countries in 2024. Several are above 50 per cent (Côte d'Ivoire, Benin, Sierra Leone, Guinea, Senegal). Nigeria is the highest, and it is the only one above 100 per cent in 2025. This is not a Nigeria typo sitting in an otherwise clean regional file. It is a regional solar problem that is worst in Nigeria. I say that explicitly so I am not accused of picking the country and then finding a unique scandal in the total. The total gap is not unique. The solar factor is the extreme.

### 4. Do not add the months up and call it the year

Ember's methodology has two sentences I checked are actually in the PDF, not just in a summary I remembered.

- "Monthly generation is taken from TCN. All thermal power generation is assumed to be Gas. Distributed generation, including Solar, is not captured in monthly data."
- "Simply summing up monthly values will not produce the same results as our annual values for any given year."

The second sentence is an instruction. I still did the sum, because the size of the miss is the finding. Complete years only:

| Year | Sum of months (TWh) | Annual file (TWh) | Months / annual |
| --- | ---: | ---: | ---: |
| 2019 | 23.542 | 36.557 | 64% |
| 2022 | 32.045 | 38.601 | 83% |
| 2024 | 33.611 | 39.306 | 86% |
| 2025 | 39.868 | 45.561 | 88% |

The 2019 ratio is the sort of break that gets waved through in a regional model and then dominates a Nigeria chart. Gas and hydro are what the annual file scales up. Solar is not: the monthly solar sum and the annual solar figure match to 0.002 TWh. So the methodology's comfort — "distributed solar is missing from the monthly file" — does not explain this solar row. The implausible solar number is already in the monthly file. The annual file then adds several terawatt-hours of gas and hydro on top.

I left 2026 out of every annual comparison. The monthly file has January to August only. Annualising eight months would be a forecast, and I am not making one.

### 5. Read NERC as NERC, not as a correction factor

NERC's 2024 annual report says total generation was 37,093.70 GWh, from an average hourly generation of 4,222.87 MWh/h, and that hydro contributed 11,469.85 GWh (30.92 per cent). Average available capacity was 4,853.69 MW and the availability factor was 37.43 per cent. The 2025 report says 39,208.68 GWh, hydro 12,804.18 GWh (32.66 per cent), available capacity 5,398.33 MW, availability factor 39.62 per cent.

I use those gigawatt-hour totals as published. I do not recompute them from the hourly average, although the arithmetic is the one NERC prints (hourly average times 24 times days).

Hydro is a useful warning against assuming NERC is just "Ember, but smaller". In 2024 NERC's hydro (11.47 TWh) is *above* Ember (9.20) and the EIA (10.78), even though NERC's total is below both. The grid series is not a subset of the international series with the same fuel split. If I applied one scale factor to every fuel, I would invent a hydro error in the wrong direction.

Availability is a second boundary, and I keep it in megawatts so I do not mix it into the terawatt-hour chart. Implied nameplate is available capacity divided by the availability factor: 4,853.69 / 0.3743 ≈ 12,970 MW in 2024, and 5,398.33 / 0.3962 ≈ 13,630 MW in 2025. Ember's total capacity column is 15.40 GW and 15.45 GW. I report the implied figure as mine, from NERC's two published inputs. NERC did not print "installed capacity was 12.97 GW" in the sentence I used. Ember's capacity note for Nigeria says coal and gas come from GEM and the rest from IRENA, which is not the same plant list as NERC's grid-connected fleet.

For 2023 I do not have an annual report in the set I downloaded. I added the four quarters: 9,350.24 + 8,867.05 + 8,664.82 + 9,789.87 = 36,671.98 GWh. I label that as a sum. The Q2 PDF would not yield text reliably, so 8,867.05 GWh is the figure the Q3 report states for the previous quarter. I cross-checked Q3: the Q3 report's own total and the Q4 report's look-back agree within 0.05 GWh. Where they had not, I would have stopped rather than picked one.

For 2025 I did both. The four quarters sum to 39,193.93 GWh. The annual report says 39,208.68 GWh. The difference is 14.75 GWh, about 0.04 per cent. I keep both numbers. An official series can fail to match itself at the level of a rounding or a late revision. That is worth a sentence in a footnote. It is not an explanation of Ember being 6.35 TWh higher than the annual report.

I did not build a 2022 annual total. The 2022 report gives 3,988 MWh/h as the average, and a table gives 3,944 MW. Those are not the same, and neither is an annual gigawatt-hour NERC printed. Annualising one of them would look, in a chart, like the same kind of point as 37,093.70. It is not.

### 6. Captive generation stays in its own column

This is the part that is easy to overclaim, so I was stricter here than anywhere else.

The grid figures above are on the order of 37 to 46 TWh in recent years. Published work says a large further quantity exists and is mostly unseen by those systems.

- **IEA, Africa Energy Outlook 2019, Box 1.5.** I checked the sentence in the PDF: Nigeria generated 18 TWh in 2018 from about 9 GW of back-up generation, almost half of an estimated 40 TWh from 40 GW across sub-Saharan Africa, equal to 8 per cent of electricity generation in that region. This is IEA analysis of back-up generators. It is one year, 2018. It is not a line I can extend to 2024.
- **World Bank, 2014 diesel-genset inventory.** The low-carbon study they cite put total self-generation at 16,360 GWh in 2009, covering diesel, gas and gasoline. Their own work, across sectors and years around 2007–2012, gives a range of 5,240 to 20,380 GWh. The text says it is not accurate to compare or aggregate across sectors, and that they did it only to see the magnitude. The width of the range is mostly two different methods for the commercial sector. A diesel-only band of 3,262 to 3,423 GWh sits inside that and excludes most gasoline generators, which are the common household sets. I plot the wide range and the diesel-only band and the 16.36 TWh point. I do not replace the range with its midpoint.
- **IFC, 2019.** The summary says Nigeria's back-up fleet is conservatively 15–20 GW, against grid capacity of 5–15 GW. The full report, after adjusting import data with household and business surveys, says 2.8 million residential sites and 210 thousand commercial sites, 13 GW, and $5.4 billion of fuel a year. It also says generators account for over 40 per cent of electricity consumed in western Africa, and that Nigeria is 16 per cent of back-up energy service among the low- and middle-income countries modelled. The same report gives that modelled generation as 120 TWh with a wide uncertainty band. I do not multiply 16 per cent by 120. The report does not print the product, the 16 per cent is not given an uncertainty, and a derived 19 TWh would look like a third official estimate. It would be mine.

Figure 5 draws the 2024 grid totals and these older estimates on one axis so the scale is obvious. The caption says they are not additive. I would rather the chart be slightly uncomfortable than have a false stacked bar called "true Nigerian generation".

A 2026 market note I opened repeated the 18 TWh and attributed it to the Africa Energy Outlook. I did not use that note as a source. Repeating a 2018 estimate in 2026 does not make it a 2026 measurement.

## West Africa, so Nigeria is not the whole story

I included the fifteen ECOWAS members. Two comparisons, both for 2024.

Generation per person, using Ember's total and Our World in Data's population, puts Nigeria at 169 kWh. Ghana is 718. Cabo Verde is higher still, on a very small system. Sierra Leone, Niger and Guinea-Bissau are lower. Nigeria is a large country with a small grid series, which is the context, not the data bug.

The Ember-minus-EIA percentage gap is worse in several neighbours than in Nigeria. Mali is about +44 per cent, Cabo Verde about −44 per cent, Niger about −26 per cent, Côte d'Ivoire about −21 per cent. Nigeria is −3.7 per cent, close to Ghana's −3.7 per cent. I included that chart so I would not walk into a conversation claiming Nigeria's headline total was uniquely broken. The defensible Nigeria-specific points are the solar capacity factor, the NERC comparison, and the size of the captive fleet in the studies above.

## What I would hand to someone who had to publish a number

If they asked "what did the Nigerian grid produce in 2024?", I would say 37.1 TWh, NERC, grid-connected plants, and I would add the hydro share and the available capacity, because 4.9 GW available against a much larger nameplate is the operational fact. I would not say 39.3.

If they asked "what do the international series say?", I would show Ember 39.3, EIA 40.8 and Our World in Data 37.6, state that Ember's note points at the EIA, and show the fuel table. I would not pick the middle value.

If they asked "what should the solar share be?", I would say I do not know, and that Ember's solar row cannot be used until the capacity factor is explained. The EIA's 0.27 TWh is at least physically possible next to 0.23 GW. That is not the same as saying the EIA is correct.

If they asked "how much electricity did Nigeria really generate, including generators?", I would say the grid series is an incomplete lower bound on a quantity nobody meters, and I would quote the IEA's 18 TWh for 2018 and the World Bank's 5 to 20 TWh range with the years attached. I would not add them to 2024.

## What I could not get

- IEA electricity balances, as a time series. Browser: HTTP 403.
- World Bank `EG.ELC.PROD.KH`. The indicator is no longer in the API.
- A TCN or Nigerian Electricity Hub file I could put in `data/raw` and parse.
- A clean text layer for the 2023 Q2 NERC PDF. The quarter is taken from the following report.
- A NERC annual total for 2023 in the documents I fetched. The 2023 figure is a sum of quarters.
- Any metered national total for captive diesel and petrol. The studies are models and inventories. Treating them as meter data would be the mistake this project is about.

## The rule I am willing to say out loud

When two energy series disagree, the first job is to decide whether they are trying to measure the same thing. If they are, and the publisher says one is copied from the other, a gap is a vintage or an adjustment and it has to be split by fuel. If a fuel then implies a machine that cannot exist, that fuel is flagged, not repaired. If a third series is the grid operator, it gets its own column, not a scaling factor. And the electricity that never goes through the grid does not get quietly added at the end.
