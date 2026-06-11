# ADNI MCI Progression Prediction Project

## A unified analysis of minimal-marker and stepwise multimodal prediction of 2-year MCI-to-dementia progression

---

## 1. Executive Summary

This project evaluates whether baseline ADNI data can predict which individuals with **mild cognitive impairment (MCI)** will progress to **dementia within 2 years**, and whether most of that predictive signal can be captured with lower-burden clinical and cognitive markers rather than requiring the full multimodal data stack.

The analysis combines two related modeling strategies into one unified framework:

1. **Minimal-marker modeling** asks whether small, practical marker panels can predict 2-year MCI-to-dementia conversion nearly as well as larger models.
2. **Stepwise multimodal modeling** asks how predictive performance changes as additional phenotyping layers are added: demographics, clinical variables, MMSE, MoCA, broader cognitive testing, APOE genotype, MRI, and biomarkers.

Together, these analyses address the same central question:

> **How accurately can 2-year MCI-to-dementia progression be predicted from baseline ADNI data, and how much additional value is gained by moving from low-burden cognitive/clinical markers to higher-burden multimodal data?**

The main result is that the **full multimodal model achieved the highest performance**, but the largest predictive gain came from **broad cognitive testing**, and compact clinical/APOE marker panels captured much of the performance of more complex multimodal models.

The best full model achieved:

```text
ROC-AUC = 0.826
PR-AUC = 0.638
```

But a much smaller clinical/APOE 5-marker panel achieved:

```text
AUC = 0.816
```

while the best multimodal 5-marker panel achieved:

```text
AUC = 0.819
```

The difference between those compact 5-marker models was only:

```text
+0.003 AUC
```

This suggests that although MRI and biomarkers add useful information, much of the practical prediction signal in this ADNI MCI cohort comes from cognitive performance and APOE-related risk.

---

## 2. Research Question and Framing

### Main research question

**Among ADNI participants with MCI, can baseline clinical, cognitive, genetic, MRI, and biomarker data predict 2-year progression to dementia, and what is the tradeoff between predictive performance and testing burden?**

### Why both notebooks belong together

The two original notebooks are not separate projects. They answer complementary parts of the same question.

The **minimal-marker notebook** focuses on parsimony:

> If we had to choose only a few predictors, which ones would retain most of the predictive value?

The **stepwise phenotyping notebook** focuses on incremental value:

> If we add richer data layers one at a time, which layer produces the largest improvement?

Together, they create a coherent research design:

| Analysis Component | Purpose | Main Question |
|---|---|---|
| Minimal-marker modeling | Finds compact practical panels | How few markers can still predict well? |
| Stepwise phenotyping | Tests incremental value of richer data | Which data layers add meaningful performance? |
| Burden analysis | Compares accuracy against practical feasibility | Are higher-burden modalities worth the gain? |
| Regression outcomes | Tests continuous decline prediction | Can models predict amount of cognitive/clinical change? |
| LASSO stability | Identifies interpretable stable predictors | Which features are consistently selected? |

This README treats them as one integrated analysis rather than two separate workflows.

---

## 3. Data and Cohort

The analysis uses ADNI data exported from `.rda` files into CSV format. The included R script converts selected ADNI `.rda` files into `csv_exports/`, including diagnosis, demographic, cognitive, APOE, MRI, biomarker, and related clinical data.

Key input domains:

| Domain | Example Files | Role in Analysis |
|---|---|---|
| Diagnosis / visits | `DXSUM.csv`, `VISITS.csv`, `REGISTRY.csv`, `ADSL.csv` | Define longitudinal diagnosis history |
| Demographics | `PTDEMOG.csv` | Background covariates |
| Cognitive / clinical | `MMSE.csv`, `MOCA.csv`, `CDR.csv`, `NEUROBAT.csv`, `UWNPSYCHSUM.csv`, `FAQ.csv`, `ADAS.csv`, `GDSCALE.csv` | Core prediction signal |
| Genetics | `APOERES.csv` | APOE-derived genetic risk |
| MRI | `UCSFFSX6.csv`, `UCSFFSX7.csv` | Structural MRI features |
| Biomarkers | `UPENNBIOMK_MASTER.csv`, `UPENNBIOMK_ROCHE_ELECSYS.csv`, `UPENNPLASMA.csv`, `UGOTPTAU181.csv`, `C2N_PRECIVITYAD2_PLASMA.csv`, `FUJIREBIOABETA.csv` | Amyloid/tau/plasma/CSF-related measures |

The main cohort was built by identifying each participant’s first MCI visit and using that as the index visit for prediction.

---

## 4. Outcome Definition

The primary outcome was **2-year MCI-to-dementia conversion**.

A participant was labeled as:

| Label | Definition |
|---|---|
| `1` | Converted from MCI to dementia within 24 months of the index MCI visit |
| `0` | Remained stable without dementia through 24 months, with adequate follow-up |

The labeling logic used a hybrid approach:

```python
window = after[
    (after["months_after_index"] > 0) &
    (after["months_after_index"] <= 24)
]

converted_within_window = (window["dx"] == "DEM").any()

if converted_within_window:
    y = 1
elif max_follow >= 24:
    y = 0
else:
    continue
```

This rule keeps known converters while avoiding the mistake of labeling short-follow-up participants as stable.

The final cohort was:

| Outcome | Count |
|---|---:|
| Stable MCI | 743 |
| Converted to dementia | 261 |
| Total | 1,004 |

### Figure 1: Primary outcome distribution

Bar chart showing the number of stable MCI participants and converters.

> **Figure 1. Primary outcome distribution.** The final 2-year MCI conversion cohort included 1,004 participants: 743 stable MCI participants and 261 who converted to dementia within 24 months.


```markdown
<img width="1200" height="800" alt="diagnosis_counts" src="https://github.com/user-attachments/assets/0eb9b0af-3624-47c0-b16f-d74e2aecbb89" />
```

---

## 5. Broad Methodology

The analysis follows one unified modeling pipeline:

1. Harmonize longitudinal diagnosis labels.
2. Identify each participant’s first MCI visit.
3. Define 2-year conversion status.
4. Merge baseline/index-visit predictors.
5. Clean metadata and leakage-prone variables.
6. Build feature groups representing increasing phenotyping complexity.
7. Evaluate prediction models using cross-validation.
8. Compare full multimodal performance against lower-burden and minimal-marker alternatives.
9. Evaluate secondary continuous decline outcomes.
10. Interpret stable predictors using LASSO feature selection.

The goal was not simply to maximize accuracy. The goal was to understand the relationship between:

```text
Predictive performance
    vs.
Data burden / clinical practicality
```

---

## 6. Diagnosis Harmonization

Diagnosis data were harmonized from `DXSUM.csv` into three major categories:

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

After harmonization, the diagnosis backbone contained:

| Diagnosis | Visit Count |
|---|---:|
| MCI | 6,565 |
| CN | 6,275 |
| Dementia | 2,996 |

The diagnosis backbone included:

```text
15,836 usable diagnosis visits
3,777 unique participants
```

---

## 7. Feature Design

The models were built using feature sets that reflect increasingly complex phenotyping.

| Feature Layer | Reason for Inclusion |
|---|---|
| Demographics | Basic adjustment variables |
| Basic clinical variables | Low-burden symptom and clinical context |
| MMSE | Simple global cognitive screen |
| MoCA | Additional brief cognitive screen |
| CDR / CDR-SB | Clinical severity and functional staging |
| Broad cognitive battery | Detailed memory, language, and executive-function measures |
| APOE | Genetic risk information |
| MRI | Structural brain measures |
| Biomarkers | Amyloid/tau/plasma/CSF-related disease biology |

The cleaned feature groups included approximately:

| Group | Feature Count |
|---|---:|
| Demographics | 9 |
| Basic clinical | 17 |
| MMSE | 1 |
| MoCA | 44 |
| CDR | 2 |
| Broad cognitive | 52 |
| APOE | 1 |
| MRI | 652 |
| Biomarkers | 27–29 |

---

## 8. Leakage and Metadata Control

The modeling pipeline excludes fields that could create artificial performance.

Examples include:

- Diagnosis labels
- Future outcomes
- Visit timing artifacts
- IDs
- Batch labels
- Comments
- Administrative metadata
- MRI image identifiers
- Non-biological biomarker metadata

Example cleanup logic:

```python
bad_biomarker_terms = [
    "BATCH", "COMMENT", "COMMENTS", "GUSPECID", "VID", "RUNDATE",
    "DRAWDTE", "EXAMDATE", "ORIGPROT", "COLPROT", "PTID",
    "UPDATE", "STAMP", "SPECIMEN", "SITE"
]

bad_mri_terms = [
    "IMAGEUID", "EXAMDATE", "RUNDATE", "STATUS",
    "OVERALLQC", "TEMPQC", "FRONTQC", "PARQC", "INSULAQC"
]
```

Plain-English rationale:

> The model should learn from clinical, cognitive, biological, and imaging information, not from file IDs, batch labels, comments, or administrative artifacts.

---

## 9. Machine Learning Strategy

The project used both interpretable and nonlinear models.

### Classification models

| Model | Role |
|---|---|
| Logistic regression with L1 penalty | Interpretable model with feature selection |
| Logistic regression with L2 penalty | Stable linear baseline |
| Random forest | Nonlinear model capturing interactions |
| Extra trees | More randomized tree model for robustness |

### Regression models

| Model | Role |
|---|---|
| Linear regression | Simple continuous-outcome baseline |
| Ridge regression | Regularized linear regression |
| Random forest regressor | Nonlinear prediction of score change |
| Extra trees regressor | Robust nonlinear comparison |

Classification was evaluated with 5-fold stratified cross-validation:

```python
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

This means each participant is tested once across five held-out folds, giving a more reliable estimate than a single train/test split.

---

## 10. Primary Classification Results

The full stepwise analysis showed a clear pattern: performance increased as richer phenotyping layers were added.

| Step | Feature Set | Best Model | ROC-AUC | PR-AUC | Sensitivity | Specificity |
|---|---|---|---:|---:|---:|---:|
| 01 | Demo only | Logistic L1 | 0.563 | 0.301 | 0.663 | 0.456 |
| 02 | Demo + basic clinical | Logistic L2 | 0.588 | 0.317 | 0.686 | 0.464 |
| 03 | Demo + MMSE | Logistic L1 | 0.626 | 0.351 | 0.778 | 0.447 |
| 04 | Demo + MoCA | Logistic L1 | 0.661 | 0.388 | 0.602 | 0.658 |
| 05 | Demo + MMSE + MoCA | Logistic L1 | 0.705 | 0.415 | 0.743 | 0.611 |
| 06 | Demo + CDR | Logistic L1 | 0.682 | 0.404 | 0.831 | 0.459 |
| 07 | Demo + broad cognitive | Random forest | 0.804 | 0.585 | 0.376 | 0.917 |
| 08 | Screens + broad cognitive | Random forest | 0.811 | 0.592 | 0.387 | 0.910 |
| 09 | Cognitive + APOE | Random forest | 0.814 | 0.603 | 0.387 | 0.922 |
| 10 | Cognitive + APOE + MRI | Random forest | 0.823 | 0.637 | 0.398 | 0.931 |
| 11 | Cognitive + APOE + biomarkers | Random forest | 0.821 | 0.629 | 0.395 | 0.925 |
| 12 | Cognitive + APOE + MRI + biomarkers | Random forest | 0.826 | 0.638 | 0.395 | 0.926 |

### Figure 2: Stepwise ROC-AUC performance

> **Stepwise ROC-AUC by phenotyping layer.** Model performance increased from AUC 0.563 using demographics alone to AUC 0.826 using the full multimodal feature set. The largest improvement occurred when broad cognitive features were added.


```markdown
<img width="2400" height="1000" alt="stepwise_auc_bar" src="https://github.com/user-attachments/assets/a9f45672-9a7b-4c3b-9b37-a887f31b795a" />```

### Interpretation

The main pattern is:

```text
Demographics alone: weak prediction
Brief cognitive screens: moderate improvement
Broad cognitive battery: large improvement
APOE/MRI/biomarkers: smaller incremental gains
Full multimodal model: best overall AUC
```

The strongest jump occurred when broad cognitive features were added:

```text
CDR sensitivity model AUC: 0.682
Broad cognitive model AUC: 0.804
```

This suggests that detailed cognitive testing carried the strongest practical signal for predicting 2-year conversion.

---

## 11. Best Full Model

The highest-performing model was:

| Feature Set | Model | ROC-AUC | PR-AUC | Sensitivity | Specificity |
|---|---|---:|---:|---:|---:|
| Cognitive + APOE + MRI + biomarkers | Random forest | 0.826 | 0.638 | 0.395 | 0.926 |

This model had high specificity but lower sensitivity.

Plain-English interpretation:

> The best full model was good at identifying stable MCI participants, but at the default threshold it missed a meaningful number of converters.

This is not necessarily a failure of the model. It means the threshold is conservative. If the goal were to screen for likely converters, threshold tuning would be needed.

---

## 12. Incremental Value and Burden

The stepwise analysis showed that MRI and biomarkers improved AUC, but only modestly after cognition and APOE.

| Feature Set | ROC-AUC |
|---|---:|
| Cognitive + APOE | 0.814 |
| Cognitive + APOE + MRI | 0.823 |
| Cognitive + APOE + biomarkers | 0.821 |
| Cognitive + APOE + MRI + biomarkers | 0.826 |

This pattern suggests:

```text
Cognitive + APOE already captures much of the predictive signal.
MRI adds a small additional improvement.
Biomarkers add a small additional improvement.
The full multimodal model performs best, but at higher testing burden.
```

### Figure 3: Incremental AUC gain

Suggested caption:

> **Incremental AUC gain by added data layer.** Broad cognitive features contributed the largest performance gain, while APOE, MRI, and biomarkers added smaller improvements.

Suggested Markdown:

```markdown
<img width="2400" height="800" alt="incremental_auc_gain" src="https://github.com/user-attachments/assets/1b42dee0-90f2-4bdb-a20d-10c28961b230" />
```

### Figure 4: Performance vs testing burden

> ** Predictive performance versus testing burden.** Cognitive + APOE provided a strong balance between accuracy and feasibility, while MRI and biomarkers increased model burden for smaller incremental gains.

Suggested Markdown:

```markdown
<img width="2400" height="800" alt="incremental_auc_gain" src="https://github.com/user-attachments/assets/edc89e68-7dd0-4423-be4a-e964169f0422" />
```

---

## 13. Minimal-Marker Results

The minimal-marker analysis asked whether compact panels could retain most of the predictive performance.

| Marker Panel | Approximate AUC |
|---|---:|
| Best single marker: delayed memory total | 0.756 |
| Best clinical 2-marker panel | 0.792 |
| Best clinical 3-marker panel | 0.800 |
| Best clinical/APOE 5-marker panel | 0.816 |
| Best multimodal 5-marker panel | 0.819 |

### Best clinical/APOE 5-marker panel

- `NEUROBAT__LDELTOTAL`
- `UWNPSYCHSUM__ADNI_MEM`
- `GDSCALE__GDHOME`
- `UWNPSYCHSUM__ADNI_EF2`
- APOE-derived genotype/risk information

### Best multimodal 5-marker panel

- `NEUROBAT__LDELTOTAL`
- `UCSFFSX7__ST99TA`
- `UWNPSYCHSUM__ADNI_MEM`
- `UCSFFSX7__ST88SV`
- `UCSFFSX7__ST13TA`

The key comparison:

| Model | AUC |
|---|---:|
| Clinical/APOE 5-marker | 0.816 |
| Multimodal 5-marker | 0.819 |
| Difference | +0.003 |

### Figure 5: Minimal-marker panel comparison

> ** Minimal-marker model comparison.** A compact clinical/APOE 5-marker panel achieved AUC 0.816, nearly matching the best multimodal 5-marker panel at AUC 0.819.

```markdown
<img width="1200" height="1000" alt="best_minimal_roc" src="https://github.com/user-attachments/assets/580de212-4ec0-4322-bb1e-a3f22b2f8e9e" />
```

### Interpretation

The minimal-marker results align with the stepwise results.

Both analyses show that:

```text
Cognitive features are central.
APOE adds useful risk information.
MRI can improve performance but may not dramatically outperform compact clinical/APOE panels.
```

This is the key reason the two notebooks should be interpreted together.

---

## 14. Continuous Decline Results

The project also tested whether baseline data could predict continuous 2-year cognitive or clinical score changes.

Outcomes:

- `MMSE_change_2yr`
- `CDRSB_change_2yr`
- `MOCA_change_2yr`

Sample sizes:

| Outcome | Sample Size |
|---|---:|
| MMSE 2-year change | 892 |
| CDR-SB 2-year change | 898 |
| MoCA 2-year change | 136 |

Best regression results:

| Outcome | Best Feature Set | Best Model | R² | RMSE | MAE |
|---|---|---|---:|---:|---:|
| MMSE change | Cognitive + APOE + MRI + biomarkers | Extra trees | 0.230 | 2.64 | 1.98 |
| CDR-SB change | Cognitive + APOE + MRI | Random forest | 0.165 | 1.66 | 1.20 |
| MoCA change | Cognitive + APOE + MRI | Random forest | 0.041 | 2.91 | 2.25 |

### Figure 6: Regression performance for continuous decline

> **Best regression performance for continuous 2-year decline outcomes.** MMSE and CDR-SB showed modest predictability, while MoCA prediction was weak and exploratory due to smaller sample size.

```markdown
<img width="2400" height="1000" alt="mmse_change_2yr_stepwise_r2" src="https://github.com/user-attachments/assets/29a7b7cf-b022-41ea-9128-b4331b8d6a19" />
<img width="2400" height="1000" alt="moca_change_2yr_stepwise_r2" src="https://github.com/user-attachments/assets/3379089c-abfe-4e82-a704-04e099ff5ec5" />
<img width="2400" height="1000" alt="cdrsb_change_2yr_stepwise_r2" src="https://github.com/user-attachments/assets/b5c59119-e326-41b9-a855-69564161181a" />
```

### Interpretation

The regression results were weaker than the binary conversion results.

Plain-English interpretation:

> It is easier to predict whether someone converts to dementia within 2 years than to predict exactly how many MMSE, MoCA, or CDR-SB points they will change.

The MoCA result should be treated as exploratory because the usable sample size was much smaller.

---

## 15. LASSO Feature Stability

The LASSO stability analysis identified features selected consistently across cross-validation folds.

The most stable interpretable feature set was:

```text
Cognitive + APOE + biomarkers
```

Consistently selected features included:

- Delayed memory measures
- MMSE score
- MoCA delayed recall items
- APOE4 count
- Amyloid/tau biomarker values
- Plasma pTau181

### Figure 7: LASSO feature stability

> **LASSO feature stability.** Delayed memory, MMSE, APOE4 count, and amyloid/tau biomarker measures were consistently selected across cross-validation folds, supporting their role as stable predictors.

```markdown
<img width="1600" height="1200" alt="feature_stability" src="https://github.com/user-attachments/assets/eb8eb04a-6f9e-4eaf-bea5-3428aef97af4" />
```

### Interpretation

The interpretable model did not require MRI to identify stable predictors. This supports the broader conclusion that memory/cognitive features, APOE, and biomarker measures form a stable core predictor set.

Demographic one-hot features that appeared in LASSO should not be interpreted causally. They may reflect cohort composition, missingness patterns, site effects, or sampling variation.

---

## 16. Biological Interpretation

### What the results suggest

1. **Memory measures are highly predictive.**  
   This is clinically plausible because Alzheimer’s disease often affects memory-related function early.

2. **APOE4 adds genetic risk information.**  
   APOE4 is a known Alzheimer’s disease risk marker. In this analysis, APOE added some value beyond cognitive testing.

3. **Amyloid and tau biomarkers add disease-biology information.**  
   Amyloid and tau measures relate to Alzheimer’s pathology. Their stable selection supports their role as biologically meaningful predictors.

4. **MRI adds incremental value.**  
   Structural MRI features improved prediction modestly, but the gain was smaller than the gain from broad cognitive testing.

### What not to overclaim

This analysis does **not** show:

- Causality
- Clinical readiness
- That demographic variables cause progression
- That specific MRI brain regions are important before FreeSurfer ST codes are mapped
- That the model has been externally validated outside ADNI

Preferred wording:

> The results suggest that cognitive performance, APOE genetic risk, and amyloid/tau biomarker measures provide complementary information for predicting 2-year MCI progression in ADNI. MRI features add incremental predictive value, but anatomical interpretation requires mapping FreeSurfer feature codes to brain regions.

---

## 17. Integrated Interpretation Across Both Notebooks

The two notebooks converge on the same conclusion.

The stepwise analysis shows:

```text
Full multimodal model = highest AUC
Broad cognitive features = largest performance jump
MRI/biomarkers = smaller incremental gains
```

The minimal-marker analysis shows:

```text
Small cognitive/APOE panel = nearly as strong as compact multimodal panel
```

Together, this supports a practical model of the findings:

```text
Core signal: cognitive performance
Additional signal: APOE and biomarkers
Incremental signal: MRI
Highest performance: full multimodal model
Best practical tradeoff: cognitive + APOE or compact clinical/APOE panel
```

The result is not that MRI or biomarkers are unimportant. Rather:

> MRI and biomarkers add information, but in this 2-year ADNI MCI prediction task, much of the predictive value is already captured by cognitive phenotyping and APOE.

---

## 18. Limitations

Important limitations:

1. **ADNI is a research cohort.**  
   Results may not generalize directly to routine clinical populations.

2. **MRI features need anatomical mapping.**  
   FreeSurfer `ST` codes should be mapped before making brain-region-level claims.

3. **Biomarker availability is incomplete.**  
   Some biomarker results may depend on missingness and imputation.

4. **MoCA change sample was small.**  
   MoCA regression should be considered exploratory.

5. **Prediction is not causation.**  
   Selected variables are predictive, not necessarily causal.

6. **The model is not ready for clinical deployment.**  
   External validation, calibration, and threshold tuning would be needed.

7. **Sensitivity/specificity tradeoff matters.**  
   The best random forest model had high specificity but lower sensitivity at the default threshold.

---

## 19. Suggested Final Presentation Story

For a professor/team presentation, the story can be framed as:

1. We built a longitudinal ADNI MCI cohort.
2. We defined a clean 2-year conversion outcome.
3. We tested both compact marker panels and stepwise multimodal models.
4. The full multimodal model performed best.
5. Broad cognitive testing created the largest performance gain.
6. APOE, MRI, and biomarkers added smaller incremental value.
7. Compact clinical/APOE panels came close to multimodal performance.
8. Continuous decline prediction was weaker than binary conversion prediction.
9. The strongest practical conclusion is that cognitive phenotyping carries most of the predictive signal, with APOE and biomarkers adding complementary information.

---

## 20. Final Conclusion

This project shows that 2-year MCI-to-dementia conversion can be predicted in ADNI with moderate-to-strong discrimination.

The best full multimodal model achieved:

```text
ROC-AUC ≈ 0.826
```

However, the main practical conclusion is:

> Broad cognitive testing produced the largest performance improvement. APOE, MRI, and biomarkers added incremental value, but the gains were smaller relative to their added testing burden.

The minimal-marker analysis supports the same conclusion:

> A compact clinical/APOE marker panel performed nearly as well as a more burdensome multimodal MRI-containing panel.

The continuous outcome analysis showed:

> MMSE and CDR-SB change were modestly predictable, while MoCA change was weak and exploratory.

Overall:

> **Cognitive phenotyping is the strongest practical predictor of 2-year MCI-to-dementia conversion in this ADNI analysis. APOE, MRI, and biomarkers provide complementary information, but their incremental gains should be weighed against testing burden.**
