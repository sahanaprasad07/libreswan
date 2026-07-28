/testing/guestbin/swan-prep --nokeys

/testing/x509/import.sh real/mainmldsa87/`hostname`.p12

ipsec start
../../guestbin/wait-until-pluto-started
ipsec auto --add westnet-eastnet-ikev2
echo "initdone"
