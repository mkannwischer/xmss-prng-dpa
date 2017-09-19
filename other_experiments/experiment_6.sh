
inputfile="data/good_seeds_exp5.txt"
ctr=0;
while read seed; do
  echo $ctr
  ctr=$((ctr+1))

  for i in 16 32 64 96 128 256 512 1024 2048 4048 8096; do
    file="data/exp_6/$i.log"
    # remove traces that might exist
    rm *.bin
    rm *.txt
    ./simulation/simulate $i HW $seed >/dev/null 2>&1
    # perform the analysis - will contain the resulst
    ./analysis/analyze_32bit_and.py *.bin secret_data.txt 0.5 --silent >> $file
  done
done < $inputfile
