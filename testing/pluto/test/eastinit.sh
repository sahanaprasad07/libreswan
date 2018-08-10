
/testing/guestbin/swan-prep  
/usr/bin/pk12util -i /testing/x509/strongswan_pss_256/strongEast.p12 -d sql:/etc/ipsec.d -w /testing/x509/nss-pw
/usr/bin/pk12util -i /testing/x509/strongswan_pss_256/strongWest.p12 -d sql:/etc/ipsec.d -w /testing/x509/nss-pw
ipsec start
/testing/pluto/bin/wait-until-pluto-started
ipsec auto --add westnet-eastnet-ikev2
echo "initdone"
