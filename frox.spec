
%define		_kernel_ver	%(grep UTS_RELEASE %{_kernelsrcdir}/include/linux/version.h 2>/dev/null | cut -d'"' -f2)
%define		_kernel24	%(echo %{_kernel_ver} | grep -q '2\.[012]\.' ; echo $?)
%if %{_kernel24}
%define		_kernel_series	2.4
%else
%define		_kernel_series	2.2
%endif

Summary:	Transparent FTP proxy
Summary(pl):	Prze¼roczyste proxy FTP
Name:		frox
Version:	0.7.6
Release:	1@%{_kernel_series}
License:	GPL
Group:		Networking/Daemons
Source0:	http://frox.sourceforge.net/download/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
URL:		http://frox.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Frox is transparent FTP proxy. It also has support for non-transparent
connections, caching of anonymous ftp, and active --> passive
conversion of data connections.

%description -l pl
Frox to prze¼roczyste proxy FTP, posiada równie¿ wsparcie do
nie-transparentnych po³aczen, buforowania anonimowego ftp, i konwersji
aktywne-pasywne polaczenia.

%prep
%setup -q
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
%configure \
	--enable-http-cache \
	--enable-local-cache \
	%{?_kernel24:--enable-libiptc} \
	%{?!_kernel24:--disable-libiptc} \
	--enable-transparent-data \
	--enable-configfile=%{_sysconfdir}/frox.conf
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig,%{_mandir}/man{5,8}} \
	$RPM_BUILD_ROOT/var/lib/frox

%{__make} install DESTDIR=$RPM_BUILD_ROOT
install src/frox.conf	$RPM_BUILD_ROOT%{_sysconfdir}/frox.conf

install doc/frox.man	$RPM_BUILD_ROOT%{_mandir}/man8/frox.8
install doc/frox.conf.man	$RPM_BUILD_ROOT%{_mandir}/man5/frox.5
install %{SOURCE1}	$RPM_BUILD_ROOT/etc/rc.d/init.d/frox
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/sysconfig/frox

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ ! -n "`getgid frox`" ]; then
	/usr/sbin/groupadd -g 97 -r -f frox 1>&2 || :
fi

if [ ! -n "`id -u frox 2>/dev/null`" ]; then
	/usr/sbin/useradd -M -o -r -u 97 -s /bin/false \
		-g frox -c "FROX ftp caching daemon" -d /var/cache/frox frox 1>&2 || :
fi

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
	/usr/sbin/userdel frox 2> /dev/null
	/usr/sbin/groupdel frox 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/{FAQ,README.transdata,RELEASE,SECURITY,TODO}
%attr(754,root,root) /etc/rc.d/init.d/frox
%attr(750,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/frox
%attr(640,root,frox) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/frox.conf
%attr(755,root,root) %{_sbindir}/frox
%attr(770,root,frox) /var/lib/frox
%{_mandir}/man*/*
