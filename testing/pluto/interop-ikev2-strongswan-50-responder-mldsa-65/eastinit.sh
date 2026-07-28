/testing/guestbin/swan-prep --userland strongswan

cp /testing/x509/pki/real/mainmldsa65/root.cert /etc/strongswan/ipsec.d/cacerts/mainmldsa65.crt
cp /testing/x509/pki/real/mainmldsa65/east.end.cert /etc/strongswan/ipsec.d/certs/east.crt
cp /testing/x509/pki/real/mainmldsa65/east.key /etc/strongswan/ipsec.d/private/east.key
chmod 600 /etc/strongswan/ipsec.d/private/*

../../guestbin/strongswan-start.sh
echo "initdone"
