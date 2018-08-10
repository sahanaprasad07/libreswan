/testing/guestbin/swan-prep --userland strongswan
rm -f /etc/strongswan/ipsec.d/cacerts/*
rm -f /etc/strongswan/ipsec.d/certs/*
rm -f /etc/strongswan/ipsec.d/private/*
cp /testing/x509/strongswan_pss_256/strongCAcert.der /etc/strongswan/ipsec.d/cacerts/
cp /testing/x509/strongswan_pss_256/strongWestCert.der /etc/strongswan/ipsec.d/certs/
cp /testing/x509/strongswan_pss_256/strongWestKey.der /etc/strongswan/ipsec.d/private/
chmod 600 /etc/strongswan/ipsec.d/private/*
# example import for libreswan
/usr/bin/pk12util -i /testing/x509/strongswan_pss_256/strongWest.p12 -d sql:/etc/ipsec.d -w /testing/x509/nss-pw
../../pluto/bin/strongswan-start.sh
echo "initdone"
