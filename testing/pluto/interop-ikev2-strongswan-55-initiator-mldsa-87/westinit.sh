/testing/guestbin/swan-prep --userland strongswan

cp /testing/x509/pki/real/mainmldsa87/root.cert /etc/strongswan/ipsec.d/cacerts/mainmldsa87.crt
cp /testing/x509/pki/real/mainmldsa87/west.end.cert /etc/strongswan/ipsec.d/certs/west.crt
cp /testing/x509/pki/real/mainmldsa87/west.key /etc/strongswan/ipsec.d/private/west.key
chmod 600 /etc/strongswan/ipsec.d/private/*

../../guestbin/strongswan-start.sh
echo "initdone"
