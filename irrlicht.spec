%define major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s

Summary:		The Irrlicht Engine SDK
Name:			irrlicht
Version:		1.3.1
Release:		%mkrel 1
License:		Zlib/libpng
Group:			Graphics
URL:			http://irrlicht.sourceforge.net/
Source:			http://prdownloads.sourceforge.net/irrlicht/%{name}-%{version}.tar.bz2
Patch0:			%{name}-1.3.1-dimension.patch
Patch1:			%{name}-1.3.1-library-makefile.patch
Patch2:			%{name}-1.3.1-use-system-libs.patch
BuildRequires:		imagemagick
BuildRequires:		zlib-devel
BuildRequires:		libjpeg-devel
BuildRequires:		libpng-devel
BuildRequires:		mesa-common-devel
#Requires:		%{libname} = %{version}-%{release}
BuildRoot:		%{_tmppath}/%{name}-%{version}-buildroot

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

%description -n %{develname}
Development files for Irrlicht 3D engine.

%package -n %{staticname}
Summary:	Static files for Irrlicht 3D engine
Group:		Development/C
Requires:	%{develname}  = %{version}-%{release}

%description -n %{staticname}
Static files for Irrlicht 3D engine.

#%package -n %{name}-examples
#Summary:	Demos and examples for the Irrlicht 3D engine
#Group:		Other
#Requires:	%{libname} = %{version}-%{release}

#%description -n %{name}-examples
#Demos and examples for the Irrlicht 3D engine.

#%package -n %{name}-media
#Summary:	Some media files for Irrlicht 3D engine
#Group:		Development/C

#%description -n %{name}-media
#Some media files for Irrlicht tools and demos.

#%package -n %{name}-doc
#Summary:	User documentation for the Irrlicht 3D engine
#Group:		Documentation/Other

#%description -n %{name}-doc
#User documentation for the Irrlicht 3D engine.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
export CFLAGS="%{optflags} -fPIC"
export CXXFLAGS="%{optflags} -fPIC"
export LIBDIR="%{_libdir}"

# really not needed :)
rm -r examples/14.Win32Window

# needs irrKlang
rm -r examples/Demo
sed -i -e 's|Demo||g' examples/buildAllExamples.sh

# media path
sed -i -e 's|../../media/|%{_datadir}/irrlicht/|g' tools/GUIEditor/main.cpp
find ./examples -name *.cpp | xargs sed -i -e 's|../../media/|%{_datadir}/irrlicht/|g'

# create shared-lib first
pushd source/Irrlicht
%make sharedlib
popd

# create necessary links to avoid linker-error for tools/examples
#pushd lib/Linux
#ln -s libIrrlicht.so.1.3.0 libIrrlicht.so.1
#ln -s libIrrlicht.so.1.3.0 libIrrlicht.so
#popd

# tools
#pushd tools
#cd GUIEditor
#%make
#cd ..
#cd IrrFontTool/newFontTool
#%make
#cd ../..
#popd

# examples
#pushd examples
#sh buildAllExamples.sh
#popd

# build static lib
pushd source/Irrlicht
make clean
%make
popd

%install
mkdir -p %{buildroot}%{_libdir}

install -m 644 lib/Linux/libIrrlicht.a %{buildroot}%{_libdir}
install -m 755  lib/Linux/libIrrlicht.so.%{major}* %{buildroot}%{_libdir}

%ifarch x86_64
pushd %{buildroot}%{_libdir}
ln -s libIrrlicht.so.1.3.0 libIrrlicht.so
popd
%endif

# includes
mkdir -p %{buildroot}%{_includedir}/irrlicht
cp -f include/*.h %{buildroot}%{_includedir}/irrlicht

# tools
#install -dm 755 %{buildroot}%{_bindir}
#install -m 755 tools/GUIEditor/GUIEditor %{buildroot}%{_bindir}/irrlicht-GUIEditor
#install -m 755 bin/Linux/FontTool %{buildroot}%{_bindir}/irrlicht-FontTool

# examples
#install -dm 755 %{buildroot}%{_bindir}
#ex_list=`ls -1 bin/Linux/??.*`
#for i in $ex_list; do
#	FE=`echo $i | awk 'BEGIN { FS="." }{ print $2 }'`
#	    install -m 755 $i %{buildroot}%{_bindir}/irrlicht-$FE
#done

# examples-docs
#pushd examples
#install -dm 755 %{buildroot}%{_docdir}/Irrlicht-examples
#install -m 644 * %{buildroot}%{_docdir}/Irrlicht-examples

# ex_dir=`find . -name tutorial.html`
#for i in $ex_dir; do
#	dir_name=`dirname $i`
#	install -dm 755 %{buildroot}%{_docdir}/Irrlicht-examples/$dir_name
#	install -m 644 $i %{buildroot}%{_docdir}/Irrlicht-examples/$dir_name
#done
#rm -r %{buildroot}%{_docdir}/Irrlicht-examples/09.Meshviewer
#popd

# examples sources
#install -m 644 irrlicht-examples-src.tar.bz2 %{buildroot}%{_docdir}/Irrlicht-examples

# media
#mkdir -p %{buildroot}%{_datadir}/irrlicht
#install -m 755 media/* %{buildroot}%{_datadir}/irrlicht

# icons
#install -dm 755 %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
#convert examples/09.Meshviewer/icon.ico -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/irrlicht-Meshviewer.png
#convert bin/Win32-gcc/irrlicht.ico -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/irrlicht.png

#convert examples/09.Meshviewer/icon.ico -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/irrlicht-Meshviewer.png
#convert bin/Win32-gcc/irrlicht.ico -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/irrlicht.png

#convert examples/09.Meshviewer/icon.ico -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/irrlicht-Meshviewer.png
#convert bin/Win32-gcc/irrlicht.ico -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/irrlicht.png

# menu
#mkdir -p %{buildroot}%{_datadir}/applications
#cat > %{buildroot}%{_datadir}/applications/irrlicht-GUIEditor.desktop << EOF
#[Desktop Entry]
#Encoding=UTF-8
#Name=Irrlicht GUI Editor
#Comment=Irrlicht GUI Editor
#Exec=%{_bindir}/irrlicht-GUIEditor
#Icon=%{name}.png
#Terminal=false
#Type=Application
#StartupNotify=true
#Categories=Graphics;3DGraphics;GTK;
#EOF

#cat > %{buildroot}%{_datadir}/applications/irrlicht-FontTool.desktop << EOF
#[Desktop Entry]
#Encoding=UTF-8
#Name=Irrlicht Font Tool
#Comment=Irrlicht Font Tool
#Exec=%{_bindir}/irrlicht-FontTool
#Icon=%{name}.png
#Terminal=false
#Type=Application
#StartupNotify=true
#Categories=Graphics;3dGraphics;GTK;
#EOF

#cat > %{buildroot}%{_datadir}/applications/irrlicht-Meshviewer.desktop << EOF
#[Desktop Entry]
#Encoding=UTF-8
#Name=Irrlicht Mesh Viewer
#Comment=Irrlicht Mesh Viewer
#Exec=%{_bindir}/irrlicht-Meshviewer
#Icon=irrlicht-Meshviewer.png
#Terminal=true
#Type=Application
#StartupNotify=true
#Categories=Graphics;3Dgraphics;GTK;
#EOF

#post
#{update_menus}
#update_icon_cache hicolor

#postun
#{clean_menus}
#clean_icon_cache hicolor

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

#files
#%defattr(-,root,root)
#%doc examples/09.Meshviewer/tutorial.html
#%{_bindir}/irrlicht-GUIEditor
#%{_bindir}/irrlicht-FontTool
#%{_bindir}/irrlicht-Meshviewer
#%{_datadir}/applications/irrlicht-GUIEditor.desktop
#%{_datadir}/applications/irrlicht-FontTool.desktop
#%{_datadir}/applications/irrlicht-Meshviewer.desktop
#%{_iconsdir}/hicolor/*/apps/*.png

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

#files -n %{name}-examples
#%defattr(-,root,root)
#%dir %{_docdir}/Irrlicht-examples
#%{_docdir}/Irrlicht-examples/*
#%exclude %{_bindir}/irrlicht-GUIEditor
#%exclude %{_bindir}/irrlicht-FontTool
#%exclude %{_bindir}/irrlicht-Meshviewer
#%{_bindir}/irrlicht-*

#files -n %{name}-media
#%defattr(-,root,root)
#%dir %{_datadir}/irrlicht
#%{_datadir}/irrlicht/*

#files -n %{name}-doc
#%defattr(-,root,root)
#%doc doc/irrlicht.chm
#%doc doc/*.txt
