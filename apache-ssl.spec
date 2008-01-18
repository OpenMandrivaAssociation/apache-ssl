%define rver	1.3.41
%define sslver	1.57

%define target	httpsd
%define __root	/var/lib/%{target}
%define u_name	apassl
%define g_name	apassl

Summary:	Apache-SSL is a secure Webserver
Name:		apache-ssl
Version:	%{rver}_%{sslver}
Release:	%mkrel 1
Group:		System/Servers
License:	BSD-style
URL:		http://www.apache-ssl.org/
Source0:	http://archive.apache.org/dist/httpd/apache_%{rver}.tar.gz
Source1:	http://archive.apache.org/dist/httpd/apache_%{rver}.tar.gz.asc
Source2:	apache_1.3.34+ssl_%{sslver}.tar.gz
Source3:	apache-ssl.init
Source4:	apache-ssl.conf
Source5:	mandrivalinux_web_contents.tar.gz
Source100:	mod_throttle-3.1.2.tar.gz
# http://sourceforge.net/projects/mod-gzip/
Source101:	mod_gzip-1.3.26.1a.tar.gz
Source102:	mod_put-1.3.tar.gz
Patch0:		apache_1.3.11-apxs.patch
Patch1:		apache_1.3.26-srvroot.patch
Patch2:		apache-1.3.23-dbm.patch
Patch3:		apache-1.3.33_db4.diff
Patch5:		apache-1.3.14-mkstemp.patch
Patch6:		apache-1.3.20.manpage.patch
Patch7:		apache-1.3.22-man.patch
Patch8:		apache_1.3.29-fPIC.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	perl >= 0:5.601
BuildRequires:	db4-devel
BuildRequires:	glibc-devel
BuildRequires:	openssl-devel >= 0.9.8a
Provides:	webserver 
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
Apache-SSL is a secure Webserver, based on Apache and SSLeay/OpenSSL. It is 
licensed under a BSD-style licence, which means, in short, that you are free 
to use it for commercial or non-commercial purposes, so long as you retain 
the copyright notices. This is the same licence as used by Apache from
version 0.8.15.

%package	devel
Summary:	Module development tools for Apache-SSL
Group:		Development/C
Requires:	perl >= 0:5.601
Requires:	db4-devel
Requires:	glibc-devel
Requires:	openssl-devel >= 0.9.8a

%description	devel
Apache-SSL is a secure Webserver, based on Apache and SSLeay/OpenSSL. It is 
licensed under a BSD-style licence, which means, in short, that you are free 
to use it for commercial or non-commercial purposes, so long as you retain 
the copyright notices. This is the same licence as used by Apache from
version 0.8.15.

The apache-devel package contains the header files and libraries 
for Apache 1.3 and the APXS binary you'll need to build Dynamic
Shared Objects (DSOs) for Apache.

If you are installing the Apache 1.3 server and
you want to be able to compile or develop additional modules
for it, you'll need to install this package.

%prep

%setup -q -n apache_%{rver} -a2 -a5 -a100 -a101 -a102
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0
%patch5 -p1 -b .mkstemp
%patch6 -p0
%patch7 -p0
%patch8 -p0 -b .fPIC

# apply the apache-ssl patch
perl -pi -e "s|\"1\.3\.34\"|\"%{rver}\"|g" SSLpatch
patch -p1 < SSLpatch

#Correct perl paths
find -type f|xargs perl -pi -e " s|/usr/local/bin/perl|%{_bindir}/perl|g; \
	s|/usr/local/bin/perl5|%{_bindir}/perl|g; \
	s|/path/to/bin/perl|%{_bindir}/perl|g; \
	" 
# fix paths
#perl -pi -e "s|^KEYNOTE_BASE=.*|KEYNOTE_BASE=%{_sysconfdir}/%{target}/conf/keynote|g" src/Configuration*
perl -pi -e "s|^SSL_BASE=.*|SSL_BASE=SYSTEM|g" src/Configuration*
perl -pi -e "s|^SSL_INCLUDE=.*|SSL_INCLUDE=-I%{_includedir}/openssl|g" src/Configuration*
perl -pi -e "s|^SSL_CFLAGS=.*|SSL_CFLAGS=-DAPACHE_SSL|g" src/Configuration*
perl -pi -e "s|^SSL_LIB_DIR=.*|SSL_LIB_DIR=-L%{_libdir}|g" src/Configuration*
perl -pi -e "s|^SSL_LIBS=.*|SSL_LIBS=-L%{_libdir} -lssl -lcrypto|g" src/Configuration*
perl -pi -e "s|^SSL_APP_DIR=.*|SSL_APP_DIR=%{_bindir}|g" src/Configuration*
perl -pi -e "s|^SSL_APP=.*|SSL_APP=%{_bindir}/openssl|g" src/Configuration*
perl -pi -e "s|^TARGET=.*|TARGET=%{target}|g" src/Configuration*

cp %{SOURCE3} httpsd.init
cp %{SOURCE4} httpsd.conf

# move extra modules in place
cp mod_throttle-3.1.2/mod_throttle.c src/modules/extra/
mv mod_gzip-1.3.26.1a src/modules/gzip
cp mod_put-1.3/mod_put.c src/modules/extra/

# activate extra modules
echo "AddModule modules/extra/mod_throttle.o" >> src/Configuration.tmpl
echo "AddModule modules/gzip/mod_gzip.o" >> src/Configuration.tmpl
echo "AddModule modules/extra/mod_put.o" >> src/Configuration.tmpl

# fix mod_throttle (the NPTL issue...)
perl -pi -e "s|^#define USE_SYSTEM_V_SERIALIZATION|#undef USE_SYSTEM_V_SERIALIZATION|g" src/modules/extra/mod_throttle.c
#perl -pi -e "s|^#define USE_SYSTEM_V_SHARED_MEMORY|#undef USE_SYSTEM_V_SHARED_MEMORY|g" src/modules/extra/mod_throttle.c
perl -pi -e "s|^#undef USE_FCNTL_SERIALIZATION|#define USE_FCNTL_SERIALIZATION|g" src/modules/extra/mod_throttle.c
#perl -pi -e "s|^#undef USE_POSIX_SHARED_MEMORY|#define USE_POSIX_SHARED_MEMORY|g" src/modules/extra/mod_throttle.c

# fix mod_throttle docs
cp mod_throttle-3.1.2/CHANGES.txt mod_throttle.CHANGES
cp mod_throttle-3.1.2/index.shtml mod_throttle.html
cp mod_throttle-3.1.2/LICENSE.txt mod_throttle.LICENSE

# fix mod_gzip docs
cp -rp src/modules/gzip/docs/manual/english mod_gzip
cp src/modules/gzip/ChangeLog ChangeLog.mod_gzip
cp src/modules/gzip/docs/mod_gzip.conf.sample .

# fix mod_put docs
cp mod_put-1.3/mod_put.html .

# fix funny naming...
perl -pi -e "s|libssl|mod_ssl|g" src/modules/ssl/Makefile.tmpl
perl -pi -e "s|libproxy|mod_proxy|g" src/modules/proxy/Makefile.tmpl
perl -pi -e "s|libgzip|mod_gzip|g" src/modules/gzip/Makefile.tmpl

%build

%serverbuild

export OPTIM="%{optflags} -fno-strict-aliasing"
export CFLAGS="-D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 -DUSE_FCNTL_SERIALIZED_ACCEPT -DHARD_SERVER_LIMIT=2048 -DDB_DBM_HSEARCH"
export LIBS="-lpthread"

./configure \
    --prefix=%{_sysconfdir}/%{target} \
    --exec-prefix=%{_exec_prefix} \
    --bindir=%{_bindir} \
    --sbindir=%{_sbindir} \
    --sysconfdir=%{_sysconfdir}/%{target}/conf \
    --datadir=%{_datadir} \
    --includedir=%{_includedir}/%{target} \
    --libexecdir=%{_libdir}/%{target} \
    --localstatedir=%{_localstatedir} \
    --mandir=%{_mandir} \
    --iconsdir=%{__root}/icons \
    --htdocsdir=%{__root}/html \
    --manualdir=%{_docdir}/%{name}-%{version}/manual \
    --cgidir=%{__root}/cgi-bin \
    --runtimedir=/var/run/%{target} \
    --logfiledir=/var/log/%{target} \
    --with-perl=%{_bindir}/perl \
    --with-port=444 \
    --server-uid=%{u_name} \
    --server-gid=%{g_name} \
    --disable-rule=expat \
    --disable-rule=WANTHSREGEX \
    --enable-rule=SHARED_CORE \
    --enable-rule=DEV_RANDOM=/dev/urandom \
    --enable-module=env --enable-shared=env \
    --enable-module=log_config --enable-shared=log_config \
    --enable-module=mime_magic --enable-shared=mime_magic \
    --enable-module=mime --enable-shared=mime \
    --enable-module=negotiation --enable-shared=negotiation \
    --enable-module=status --enable-shared=status \
    --enable-module=info --enable-shared=info \
    --enable-module=include --enable-shared=include \
    --enable-module=autoindex --enable-shared=autoindex \
    --enable-module=digest --enable-shared=digest \
    --enable-module=dir --enable-shared=dir \
    --enable-module=cgi --enable-shared=cgi \
    --enable-module=asis --enable-shared=asis \
    --enable-module=imap --enable-shared=imap \
    --enable-module=actions --enable-shared=actions \
    --enable-module=speling --enable-shared=speling \
    --enable-module=userdir --enable-shared=userdir \
    --enable-module=alias --enable-shared=alias \
    --enable-module=rewrite --enable-shared=rewrite \
    --enable-module=access --enable-shared=access \
    --enable-module=auth --enable-shared=auth \
    --enable-module=auth_anon --enable-shared=auth_anon \
    --enable-module=auth_db --enable-shared=auth_db \
    --enable-module=auth_dbm --enable-shared=auth_dbm \
    --enable-module=proxy --enable-shared=proxy --proxycachedir=/var/cache/%{target} \
    --enable-module=expires --enable-shared=expires \
    --enable-module=headers --enable-shared=headers \
    --enable-module=usertrack --enable-shared=usertrack \
    --enable-module=unique_id --enable-shared=unique_id \
    --enable-module=setenvif --enable-shared=setenvif \
    --enable-module=vhost_alias --enable-shared=vhost_alias \
    --enable-module=apache_ssl --enable-shared=apache_ssl \
    --enable-suexec --suexec-caller=%{u_name} --suexec-docroot=%{__root}/html \
    --suexec-logfile=/var/log/%{target}/suexec_log --suexec-userdir=public_html \
    --suexec-uidmin=500 --suexec-gidmin=500 --suexec-safepath="/usr/local/bin:/usr/bin:/bin" \
    --suexec-umask=022 \
    --enable-module=throttle --enable-shared=throttle \
    --enable-module=gzip --enable-shared=gzip \
    --enable-module=put --enable-shared=put

# call the correct wrapper
perl -pi -e "s|%{_sbindir}/suexec|%{_sbindir}/%{target}-suexec|g" src/apaci

# seems to build just fine without ndbm (db2)
# find -name "Makefile" | xargs perl -pi -e "s|\-lndbm ||g"

make

# enable ssl in ab
rm -f src/support/ab src/support/ab.o
make -C src/support \
    CFLAGS="$CFLAGS -I%{_includedir}/openssl -DUSE_SSL " \
    LIBS="-L../os/unix -L../ap -lap -los -lpthread -lm -lcrypt -ldb -ldl -L%{_libdir} -lssl -lcrypto" \
    ab

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

make \
    root=%{buildroot} \
    install

# for some reason these files don't get installed...
install -m0755 src/modules/ssl/mod_ssl.so %{buildroot}%{_libdir}/%{target}/mod_ssl.so
install -m0755 src/modules/proxy/mod_proxy.so %{buildroot}%{_libdir}/%{target}/mod_proxy.so

install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/ssl/%{target}

cat > %{name}.logrotate << EOF
/var/log/%{target}/ssl_log /var/log/%{target}/access_log /var/log/%{target}/error_log /var/log/%{target}/agent_log /var/log/%{target}/referer_log /var/log/%{target}/apache_runtime_status /var/log/%{target}/suexec_log
{
    size=2000M
    rotate 5
    monthly
    missingok
    notifempty
    nocompress
    prerotate
	%{_initrddir}/%{target} restart
    endscript
    postrotate
	%{_initrddir}/%{target} restart
    endscript
}
EOF
install -m0644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{target}

# install the init script
install -m755 httpsd.init %{buildroot}%{_initrddir}/%{target}

# fix manual
rm -rf manual
mv %{buildroot}%{_docdir}/%{name}-%{version}/manual .

# install static libs
find -type f|grep "\.a$"|xargs -iFL cp -f FL %{buildroot}%{_libdir}/%{target}/

# rename some files
mv %{buildroot}%{_bindir}/checkgid %{buildroot}%{_bindir}/%{target}-checkgid
mv %{buildroot}%{_bindir}/dbmmanage %{buildroot}%{_bindir}/%{target}-dbmmanage
mv %{buildroot}%{_bindir}/htdigest %{buildroot}%{_bindir}/%{target}-htdigest
mv %{buildroot}%{_bindir}/htpasswd %{buildroot}%{_bindir}/%{target}-htpasswd
mv %{buildroot}%{_sbindir}/ab %{buildroot}%{_sbindir}/%{target}-ab
mv %{buildroot}%{_sbindir}/apxs %{buildroot}%{_sbindir}/%{target}-apxs
mv %{buildroot}%{_sbindir}/suexec %{buildroot}%{_sbindir}/%{target}-suexec
mv %{buildroot}%{_sbindir}/logresolve %{buildroot}%{_sbindir}/%{target}-logresolve
mv %{buildroot}%{_sbindir}/rotatelogs %{buildroot}%{_sbindir}/%{target}-rotatelogs
mv %{buildroot}%{_mandir}/man1/dbmmanage.1 %{buildroot}%{_mandir}/man1/%{target}-dbmmanage.1
mv %{buildroot}%{_mandir}/man1/htdigest.1 %{buildroot}%{_mandir}/man1/%{target}-htdigest.1
mv %{buildroot}%{_mandir}/man1/htpasswd.1 %{buildroot}%{_mandir}/man1/%{target}-htpasswd.1
mv %{buildroot}%{_mandir}/man8/ab.8 %{buildroot}%{_mandir}/man8/%{target}-ab.8 
mv %{buildroot}%{_mandir}/man8/apxs.8 %{buildroot}%{_mandir}/man8/%{target}-apxs.8 
mv %{buildroot}%{_mandir}/man8/logresolve.8 %{buildroot}%{_mandir}/man8/%{target}-logresolve.8 
mv %{buildroot}%{_mandir}/man8/rotatelogs.8 %{buildroot}%{_mandir}/man8/%{target}-rotatelogs.8 
mv %{buildroot}%{_mandir}/man8/suexec.8 %{buildroot}%{_mandir}/man8/%{target}-suexec.8 

# house cleaning
rm -f %{buildroot}%{__root}/cgi-bin/*
rm -f %{buildroot}%{_sysconfdir}/%{target}/conf/*.default
rm -f %{buildroot}%{__root}/html/index*
rm -f %{buildroot}%{__root}/html/*.gif
rm -f %{buildroot}%{_sysconfdir}/%{target}/conf/access.conf
rm -f %{buildroot}%{_sysconfdir}/%{target}/conf/srm.conf

# use our own web contents, call it branding if you like...
install -m0644 mandrivalinux_web_contents/* %{buildroot}%{__root}/html/

# fix funny naming...
perl -pi -e "s|apache_ssl\.so|mod_ssl\.so|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|libproxy\.so|mod_proxy.\so|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf

# now tuck the config file away as we use our own 
mv %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf %{target}-VANILLA.conf 
install -m0644 httpsd.conf %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf


# fix manual
pushd manual
    for i in `find -name "*.html.en"`; do
	new_name=`echo $i | sed -e "s/.html.en/.html/g"`
	mv -f $i $new_name
    done
# we don't need these
find -name "*.ja.jis" | xargs rm -f
find -name "*.fr" | xargs rm -f
find -name "*.html.html" | xargs rm -f
rm -rf search
popd

# do some replacing...
perl -pi -e "s|_TARGET_|%{target}|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|_TARGET_|%{target}|g" %{buildroot}%{_initrddir}/%{target}
perl -pi -e "s|_USERNAME_|%{u_name}|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|_GROUPNAME_|%{g_name}|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|_ROOT_|%{__root}|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|_VERSION_|%{version}|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|_LIBDIR_|%{_libdir}|g" %{buildroot}%{_sysconfdir}/%{target}/conf/%{target}.conf
perl -pi -e "s|_VERSION_|%{version}|g" %{buildroot}%{__root}/html/index.html

%pre
%_pre_useradd %{u_name} %{__root} /bin/sh

%post
umask 077
if [ ! -f %{_sysconfdir}/ssl/%{target}/dummycert.key ] ; then
    %{_bindir}/openssl genrsa -rand /proc/apm:/proc/cpuinfo:/proc/dma:/proc/filesystems:/proc/interrupts:/proc/ioports:/proc/pci:/proc/rtc:/proc/uptime 1024 > %{_sysconfdir}/ssl/%{target}/dummycert.key 2> /dev/null
fi

FQDN=`hostname`
if [ "x${FQDN}" = "x" ]; then
    FQDN=localhost.localdomain
fi

if [ ! -f %{_sysconfdir}/ssl/%{target}/dummycert.crt ] ; then
cat << EOF | %{_bindir}/openssl req -new -key %{_sysconfdir}/ssl/%{target}/dummycert.key -x509 -days 365 -out %{_sysconfdir}/ssl/%{target}/dummycert.crt 2>/dev/null
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
${FQDN}
root@${FQDN}
EOF
fi

%_post_service %{target}

%preun
%_preun_service %{target}

%postun
%_postun_userdel %{u_name}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 

%files 
%defattr(-,root,root)
%doc CHANGES.SSL EXTRAS.SSL LICENCE.SSL README.SSL SECURITY manual %{target}-VANILLA.conf
%doc mod_throttle.CHANGES mod_throttle.html mod_throttle.LICENSE
%doc mod_put.html mod_gzip ChangeLog.mod_gzip mod_gzip.conf.sample
%attr(0755,root,root) %dir %{_sysconfdir}/%{target}
%attr(0755,root,root) %dir %{_sysconfdir}/%{target}/conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{target}/conf/%{target}.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{target}/conf/magic
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{target}/conf/mime.types
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{target}
#%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ssl/%{target}/
%attr(0755,root,root) %{_initrddir}/%{target}
%attr(0700,root,root) %dir %{_sysconfdir}/ssl/%{target}

%{_bindir}/%{target}-checkgid
%{_bindir}/%{target}-dbmmanage
%{_bindir}/%{target}-htdigest
%{_bindir}/%{target}-htpasswd
%{_sbindir}/%{target}-ab
%{_sbindir}/%{target}-suexec
%{_sbindir}/httpsdctl
%{_sbindir}/%{target}-logresolve
%{_sbindir}/%{target}-rotatelogs
%{_sbindir}/%{target}
%{_sbindir}/gcache

%attr(0755,root,root) %dir %{_libdir}/%{target}
%{_libdir}/%{target}/*.exp
%{_libdir}/%{target}/*.ep
%{_libdir}/%{target}/*.so

%attr(0754,%{u_name},%{g_name}) %dir %{__root}
%attr(0754,%{u_name},%{g_name}) %dir %{__root}/html
%attr(0754,%{u_name},%{g_name}) %dir %{__root}/icons
%attr(0754,%{u_name},%{g_name}) %dir /var/run/%{target}
%attr(0754,%{u_name},%{g_name}) %dir /var/log/%{target}
%attr(0754,%{u_name},%{g_name}) %dir /var/cache/%{target}
%attr(0754,%{u_name},%{g_name}) %dir %{__root}/cgi-bin

# web contents
%{__root}/icons/*
%attr(0644,root,root) %config(noreplace) %{__root}/html/index.html
%attr(0644,root,root) %config(noreplace) %{__root}/html/favicon.ico
%attr(0644,root,root) %config(noreplace) %{__root}/html/robots.txt
%attr(0644,root,root) %config(noreplace) %{__root}/html/apache_pb.png
%attr(0644,root,root) %config(noreplace) %{__root}/html/apache_ssl_button.png
%attr(0644,root,root) %config(noreplace) %{__root}/html/mandriva.png
%attr(0644,root,root) %config(noreplace) %{__root}/html/openssl.png

%{_mandir}/man1/%{target}-dbmmanage.1*
%{_mandir}/man1/%{target}-htdigest.1*
%{_mandir}/man1/%{target}-htpasswd.1*
%{_mandir}/man8/%{target}-ab.8*
%{_mandir}/man8/%{target}-suexec.8*
%{_mandir}/man8/%{target}-logresolve.8*
%{_mandir}/man8/%{target}-rotatelogs.8*
%{_mandir}/man8/httpsd.8*
%{_mandir}/man8/httpsdctl.8*

%files devel
%defattr(-,root,root)
%doc src/support/suexec.[ch]
%{_sbindir}/%{target}-apxs
%{_libdir}/%{target}/*.a
%attr(0755,root,root) %dir %{_includedir}/%{target}
%{_includedir}/%{target}/*
%{_mandir}/man8/%{target}-apxs.8*
