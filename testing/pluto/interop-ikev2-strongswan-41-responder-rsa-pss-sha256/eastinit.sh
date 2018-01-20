/testing/guestbin/swan-prep --userland strongswan --x509
setenforce 0
../../pluto/bin/strongswan-start.sh
echo "initdone"
