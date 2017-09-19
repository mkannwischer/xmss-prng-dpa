
inputfile="data/good_seeds_exp1.txt"
ctr=0;
while read seed; do
  echo $ctr
  ctr= $((ctr+1))

  for i in 8 10 16 32 64 128 256 512; do
    file="data/exp_2/$i.log"
    # remove traces that might exist
    rm *.bin
    rm *.txt
    ./simulation/simulate $i HW_BYTE $seed >/dev/null 2>&1
    # perform the analysis - will contain the resulst
    ./analysis/analyze_8bit.py *.bin secret_data.txt --silent >> $file
  done
done < $inputfile
