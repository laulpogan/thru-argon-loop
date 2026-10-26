X=$(cat /tmp/hkX.txt)
bash /tmp/passhk.sh 1260 <pod-ip> hkfull 0 754 "$X" > /tmp/hf_u3.log 2>&1 &
bash /tmp/passhk.sh 1838 <pod-ip> hkfull 754 1508 "$X" > /tmp/hf_u1.log 2>&1 &
bash /tmp/passhk.sh 12181 <pod-ip> hkfull 1508 2262 "$X" > /tmp/hf_u2.log 2>&1 &
bash /tmp/passhk.sh 1673 <pod-ip> hkfull 2262 3013 "$X" > /tmp/hf_u6.log 2>&1 &
wait
