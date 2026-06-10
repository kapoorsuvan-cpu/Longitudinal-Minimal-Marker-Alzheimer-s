# ADNI MCI Progression Prediction Project

## Project Title

**Stepwise and Minimal-Marker Prediction of 2-Year MCI-to-Dementia Progression Using ADNI Data**

---

## 1. Project Overview

This project studies whether we can predict which people with **mild cognitive impairment (MCI)** will progress to **dementia within 2 years** using data from ADNI.

The project combines two related analyses into one coherent research story:

1. **Minimal-marker modeling**  
   This asks: *Can a small, practical set of clinical, cognitive, genetic, or MRI markers predict progression nearly as well as larger models?*

2. **Stepwise phenotyping modeling**  
   This asks: *How much predictive value is gained as we add increasingly complex data layers, such as MMSE, MoCA, broader cognitive testing, APOE genotype, MRI, and biomarkers?*

Together, the project evaluates both **prediction accuracy** and **testing burden**. The goal is not just to find the highest-performing model, but also to understand whether simpler and more practical clinical/cognitive data capture most of the predictive signal.

---

## 2. Main Research Question

**Among ADNI participants with mild cognitive impairment, how accurately can baseline clinical, cognitive, genetic, MRI, and biomarker information predict 2-year progression to dementia, and how much incremental value is gained from each additional phenotyping layer?**

---

## 3. Secondary Research Questions

This project also asks:

1. Which small marker panels best predict 2-year MCI-to-dementia conversion?
2. Does adding MRI improve prediction beyond cognitive testing and APOE genotype?
3. Do amyloid/tau biomarkers improve prediction beyond clinical and cognitive data?
4. Is the full multimodal model meaningfully better than lower-burden models?
5. Can baseline data predict continuous cognitive decline over 2 years, such as MMSE change, MoCA change, or CDR-SB change?

---

## 4. Why This Matters

MCI is a clinically important stage because some people remain stable while others progress to dementia. A useful prediction model could help identify higher-risk individuals earlier.

However, different data types have very different practical burdens:

| Data Type | Practical Burden |
|---|---|
| Demographics | Low |
| Clinical history / symptom scales | Low to moderate |
| Cognitive testing | Moderate |
| APOE genotype | Moderate; requires genetic testing |
| MRI | Higher; requires imaging |
| Biomarkers | Higher; may require blood, CSF, PET, specialized assays, or added cost |

Because of this, the project evaluates not only the best-performing model, but also whether the performance gain from higher-burden data is large enough to justify the added complexity.

---

## 5. Data Source

The project uses ADNI data exported from `.rda` files into CSV format.

The included R script:

```r
Parse_R_Files_Longitudinal_Minimal_Markers.R
```

converts selected ADNI `.rda` files into CSVs inside:

```text
csv_exports/
```

The script is designed to export the ADNI files needed for diagnosis, visits, demographics, cognitive testing, APOE genotype, MRI, and biomarkers.

Important CSVs include:

| Data Layer | Example CSVs |
|---|---|
| Diagnosis / visit structure | `DXSUM.csv`, `VISITS.csv`, `REGISTRY.csv`, `ADSL.csv` |
| Demographics | `PTDEMOG.csv`, `RMT_PTDEMOG.csv` |
| Cognitive / clinical tests | `MMSE.csv`, `MOCA.csv`, `CDR.csv`, `NEUROBAT.csv`, `UWNPSYCHSUM.csv`, `FAQ.csv`, `ADAS.csv`, `GDSCALE.csv` |
| Genetics | `APOERES.csv`, `RMT_APOERES.csv`, `GENETIC.csv` |
| MRI / FreeSurfer | `UCSFFSX6.csv`, `UCSFFSX7.csv`, `UCSFFSX.csv` |
| Biomarkers | `UPENNBIOMK_MASTER.csv`, `UPENNBIOMK_ROCHE_ELECSYS.csv`, `UPENNPLASMA.csv`, `UGOTPTAU181.csv`, `C2N_PRECIVITYAD2_PLASMA.csv`, `FUJIREBIOABETA.csv`, `FUJIREBIOABETAPLASMA.csv` |

---

## 6. Repository / Package Contents

| File or Folder | Purpose |
|---|---|
| `ADNI_progression_full_combined_pipeline.ipynb` | Main combined notebook |
| `README.md` | This project explanation |
| `Parse_R_Files_Longitudinal_Minimal_Markers.R` | Converts ADNI `.rda` files into CSVs |
| `csv_exports/` | Folder where required CSVs should be placed |
| `outputs_stepwise/` or `outputs/` | Model results and output tables |
| `figures_stepwise/` or `figures/` | Saved visualizations |
| `csv_manifest_required.csv` | List of CSV files needed for a full run |
| `stepwise_best_classification_summary.csv` | Best classification results by feature step |
| `best_regression_summary.csv` | Best regression results for continuous outcomes |

---

## 7. Cohort Definition

The primary cohort consists of ADNI participants whose **index visit** is their first observed MCI visit.

### Primary Outcome

The main prediction target is:

```text
2-year MCI-to-dementia conversion
```

Participants are labeled as:

| Label | Meaning |
|---|---|
| `1` | Converted from MCI to dementia within 24 months |
| `0` | Remained stable through 24 months with enough follow-up |

A hybrid outcome rule is used:

- Keep anyone who converted to dementia within 24 months.
- Keep stable participants only if they had enough follow-up to confirm no dementia conversion through the 24-month window.
- Exclude participants without enough follow-up to confidently label them stable.

This avoids incorrectly labeling short-follow-up patients as stable.

### Final Primary Cohort

| Outcome | Count |
|---|---:|
| Stable MCI | 743 |
| Converted to dementia | 261 |
| Total | 1,004 |

---

## 8. Diagnosis Harmonization

The diagnosis backbone was built from `DXSUM.csv`.

Raw ADNI diagnosis values were harmonized into:

| Harmonized Label | Meaning |
|---|---|
| `CN` | Cognitively normal |
| `MCI` | Mild cognitive impairment |
| `DEM` | Dementia |

Simplified code:

```python
def harmonize_dx_value(x):
    s = str(x).strip().upper()

    if s in ["CN", "NORMAL", "COGNITIVELY NORMAL"]:
        return "CN"
    if "MCI" in s:
        return "MCI"
    if s in ["DEM", "DEMENTIA"] or "DEMENTIA" in s:
        return "DEM"

    return np.nan
```

Diagnosis visit counts after harmonization:

| Diagnosis | Visit Count |
|---|---:|
| MCI | 6,565 |
| CN | 6,275 |
| Dementia | 2,996 |

The harmonized diagnosis backbone included **3,777 unique participants**.

---

## 9. How the MCI Conversion Outcome Was Built

For each participant:

1. Sort all diagnosis visits by time.
2. Find the first visit where diagnosis is MCI.
3. Treat that visit as the prediction baseline.
4. Look forward 24 months.
5. Label the participant as a converter if dementia appears within that window.

Simplified code:

```python
mci_visits = g[g["dx"] == "MCI"]
index_row = mci_visits.iloc[0]

after = g[g["visit_month"] > index_month].copy()
after["months_after_index"] = after["visit_month"] - index_month

window = after[
    (after["months_after_index"] > 0) &
    (after["months_after_index"] <= 24)
]

converted_within_window = (window["dx"] == "DEM").any()
```

Stable cases were only retained if they had enough follow-up:

```python
if converted_within_window:
    y = 1
elif max_follow >= 24:
    y = 0
else:
    continue
```

Plain-English interpretation:

> A person is labeled as a converter if dementia is observed within 2 years. A person is labeled stable only if they were followed long enough to confirm that dementia did not occur within 2 years.

---

## 10. Feature Groups

The project organizes features into clinically meaningful layers.

| Step | Feature Set | Plain-English Meaning |
|---|---|---|
| 01 | Demographics | Basic patient background variables |
| 02 | Demographics + basic clinical | Adds clinical symptom variables such as geriatric depression scale items |
| 03 | Demographics + MMSE | Adds a brief global cognitive screen |
| 04 | Demographics + MoCA | Adds another brief global cognitive screen |
| 05 | Demographics + MMSE + MoCA | Combines brief cognitive screens |
| 06 | Demographics + CDR | Adds CDR global and CDR Sum of Boxes |
| 07 | Demographics + broad cognitive battery | Adds detailed cognitive test measures |
| 08 | Simple screens + broad cognitive | Combines MMSE/MoCA and broader cognitive testing |
| 09 | Cognitive + APOE | Adds genetic risk |
| 10 | Cognitive + APOE + MRI | Adds structural MRI features |
| 11 | Cognitive + APOE + biomarkers | Adds amyloid/tau/plasma/CSF-type biomarkers |
| 12 | Cognitive + APOE + MRI + biomarkers | Full multimodal model |

This structure allows us to measure the incremental value of each added data layer.

---

## 11. Feature Cleaning and Leakage Prevention

The analysis removes or avoids variables that could create misleading results.

### Why leakage matters

Data leakage happens when a model is accidentally given information that would not be available at prediction time or that directly encodes the outcome.

For example, if a diagnosis-related field or future measurement is included as a predictor, the model may look accurate but would not be valid in real-world use.

### Metadata removed

Administrative or non-biological fields were removed from modeling feature groups.

Examples include:

```python
bad_biomarker_terms = [
    "BATCH", "COMMENT", "COMMENTS", "GUSPECID", "VID", "RUNDATE",
    "DRAWDTE", "EXAMDATE", "ORIGPROT", "COLPROT", "PTID",
    "UPDATE", "STAMP", "SPECIMEN", "SITE"
]
```

MRI metadata and image identifiers were also removed:

```python
bad_mri_terms = [
    "IMAGEUID", "EXAMDATE", "RUNDATE", "STATUS",
    "OVERALLQC", "TEMPQC", "FRONTQC", "PARQC", "INSULAQC"
]
```

### Final cleaned feature groups

After cleanup:

| Feature Group | Number of Features |
|---|---:|
| Demographics | 9 |
| Basic clinical | 17 |
| MMSE | 1 |
| MoCA | 44 |
| CDR | 2 |
| Broad cognitive | 52 |
| APOE | 1 |
| MRI | 652 |
| Biomarkers | 27 to 29 depending on final exclusions |

---

## 12. Machine Learning Models

### Classification models

Used for predicting 2-year MCI-to-dementia conversion:

| Model | Why It Was Used |
|---|---|
| Logistic regression with L1 penalty | Interpretable model that can select features |
| Logistic regression with L2 penalty | Stable linear baseline |
| Random forest | Captures nonlinear relationships and feature interactions |
| Extra trees | Similar to random forest but more randomized; useful robustness comparison |

### Regression models

Used for predicting continuous score change:

| Model | Why It Was Used |
|---|---|
| Linear regression | Simple interpretable baseline |
| Ridge regression | Linear model with regularization |
| Random forest regressor | Nonlinear model for continuous outcomes |
| Extra trees regressor | Robust nonlinear comparison model |

---

## 13. Cross-Validation

The project uses 5-fold cross-validation.

For classification:

```python
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

Plain-English explanation:

> The data are split into five parts. The model trains on four parts and tests on the remaining part. This repeats five times, so every participant is tested once. The reported result is the average across all five test folds.

This reduces the chance that results are driven by one lucky train/test split.

---

## 14. Evaluation Metrics

### Classification Metrics

| Metric | Meaning |
|---|---|
| ROC-AUC | How well the model ranks converters above stable patients |
| PR-AUC | Useful when converters are less common than stable patients |
| Sensitivity | Of true converters, how many the model detects |
| Specificity | Of stable patients, how many the model correctly identifies |
| Balanced accuracy | Average of sensitivity and specificity |
| F1 score | Balance of precision and sensitivity |

### Regression Metrics

| Metric | Meaning |
|---|---|
| R² | Percent of score-change variance explained by the model |
| RMSE | Typical prediction error, with larger errors penalized more |
| MAE | Average absolute prediction error |
| Median absolute error | Typical error less affected by outliers |

---

## 15. Main Classification Results

### Best Overall Model

| Feature Set | Model | ROC-AUC | PR-AUC | Sensitivity | Specificity |
|---|---|---:|---:|---:|---:|
| Cognitive + APOE + MRI + biomarkers | Random forest | 0.826 | 0.638 | 0.395 | 0.926 |

The full multimodal model had the highest ROC-AUC.

However, sensitivity was lower than specificity. This means:

> At the default threshold, the best random forest model was better at identifying stable MCI patients than detecting all future converters.

For clinical screening, threshold tuning would be needed if the goal is to detect more converters.

---

## 16. Best ROC-AUC by Phenotyping Step

| Step | Feature Set | Best Model | ROC-AUC | PR-AUC |
|---|---|---|---:|---:|
| 01 | Demo only | Logistic L1 | 0.563 | 0.301 |
| 02 | Demo + basic clinical | Logistic L2 | 0.588 | 0.317 |
| 03 | Demo + MMSE | Logistic L1 | 0.626 | 0.351 |
| 04 | Demo + MoCA | Logistic L1 | 0.661 | 0.388 |
| 05 | Demo + MMSE + MoCA | Logistic L1 | 0.705 | 0.415 |
| 06 | Demo + CDR | Logistic L1 | 0.682 | 0.404 |
| 07 | Demo + broad cognitive | Random forest | 0.804 | 0.585 |
| 08 | Screens + broad cognitive | Random forest | 0.811 | 0.592 |
| 09 | Cognitive + APOE | Random forest | 0.814 | 0.603 |
| 10 | Cognitive + APOE + MRI | Random forest | 0.823 | 0.637 |
| 11 | Cognitive + APOE + biomarkers | Random forest | 0.821 | 0.629 |
| 12 | Cognitive + APOE + MRI + biomarkers | Random forest | 0.826 | 0.638 |

### Interpretation

The largest jump occurred when the model added the **broad cognitive battery**.

Plain-English takeaway:

> Detailed cognitive testing carried the strongest predictive signal. APOE, MRI, and biomarkers added additional information, but the improvement after cognition was smaller.

---

## 17. Minimal-Marker Results

The minimal-marker analysis tested whether smaller feature panels could perform nearly as well as larger multimodal models.

| Panel | Approximate AUC |
|---|---:|
| Best single marker: delayed memory total | 0.756 |
| Best clinical 2-marker panel | 0.792 |
| Best clinical 3-marker panel | 0.800 |
| Best clinical/APOE 5-marker panel | 0.816 |
| Best multimodal 5-marker panel | 0.819 |

Best clinical/APOE 5-marker panel:

- `NEUROBAT__LDELTOTAL`
- `UWNPSYCHSUM__ADNI_MEM`
- `GDSCALE__GDHOME`
- `UWNPSYCHSUM__ADNI_EF2`
- `APOE`-derived genotype/risk information

Best multimodal 5-marker panel:

- `NEUROBAT__LDELTOTAL`
- `UCSFFSX7__ST99TA`
- `UWNPSYCHSUM__ADNI_MEM`
- `UCSFFSX7__ST88SV`
- `UCSFFSX7__ST13TA`

Comparison:

| Model | AUC |
|---|---:|
| Clinical/APOE 5-marker | 0.816 |
| Multimodal 5-marker | 0.819 |
| Difference | +0.003 |

### Interpretation

> A compact clinical/APOE marker panel captured nearly the same predictive performance as a more burdensome multimodal MRI-containing panel.

---

## 18. Testing Burden Analysis

The project compares model performance against approximate testing burden.

General burden logic:

| Data Layer | Burden |
|---|---|
| Demographics | Lowest |
| Clinical variables | Low |
| Cognitive testing | Moderate |
| APOE | Moderate |
| MRI | Higher |
| Biomarkers | Higher |

### Main burden finding

| Model Type | Interpretation |
|---|---|
| Cognitive + APOE | Strong practical balance |
| Cognitive + APOE + MRI | Slightly higher AUC but higher burden |
| Cognitive + APOE + biomarkers | Slightly higher AUC but higher burden |
| Full multimodal | Highest AUC and highest burden |

Plain-English conclusion:

> If the only goal is maximum AUC, the full multimodal model is best. If the goal is a practical lower-burden model, cognitive + APOE features capture much of the signal.

---

## 19. Continuous Cognitive Decline Outcomes

The stepwise notebook also tested whether baseline data could predict continuous score changes over about 2 years.

Outcomes:

- `MMSE_change_2yr`
- `MOCA_change_2yr`
- `CDRSB_change_2yr`

Sample sizes:

| Outcome | Sample Size |
|---|---:|
| MMSE 2-year change | 892 |
| CDR-SB 2-year change | 898 |
| MoCA 2-year change | 136 |

### Best Regression Models

| Outcome | Best Feature Set | Best Model | R² | RMSE | MAE |
|---|---|---|---:|---:|---:|
| MMSE change | Cognitive + APOE + MRI + biomarkers | Extra trees | 0.230 | 2.64 | 1.98 |
| CDR-SB change | Cognitive + APOE + MRI | Random forest | 0.165 | 1.66 | 1.20 |
| MoCA change | Cognitive + APOE + MRI | Random forest | 0.041 | 2.91 | 2.25 |

### Interpretation

Continuous score-change prediction was weaker than binary conversion prediction.

Plain-English explanation:

> It is easier to predict whether someone converts to dementia within 2 years than to predict the exact number of MMSE, MoCA, or CDR-SB points they will change by.

MoCA should be treated as exploratory because only 136 participants had complete 2-year MoCA data.

---

## 20. LASSO Feature Stability

LASSO was used as an interpretable model to identify features selected consistently across cross-validation folds.

Stable selected features included:

- Delayed memory measures
- MMSE score
- MoCA delayed recall items
- APOE4 count
- Amyloid/tau biomarkers
- Plasma pTau181

The best stable interpretable feature set was:

```text
Cognitive + APOE + biomarkers
```

Interpretation:

> The interpretable model did not require MRI to identify a stable predictor set. Much of the stable signal came from memory/cognitive performance, APOE genetic risk, and amyloid/tau biology.

Caution:

> Some demographic one-hot variables were selected, but these should not be interpreted as causal. They may reflect cohort composition, site effects, or missingness patterns.

---

## 21. Biological Interpretation in Simple Terms

The biological interpretation is intentionally cautious.

### What the results suggest

1. **Memory measures are strong predictors.**  
   Alzheimer’s disease often affects memory-related function early, so delayed memory performance being predictive is clinically plausible.

2. **APOE4 adds risk information.**  
   APOE4 is a known genetic risk marker for Alzheimer’s disease. Here, it added some predictive value beyond cognitive testing.

3. **Amyloid and tau biomarkers add disease-biology information.**  
   Amyloid and tau markers are related to Alzheimer’s pathology. Their stable selection supports the idea that biological disease markers help prediction.

4. **MRI adds incremental value.**  
   MRI features improved AUC slightly, but the gain was not large compared with cognitive features.

### What not to overclaim

Do not claim:

- The model proves causality.
- Demographic variables cause progression.
- Specific MRI regions are biologically important until FreeSurfer ST codes are mapped.
- The model is ready for clinical deployment.

Better wording:

> The results suggest that cognitive performance, APOE genetic risk, and amyloid/tau biomarker measures provide complementary information for predicting 2-year MCI progression in ADNI. MRI features add incremental predictive value, but anatomical interpretation requires mapping FreeSurfer feature codes to brain regions.

---

## 22. Key Visualizations

Recommended figures to include when presenting this project:

1. **Diagnosis counts across harmonized ADNI visits**  
   Shows the distribution of CN, MCI, and dementia visits.

2. **Primary outcome distribution**  
   Shows stable MCI vs converted-to-dementia counts.

3. **Stepwise classification performance**  
   Shows how ROC-AUC improves as phenotyping layers are added.

4. **Incremental AUC gain**  
   Shows which added layer produced the largest performance jump.

5. **Performance vs testing burden**  
   Shows the tradeoff between model performance and data collection burden.

6. **MMSE, MoCA, and CDR-SB 2-year change distributions**  
   Shows continuous cognitive/clinical progression patterns.

7. **LASSO feature stability**  
   Shows which features were repeatedly selected across cross-validation folds.

---

## 23. How to Run the Project

### Step 1: Export ADNI `.rda` files to CSV

Run this in R:

```r
source("Parse_R_Files_Longitudinal_Minimal_Markers.R")
```

This creates:

```text
csv_exports/
```

and saves a conversion log:

```text
csv_exports/conversion_log.csv
```

### Step 2: Confirm required CSVs exist

At minimum, the full pipeline expects:

```text
DXSUM.csv
PTDEMOG.csv
MMSE.csv
MOCA.csv
CDR.csv
GDSCALE.csv
NEUROBAT.csv
UWNPSYCHSUM.csv
FAQ.csv
ADAS.csv
APOERES.csv
UCSFFSX6.csv
UCSFFSX7.csv
UPENNBIOMK_MASTER.csv
UPENNBIOMK_ROCHE_ELECSYS.csv
UPENNPLASMA.csv
C2N_PRECIVITYAD2_PLASMA.csv
FUJIREBIOABETA.csv
FUJIREBIOABETAPLASMA.csv
UGOTPTAU181.csv
```

### Step 3: Open the notebook

Open:

```text
ADNI_progression_full_combined_pipeline.ipynb
```

### Step 4: Set paths if needed

The notebook expects:

```python
CSV_DIR = Path("csv_exports")
OUTPUT_DIR = Path("outputs_stepwise")
FIG_DIR = Path("figures_stepwise")
```

If your local folder is different, update `CSV_DIR`.

### Step 5: Run all cells

The notebook will:

1. Load ADNI CSV files.
2. Harmonize diagnosis labels.
3. Build the MCI index cohort.
4. Define 2-year conversion.
5. Define MMSE, MoCA, and CDR-SB 2-year change outcomes.
6. Merge baseline/index-visit features.
7. Clean metadata and leakage-prone variables.
8. Build stepwise feature sets.
9. Train and evaluate classification models.
10. Run testing-burden analysis.
11. Train regression models for continuous decline.
12. Run LASSO feature stability.
13. Export summary tables and figures.

---

## 24. Reproducibility Notes

- Random seed: `RANDOM_STATE = 42`
- Classification: 5-fold stratified cross-validation
- Regression: 5-fold cross-validation
- Missing numeric values are imputed.
- Missing categorical values are imputed as `"missing"`.
- Categorical variables are one-hot encoded.
- Numeric variables are scaled for linear/logistic models.
- Tree models are evaluated through the same pipeline framework for consistency.

---

## 25. Limitations

Important limitations:

1. **ADNI is a research cohort.**  
   Results may not generalize directly to all clinical populations.

2. **MRI feature codes need anatomical mapping.**  
   FreeSurfer `ST` codes should be mapped before making region-level biological claims.

3. **Biomarker availability is incomplete.**  
   Some biomarker models may use fewer effective observations or rely heavily on imputation.

4. **MoCA change sample is small.**  
   MoCA regression should be treated as exploratory.

5. **Prediction is not causation.**  
   Selected features are predictive, not necessarily causal.

6. **The model is not ready for clinical deployment.**  
   External validation and threshold tuning would be required.

---

## 26. Final Takeaway

This project shows that 2-year MCI-to-dementia progression can be predicted in ADNI with moderate-to-strong discrimination.

The best full multimodal model achieved:

```text
ROC-AUC ≈ 0.826
```

However, the most important practical finding is:

> Broad cognitive testing produced the largest improvement, and cognitive + APOE features captured much of the predictive signal. MRI and biomarkers added incremental value, but the gains were smaller relative to their added testing burden.

The minimal-marker analysis supports the same conclusion:

> A compact clinical/APOE marker panel performed nearly as well as a more burdensome multimodal MRI-containing panel.

Overall:

> **Cognitive phenotyping is the strongest practical predictor of 2-year MCI-to-dementia conversion in this ADNI analysis. APOE, MRI, and biomarkers provide complementary information, but their incremental gains should be weighed against testing burden. Continuous cognitive decline is harder to predict than binary conversion, with modest results for MMSE and CDR-SB change and weak exploratory results for MoCA change.**
