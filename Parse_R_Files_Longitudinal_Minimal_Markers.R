# Parse R Files - Longitudinal Minimal-Marker ADNI Project
# Purpose:
# Convert selected ADNI .rda files into CSVs for Python modeling.
# This replaces the old script that only converted ADSL.rda and UCSFFSX6.rda.

# -----------------------------
# 1. PATH CONFIG
# -----------------------------
project_dir <- "/Users/suvankapoor/Documents/Multimodal Alzheimer's Research"
data_dir <- file.path(project_dir, "ADNIMERGE2", "data")
out_dir <- file.path(project_dir, "csv_exports")

if (!dir.exists(out_dir)) {
  dir.create(out_dir, recursive = TRUE)
}

# -----------------------------
# 2. EXACT FILES TO EXPORT FIRST
# -----------------------------
selected_files <- c(
  # Core subject / diagnosis / visit structure
  "ADSL.rda",
  "DXSUM.rda",
  "VISITS.rda",
  "REGISTRY.rda",
  "PTDEMOG.rda",
  "RMT_PTDEMOG.rda",

  # Cognitive / clinical tests
  "NEUROBAT.rda",
  "NEUROEXM.rda",
  "UWNPSYCHSUM.rda",
  "MMSE.rda",
  "MOCA.rda",
  "CDR.rda",
  "FAQ.rda",
  "ADAS.rda",
  "ECOGPT.rda",
  "ECOGSP.rda",
  "ECOG12PT.rda",
  "ECOG12SP.rda",
  "NPI.rda",
  "NPIQ.rda",
  "GDSCALE.rda",

  # MRI / FreeSurfer imaging
  "UCSFFSX6.rda",
  "UCSFFSX7.rda",
  "UCSFFSX.rda",
  "UCSFFSL.rda",
  "UCSFFSL51.rda",
  "UCSFFSL51ALL.rda",
  "UCSFFSL51Y1.rda",
  "UCSFFSX51.rda",
  "UCSFFSX51_ADNI1_3T.rda",
  "UCSFSNTVOL.rda",
  "UCSFASLFS_V2.rda",
  "UCSFASLFSCBF.rda",
  "UCSFASLQC.rda",
  "UCSFATROPHY.rda",
  "MRIMETA.rda",
  "MRI3META.rda",
  "MRIQC.rda",
  "MRIINFQ.rda",
  "MRIINCLUSIO.rda",
  "MRI_INFARCTS.rda",

  # APOE / genetics
  "APOERES.rda",
  "RMT_APOERES.rda",
  "GENETIC.rda",

  # Blood / plasma / CSF biomarkers
  "UPENNBIOMK_MASTER.rda",
  "UPENNBIOMK_ROCHE_ELECSYS.rda",
  "UPENNBIOMKADNIDIAN2017.rda",
  "UPENNPLASMA.rda",
  "FUJIREBIOABETA.rda",
  "FUJIREBIOABETAPLASMA.rda",
  "BLENNOWPLASMANFL.rda",
  "BLENNOWPLASMANFLLONG.rda",
  "BLENNOWPLASMATAU.rda",
  "BLENNOWCSFNFL.rda",
  "BLENNOWCSFNG.rda",
  "UGOTPTAU181.rda",
  "C2N_PRECIVITYAD2_PLASMA.rda",
  "BIOMARK.rda",
  "LABDATA.rda",
  "LABTESTS.rda",
  "URMC_LABDATA.rda",

  # PET imaging optional benchmark
  "AMYDISC.rda",
  "AMYMETA.rda",
  "AMYQC.rda",
  "AMYREAD.rda",
  "AV45META.rda",
  "AV45QC.rda",
  "AV45FOLLOW.rda",
  "TAUMETA.rda",
  "TAUQC.rda",
  "PETC3.rda",
  "PETMETA_ADNI1.rda",
  "PETMETA3.rda",
  "PETQC.rda",
  "PIBMETA.rda",
  "PIBPETSUVR.rda",
  "PIBQC.rda",
  "UCBERKELEY_AMY_6MM.rda",
  "UCBERKELEY_TAU_6MM.rda",
  "UCBERKELEY_TAUPVC_6MM.rda",
  "UCBERKELEYFDG_8mm.rda",
  "BAIPETNMRC.rda",
  "BAIPETNMRCAV45.rda",
  "BAIPETNMRCFDG.rda",
  "BAIPETNMRCFTP.rda",

  # Other clinical covariates
  "VITALS.rda",
  "PHYSICAL.rda",
  "MEDHIST.rda",
  "RECMEDS.rda",
  "RECMHIST.rda",
  "FAMHXPAR.rda",
  "FAMHXSIB.rda",
  "FHQ.rda"
)

# Files in your screenshot with truncated names. This grabs them by prefix if present.
prefix_patterns <- c(
  "^UPENN_PLASMA_FUJIREBIO_QUANTE",
  "^FNIHBC_BLOOD_BIOMARKER_TRAJEC",
  "^PETMETA_ADNIGO2"
)

all_rda_files <- list.files(data_dir, pattern = "\\.rda$", full.names = FALSE)
prefix_matches <- unique(unlist(lapply(prefix_patterns, function(p) {
  grep(p, all_rda_files, value = TRUE)
})))

files_to_convert <- unique(c(selected_files, prefix_matches))

# -----------------------------
# 3. SAFE EXPORT FUNCTION
# -----------------------------
convert_one_rda <- function(filename) {
  input_path <- file.path(data_dir, filename)
  base_name <- tools::file_path_sans_ext(filename)
  output_path <- file.path(out_dir, paste0(base_name, ".csv"))

  result <- data.frame(
    filename = filename,
    object_name = NA_character_,
    rows = NA_integer_,
    columns = NA_integer_,
    status = NA_character_,
    error_message = NA_character_,
    output_path = output_path,
    stringsAsFactors = FALSE
  )

  if (!file.exists(input_path)) {
    result$status <- "missing_file_skipped"
    result$error_message <- paste("File not found:", input_path)
    print(paste("SKIP:", filename, "- file not found"))
    return(result)
  }

  tryCatch({
    env <- new.env()
    obj_names <- load(input_path, envir = env)

    if (length(obj_names) == 0) {
      stop("No object loaded from .rda file")
    }

    # Usually ADNI .rda files contain one object. If multiple, use the first data.frame-like object.
    obj_name <- obj_names[1]
    if (length(obj_names) > 1) {
      data_like <- obj_names[sapply(obj_names, function(nm) {
        is.data.frame(get(nm, envir = env)) || is.matrix(get(nm, envir = env))
      })]
      if (length(data_like) > 0) {
        obj_name <- data_like[1]
      }
    }

    obj <- get(obj_name, envir = env)
    df <- as.data.frame(obj)

    write.csv(df, output_path, row.names = FALSE, na = "")

    result$object_name <- obj_name
    result$rows <- nrow(df)
    result$columns <- ncol(df)
    result$status <- "converted"

    print(paste("CONVERTED:", filename, "->", basename(output_path),
                "| object:", obj_name,
                "| rows:", nrow(df),
                "| cols:", ncol(df)))

    return(result)
  }, error = function(e) {
    result$status <- "error"
    result$error_message <- as.character(e$message)
    print(paste("ERROR:", filename, "-", e$message))
    return(result)
  })
}

# -----------------------------
# 4. RUN CONVERSION + LOG
# -----------------------------
log_list <- lapply(files_to_convert, convert_one_rda)
conversion_log <- do.call(rbind, log_list)

log_path <- file.path(out_dir, "conversion_log.csv")
write.csv(conversion_log, log_path, row.names = FALSE)

print("Done.")
print(paste("CSV exports folder:", out_dir))
print(paste("Conversion log:", log_path))
print(table(conversion_log$status))
