%define _prefix /usr
%define _bindir /usr/bin
%define _sbindir /usr/sbin
%define _includedir /usr/include
%ifarch x86_64
%define _libdir /usr/lib64
%else
%define _libdir /usr/lib
%endif
%define _sysconfdir /etc
%define _localstatedir /var
%define _infodir /usr/share/info
%define _mandir /usr/share/man

Name:		fwknop
Version:	2.0.3
Epoch:      1
Release:	1%{?dist}
Summary:	Firewall Knock Operator client.  An implementation of Single Packet Authorization.

Group:		Applications/Internet
License:	GPL
URL:		http://www.cipherdyne.org/fwknop/
Source0:	fwknop-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	gpg, gpgme-devel, libpcap-devel, gdbm-devel, iptables

Requires:	libfko, iptables


%package -n libfko
Version:	0.0.3
Summary:	The fwknop library
Group:		Development/Libraries
Requires:   gpg, gpgme

%package -n libfko-devel
Version:	0.0.3
Summary:	The fwknop library header and API docs
Group:		Development/Libraries
Requires:	libfko

%package server
Summary:	The Firewall Knock Operator server.  An implementation of Single Packet Authorization.
Group:		System Environment/Daemons
Requires:	libfko, libpcap, gdbm, iptables


%description
Fwknop implements an authorization scheme known as Single Packet Authorization
(SPA) for Linux systems running iptables.  This mechanism requires only a
single encrypted and non-replayed packet to communicate various pieces of
information including desired access through an iptables policy. The main
application of this program is to use iptables in a default-drop stance to
protect services such as SSH with an additional layer of security in order
to make the exploitation of vulnerabilities (both 0-day and unpatched code)
much more difficult.

%description -n libfko
The Firewall Knock Operator library, libfko, provides the Single Packet
Authorization implementation and API for the other fwknop components.

%description -n libfko-devel
This is the libfko development header and API documentation.

%description server
The Firewall Knock Operator server component for the FireWall Knock Operator,
and is responsible for monitoring Single Packet Authorization (SPA) packets
that are generated by fwknop clients, modifying a firewall or acl policy to
allow the desired access after decrypting a valid SPA packet, and removing
access after a configurable timeout.

%prep
%setup -q


%build
./configure \
    --prefix=%{_prefix} \
    --sysconfdir=%{_sysconfdir} \
    --localstatedir=%{_localstatedir} \
    --libdir=%{_libdir} \
    --with-gpgme

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
install -D ./extras/fwknop.init.redhat ${RPM_BUILD_ROOT}/etc/rc.d/init.d/fwknopd
# Just in case...
[ -d "${RPM_BUILD_ROOT}/usr/share/info" ] \
    || mkdir -p ${RPM_BUILD_ROOT}/usr/share/info
[ -f "${RPM_BUILD_ROOT}/usr/share/info/dir" ] \
    || touch ${RPM_BUILD_ROOT}/usr/share/info/dir

%clean
rm -rf $RPM_BUILD_ROOT

%post -n libfko-devel
/sbin/ldconfig
/sbin/install-info %{_infodir}/libfko.info* %{_infodir}/dir

%post -n fwknop-server
/sbin/chkconfig --add fwknopd
/sbin/chkconfig fwknopd off

%preun -n fwknop-server
/sbin/chkconfig --del fwknopd

%preun -n libfko-devel
if [ "$1" = 0 ]; then
 /sbin/install-info --delete %{_infodir}/libfko.info* %{_infodir}/dir
fi

%postun -n libfko
/sbin/ldconfig

%files
%defattr(-,root,root,-)
%attr(0755,root,root) %{_bindir}/fwknop
%attr(0644,root,root) %{_mandir}/man8/fwknop.8*
%exclude %{_infodir}/dir

%files -n libfko
%defattr(-,root,root,-)
%attr(0644,root,root) %{_libdir}/libfko.*

%files -n libfko-devel
%defattr(-,root,root,-)
%attr(0644,root,root) %{_includedir}/fko.h
%attr(0644,root,root) %{_infodir}/libfko.info*

%files server
%defattr(-,root,root,-)
%attr(0755,root,root) %{_sbindir}/fwknopd
%attr(0755,root,root) /etc/rc.d/init.d/fwknopd
%attr(0644,root,root) %{_mandir}/man8/fwknopd.8*
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/fwknop/fwknopd.conf
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/fwknop/access.conf

%changelog
* Thu Jul 15 2010 Damien Stuart <dstuart@dstuart.org>
- Fixed some misplaced depenencies (moved gpgpme from server to libfko).

* Wed Jul  7 2010 Damien Stuart <dstuart@dstuart.org>
- Made the post and preun steps specific to libfko-devel.

* Tue Jul  6 2010 Damien Stuart <dstuart@dstuart.org>
- Initial RPMification.

###EOF###
