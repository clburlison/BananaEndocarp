# otool -L /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/lib-dynload/_tkinter.so
#################################################
PKGTITLE="Tkinker_NetInstall_Frameworks"
PKGVERSION=1.0
PKGID=com.clburlison.Tkinker_Frameworks

pkg:

##Help - Show this help menu
help: 
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##  copy - copy frameworks
copy:
	mkdir -p payload/System/Library/Frameworks
	cp -rf /System/Library/Frameworks/Tcl.framework payload/System/Library/Frameworks
	cp -rf /System/Library/Frameworks/Tk.framework payload/System/Library/Frameworks

##  pkg - Create a package using pkgbuild
pkg: copy
	pkgbuild --root payload --identifier ${PKGID} --version ${PKGVERSION} --ownership recommended ./${PKGTITLE}-${PKGVERSION}.pkg