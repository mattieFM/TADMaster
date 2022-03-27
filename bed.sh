source /storage/store/TADMaster/data/job_$1/TADMaster.config
echo "Running TADMaster on $input_matrix"

#--------------------------------------------------------------------------------------------------------
#Make paths
#--------------------------------------------------------------------------------------------------------


home_path="/var/www/html/TADMaster"
Caller_path="${home_path}/TADCallers"
Norm_method_path="${home_path}/normalization" 
job_path="/storage/store/TADMaster/data/job_$1"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
input_path="${input_matrix}"
output_path="${job_path}/output"
temp_path="${job_path}/temp"
additional_file_path="${job_path}/additional_files"
normalized_path="${job_path}/normalizations"

#--------------------------------------------------------------------------------------------------------
# Create the folder structure in job path
#--------------------------------------------------------------------------------------------------------


if [ -d $job_path ]
then
	mkdir $temp_path
	mkdir $additional_file_path
fi


#--------------------------------------------------------------------------------------------------------
#Enter normalization methods
#--------------------------------------------------------------------------------------------------------

cd $Norm_method_path

if [ $data_input_type == 'square' ]
then
	Rscript full2sparse.r ${input_path} ${resolution} ${job_path}/sparse_input.txt
	input_path="${job_path}/sparse_input.txt"
fi 

if [ $data_input_type == 'cool' ]
then
	cool_or_h5_path="${input_path}"
	cooler dump --join -H ${input_path} > $temp_path/temp.txt
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


# Converting from ccmap to sparse
python3 ccmapConvert.py ${temp_path} $norm_kr $norm_vc $norm_ice $norm_mcfs

# Takes the sparse matrices and converts them to full, also runs SCN normalization if specified in config file
Rscript convert2fullFin.r ${temp_path} ${normalized_path} $norm_kr $norm_vc $norm_ice $norm_mcfs $norm_scn ${input_path}



if [ $norm_mcfs == 'False' ] && [ $norm_vc == 'False' ] && [ $norm_kr == 'False' ] && [ $norm_ice == 'False' ] && [ $norm_chromor == 'False' ]
then
	Rscript sparse2matrix_no_norm.r ${input_path} ${normalized_path}
fi
cd $home_path
