# 32 bit HW model; only DPA1
# producing 2000 samples for each trace number
for (( i=0; i<=100; i++))
do
  for i in 16 32 64 96 128 256 512 1024 2048 4048 8096; do
    NOW=$(date +"%Y_%m_%d_%H_%M_%S_%N")
    tmpfile="data/exp_3/$i/$(hostname)_$NOW.log"
    for (( c=1; c<=20; c++ ))
    do
      # remove traces that might exist
      rm *.bin
      rm *.txt
      # random key with 32-bit leakage - output is not required
      ./simulation/simulate $i HW >/dev/null 2>&1

      # perform the analysis - will contain the resulst
      ./analysis/analyze_32bit_addition.py *.bin secret_data.txt 0.5 --silent >> $tmpfile
    done
  done
done
