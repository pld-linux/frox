#
# Conditional build:
%bcond_with	kernel22
#
Summary:	Transparent FTP proxy
Summary(pl):	Przezroczyste proxy FTP
Name:		frox
Version:	0.7.18
%if %{with kernel22}
Release:	1@2.2
%else
Release:	1
%endif
License:	GPL
Group:		Networking/Daemons
Source0:	http://frox.sourceforge.net/download/%{name}-%{version}.tar.bz2
# Source0-md5:	d30c35b9820d706ff2f9a6ab3b501247
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
URL:		http://frox.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	rpmbuild(macros) >= 1.202
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/groupmod
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(post,preun):	/sbin/chkconfig
Provides:	group(frox)
Provides:	user(frox)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Frox is transparent FTP proxy. It also has support for non-transparent
connections, caching of anonymous ftp, and active --> passive
conversion of data connections.

%description -l pl
Frox to przezroczyste proxy FTP, posiada równie¿ wsparcie do
nieprzezroczystych po³±czeñ, buforowania anonimowego ftp, i konwersji
po³±czeñ z aktywnych na pasywne.

%prep
%setup -q
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
%configure \
	--enable-http-cache \
	--enable-local-cache \
	%{?!with_kernel22:--enable-libiptc} \
	%{?with_kernel22:--disable-libiptc} \
	--enable-transparent-data \
	--enable-configfile=%{_sysconfdir}/frox.conf
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/lib/frox,%{_mandir}/man{5,8}} \
	$RPM_BUILD_ROOT/etc/{logrotate.d,sysconfig,rc.d/init.d} \
	$RPM_BUILD_ROOT/var/{log/{archiv/frox,frox},cache/frox}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install src/frox.conf	$RPM_BUILD_ROOT%{_sysconfdir}/frox.conf
install doc/frox.man	$RPM_BUILD_ROOT%{_mandir}/man8/frox.8
install doc/frox.conf.man	$RPM_BUILD_ROOT%{_mandir}/man5/frox.5
install %{SOURCE1}	$RPM_BUILD_ROOT/etc/rc.d/init.d/frox
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/sysconfig/frox

cat >$RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/frox << EOF
/var/log/frox/frox-log {
	olddir /var/log/archiv/frox
	nocreate
}
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "`/usr/bin/getgid frox`" = 97 ]; then
	/usr/sbin/groupmod -g 103 frox
fi
%groupadd -g 103 frox

if [ -n "`id -u frox 2>/dev/null`" ] && [ "`/bin/id -u frox`" = 97 ]; then
	/usr/sbin/usermod -u 103 frox
	chown -R frox:frox /var/cache/frox ||:
	chown -R root:frox /var/log/frox /var/log/archiv/frox ||:
fi
%useradd -u 103 -s /bin/false -g frox -c "FROX ftp caching daemon" -d /var/cache/frox frox

%post
/sbin/chkconfig --add frox
if [ -f /var/lock/subsys/frox ]; then
	/etc/rc.d/init.d/frox restart >&2
else
	echo "Run \"/etc/rc.d/init.d/frox start\" to start frox daemons."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/frox ]; then
		/etc/rc.d/init.d/frox stop >&2
	fi
	/sbin/chkconfig --del frox
fi

%postun
if [ "$1" = "0" ]; then
	%userremove frox
	%groupremove frox
fi

%files
%defattr(644,root,root,755)
%doc doc/{ChangeLog,FAQ,README.transdata,RELEASE,SECURITY,TODO}
%attr(754,root,root) /etc/rc.d/init.d/frox
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/frox
%attr(640,root,frox) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/frox.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/frox
%attr(755,root,root) %{_sbindir}/frox
%attr(770,root,frox) /var/lib/frox
%attr(770,root,frox) /var/log/frox
%attr(770,root,frox) /var/log/archiv/frox
%attr(770,frox,frox) /var/cache/frox
%{_mandir}/man*/*
