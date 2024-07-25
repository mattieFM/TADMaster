library(CaTCH)
input <- "/var/www/html/TADMaster/Site/storage/data/job_00f03b6b-ad48-4c1d-a96e-28bca77d2c47/temp/CaTCH.bed"
options(max.print = .Machine$integer.max)
sink("/var/www/html/TADMaster/Site/storage/data/job_00f03b6b-ad48-4c1d-a96e-28bca77d2c47/temp/CaTCH_results_raw.bed")
domain.call(input)
