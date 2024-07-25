source /var/www/html/TADMaster/Site/data/job_$1/TADMaster.config
echo "Running TADMaster on $input_matrix"

#--------------------------------------------------------------------------------------------------------
#Make paths
#--------------------------------------------------------------------------------------------------------


home_path="/var/www/html/TADMaster"
Caller_path="${home_path}/TADCallers"
Norm_method_path="${home_path}/normalization" 
job_path="${home_path}/Site/data/job_$1"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
input_path="${input_matrix}"
output_path="${job_path}/output"
temp_path="${job_path}/temp"
additional_file_path="${job_path}/additional_files"
normalized_path="${job_path}/normalizations"
log_path="${home_path}/Site/data/job_$1/log.txt"

#--------------------------------------------------------------------------------------------------------
# Create the folder structure in job path
#--------------------------------------------------------------------------------------------------------

echo "Creating Folder Structure" > $log_path

if [ -d $job_path ]
then
	mkdir $output_path
	mkdir $temp_path
	mkdir $additional_file_path
	mkdir $normalized_path

fi


#--------------------------------------------------------------------------------------------------------
#Enter normalization methods
#--------------------------------------------------------------------------------------------------------

echo "Normalizing Matrix" > $log_path

cd $Norm_method_path

if [ $data_input_type == 'square' ]
then
	Rscript full2sparse.r ${input_path} ${resolution} ${job_path}/sparse_input.txt
	input_path="${job_path}/sparse_input.txt"
fi 

if [ $data_input_type == 'cool' ]
then
	cool_or_h5_path="${input_path}"
	cooler dump --join ${input_path} > $temp_path/temp.txt
	Rscript cool2sparse.r $temp_path/temp.txt ${chr} ${job_path}/sparse_input.txt
	input_path="${job_path}/sparse_input.txt"
fi

if [ $data_input_type == 'hic' ]
then
	hic_path="${input_path}"
	hicConvertFormat -m ${input_path} --inputFormat hic --outputFormat cool -o ${job_path}/matrix.cool --resolutions ${resolution} --chromosome ${chr}
	mv "${job_path}/matrix_${resolution}.cool" "${job_path}/matrix.cool"
	cool_or_h5_path="${job_path}/matrix.cool"
	cooler dump --join ${job_path}/matrix.cool > $temp_path/temp.txt
	Rscript cool2sparse.r $temp_path/temp.txt ${chr} ${job_path}/sparse_input.txt
	input_path="${job_path}/sparse_input.txt"
fi

if [ $data_input_type == 'h5' ]
then
	cool_or_h5_path=input_path
	hicConvertFormat -m ${input_path} --inputFormat h5 --outputFormat cool -o ${job_path}/matrix.cool --resolutions ${resolution} --chromosome ${chr}
	cooler dump --join ${job_path}/matrix.cool > $temp_path/temp.txt
	Rscript cool2sparse.r $temp_path/temp.txt ${chr} ${job_path}/sparse_input.txt
	input_path="${job_path}/sparse_input.txt"
fi




# converting sparse matrix to ccmap
python3 sparse2ccmap.py ${input_path} ${temp_path}


# ChromoR
if [ $norm_chromor == 'True' ]
then
	Rscript chromoRNorm.r ${input_path} ${normalized_path} ${species} ${chr} ${resolution} ${input_path}
fi


# Note: the input file is the ccmap generated from the matrix input, output is also ccmap


# IC
if [ $norm_ice == 'True' ]
then
	gcMapExplorer normIC -i ${temp_path}/exCCMap.ccmap -fi ccmap -fo ccmap -o ${temp_path}/ICEoutput.ccmap
#	gcMapExplorer normIC -i ${temp_path}/exCCMap.ccmap -fi ccmap -fo gcmap -o ${temp_path}/ICEoutput.gcmap
fi


# KR
if [ $norm_kr == 'True' ]
then
	gcMapExplorer normKR -i ${temp_path}/exCCMap.ccmap -fi ccmap -fo ccmap -o ${temp_path}/KRoutput.ccmap
fi


# VC
if [ $norm_vc == 'True' ]
then
	gcMapExplorer normVC -i ${temp_path}/exCCMap.ccmap -fi ccmap -fo ccmap -o ${temp_path}/VCoutput.ccmap
fi


# MCFS
if [ $norm_mcfs == 'True' ]
then
	gcMapExplorer normMCFS -i ${temp_path}/exCCMap.ccmap -fi ccmap -fo ccmap -o ${temp_path}/MCFSoutput.ccmap
fi


# Converting from ccmap to sparse
python3 ccmapConvert.py ${temp_path} $norm_kr $norm_vc $norm_ice $norm_mcfs

# Takes the sparse matrices and converts them to full, also runs SCN normalization if specified in config file
Rscript convert2fullFin.r ${temp_path} ${normalized_path} $norm_kr $norm_vc $norm_ice $norm_mcfs $norm_scn ${input_path}



if [ $norm_mcfs == 'False' ] && [ $norm_vc == 'False' ] && [ $norm_kr == 'False' ] && [ $norm_ice == 'False' ] && [ $norm_chromor == 'False' ]
then
	Rscript sparse2matrix_no_norm.r ${input_path} ${normalized_path}
fi
cd $home_path
#--------------------------------------------------------------------------------------------------------
#Enter caller methods
#--------------------------------------------------------------------------------------------------------
echo "Entering caller methods" >> $log_path
#if [ "$(ls -A $normalized_path)" ]; then
for normalized_input in ${normalized_path}/*.txt; do
	#Changing directories
	norm_name=$(basename $normalized_input .txt)
	input_path="$normalized_input"
	output_path="${job_path}/output/$norm_name/"
	mkdir $output_path

	#CleanUp and remake
	rm -r ${temp_path}
	mkdir $temp_path
	echo "${input_path}" >> $log_path
	echo "Processing ${norm_name}" >> $log_path
	#Armatus
	if [ $armatus == 'True' ]
	then
		printf 'Entering Armatus\n-----------------\n'
		echo "Entering Armatus" >> $log_path
		cd $Caller_path
		cd armatus-2.2
		gzip -k $input_path
		armatus_input="${input_path}.gz"
		./armatus-linux-x64 -i $armatus_input -g $armatus_gamma -o $temp_path/test -r $resolution -s 0.025
		python3 $home_path/Analysis/cleanArmatus.py $temp_path/test.consensus.txt $output_path
		rm -rf $armatus_input
		cd $home_path
		echo "Exiting Armatus" >> $log_path
	fi


	# Arrowhead Need to add normalization
	if [ $arrowhead == 'True' ] && [ $data_input_type == 'hic' ]
	then
		echo "Entering Arrowhead" >> $log_path

		if [ $norm_name == 'VCnorm' ]
		then
			arrowhead_norm='VC'
		elif [ $norm_name == 'KRnorm' ]
		then
			arrowhead_norm='KR'
		elif [ $norm_name == 'Pre_Normalized' ]
		then	
			arrowhead_norm='NONE'
		fi
		printf 'Entering Arrowhead\n-----------------\n'
		cd $Caller_path/Juicer/scripts
		java -jar juicer_tools_1.22.01.jar arrowhead -c $chr  -r $resolution --threads 0 -k arrowhead_norm $hic_path $additional_file_path/Arrowhead.bed --ignore-sparsity
		cd $home_path
		echo "Exiting Arrowhead" >> $log_path

	fi


	# CaTCH
	if [ $catch == 'True' ]
	then
		printf 'Entering CaTCH\n-----------------\n'
		echo "Entering CaTCH" >> $log_path
		cd $Caller_path/CaTCH_R
		python3 $home_path/Analysis/preprocessCaTCH.py $input_path $temp_path $chr
		catch_path=${Caller_path}/NormCompare/CaTCH_${job_id}.r
		echo "library(CaTCH)" > $catch_path
		echo "input <- \"${temp_path}/CaTCH.bed\"" >> $catch_path
		# without this line, most of the results won't output
		echo "options(max.print = .Machine\$integer.max)" >> $catch_path
		echo "sink(\"${temp_path}/CaTCH_results_raw.bed\")" >> $catch_path
		echo "domain.call(input)" >> $catch_path
		chmod 777 "${catch_path}"
		dos2unix $catch_path
		Rscript "${catch_path}"
		python3 $home_path/Analysis/postprocessCaTCH.py $temp_path/CaTCH_results_raw.bed 0.650,0.550 $resolution $output_path 
		rm -rf ${Caller_path}/NormCompare/CaTCH_${job_id}.r
		cd $home_path
		echo "Exiting CaTCH" >> $log_path
	fi


	#CHDF Curently fails due to unknown issue
	if [ $chdf == 'True' ]
	then
		printf 'Entering chdf\n-----------------\n'
		cd $Caller_path
		./CHDF $input_path $output_path/chdf.bed 1535 1000 1000
	fi


	# ClusterTAD
	if [ $clustertad == 'True' ]
	then
		cd $Caller_path
		printf 'Entering ClusterTAD\n-----------------\n'
		echo "Entering ClusterTAD" >> $log_path
		java -jar ClusterTAD.jar $input_path $resolution
		# move the best result to the output folder
		# Currently leaves all other in a file in TADCallers!!!!
		shopt -s nullglob
		for d in Output_*/ ; do
			for f in $d/TADs/BestTAD_* ; do
				mv $f "${output_path}/ClusterTAD.bed"
			done
		done
		mv Output_* "${additional_file_path}/Cluster"
		# convert ClusterTAD results
		python3 $home_path/Analysis/convertClusterTAD.py $output_path/ClusterTAD.bed
		echo "Exiting ClusterTAD" >> $log_path
	fi


	# TopDom
	if [ $topdom == 'True' ]
	then
		cd $Caller_path/TopDom
		printf 'Entering TopDom\n-----------------\n'
		echo "Entering TopDom" >> $log_path
		#NxN to NxN+3 format
		python3 preprocessTopDom.py $input_path $temp_path/ $chr $resolution $job_id
		#set up driver code
		topdom_path=${temp_path}/Topdom_${job_id}.r
		echo "setwd(\"${Caller_path}/TopDom/\")" > $topdom_path
		echo "source(\"TopDom.R\")" >> $topdom_path
		echo "TopDom(matrix.file=\"${temp_path}/TopDom_${job_id}.bed\", window.size=${topdom_window}, outFile=\"${output_path}/TopDom\")" >> $topdom_path
		#Run topdom
		Rscript "${topdom_path}"
		rm -rf ${output_path}/TopDom.domain
		rm -rf ${output_path}/TopDom.binSignal
		python3 $home_path/Analysis/cleanTopDom.py $output_path/TopDom.bed $output_path
		cd $home_path
		echo "Exiting TopDom" >> $log_path
	fi


	#GMAP
	if [ $gmap == 'True' ]
	then
		cd $Caller_path
		gmap_path=GMAP_${job_id}.r
		printf 'Entering GMAP\n-----------------\n'
		echo "Entering GMAP" >> $log_path
		echo "library(rGMAP)" > $gmap_path
		echo "res = rGMAP(\"${input_path}\", resl = $resolution)" >> $gmap_path
		echo "sink(\"${output_path}/GMAP.txt\")" >> $gmap_path
		echo "print(res)" >> $gmap_path
		echo "sink()" >> $gmap_path
		Rscript "${gmap_path}"
		rm -rf GMAP_${job_id}.r
		python3 $home_path/Analysis/GMAPClean.py $output_path/GMAP.txt
		echo "Exiting GMAP" >> $log_path
	fi


	#IC-Finder
	if [ $ic_finder == 'True' ]
	then
		printf 'Entering IC-Finder\n-----------------\n'
		echo "Entering IC-Finder" >> $log_path
		cd $Caller_path/IC-Finder
		path=ic-finder_${job_id}.m
		{
		echo "pkg load statistics;"
		echo "dom = IC_Finder('${input_path}','Option','hierarchy','SigmaZero',5, 'SaveFigures',0, 'path', '${output_path}/');"
		}> $path
		octave --no-gui "${path}"
		rm -rf ic-finder_${job_id}.m
		python3 $home_path/Analysis/IC-FinderClean.py $output_path/ICEnorm_sigmaZero5_domains.txt $resolution 
		mv $output_path/ICEnorm_sigmaZero5_domains.txt $output_path/IC_Finder.txt
		echo "Exiting IC-Finder" >> $log_path
	fi


	#chromoR
	if [ $chromo_r == 'True' ]
	then
		cd $Caller_path
		printf 'Entering ChromoR\n-----------------\n'
		path=chromoR_${job_id}.r
		echo "library(chromoR)" > $path
		echo "matrix <- read.delim(\"${input_path}\", header = FALSE, sep = \"\t\", quote = \"\" )" >> $path
		echo "data = rowSums(matrix, na.rm=TRUE)" >> $path
		echo "res = segmentCIM(data)" >> $path
		echo "sink(\"${output_path}/chromoR.txt\")" >> $path
		echo "print(res)" >> $path
		echo "sink()" >> $path
		Rscript "${path}"
		rm -rf chromoR_${job_id}.r
		python3 $home_path/Analysis/chromoRClean.py $output_path/chromoR.txt $resolution $input_path
	fi


	#HiCseg
	if [ $hic_seg == 'True' ]
	then
		cd $Caller_path
		printf 'Entering HiCseg\n-----------------\n'
		echo "Entering HiCseg" >> $log_path
		path=HiCseg_${job_id}.r
		echo "library(HiCseg)" > $path
		echo "options(max.print=1000000)" >> $path
		echo "matrix <- read.table(\"${input_path}\", sep = \"\t\")" >> $path
		echo "hold <- matrix[,colSums(is.na(matrix))<nrow(matrix)]" >> $path
		echo "df <- as.numeric(unlist(hold))" >> $path
		echo "sink(\"${output_path}/HiCseg.txt\")" >> $path
		echo "HiCseg_linkC_R(length(hold), 1000, \"G\", df, \"D\")" >> $path
		echo "sink()" >> $path
		Rscript "${path}"
		rm -rf HiCseg_${job_id}.r
		python3 $home_path/Analysis/HiCsegClean.py $output_path/HiCseg.txt $resolution $input_path
		echo "Exiting HiCseg" >> $log_path
	fi


	#Insulation
	if [ $insulation == 'True' ]
	then
		cd $Caller_path
		printf 'Entering insulation\n-----------------\n'
		echo "Entering insulation" >> $log_path
		python3 tadtool_bed.py $input_path $temp_path/ insulation $chr $resolution
		tadtool tads $input_path ${temp_path}/insulation.bin $resolution $insulation_window $temp_path/insulation.results
		python3 $home_path/Analysis/cleanTADTool.py  $temp_path/insulation.results $output_path Insulation_Score
		echo "Exiting insulation" >> $log_path
		fi

	#DI
	if [ $di == 'True' ]
	then
		cd $Caller_path
		printf 'Entering DI\n-----------------\n'
		echo "Entering DI" >> $log_path
		python3 tadtool_bed.py $input_path $temp_path di $chr $resolution 
		tadtool tads $input_path ${temp_path}/di.bin $resolution $di_length $temp_path/di.results -a directionality
		python3 $home_path/Analysis/cleanTADTool.py  $temp_path/di.results $output_path DI
		echo "Exiting DI" >> $log_path
	fi

	#HiCExplorer
	if [ $hic_explorer == 'True' ] && [ $data_input_type != 'sparse' ] && [ $data_input_type != 'square' ]
	then
		echo "Entering HiCExplorer" >> $log_path
		cd $additional_file_path
		hicFindTADs -m $cool_or_h5_path --outPrefix HICExplorer --correctForMultipleTesting fdr --chromosomes $chr
		python3 $home_path/Analysis/HiCExplorerClean.py $additional_file_path/HICExplorer_domains.bed $resolution $output_path/HiCExplorer.bed
		echo "Exiting HiCExplorer" >> $log_path
	fi

	#Spectral
	if [ $spectral == 'True' ]
	then
		cd $Caller_path
		python3 $home_path/Analysis/shift_nxn.py $input_path $temp_path spectral.matrix $chr $resolution
		spectral_input=${temp_path}/spectral.matrix
		spectral_path=spectral_${job_id}.r
		printf 'Entering spectral\n-----------------\n'
		echo "Entering Spectral" >> $log_path
		echo "library(SpectralTAD)" > $spectral_path
		echo "matrix <- read.table(\"${spectral_input}\", sep = \"\t\")" >> $spectral_path
		echo "hold <- matrix[,colSums(is.na(matrix))<nrow(matrix)]" >> $spectral_path
		echo "spec_table <- SpectralTAD(hold, chr= \"chr${chr}\", out_format= \"bed\", out_path= \"${temp_path}/spectral.bed\")" >> $spectral_path
		Rscript "${spectral_path}"
		rm -rf spectral_${job_id}.r
		python3 $home_path/Analysis/cleanSpectral.py $temp_path/spectral.bed  $output_path
		echo "Exiting Spectral" >> $log_path
	fi

done
