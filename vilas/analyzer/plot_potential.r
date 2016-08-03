residues <- read.table(file='../cutoff-resid-5angstroms',header=F)

for(res in residues){

line <- read.table(file=paste(res,".dat",sep=""),header=TRUE) ## if you have headers in your files ##
if (res == residues[1]){
resid <- res
meanCoul <- mean(line$CoulSRresRNA)
errCoul <- sd(line$CoulSRresRNA)
meanLJ <- mean(line$LJSRresRNA)
errLJ <- sd(line$LJSRresRNA)
sumMean <- mean(line$CoulSRresRNA) + mean(line$LJSRresRNA)
sumError <- sd(line$CoulSRresRNA) + sd(line$LJSRresRNA)
} else {
resid <- append(resid, res)
meanCoul <- append(meanCoul,mean(line$CoulSRresRNA))
errCoul <- append(errCoul,sd(line$CoulSRresRNA))
meanLJ <- append(meanLJ,mean(line$LJSRresRNA))
errLJ <- append(errLJ,sd(line$LJSRresRNA))
sumMean <- append(sumMean, mean(line$CoulSRresRNA) + mean(line$LJSRresRNA) )
sumError <- append(sumError, sd(line$CoulSRresRNA) + sd(line$LJSRresRNA) )
}
}

write.table(x=cbind(resid, meanCoul, errCoul, meanLJ, errLJ, sumMean, sumError), file="mean.dat",sep=" \t",append=TRUE,quote=FALSE)
