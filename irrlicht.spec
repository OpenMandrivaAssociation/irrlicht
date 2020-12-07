%define major %(echo %{version} |cut -d. -f1)
%define minor %(echo %{version} |cut -d. -f2)

%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s

Summary:	The Irrlicht Engine SDK
Name:		irrlicht
Version:	1.8.4
Release:	3
License:	Zlib
Group:		Graphics
URL:		http://irrlicht.sourceforge.net/
Source0:	http://heanet.dl.sourceforge.net/project/irrlicht/Irrlicht%20SDK/%{major}.%{minor}/irrlicht-%version.zip
Source1:	%{name}.rpmlintrc
Patch0:		irrlicht-1.8.4-remove-sys-sysctl.h.patch
Patch1:		irrlicht-1.8-library-makefile.patch
Patch2:		irrlicht-1.8-use-system-libs.patch
Patch3:		irrlicht-1.7.1-GUIEditor-makefile.patch
Patch4:		irrlicht-1.7.3-IrrFontTool-makefile.patch
Patch7:		irrlicht-1.5.1-glext.patch


BuildRequires:	imagemagick
BuildRequires:	zlib-devel
BuildRequires:	jpeg-devel
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xxf86vm)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xft)
BuildRequires:	pkgconfig(xcursor)
BuildRequires:	bzip2-devel
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name}-media = %{version}-%{release}
# We need a spec-helper that can deal with filenames containing spaces
BuildRequires:	spec-helper >= 0.31.24

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
%autopatch -p1

find . -name Makefile |xargs sed -i -e 's,-lX11,-lX11 -lz -lpng -ljpeg,g'

%build
%setup_compile_flags
export LIBDIR="%{_libdir}"
export PREFIX="%{_prefix}"
export INCLUDEDIR="%{_includedir}"

# really not needed :)
rm -r examples/14.Win32Window
rm -r source/Irrlicht/MacOSX
# (tpg) use system wide libs, see patch2
rm -rf source/Irrlicht/jpeglib source/Irrlicht/zlib source/Irrlicht/libpng source/Irrlicht/bzip2 
#source/Irrlicht/lzma source/Irrlicht/aesGladman
find source/Irrlicht -name '*.cpp' | xargs sed -i -e 's|zlib/zlib.h|zlib.h|g' -e 's|libpng/png.h|png.h|g' -e 's|jpeglib/jerror.h|jerror.h|g' -e 's|jpeglib/jpeglib.h|jpeglib.h|g'
find source/Irrlicht -name '*.h'   | xargs sed -i -e 's|jpeglib/jpeglib.h|jpeglib.h|g' -e 's|libpng/png.h|png.h|g' -e 's|jpeglib/jerror.h|jerror.h|g'

# needs irrKlang
rm -r examples/Demo
sed -i -e 's|Demo||g' examples/buildAllExamples.sh

# media path
sed -i -e 's|../../media/|%{_datadir}/irrlicht/|g' tools/GUIEditor/main.cpp
find ./examples -name *.cpp | xargs sed -i -e 's|../../media/|%{_datadir}/irrlicht/|g'

# (tpg) clean this mess
for i in include/*.h doc/upgrade-guide.txt source/Irrlicht/*.cpp source/Irrlicht/*.h source/Irrlicht/Makefile; do
    sed -i 's/\r//' $i
    chmod -x $i
    touch -r changes.txt $i
done

#(tpg) correct version
sed -i -e 's/0-SVN/1/g' source/Irrlicht/Makefile

# build static library
%make -C source/Irrlicht \
    CFLAGS="%{optflags}" \
    CXXFLAGS="%{optflags}" \
    LDFLAGS="%{ldflags} -L$(pwd)/lib/Linux"

# clean it
%make -C source/Irrlicht clean

# build shared library
%make -C source/Irrlicht sharedlib NDEBUG=1 \
    %ifnarch ix86
    CFLAGS="%{optflags} -fPIC" \
    CXXFLAGS="%{optflags} -fPIC" \
    LDFLAGS="%{ldflags}"
    %else
    CFLAGS="%{optflags}" \
    CXXFLAGS="%{optflags}" \
    LDFLAGS="%{ldflags}"
    %endif

# create necessary links to avoid linker-error for tools/examples
pushd lib/Linux
ln -s libIrrlicht.so.%{version} libIrrlicht.so
ln -s libIrrlicht.so.%{version} libIrrlicht.so.%{major}
popd

# build tools
pushd tools
cd GUIEditor
%make CFLAGS="%{optflags}" CXXFLAGS="%{optflags} -ffast-math" LDFLAGS="%{ldflags}"
cd ../IrrFontTool/newFontTool
%make CFLAGS="%{optflags}" CXXFLAGS="%{optflags}" LDFLAGS="%{ldflags}"
popd

# build examples
pushd examples
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{ldflags}"
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
install -m 755 bin/Linux/GUIEditor %{buildroot}%{_bindir}/irrlicht-GUIEditor
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
convert bin/Win32-VisualStudio/irrlicht.ico -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/irrlicht.png

convert examples/09.Meshviewer/icon.ico -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/irrlicht-Meshviewer.png
convert bin/Win32-VisualStudio/irrlicht.ico -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/irrlicht.png

convert examples/09.Meshviewer/icon.ico -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/irrlicht-Meshviewer.png
convert bin/Win32-VisualStudio/irrlicht.ico -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/irrlicht.png

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
Categories=3DGraphics;
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
Categories=3DGraphics;
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
Categories=3DGraphics;
EOF

%files
%doc examples/09.Meshviewer/tutorial.html
%{_bindir}/irrlicht-GUIEditor
%{_bindir}/irrlicht-FontTool
%{_bindir}/irrlicht-Meshviewer
%{_datadir}/applications/*.desktop
%{_iconsdir}/hicolor/*/apps/*.png

%files -n %{libname}
%{_libdir}/lib*.so.%{major}*

%files -n %{develname}
%dir %{_includedir}/irrlicht
%{_libdir}/lib*.so
%{_includedir}/irrlicht/*.h

%files -n %{staticname}
%{_libdir}/lib*.a

%files examples
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
%doc doc/*
