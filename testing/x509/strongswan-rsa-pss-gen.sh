#!/bin/sh

libreswandir=$(cd $(dirname $(realpath -m $0)); cd ../..; pwd)
cd ${libreswandir}/testing/x509
rm -f strongswan_pss_256/*
mkdir -p strongswan_pss_256
cd strongswan_pss_256
echo "ignore strongswan.conf errors"
strongswan pki --gen --type rsa --size 3074  > strongCAkey.der
strongswan pki --self --in strongCAkey.der --rsa-padding pss --digest sha256 --dn "C=CH, O=strongSwan, CN=strongSwan CA" --ca > strongCAcert.der
strongswan pki --gen --type rsa --size 3074  > strongWestKey.der
strongswan pki --pub --in strongWestKey.der | strongswan pki --issue --cacert strongCAcert.der --cakey strongCAkey.der --rsa-padding pss --digest sha256 --dn "C=CH, O=strongSwan, CN=strongWest" > strongWestCert.der
strongswan pki --gen --type rsa --size 3074  > strongEastKey.der
strongswan pki --pub --in strongEastKey.der | strongswan pki --issue --cacert strongCAcert.der --cakey strongCAkey.der --rsa-padding pss --digest sha256 --dn "C=CH, O=strongSwan, CN=strongEast" > strongEastCert.der
openssl x509 -inform der -outform pem -in strongCAcert.der -out strongCAcert.pem
openssl x509 -inform der -outform pem -in strongWestCert.der -out strongWestCert.pem
openssl x509 -inform der -outform pem -in strongEastCert.der -out strongEastCert.pem
openssl rsa -inform der -outform pem -in strongWestKey.der -out strongWestKey.pem
openssl rsa -inform der -outform pem -in strongEastKey.der -out strongEastKey.pem
openssl pkcs12 -export -nodes -in strongWestCert.pem -inkey strongWestKey.pem -certfile strongCAcert.pem -name strongWest -export -out strongWest.p12 -passout pass:foobar
openssl pkcs12 -export -nodes -in strongEastCert.pem -inkey strongEastKey.pem -certfile strongCAcert.pem -name strongEast -export -out strongEast.p12 -passout pass:foobar
