%define major 1
%define minor 4
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s

Summary:		The Irrlicht Engine SDK
Name:			irrlicht
Version:		1.4
Release:		%mkrel 2
License:		zlib
Group:			Graphics
URL:			http://irrlicht.sourceforge.net/
Source:			http://prdownloads.sourceforge.net/irrlicht/%{name}-%{version}.zip
Patch1:			%{name}-1.4-library-makefile.patch
Patch2:			%{name}-1.4-use-system-libs.patch
Patch3:			%{name}-1.4-GUIEditor-makefile.patch
Patch4:			%{name}-1.4-IrrFontTool-makefile.patch
Patch5:			%{name}-1.4-glXGetProcAddress.patch
Patch6:			%{name}-1.4-examples-makefile.patch
BuildRequires:		imagemagick
BuildRequires:		zlib-devel
BuildRequires:		libjpeg-devel
BuildRequires:		libpng-devel
BuildRequires:		mesa-common-devel
Requires:		%{libname} = %{version}-%{release}
Requires:		%{name}-media = %{version}-%{release}

%description
The Irrlicht Engine is an open source high performance realtime
3D engine written and usable in C++ and also available for .NET
languages. It is completely cross-platform, using D3D, OpenGL
and its own software renderer, and has all of the state-of-the-art
features which can be found in commercial 3d engines.

We've got a huge active community, and there are lots of projects
in development that use the engine. You can find enhancements for
Irrlicht all over the web, like alternative terrain renderers,
portal renderers, exporters, world layers, tutorials, editors,
language bindings for java, perl, ruby, basic, python, lua, and so
on. And best of all: It's completely free.

%package -n %{libname}
Summary:	Shared libraries for Irrlicht 3D engine
Group:		System/Libraries

%description -n %{libname}
Shared libraries for Irrlicht 3D engine.

%package -n %{develname}
Summary:	Development files for Irrlicht 3D engine
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n %{develname}
Development files for Irrlicht 3D engine.

%package -n %{staticname}
Summary:	Static files for Irrlicht 3D engine
Group:		Development/C
Requires:	%{develname}  = %{version}-%{release}

%description -n %{staticname}
Static files for Irrlicht 3D engine.

%package examples
Summary:	Demos and examples for the Irrlicht 3D engine
Group:		Graphics
Requires:	%{libname} = %{version}-%{release}

%description examples
Demos and examples for the Irrlicht 3D engine.

%package media
Summary:	Media files for Irrlicht 3D engine
Group:		Graphics
Requires:	%{name} = %{version}-%{release}

%description media
Media files needed by Irrlicht tools and demos.

%package doc
Summary:	User documentation for the Irrlicht 3D engine
Group:		Graphics
Requires:	%{libname} = %{version}-%{release}

%description doc
User documentation for the Irrlicht 3D engine.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%build
export LIBDIR="%{_libdir}"
export PREFIX="%{_prefix}"
export INCLUDEDIR="%{_includedir}"

# really not needed :)
rm -r examples/14.Win32Window

# needs irrKlang
rm -r examples/Demo
sed -i -e 's|Demo||g' examples/buildAllExamples.sh

# media path
sed -i -e 's|../../media/|%{_datadir}/irrlicht/|g' tools/GUIEditor/main.cpp
find ./examples -name *.cpp | xargs sed -i -e 's|../../media/|%{_datadir}/irrlicht/|g'

# build static library
%make -C source/Irrlicht \
    CFLAGS="%{optflags}" \
    CXXFLAGS="%{optflags}"

# clean it    
%make -C source/Irrlicht clean

# build shared library
%make -C source/Irrlicht sharedlib NDEBUG=1 \
    %ifnarch ix86
    CFLAGS="%{optflags} -fPIC" \
    CXXFLAGS="%{optflags} -fPIC"
    %else
    CFLAGS="%{optflags}" \
    CXXFLAGS="%{optflags}"
    %endif

# create necessary links to avoid linker-error for tools/examples
pushd lib/Linux
ln -s libIrrlicht.so.%{major}.%{minor} libIrrlicht.so.1
ln -s libIrrlicht.so.%{major}.%{minor} libIrrlicht.so
popd

# build tools
pushd tools
cd GUIEditor
%make CFLAGS="%{optflags}" CXXFLAGS="%{optflags}"
cd ..
cd IrrFontTool/newFontTool
%make CFLAGS="%{optflags}" CXXFLAGS="%{optflags}"
cd ../..
popd

# build examples
pushd examples
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
sh buildAllExamples.sh
popd

%install
mkdir -p %{buildroot}%{_libdir}

install -m 644 lib/Linux/libIrrlicht.a %{buildroot}%{_libdir}
install -m 755  lib/Linux/libIrrlicht.so.%{major}.%{minor}* %{buildroot}%{_libdir}

pushd %{buildroot}%{_libdir}
ln -s libIrrlicht.so.%{major}.%{minor} libIrrlicht.so
popd

# includes
mkdir -p %{buildroot}%{_includedir}/irrlicht
cp -f include/*.h %{buildroot}%{_includedir}/irrlicht

# tools
install -dm 755 %{buildroot}%{_bindir}
install -m 755 tools/GUIEditor/GUIEditor %{buildroot}%{_bindir}/irrlicht-GUIEditor
install -m 755 bin/Linux/FontTool %{buildroot}%{_bindir}/irrlicht-FontTool

# examples
install -dm 755 %{buildroot}%{_bindir}
ex_list=`ls -1 bin/Linux/??.*`
for i in $ex_list; do
	FE=`echo $i | awk 'BEGIN { FS="." }{ print $2 }'`
	    install -m 755 $i %{buildroot}%{_bindir}/irrlicht-$FE
done

# examples-docs
pushd examples
install -dm 755 %{buildroot}%{_docdir}/Irrlicht-examples
#install -m 644 * %{buildroot}%{_docdir}/Irrlicht-examples

ex_dir=`find . -name tutorial.html`
for i in $ex_dir; do
	dir_name=`dirname $i`
	install -dm 755 %{buildroot}%{_docdir}/Irrlicht-examples/$dir_name
	install -m 644 $i %{buildroot}%{_docdir}/Irrlicht-examples/$dir_name
done
rm -r %{buildroot}%{_docdir}/Irrlicht-examples/09.Meshviewer
popd

# media
mkdir -p %{buildroot}%{_datadir}/irrlicht
install -m 755 media/* %{buildroot}%{_datadir}/irrlicht

# icons
install -dm 755 %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
convert examples/09.Meshviewer/icon.ico -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/irrlicht-Meshviewer.png
convert bin/Win32-gcc/irrlicht.ico -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/irrlicht.png

convert examples/09.Meshviewer/icon.ico -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/irrlicht-Meshviewer.png
convert bin/Win32-gcc/irrlicht.ico -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/irrlicht.png

convert examples/09.Meshviewer/icon.ico -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/irrlicht-Meshviewer.png
convert bin/Win32-gcc/irrlicht.ico -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/irrlicht.png

# menu
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/irrlicht-GUIEditor.desktop << EOF
[Desktop Entry]
Name=Irrlicht GUI Editor
Comment=Irrlicht GUI Editor
Exec=%{_bindir}/irrlicht-GUIEditor
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=3DGraphics;GTK;
EOF

cat > %{buildroot}%{_datadir}/applications/irrlicht-FontTool.desktop << EOF
[Desktop Entry]
Name=Irrlicht Font Tool
Comment=Irrlicht Font Tool
Exec=%{_bindir}/irrlicht-FontTool
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=3DGraphics;GTK;
EOF

cat > %{buildroot}%{_datadir}/applications/irrlicht-Meshviewer.desktop << EOF
[Desktop Entry]
Name=Irrlicht Mesh Viewer
Comment=Irrlicht Mesh Viewer
Exec=%{_bindir}/irrlicht-Meshviewer
Icon=irrlicht-Meshviewer
Terminal=true
Type=Application
StartupNotify=true
Categories=3DGraphics;GTK;
EOF

%post
%{update_menus}
%update_icon_cache hicolor

%postun
%{clean_menus}
%clean_icon_cache hicolor

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc examples/09.Meshviewer/tutorial.html
%{_bindir}/irrlicht-GUIEditor
%{_bindir}/irrlicht-FontTool
%{_bindir}/irrlicht-Meshviewer
%{_datadir}/applications/*.desktop
%{_iconsdir}/hicolor/*/apps/*.png

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/lib*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%dir %{_includedir}/irrlicht
%{_libdir}/lib*.so
%{_includedir}/irrlicht/*.h

%files -n %{staticname}
%defattr(-,root,root)
%{_libdir}/lib*.a

%files examples
%defattr(-,root,root)
%dir %{_docdir}/Irrlicht-examples
%{_docdir}/Irrlicht-examples/*
%exclude %{_bindir}/irrlicht-GUIEditor
%exclude %{_bindir}/irrlicht-FontTool
%exclude %{_bindir}/irrlicht-Meshviewer
%{_bindir}/irrlicht-*

%files media
%defattr(644,root,root)
%dir %{_datadir}/irrlicht
%{_datadir}/irrlicht/*

%files doc
%defattr(-,root,root)
%doc doc/irrlicht.chm
%doc doc/*.txt
