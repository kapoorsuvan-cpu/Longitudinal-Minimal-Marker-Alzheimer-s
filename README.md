# Longitudinal-Minimal-Marker-Alzheimer's
# Minimal Marker Discovery for 2-Year Alzheimer’s Progression Prediction

This repository contains a longitudinal machine-learning pipeline for predicting **2-year MCI-to-dementia progression** using ADNI clinical, cognitive, APOE genotype, and FreeSurfer MRI-derived structural biomarkers.

The project is not simply asking whether a high-dimensional multimodal model can classify Alzheimer’s progression. The main question is:

> **How much clinical and imaging information is actually necessary to predict 2-year Alzheimer’s disease progression, and can a small leakage-resistant marker panel perform comparably to a full multimodal feature set?**

The motivation is clinical efficiency. In real-world neurology and memory-care settings, collecting many cognitive tests, MRI features, genetic markers, and biomarkers increases cost, time, patient burden, and missingness. This project tests whether a compact panel of high-value markers can preserve most of the predictive performance of larger models.

---

## Repository Goals

This pipeline is designed to answer the following research questions:

1. What is the best single marker for predicting 2-year MCI-to-dementia progression?
2. What is the best 2-marker panel?
3. What is the best 3-marker panel?
4. What is the best 5-marker panel?
5. How close do minimal panels get to full multimodal models?
6. Does MRI add meaningful value beyond clinical and cognitive tests?
7. Does a small clinical panel outperform MRI alone?
8. Which features are stable across top-performing panels?
9. What is the best accuracy-versus-testing-burden tradeoff?
10. Can these features generalize to unseen patients in a held-out patient-level test set?

---

## Data Sources

The project uses ADNI-derived CSV exports created from `.rda` files.

### Core longitudinal and diagnosis data

| File/table | Purpose |
|---|---|
| `DXSUM` | Diagnosis history used to identify CN, MCI, and dementia status over time |
| `VISITS` | Visit-code reference table |
| `REGISTRY` | Visit participation and study status information |
| `PTDEMOG` | Demographics such as sex, education, handedness, race/ethnicity, and marital status |

### Clinical and cognitive data

| File/table | Purpose |
|---|---|
| `NEUROBAT` | Neuropsychological test scores, including memory and executive-function measures |
| `UWNPSYCHSUM` | ADNI cognitive composite scores such as memory and executive-function composites |
| `GDSCALE` | Geriatric Depression Scale items |
| `NEUROEXM` | Neurological examination variables |

### Genetic data

| File/table | Purpose |
|---|---|
| `APOERES` | APOE genotype information |
| `GENETIC` | Additional genetic collection metadata, mostly filtered out unless biologically meaningful |

### MRI / FreeSurfer data

| File/table | Purpose |
|---|---|
| `UCSFFSX6` | FreeSurfer MRI structural measures from one ADNI processing version |
| `UCSFFSX7` | FreeSurfer MRI structural measures from a newer ADNI processing version |

### Biomarker data

Blood and CSF biomarker files were parsed as available, but the main analysis shown here does not yet include a finalized blood-biomarker feature group. The code structure allows biomarker tables to be added later.

---

## Target Cohort and Prediction Task

The prediction task is:

> Among patients who are MCI at an index visit, predict whether they convert to dementia within 2 years.

The final cohort contained:

| Outcome | Count |
|---|---:|
| Stable MCI within 2 years | 768 |
| Converter to dementia within 2 years | 261 |
| Total MCI index patients | 1,029 |

This is a clinically meaningful task because MCI is a transitional stage. Some patients remain stable, while others progress to dementia. Predicting which patients are more likely to convert can support risk stratification, follow-up planning, and trial enrichment.

---

## Leakage-Resistant Design

Several highly diagnosis-adjacent features were removed from the primary modeling set, including:

- MMSE
- MoCA
- CDR/CDRSB
- FAQ
- ADAS
- Explicit diagnosis or conversion variables

These variables can be useful clinically, but they are also close to the diagnostic criteria used to define dementia progression. Including them could inflate performance and make the model less scientifically meaningful.

The goal is not to prove that obvious diagnostic variables can predict diagnosis. The goal is to identify a smaller set of markers that provide useful progression signal while reducing leakage and testing burden.

---

# Pipeline Walkthrough

The notebook is organized as a sequence of cells. Each step below explains what the code does, why the decision was made, what data it uses, and what visualization should be added manually in the README or report.

---

## Cell 1: Imports and Configuration

### What the code does

Loads required Python packages for:

- Data handling: `pandas`, `numpy`
- Modeling: `scikit-learn`
- Cross-validation: `StratifiedGroupKFold`
- Metrics: ROC-AUC, PR-AUC, balanced accuracy, sensitivity, specificity, F1
- Visualization: `matplotlib`
- File organization: output and figure directories

### Why this coding decision matters

The pipeline uses standard, reproducible Python ML tools. Output directories are defined early so that all tables and figures are saved consistently.

### Data used

No dataset is transformed in this step. This cell only prepares the notebook environment.

### Biological implication

None directly. This cell supports reproducibility rather than biological interpretation.

### Visualization to add manually

No visualization is needed for this step.

---

## Cell 2: File Registry

### What the code does

Defines which ADNI CSV files should be loaded and grouped into core, clinical, cognitive, genetic, MRI, and biomarker categories.

### Why this coding decision matters

ADNI contains many tables, and not every table is needed for every experiment. A file registry keeps the pipeline organized and makes it easier to expand the project later.

### Data used

Examples of expected files include:

- `DXSUM.csv`
- `PTDEMOG.csv`
- `NEUROBAT.csv`
- `UWNPSYCHSUM.csv`
- `GDSCALE.csv`
- `APOERES.csv`
- `UCSFFSX6.csv`
- `UCSFFSX7.csv`

### Biological implication

The registry separates clinically different data types:

- Cognitive tests reflect patient-level function.
- APOE reflects genetic risk.
- MRI reflects structural neurodegeneration.

This separation is important because the project compares whether imaging adds value beyond lower-burden clinical markers.

### Visualization to add manually

Add a simple data-source diagram here.

Recommended figure:

```text
ADNI raw tables → diagnosis backbone → MCI index cohort → feature groups → models → minimal marker panels
```

Caption:

> Overview of the data flow. ADNI clinical, cognitive, genetic, and MRI tables are merged into a longitudinal MCI cohort, then evaluated through full-model baselines and minimal-marker search.

---

## Cell 3: Load CSV Files

### What the code does

Loads available CSV files into a dictionary of dataframes. It prints each loaded file name and shape.

### Why this coding decision matters

The loader is flexible. If optional files are missing, the notebook can continue with the files that are available. This is useful because ADNI exports vary depending on the downloaded package.

### Data used

In the current run, key loaded files included:

| Table | Rows | Columns |
|---|---:|---:|
| `DXSUM` | 15,881 | 42 |
| `NEUROBAT` | 14,599+ depending export | many cognitive variables |
| `UWNPSYCHSUM` | 11,519 | 12 |
| `PTDEMOG` | several thousand | demographics |
| `APOERES` | 3,008 | 17 |
| `UCSFFSX6` | 2,270 | 347 |
| `UCSFFSX7` | 12,151 | 348 |

### Biological implication

The large number of rows reflects ADNI’s longitudinal design: many patients have repeated visits. This supports progression modeling rather than a single cross-sectional classification snapshot.

### Visualization to add manually

Add a table or bar chart of loaded dataset sizes.

Recommended figure:

```text
Bar chart: table name on x-axis, number of rows on y-axis
```

Caption:

> Loaded ADNI tables vary widely in size. Diagnosis and cognitive tables have broader coverage, while MRI and genetic tables have lower or more uneven coverage.

---

## Cell 4: Data Audit

### What the code does

Audits each loaded dataframe for:

- Presence of `RID`
- Number of rows
- Number of columns
- Number of unique patients
- Available visit-code fields such as `VISCODE` or `VISCODE2`

### Why this coding decision matters

Longitudinal modeling requires correct patient and visit alignment. If a file does not contain `RID` or usable visit identifiers, it cannot be safely merged without additional mapping.

### Data used

All loaded CSV files are audited.

### Biological implication

Visit alignment matters because Alzheimer’s progression is time-dependent. A cognitive test or MRI scan must be linked to the correct point in the patient’s disease course.

### Visualization to add manually

Add a data-coverage heatmap.

Recommended figure:

```text
Rows: ADNI tables
Columns: RID available, VISCODE available, VISCODE2 available, EXAMDATE available
Cells: yes/no or percentage coverage
```

Caption:

> Data audit showing which tables contain patient identifiers and visit-level information needed for longitudinal merging.

---

## Cell 5: Visit Alignment Utilities

### What the code does

Defines helper functions to standardize visit codes and visit months. Examples include mapping visits such as baseline, month 6, month 12, and later follow-up visits into consistent numeric time points.

### Why this coding decision matters

ADNI tables do not always use visit labels consistently. Some MRI tables use labels such as `init`, `y1`, `v02`, or `v11`, while clinical tables may use `bl`, `m06`, `m12`, and similar labels. Standardizing visit timing reduces merge errors.

### Data used

Visit-code columns from diagnosis, clinical, cognitive, and MRI tables.

### Biological implication

Progression should be evaluated relative to a biologically meaningful timeline. A patient’s baseline memory score should not be accidentally merged with a much later MRI scan unless intentionally using nearest-date matching.

### Visualization to add manually

Add a visit timeline diagram.

Recommended figure:

```text
Baseline → 6 months → 12 months → 24 months → conversion window
```

Caption:

> Visits are standardized to months from index so that progression can be measured consistently across patients.

---

## Cell 6: Diagnosis Backbone

### What the code does

Builds a longitudinal diagnosis table using `DXSUM`. Each row represents a patient visit with diagnosis status:

- CN
- MCI
- Dementia

The current run produced diagnosis counts approximately:

| Diagnosis | Count |
|---|---:|
| MCI | 6,565 |
| CN | 6,275 |
| Dementia | 2,996 |

### Why this coding decision matters

This is the backbone of the longitudinal outcome. The project needs to know each patient’s diagnosis at each timepoint in order to identify MCI index visits and future conversion.

### Data used

`DXSUM.csv`

### Biological implication

The diagnosis trajectory captures disease progression. MCI patients who later become dementia cases represent the clinically important conversion group.

### Visualization to add manually

Add a diagnosis distribution bar chart.

Recommended figure:

```text
Bar chart: CN, MCI, Dementia visit counts
```

Caption:

> Diagnosis distribution across ADNI visits. MCI visits form the candidate pool for 2-year conversion prediction.

---

## Cell 7: Define 2-Year MCI Progression Label

### What the code does

Creates the main modeling cohort:

1. Finds patients who are MCI at an index visit.
2. Looks forward up to 24 months.
3. Labels the patient as a converter if dementia appears within the 2-year window.
4. Labels the patient as stable if no dementia conversion appears in the window.

The resulting cohort:

| Outcome | Count |
|---|---:|
| Stable MCI | 768 |
| Converter | 261 |
| Total | 1,029 |

### Why this coding decision matters

This creates the actual supervised-learning target. The use of a 2-year window is clinically realistic and avoids very long prediction horizons that are harder to interpret.

### Data used

Diagnosis backbone derived from `DXSUM`.

### Biological implication

Conversion from MCI to dementia is a meaningful disease-progression event. A 2-year horizon captures near-term risk, which is useful for clinical monitoring and trial enrollment.

### Visualization to add manually

Add an outcome distribution chart.

Recommended figure:

```text
Bar chart: Stable MCI vs Converter counts
```

Caption:

> Final prediction target. The model predicts which MCI patients convert to dementia within 2 years.

---

## Cell 8: Merge Clinical and Cognitive Features

### What the code does

Merges index-visit clinical and cognitive variables into the MCI cohort. Main sources include:

- `PTDEMOG`
- `NEUROBAT`
- `UWNPSYCHSUM`
- `NEUROEXM`
- `GDSCALE`

The merge preserves one row per patient.

Current output:

```text
Analysis after clinical/cognitive merge: 1,029 rows × 207 columns
```

### Why this coding decision matters

Clinical and cognitive features are the lower-burden markers being compared against imaging. The merge is performed at the index visit to avoid accidentally using future information.

### Data used

Clinical/cognitive tables aligned by `RID` and visit code.

### Biological implication

Cognitive features measure functional expression of neurodegeneration. Memory and executive-function decline often reflect underlying Alzheimer’s pathology and are directly relevant to dementia conversion.

### Visualization to add manually

Add a clinical-feature coverage chart.

Recommended figure:

```text
Horizontal bar chart: top clinical/cognitive variables by non-missing count
```

Caption:

> Coverage of clinical and cognitive variables at the MCI index visit. Variables with broader coverage are better candidates for low-burden prediction models.

---

## Cell 9: Merge APOE / Genetic Features

### What the code does

Merges APOE genotype information from `APOERES` into the modeling dataframe.

Current output:

```text
Analysis after APOE merge: 1,029 rows × 266 columns
```

The final genetic feature used was:

```text
APOERES__GENOTYPE
```

### Why this coding decision matters

APOE genotype is one of the best-established genetic risk factors for Alzheimer’s disease. Including it allows the model to test whether genetic risk improves prediction beyond cognitive performance.

### Data used

`APOERES.csv`

### Biological implication

APOE genotype, especially APOE ε4 carrier status, is associated with increased Alzheimer’s disease risk. However, APOE alone is not deterministic. In this project, APOE had some predictive value but was much weaker than memory-based cognitive markers.

### Visualization to add manually

Add an APOE genotype distribution chart.

Recommended figure:

```text
Bar chart: APOE genotype counts among the MCI cohort
```

Caption:

> APOE genotype distribution in the modeling cohort. APOE contributes genetic risk information but does not replace cognitive markers.

---

## Cell 10: Merge MRI / FreeSurfer Features

### What the code does

Merges FreeSurfer structural MRI features from:

- `UCSFFSX6`
- `UCSFFSX7`

Current output:

```text
Analysis after MRI merge: 1,029 rows × 916 columns
MRI columns added: 650
MRI non-missing rows: 699
Clean model shape: 1,029 rows × 889 columns
```

### Why this coding decision matters

MRI features are higher-burden biomarkers. They are expensive and less universally available than cognitive testing. The project tests whether they add meaningful predictive value beyond lower-burden clinical markers.

### Data used

FreeSurfer cortical and subcortical structural measures from `UCSFFSX6` and `UCSFFSX7`.

### Biological implication

Structural MRI can capture neurodegeneration, including cortical thinning and volume loss. Alzheimer’s disease commonly affects medial temporal, hippocampal, and association cortical regions. However, in this analysis, MRI-only models underperformed clinical/cognitive models, suggesting that structural imaging alone may be less efficient for this specific 2-year conversion task.

### Visualization to add manually

Add an MRI coverage chart.

Recommended figure:

```text
Bar chart: patients with MRI features vs patients without MRI features
```

Caption:

> MRI feature availability at the index visit. Only 699 of 1,029 patients had non-missing MRI features, which may affect the stability and usefulness of MRI-based models.

---

## Cell 11: Clean Modeling Dataset

### What the code does

Removes merge artifacts, suffix columns, duplicate patient rows, and metadata columns that should not be used for modeling.

Current output:

```text
Rows: 1,029
Unique RIDs: 1,029
Duplicate RIDs: 0
Clean model shape: 1,029 rows × 889 columns
```

### Why this coding decision matters

A patient-level prediction model should not include duplicate rows for the same patient. Duplicate rows could cause leakage across train and test folds.

### Data used

Merged clinical, genetic, and MRI dataframe.

### Biological implication

None directly, but clean patient-level data is necessary for valid biological interpretation. If the same patient appears in both training and testing data, the model can appear stronger than it really is.

### Visualization to add manually

Add a simple data-cleaning flow figure.

Recommended figure:

```text
Raw merged table → remove metadata → remove duplicates → final modeling table
```

Caption:

> Data-cleaning workflow used to create one leakage-resistant modeling row per MCI patient.

---

## Cell 12: Define Feature Groups and Remove Leakage

### What the code does

Creates strict feature groups:

| Feature group | Count |
|---|---:|
| Clinical/cognitive | 108 |
| MRI | 650 |
| Genetic | 1 |
| Blood | 0 |

The final groups were:

- `clinical_cols`
- `mri_cols`
- `genetic_cols`
- `blood_cols`

The code removes metadata and leakage-prone variables.

### Why this coding decision matters

Feature grouping allows direct comparison of clinical-only, MRI-only, genetic-only, and multimodal models. Leakage filtering makes the analysis more credible.

### Data used

The cleaned modeling dataset.

### Biological implication

The groups represent different biological and clinical information levels:

- Clinical/cognitive: functional impairment and neuropsychological performance
- Genetic: inherited risk
- MRI: structural neurodegeneration

Separating these groups helps test whether expensive biological measurements add value beyond simpler clinical tests.

### Visualization to add manually

Add a feature-group size chart.

Recommended figure:

```text
Bar chart: clinical = 108, MRI = 650, genetic = 1, blood = 0
```

Caption:

> Feature counts by modality after leakage filtering. MRI contributes many more variables than clinical and genetic data, increasing dimensionality and potential noise.

---

## Cell 13: Build Modeling Feature Sets

### What the code does

Builds feature-set combinations:

- Clinical only
- MRI only
- Genetic only
- Clinical + genetic
- Clinical + MRI
- Clinical + genetic + MRI

Current coverage:

| Feature set | Feature count | Rows with at least one non-missing feature |
|---|---:|---:|
| Clinical only | 108 | 1,029 / 1,029 |
| MRI only | 650 | 699 / 1,029 |
| Genetic only | 1 | 1,028 / 1,029 |
| Clinical + genetic | 109 | 1,029 / 1,029 |
| Clinical + MRI | 758 | 1,029 / 1,029 |
| Clinical + genetic + MRI | 759 | 1,029 / 1,029 |

### Why this coding decision matters

This step sets up the main comparison: whether adding MRI improves prediction enough to justify its greater burden.

### Data used

Clean feature groups from Cell 12.

### Biological implication

The comparison tests whether structural neurodegeneration markers add incremental value beyond cognitive symptoms and genetic risk.

### Visualization to add manually

Add a feature-set coverage chart.

Recommended figure:

```text
Grouped bar chart: feature count and row coverage for each feature set
```

Caption:

> Feature-set size and coverage. MRI-only data has lower patient coverage, while clinical and APOE variables cover nearly the full cohort.

---

## Cell 14: Baseline Grouped Cross-Validation Models

### What the code does

Evaluates several full feature sets using patient-level grouped cross-validation:

- Logistic regression with L1 penalty
- Logistic regression with L2 penalty
- Random forest
- Extra trees

The cross-validation uses patient-level grouping to prevent leakage.

### Why this coding decision matters

Grouped cross-validation ensures the same patient does not appear in both training and testing folds. This is essential for longitudinal patient data.

### Data used

All feature sets from Cell 13.

### Key results

| Feature set | Model | Mean ROC-AUC |
|---|---|---:|
| Clinical + genetic | Random forest | 0.820 |
| Clinical + MRI | Random forest | 0.816 |
| Clinical + genetic + MRI | Random forest | 0.815 |
| Clinical only | Random forest | 0.815 |
| Clinical + genetic | Logistic L1 | 0.801 |
| Clinical only | Logistic L1 | 0.792 |
| MRI only | Logistic L1 | 0.638 |

### Biological implication

Clinical and cognitive variables carried more predictive signal than MRI-only models. This suggests that functional cognitive expression of disease may be more useful than structural imaging alone for 2-year conversion prediction in this setup.

### Visualization to add manually

Add a baseline model comparison chart.

Recommended figure:

```text
Horizontal bar chart: feature set + model on y-axis, mean ROC-AUC on x-axis
```

Caption:

> Baseline cross-validation performance across feature sets. Clinical and clinical+genetic models outperform MRI-only models.

---

## Cell 15: Interpretable Baseline Using Logistic L1

### What the code does

Runs a cleaner baseline comparison using L1-penalized logistic regression across major feature sets.

### Why this coding decision matters

L1 logistic regression is more interpretable than random forests because it encourages sparse feature use. This matches the minimal-marker goal.

### Data used

Full clinical, MRI, genetic, and multimodal feature sets.

### Key results

| Feature set | Mean ROC-AUC |
|---|---:|
| Full clinical + genetic | 0.801 |
| Full clinical | 0.792 |
| Full multimodal | 0.754 |
| Full clinical + MRI | 0.744 |
| Full MRI | 0.638 |

### Biological implication

Adding all MRI features did not improve the interpretable model. This likely reflects high dimensionality, missingness, redundancy, and noise. It supports the hypothesis that more biomarkers do not automatically produce better clinical prediction.

### Visualization to add manually

Add a logistic-L1 baseline chart.

Recommended figure:

```text
Bar chart: full clinical+genetic, full clinical, full multimodal, full clinical+MRI, full MRI
```

Caption:

> Interpretable L1 logistic-regression baseline. Clinical and APOE features outperform MRI-heavy feature sets.

---

## Cell 16: Minimal-Marker Search Functions

### What the code does

Defines reusable functions for:

- Ranking single features
- Evaluating candidate panels
- Exhaustive search for 1- and 2-marker panels
- Forward selection for 3- and 5-marker panels

### Why this coding decision matters

Exhaustively testing every possible 5-feature combination would be computationally expensive. The pipeline first ranks features individually, then searches among top candidates. This balances search quality and runtime.

### Data used

Filtered clinical, genetic, and MRI candidate features.

### Biological implication

This step looks for compact marker sets, not simply the largest possible model. Biologically, it helps identify which markers may represent the strongest disease-progression signals.

### Visualization to add manually

Add a search-strategy diagram.

Recommended figure:

```text
Single-feature ranking → top candidates → exhaustive 1/2 marker search → forward 3/5 marker selection
```

Caption:

> Minimal-marker search strategy. The algorithm first identifies strong individual markers, then builds small panels that improve prediction while limiting testing burden.

---

## Cell 17: Run Minimal-Marker Search

### What the code does

Runs minimal-marker search across:

- Clinical + genetic features
- MRI features
- Clinical + genetic + MRI features

### Why this coding decision matters

This directly tests the project’s central question: can small panels match or outperform full feature sets?

### Data used

Candidate features from clinical/cognitive, APOE, and MRI feature groups.

### Key results

| Panel | Feature count | Mean ROC-AUC |
|---|---:|---:|
| Best 5-marker clinical + genetic + MRI | 5 | 0.819 |
| Best 5-marker clinical + genetic | 5 | 0.816 |
| Best 3-marker clinical + genetic + MRI | 3 | 0.815 |
| Best 3-marker clinical + genetic | 3 | 0.800 |
| Best 2-marker clinical + genetic + MRI | 2 | 0.799 |
| Best 2-marker clinical + genetic | 2 | 0.792 |

### Biological implication

The strongest marker was a delayed memory measure, and the best clinical-only panels were close to the best MRI-containing panels. This suggests that cognitive markers capture much of the near-term progression signal.

### Visualization to add manually

Add a minimal-panel performance chart.

Recommended figure:

```text
Line or bar chart: number of features on x-axis, ROC-AUC on y-axis, separate lines for clinical+genetic, MRI, and clinical+genetic+MRI
```

Caption:

> Minimal-marker panels approach full-model performance with far fewer variables. Clinical/APOE panels nearly match MRI-containing panels.

---

## Cell 18: Accuracy vs Testing Burden

### What the code does

Assigns each panel a testing-burden score and compares burden against ROC-AUC.

Example burden logic:

| Feature type | Burden interpretation |
|---|---|
| Cognitive/clinical marker | Low burden |
| APOE genotype | Low-to-moderate burden |
| MRI marker | Higher burden |

### Why this coding decision matters

A model with slightly higher AUC may not be clinically preferable if it requires expensive imaging. This step formalizes the efficiency tradeoff.

### Data used

Minimal-marker results from Cell 17.

### Key result

The 5-feature clinical/APOE panel achieved:

```text
AUC = 0.816
Burden score = 4.5
```

The 5-feature clinical/APOE/MRI panel achieved:

```text
AUC = 0.819
Burden score = 17.0
```

The difference in AUC was only 0.003, while testing burden was much higher for the MRI-containing panel.

### Biological implication

MRI may capture structural neurodegeneration, but in this task its incremental value was small once strong cognitive markers were already included. That supports a lower-burden clinical-first screening approach.

### Visualization to add manually

Add the scatter plot generated from Cell 18.

Recommended figure:

<img width="790" height="490" alt="5c6f3599-f6ea-440b-b89d-5a8a002d1ad1" src="https://github.com/user-attachments/assets/5a7f8df5-cbe1-498c-b7ab-a36ed08353d3" />


Caption:

> Predictive performance versus testing burden. Clinical/APOE panels achieve high AUC with much lower burden than MRI-containing panels.

---

## Cell 19: Ablation Analysis

### What the code does

Takes the best 5-feature panel and removes one feature at a time. The AUC drop after each removal estimates that feature’s contribution.

### Why this coding decision matters

Forward selection shows which features were selected, but ablation tests how important each selected feature actually is.

### Data used

Best 5-marker multimodal panel.

### Key results

| Removed feature | AUC drop |
|---|---:|
| `NEUROBAT__LDELTOTAL` | 0.0355 |
| `UWNPSYCHSUM__ADNI_MEM` | 0.0172 |
| `UCSFFSX7__ST99TA` | 0.0093 |
| `UCSFFSX7__ST88SV` | 0.0012 |
| `UCSFFSX7__ST13TA` | 0.0011 |

### Biological implication

Delayed memory was the most important feature. Removing it caused the largest performance loss. Two MRI markers had almost no effect when removed, suggesting they may be redundant or weak contributors.

### Visualization to add manually

Add an ablation bar chart.

Recommended figure:

```text
Horizontal bar chart: removed feature on y-axis, AUC drop on x-axis
```

Caption:

> Feature ablation shows that delayed memory contributes the most to prediction, while some MRI markers add minimal incremental value.

---

## Cell 20: Feature Stability

### What the code does

Counts how often each feature appears across top-performing minimal panels.

### Why this coding decision matters

A feature that appears repeatedly across strong panels is more reliable than a feature that appears only once.

### Data used

Top minimal-marker panels from Cell 17.

### Key stable features

| Feature | Interpretation |
|---|---|
| `NEUROBAT__LDELTOTAL` | Most stable delayed memory marker |
| `UCSFFSX7__ST99TA` | Stable FreeSurfer MRI marker |
| `UWNPSYCHSUM__ADNI_MEM` | Stable ADNI memory composite |
| `UCSFFSX7__ST29SV` | Repeated MRI marker |
| `APOERES__GENOTYPE` | Appears in some strong panels but is not dominant |

### Biological implication

The stability result reinforces the biological importance of memory decline in Alzheimer’s progression. MRI markers appear in strong panels, but the most stable signal is cognitive.

### Visualization to add manually

Add the feature-stability bar chart from Cell 20.

Recommended figure:

```text
Horizontal bar chart: feature name on y-axis, selection count across top panels on x-axis
```

<img width="990" height="490" alt="e0032619-fbdc-46d8-9204-86506decbb20" src="https://github.com/user-attachments/assets/d16eb87b-e2e8-4256-ad65-1395b2332b47" />


Caption:

> Feature stability across top panels. Delayed memory is the most consistently selected marker, supporting its central role in 2-year progression prediction.

---

## Cell 21: Final Holdout Evaluation

### What the code does

Evaluates the best minimal panel on a held-out patient-level test set. The split is patient-level, so no patient appears in both training and testing.

### Why this coding decision matters

Cross-validation estimates generalization, but a final holdout test provides a cleaner check on unseen patients.

### Data used

Best 5-feature minimal multimodal panel:

```text
NEUROBAT__LDELTOTAL
UCSFFSX7__ST99TA
UWNPSYCHSUM__ADNI_MEM
UCSFFSX7__ST88SV
UCSFFSX7__ST13TA
```

<img width="590" height="490" alt="51538369-80ef-426c-a16f-0f7560bb6f12" src="https://github.com/user-attachments/assets/16ff1f9d-ca56-4a1f-b57c-2fd6589dd727" />


### Key holdout results

| Metric | Value |
|---|---:|
| ROC-AUC | 0.806 |
| PR-AUC | 0.611 |
| Balanced accuracy | 0.755 |
| Sensitivity | 0.692 |
| Specificity | 0.819 |
| F1 | 0.621 |
| Train rows | 771 |
| Test rows | 258 |

<img width="391" height="358" alt="d5edd73e-f37a-4780-933d-90d22791ebe9" src="https://github.com/user-attachments/assets/9497c55b-1e5a-4abb-b5f1-71c0ea06dc10" />

Confusion matrix:

| Actual / Predicted | Stable | Converter |
|---|---:|---:|
| Stable | 158 | 35 |
| Converter | 20 | 45 |

### Biological implication

The model correctly identified about 69% of converters and about 82% of stable patients in the holdout set. This suggests the minimal panel captures real progression-related signal, but it is not perfect. In a clinical context, false negatives matter because missed converters may need closer monitoring.

### Visualization to add manually

Add two final validation figures from Cell 21.

Recommended figure 1:

```text
ROC curve for best minimal panel
```

Caption:

> Held-out test ROC curve for the best 5-feature minimal panel. The AUC of 0.806 indicates good discrimination between stable MCI patients and converters.

Recommended figure 2:

```text
Confusion matrix for best minimal panel
```

Caption:

> Holdout confusion matrix. The model correctly identified 45 of 65 converters and 158 of 193 stable MCI patients.

---

## Cell 22: Final Summary Questions

### What the code does

Summarizes the final answers to the project’s research questions, including:

- Best single marker
- Best 2-marker panel
- Best 3-marker panel
- Best 5-marker panel
- Minimal panels versus full multimodal models
- MRI value beyond clinical testing
- Stability and burden tradeoff

### Why this coding decision matters

This cell converts raw model results into scientific conclusions. It is the bridge between code outputs and the final report.

### Data used

Outputs from baseline models, minimal-marker search, burden analysis, ablation, stability, and holdout evaluation.

### Biological implication

The final interpretation is that delayed memory is the dominant signal, APOE adds modest genetic risk information, and MRI adds limited incremental improvement relative to its burden.

### Visualization to add manually

Add a final summary table.

Recommended figure/table:

```text
Rows: best single marker, best 2-marker panel, best 3-marker panel, best 5-marker clinical/APOE panel, best 5-marker multimodal panel, final holdout model
Columns: feature count, modalities, ROC-AUC, burden score, interpretation
```

Caption:

> Final summary of minimal-marker results. Compact clinical/APOE panels preserve most of the predictive value of higher-burden multimodal models.

---

# Main Results

## Best single marker

```text
NEUROBAT__LDELTOTAL
Mean ROC-AUC = 0.756
```

This delayed-memory marker was the strongest individual predictor and the most stable feature across top panels.

## Best 2-marker panel

```text
NEUROBAT__LDELTOTAL + UCSFFSX7__ST99TA
Mean ROC-AUC = 0.799
```

Best clinical-only 2-marker panel:

```text
NEUROBAT__LDELTOTAL + UWNPSYCHSUM__ADNI_MEM
Mean ROC-AUC = 0.792
```

## Best 3-marker panel

```text
NEUROBAT__LDELTOTAL + UCSFFSX7__ST99TA + UWNPSYCHSUM__ADNI_MEM
Mean ROC-AUC = 0.815
```

Best clinical/APOE 3-marker panel:

```text
NEUROBAT__LDELTOTAL + UWNPSYCHSUM__ADNI_MEM + GDSCALE__GDHOME
Mean ROC-AUC = 0.800
```

## Best 5-marker panel

```text
NEUROBAT__LDELTOTAL
UCSFFSX7__ST99TA
UWNPSYCHSUM__ADNI_MEM
UCSFFSX7__ST88SV
UCSFFSX7__ST13TA
Mean ROC-AUC = 0.819
```

## Best practical low-burden panel

```text
NEUROBAT__LDELTOTAL
UWNPSYCHSUM__ADNI_MEM
GDSCALE__GDHOME
UWNPSYCHSUM__ADNI_EF2
APOERES__GENOTYPE
Mean ROC-AUC = 0.816
```

This panel is likely the strongest practical result because it avoids MRI while nearly matching the best MRI-containing panel.

---

# Biological Interpretation of Key Features

## `NEUROBAT__LDELTOTAL`

This appears to represent delayed recall / delayed memory performance. It was the most important and most stable predictor.

Biological meaning:

- Delayed recall is closely tied to episodic memory.
- Episodic memory decline is a hallmark of prodromal Alzheimer’s disease.
- Poor delayed recall may reflect hippocampal and medial temporal lobe dysfunction.

## `UWNPSYCHSUM__ADNI_MEM`

This is an ADNI memory composite score.

Biological meaning:

- It summarizes memory performance across multiple tests.
- Composite scores can be more stable than single raw test scores.
- Its repeated selection suggests broad memory impairment is central to conversion risk.

## `UWNPSYCHSUM__ADNI_EF` / `UWNPSYCHSUM__ADNI_EF2`

These are executive-function composite scores.

Biological meaning:

- Executive dysfunction may indicate broader cortical involvement.
- Conversion from MCI to dementia often involves decline beyond memory alone.

## `APOERES__GENOTYPE`

This is APOE genotype.

Biological meaning:

- APOE ε4 is associated with increased Alzheimer’s risk.
- APOE was useful as an added risk marker but weak as a standalone predictor.
- Genetics contributes background risk, while cognition captures current disease expression.

## `UCSFFSX7__ST...` MRI features

These are FreeSurfer structural MRI features. They should be mapped to anatomical brain regions using the ADNI/UCSF FreeSurfer data dictionary before biological claims are made about specific regions.

Biological meaning:

- MRI structural features may reflect neurodegeneration, cortical thinning, or volume loss.
- MRI markers improved the best minimal panel only slightly over clinical/APOE markers.
- Some MRI markers had almost no ablation impact, suggesting redundancy or weak incremental value.

---

# Visualization Guide

Use this section to manually add figures after generating them from the notebook.

## Figure 1: Cohort outcome distribution

Place after the section **Cell 7: Define 2-Year MCI Progression Label**.

Shows:

```text
Stable MCI vs Converter counts
```

Caption:

> Distribution of the final 2-year progression outcome. The cohort contains 768 stable MCI patients and 261 converters.

## Figure 2: Baseline model comparison

Place after **Cell 14** or **Cell 15**.

Shows:

```text
Mean ROC-AUC by feature set and model
```

Caption:

> Baseline model comparison showing that clinical and clinical+genetic models outperform MRI-only models.

## Figure 3: Minimal panel performance

Place after **Cell 17**.

Shows:

```text
ROC-AUC by number of selected markers
```

Caption:

> Minimal-marker panels achieve strong performance with far fewer features than full models.

## Figure 4: Predictive performance vs testing burden

Place after **Cell 18**.

Shows:

```text
Testing burden score on the x-axis and mean ROC-AUC on the y-axis
```

Caption:

> Clinical/APOE panels provide the strongest efficiency tradeoff, achieving high AUC with much lower testing burden than MRI-containing panels.

## Figure 5: Ablation analysis

Place after **Cell 19**.

Shows:

```text
AUC drop after removing each feature from the best 5-feature panel
```

Caption:

> Ablation analysis shows that delayed memory is the most important feature in the best minimal panel.

## Figure 6: Feature stability

Place after **Cell 20**.

Shows:

```text
Selection count across top-performing panels
```

Caption:

> Feature stability analysis shows that delayed memory is the most consistently selected marker.

## Figure 7: Holdout ROC curve

Place after **Cell 21**.

Shows:

```text
ROC curve for the best minimal panel on the held-out patient-level test set
```

Caption:

> The best minimal panel achieved a held-out ROC-AUC of 0.806, supporting reasonable generalization to unseen patients.

## Figure 8: Holdout confusion matrix

Place after **Cell 21**.

Shows:

```text
Stable and converter predictions on the holdout set
```

Caption:

> The model correctly identified 45 of 65 converters and 158 of 193 stable MCI patients in the holdout set.

---

# Final Scientific Conclusion

This project shows that a small set of clinical, cognitive, genetic, and MRI markers can predict 2-year MCI-to-dementia progression with strong performance. The best 5-feature multimodal panel achieved a cross-validated ROC-AUC of 0.819 and a held-out ROC-AUC of 0.806.

However, the practical clinical finding is that a 5-feature clinical/APOE panel achieved nearly the same cross-validated performance at much lower testing burden:

```text
Best 5-feature clinical/APOE panel: AUC = 0.816
Best 5-feature clinical/APOE/MRI panel: AUC = 0.819
Difference: 0.003 AUC
```

The strongest and most stable predictor was delayed memory performance, consistent with the biological role of episodic memory decline in prodromal Alzheimer’s disease. MRI markers contributed to some top-performing panels, but their incremental value over cognitive and APOE markers was small in this analysis.

Overall, the results support the idea that **minimal marker panels can preserve most predictive performance while reducing testing burden**, which may be useful for clinical screening, risk stratification, and future Alzheimer’s progression modeling.

---

# Limitations

1. **MRI feature names need anatomical mapping.** FreeSurfer codes such as `ST99TA` should be mapped to brain regions before making region-specific biological claims.
2. **The analysis is ADNI-specific.** ADNI participants are not fully representative of all clinical populations.
3. **The 2-year conversion label depends on visit availability.** Patients without adequate follow-up may be harder to classify.
4. **Blood biomarkers were not finalized in the main model.** Future work should add plasma biomarkers if available.
5. **Minimal-marker selection can be sample-sensitive.** Stability analysis helps, but external validation is still needed.
6. **AUC does not replace clinical decision analysis.** Future work should examine calibration, decision curves, and clinically meaningful thresholds.

---

# Future Work

- Map FreeSurfer `ST` codes to anatomical brain regions.
- Add plasma biomarker features when available.
- Validate the minimal panels in an external dataset such as OASIS or another longitudinal cohort.
- Compare 1-year, 2-year, and 3-year progression horizons.
- Evaluate calibration and clinical decision thresholds.
- Test whether clinical/APOE panels can be used as a first-stage screen before MRI.

---

# Suggested Citation / Project Description

> This project uses longitudinal ADNI data to identify minimal clinical, cognitive, genetic, and MRI marker panels for predicting 2-year MCI-to-dementia progression. The analysis shows that compact clinical/APOE panels can nearly match the performance of MRI-containing multimodal models while substantially reducing testing burden.
