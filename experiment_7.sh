for (( i=10; i<=8000; i=i+10 ))
do
  # remove traces that might exist
  echo $i
  rm *.bin
  rm *.txt
  ./simulation/simulate $i HW 3358a66f84127a1b54a90819539acee5ace514183a9671aead2131c8cdbc5800 >/dev/null 2>&1
  # perform the analysis
  ./analysis/analyze_32bit_addition.py *.bin secret_data.txt 0.5 --silent
done
