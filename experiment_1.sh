# 8 bit HW model; full attack
# producing 3000 samples each
for (( i=0; i<=150; i++))
do
  for i in 8 10 16 32 64 128 256 512; do
    NOW=$(date +"%Y_%m_%d_%H_%M_%S_%N")
    tmpfile="data/exp_1/$i/$(hostname)_$NOW.log"
    for (( c=1; c<=20; c++ ))
    do
      # remove traces that might exist
      rm *.bin
      rm *.txt
      # random key with 8-bit leakage - output is not required
      ./simulation/simulate $i HW_BYTE >/dev/null 2>&1

      # perform the analysis - will contain the resulst
      ./analysis/analyze_8bit.py *.bin secret_data.txt --silent >> $tmpfile
    done
  done
done
