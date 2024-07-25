library(CaTCH)
input <- "/var/www/html/TADMaster/Site/storage/data/job_0844f96e-a8bf-43ee-86eb-3b0cb64a7d4c/temp_KRnorm/CaTCH.bed"
options(max.print = .Machine$integer.max)
sink("/var/www/html/TADMaster/Site/storage/data/job_0844f96e-a8bf-43ee-86eb-3b0cb64a7d4c/temp_KRnorm/CaTCH_results_raw.bed")
domain.call(input)
