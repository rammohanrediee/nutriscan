# IFCT 2017 nutrition-data assessment

**Status:** Candidate source; numeric data not imported

**Reviewed:** 26 October 2026

## Source

*Indian Food Composition Tables 2017* (IFCT 2017) was published by the National Institute of
Nutrition, Indian Council of Medical Research. The book describes 528 foods across 20 food groups
and reports 151 food components. Its values are generally expressed per 100 g edible portion.

Official references:

- [ICMR-NIN IFCT 2017 PDF](https://www.nin.res.in/ebooks/IFCT2017.pdf)
- [ICMR-NIN publications and downloads](https://www.nin.res.in/downloads/index.html)

The project copy reviewed for this assessment is intentionally kept outside the repository. Do not
commit the PDF, extracted tables, OCR output, or converted nutrient records.

## Permission gate

The publication's copyright page encourages use and dissemination, and permits reproduction for
personal use with full acknowledgement. It separately states that storing or reproducing any part
in electronic format for creating a product requires prior written permission from the National
Institute of Nutrition.

NutriScan is a product, so the tables must not be imported into source control, a database, an app
bundle, backups, or generated seed files until the product owner has written permission covering
those uses. Public availability of the PDF does not by itself grant product-data rights.

Before import, retain the permission record outside the repository and document here:

- permitted commercial or non-commercial product use;
- electronic storage, transformation, backups, and deployment;
- whether derived values may be shown to end users;
- attribution wording and placement;
- redistribution and offline/mobile-cache limits;
- modification, correction, and update rights;
- effective date, expiry, and dataset/version covered.

## Product fit

IFCT is a strong candidate for canonical ingredient composition because it provides stable food
codes, scientific names, Indian-language names, analytical methods, INFOODS nutrient tags, units,
and variability information. Important interpretation rules include:

- values are based on the edible portion and generally use a 100 g basis;
- most entries describe raw foods; poultry and egg entries are exceptions described by the source;
- national values may be means of regional measurements, with standard deviation representing
  variation;
- a blank table cell means below the analytical method's detectable limit, not automatically zero;
- carbohydrate by difference and available carbohydrate are different measurements;
- the source is ingredient-oriented and cannot directly establish nutrition for a photographed
  prepared dish.

NutriScan must therefore keep the existing safety boundary:

1. Recognition produces an untrusted **Recognition Suggestion** with no nutrition.
2. The user reviews the suggested food and portion.
3. Catalog resolves the reviewed name to a canonical food or reviewed recipe.
4. Nutrition calculates values from a licensed composition source and confirmed quantities.

Prepared foods such as biryani, dosa, curry, or a mixed thali require a separately reviewed recipe
model with ingredient quantities, edible yield, and defensible cooking-retention rules. A raw IFCT
ingredient must not be silently substituted for a prepared dish.

## Future import contract

After both the model-selection gate and the permission gate pass, preserve source facts rather than
flattening them into anonymous calorie records. A future import should retain at least:

| Field | Purpose |
| --- | --- |
| Source dataset and edition | Provenance and repeatability |
| Source food code | Stable link back to the IFCT entry |
| Common, scientific, and regional names | Catalog resolution and review |
| Food group | Browsing and validation |
| Preparation state and edible basis | Prevent raw/cooked and portion errors |
| Nutrient INFOODS tag and display name | Unambiguous component identity |
| Numeric value and unit | Deterministic calculation |
| Mean/variation metadata | Avoid presenting estimates as exact facts |
| Missing-value reason | Distinguish below-detection from unknown |
| Source citation | User-visible attribution and auditability |

Use an authorized machine-readable export from NIN if one is available. Do not build production
data by OCRing the PDF: dense rotated tables, multi-page headers, blank-cell semantics, and
mean-plus-or-minus-standard-deviation values create avoidable transcription risk.

## Import acceptance checks

When import becomes authorized, require all of the following before the data is used:

- every row has a recognized source food code and food group;
- units and 100 g edible-basis metadata are explicit;
- raw and cooked/prepared states cannot be confused;
- below-detection, unavailable, and numeric zero remain distinct;
- source values and standard deviations are not collapsed into one number;
- nutrient tags are unique within each food record;
- a sample is independently checked against the official source;
- transformations, source version, checksum, and import timestamp are reproducible;
- tests cover unit conversion, portion scaling, missing values, and rounding;
- the UI identifies calculated nutrition as an estimate and shows the source attribution required
  by the permission agreement.

## Current decision

Do not import IFCT nutrient values yet. The immediate next step is to obtain written product-use
permission and, ideally, an official machine-readable dataset. Runtime schema, migrations, catalog
records, and calculation code remain deferred until the vision-model selection gate records a
winner.
