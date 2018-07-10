/testing/guestbin/swan-prep --x509 
#pk12util -i /testing/x509/pkcs12/curveca/east-ec.p12 -d sql:/etc/ipsec.d -W "foobar"
certutil -A -i /testing/x509/strongswan/strongEastCert.der -n "strongEast" -t "P,," -d sql:/etc/ipsec.d/
/usr/bin/pk12util -i /testing/x509/strongswan/strongEast.p12 -d sql:/etc/ipsec.d -w /testing/x509/nss-pw
ipsec start
/testing/pluto/bin/wait-until-pluto-started
ipsec auto --add westnet-eastnet-ikev2
#tcpdump -w OUTPUT/swan12.pcap -i eth0 -c 1000
echo "initdone"
