args = commandArgs(trailingOnly=TRUE)
library(HiCcompare)
temp <- read.table(args[1], header = FALSE)
data<-cooler2sparse(temp)
write.table(data[paste('chr', args[2], sep="")], file=args[3], row.names=FALSE, col.names=FALSE, quote = FALSE)