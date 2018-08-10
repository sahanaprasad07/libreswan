/testing/guestbin/swan-prep 
 /usr/bin/pk12util -i /testing/x509/strongswan_pss_256/strongEast.p12 -d sql:/etc/ipsec.d -w /testing/x509/nss-pw
 /usr/bin/pk12util -i /testing/x509/strongswan_pss_256/strongWest.p12 -d sql:/etc/ipsec.d -w /testing/x509/nss-pw
# confirm that the network is alive
../../pluto/bin/wait-until-alive -I 192.0.1.254 192.0.2.254
# ensure that clear text does not get through
iptables -A INPUT -i eth1 -s 192.0.2.0/24 -j LOGDROP
iptables -I INPUT -m policy --dir in --pol ipsec -j ACCEPT
# confirm with a ping
ping -n -c 4 -I 192.0.1.254 192.0.2.254
ipsec start
/testing/pluto/bin/wait-until-pluto-started
ipsec auto --add westnet-eastnet-ikev2
echo "initdone"
