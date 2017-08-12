
# These are rpm macros and are 0 or 1
%global crl_fetching 1
%global _hardened_build 1
%global fipscheck_version 1.3.0
%global buildefence 0
%global development 0
%global cavstests 1

# These are libreswan/make macros and are false or true
%global USE_FIPSCHECK true
%global USE_LIBCAP_NG true
%global USE_LABELED_IPSEC true
%global USE_DNSSEC true
%global USE_NM true
%global USE_LINUX_AUDIT true
# not production ready yet
%global USE_SECCOMP false

#global prever rc1

Name: libreswan
Summary: IPsec implementation with IKEv1 and IKEv2 keying protocols
# version is generated in the release script
Version: IPSECBASEVERSION
Release: %{?prever:0.}1%{?prever:.%{prever}}%{?dist}
License: GPLv2
Url: https://libreswan.org/
Source0: https://download.libreswan.org/%{?prever:development/}%{name}-%{version}%{?prever}.tar.gz
%if %{cavstests}
Source1: https://download.libreswan.org/cavs/ikev1_dsa.fax.bz2
Source2: https://download.libreswan.org/cavs/ikev1_psk.fax.bz2
Source3: https://download.libreswan.org/cavs/ikev2.fax.bz2

%endif
Group: System Environment/Daemons
BuildRequires: bison flex pkgconfig
BuildRequires: systemd systemd-units systemd-devel
Requires(post): coreutils bash systemd
Requires(preun): systemd
Requires(postun): systemd

Conflicts: openswan < %{version}-%{release}
Obsoletes: openswan < %{version}-%{release}
Provides: openswan = %{version}-%{release}
Provides: openswan-doc = %{version}-%{release}

BuildRequires: pkgconfig hostname
BuildRequires: nss-devel >= 3.16.1, nspr-devel
BuildRequires: pam-devel
BuildRequires: libevent-devel
%if %{USE_DNSSEC}
BuildRequires: unbound-devel >= 1.6.0-6 ldns-devel
%endif
%if %{USE_SECCOMP}
BuildRequires: libseccomp-devel
%endif
%if %{USE_LABELED_IPSEC}
BuildRequires: libselinux-devel
%endif
%if %{USE_FIPSCHECK}
BuildRequires: fipscheck-devel >= %{fipscheck_version}
Requires: fipscheck%{_isa} >= %{fipscheck_version}
%endif
%if %{USE_LINUX_AUDIT}
Buildrequires: audit-libs-devel
%endif

%if %{USE_LIBCAP_NG}
BuildRequires: libcap-ng-devel
%endif
%if %{crl_fetching}
BuildRequires: openldap-devel curl-devel
%endif
%if %{buildefence}
BuildRequires: ElectricFence
%endif
BuildRequires: xmlto

Requires: nss-tools, nss-softokn
Requires: iproute >= 2.6.8

%description
Libreswan is a free implementation of IPsec & IKE for Linux.  IPsec is
the Internet Protocol Security and uses strong cryptography to provide
both authentication and encryption services.  These services allow you
to build secure tunnels through untrusted networks.  Everything passing
through the untrusted net is encrypted by the ipsec gateway machine and
decrypted by the gateway at the other end of the tunnel.  The resulting
tunnel is a virtual private network or VPN.

This package contains the daemons and userland tools for setting up
Libreswan. To build KLIPS, see the kmod-libreswan.spec file.

Libreswan also supports IKEv2 (RFC4309) and Secure Labeling

Libreswan is based on Openswan-2.6.38 which in turn is based on FreeS/WAN-2.04

%prep
%setup -q -n libreswan-%{version}%{?prever}
sed -i "s:/usr/bin/python:/usr/bin/python3:" programs/verify/verify.in

%build
%if %{buildefence}
 %global efence "-lefence"
%endif

#796683: -fno-strict-aliasing
make %{?_smp_mflags} \
%if %{development}
   USERCOMPILE="-g -DGCC_LINT %(echo %{optflags} | sed -e s/-O[0-9]*/ /) %{?efence} -fPIE -pie -fno-strict-aliasing -Wformat-nonliteral -Wformat-security" \
%else
  USERCOMPILE="-g -DGCC_LINT %{optflags} %{?efence} -fPIE -pie -fno-strict-aliasing -Wformat-nonliteral -Wformat-security" \
%endif
  USERLINK="-g -pie -Wl,-z,relro,-z,now %{?efence}" \
  INITSYSTEM=systemd \
  USE_NM=%{USE_NM} \
  USE_XAUTHPAM=true \
%if %{USE_FIPSCHECK}
  USE_FIPSCHECK="%{USE_FIPSCHECK}" \
  FIPSPRODUCTCHECK=%{_sysconfdir}/system-fips \
%endif
  USE_LIBCAP_NG="%{USE_LIBCAP_NG}" \
  USE_LABELED_IPSEC="%{USE_LABELED_IPSEC}" \
%if %{crl_fetching}
  USE_LDAP=true \
  USE_LIBCURL=true \
%else
  USE_LDAP=false \
  USE_LIBCURL=false \
%endif
  USE_DNSSEC="%{USE_DNSSEC}" \
  USE_SECCOMP="%{USE_SECCOMP}" \
  INC_USRLOCAL=%{_prefix} \
  FINALLIBEXECDIR=%{_libexecdir}/ipsec \
  MANTREE=%{_mandir} \
  INC_RCDEFAULT=%{_initrddir} \
  NSS_REQ_AVA_COPY=false \
  programs
FS=$(pwd)

%if %{USE_FIPSCHECK}
# Add generation of HMAC checksums of the final stripped binaries
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
  fipshmac -d %{buildroot}%{_libdir}/fipscheck %{buildroot}%{_libexecdir}/ipsec/pluto \
%{nil}
%endif

%install
make \
  DESTDIR=%{buildroot} \
  INC_USRLOCAL=%{_prefix} \
  FINALLIBEXECDIR=%{_libexecdir}/ipsec \
  MANTREE=%{buildroot}%{_mandir} \
  INC_RCDEFAULT=%{_initrddir} \
  INSTMANFLAGS="-m 644" \
  INITSYSTEM=systemd \
  USE_NM=%{USE_NM} \
  USE_XAUTHPAM=true \
%if %{USE_FIPSCHECK}
  USE_FIPSCHECK="%{USE_FIPSCHECK}" \
  FIPSPRODUCTCHECK=%{_sysconfdir}/system-fips \
%endif
  USE_LIBCAP_NG="%{USE_LIBCAP_NG}" \
  USE_LABELED_IPSEC="%{USE_LABELED_IPSEC}" \
%if %{crl_fetching}
  USE_LDAP=true \
  USE_LIBCURL=true \
%else
  USE_LDAP=false \
  USE_LIBCURL=false \
%endif
  USE_DNSSEC="%{USE_DNSSEC}" \
  USE_SECCOMP="%{USE_SECCOMP}" \
  NSS_REQ_AVA_COPY=false \
  install
FS=$(pwd)
rm -rf %{buildroot}/usr/share/doc/libreswan

install -d -m 0700 %{buildroot}%{_localstatedir}/run/pluto
# used when setting --perpeerlog without --perpeerlogbase
install -d -m 0700 %{buildroot}%{_localstatedir}/log/pluto/peer
install -d %{buildroot}%{_sbindir}

install -d %{buildroot}%{_sysconfdir}/sysctl.d
install -m 0644 packaging/fedora/libreswan-sysctl.conf \
  %{buildroot}%{_sysconfdir}/sysctl.d/50-libreswan.conf

install -d %{buildroot}%{_tmpfilesdir}
install -m 0644 packaging/fedora/libreswan-tmpfiles.conf  \
  %{buildroot}%{_tmpfilesdir}/libreswan.conf

%if %{USE_FIPSCHECK}
mkdir -p %{buildroot}%{_libdir}/fipscheck
%endif

echo "include %{_sysconfdir}/ipsec.d/*.secrets" \
     > %{buildroot}%{_sysconfdir}/ipsec.secrets
rm -fr %{buildroot}%{_sysconfdir}/rc.d/rc*

%if %{cavstests}
%check
# There is an elaborate upstream testing infrastructure which we do not
# run here - it takes hours and uses kvm
# We only run the CAVS tests.
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} .
bunzip2 *.fax.bz2

# work around for older xen based machines
export NSS_DISABLE_HW_GCM=1

: starting CAVS test for IKEv2
OBJ.linux.%{_arch}/testing/cavp/cavp -v2 ikev2.fax | \
    diff -u ikev2.fax - > /dev/null
: starting CAVS test for IKEv1 RSASIG
OBJ.linux.%{_arch}/testing/cavp/cavp -v1sig ikev1_dsa.fax | \
    diff -u ikev1_dsa.fax - > /dev/null
: starting CAVS test for IKEv1 PSK
OBJ.linux.%{_arch}/testing/cavp/cavp -v1psk ikev1_psk.fax | \
    diff -u ikev1_psk.fax - > /dev/null
: CAVS tests passed
%endif

%post
%systemd_post ipsec.service

%preun
%systemd_preun ipsec.service

%postun
%systemd_postun_with_restart ipsec.service

%files
%doc CHANGES COPYING CREDITS README* LICENSE
%doc docs/*.* docs/examples
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ipsec.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ipsec.secrets
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ipsec.d/v6neighbor-hole.conf
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d/policies
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ipsec.d/policies/*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysctl.d/50-libreswan.conf
%attr(0700,root,root) %dir %{_localstatedir}/log/pluto
%attr(0700,root,root) %dir %{_localstatedir}/log/pluto/peer
%attr(0700,root,root) %dir %{_localstatedir}/run/pluto
%attr(0644,root,root) %{_tmpfilesdir}/libreswan.conf
%attr(0644,root,root) %{_unitdir}/ipsec.service
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pam.d/pluto
%{_sbindir}/ipsec
%{_libexecdir}/ipsec
%attr(0644,root,root) %doc %{_mandir}/*/*

%if %{USE_FIPSCHECK}
%{_libdir}/fipscheck/pluto.hmac
%endif

%changelog
* Wed Aug  9 2017 Team Libreswan <team@libreswan.org> - IPSECBASEVERSION-1
- Automated build from release tar ball
