# Pod hosts are redacted. Set U1_HOST, U2_HOST, U3_HOST, U6_HOST before running.
X=$(cat /tmp/hkX.txt)
bash /tmp/passhk.sh 1260 "${U3_HOST:?set U3_HOST}" hkfull 0 754 "$X" > /tmp/hf_u3.log 2>&1 &
bash /tmp/passhk.sh 1838 "${U1_HOST:?set U1_HOST}" hkfull 754 1508 "$X" > /tmp/hf_u1.log 2>&1 &
bash /tmp/passhk.sh 12181 "${U2_HOST:?set U2_HOST}" hkfull 1508 2262 "$X" > /tmp/hf_u2.log 2>&1 &
bash /tmp/passhk.sh 1673 "${U6_HOST:?set U6_HOST}" hkfull 2262 3013 "$X" > /tmp/hf_u6.log 2>&1 &
wait
