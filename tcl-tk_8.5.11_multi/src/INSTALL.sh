#!/bin/bash
cd ${0%/*}
ICI=`pwd -P`
echo Current dir=$ICI
cd ..
InstallPrefix=`pwd -P`
echo Install dir=$InstallPrefix
set -e
cd ${InstallPrefix}
cd $ICI
if [[ ! -d tcl8.5.11 ]] ; then
  tar zxf tcl8.5.11.tar.gz
  cd tcl8.5.11/unix
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix}
  make 
  make install
fi
cd ${InstallPrefix}/bin
rm -f wish tclsh 
ln -sf wish8.5 wish
ln -sf tclsh8.5 tclsh
ln -sf wish8.5 maestro_wish8.5
ln -sf tclsh8.5 maestro_tclsh8.5
cd $ICI
export PATH=${InstallPrefix}/bin:$PATH
if [[ ! -d thread2.6.7 ]] ; then
  tar zxf thread2.6.7.tar.gz
  cd thread2.6.7
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include
  make 
  make install
fi
cd $ICI
if [[ ! -d tk8.5.11 ]] ; then
  tar zxf tk8.5.11.tar.gz
  cd tk8.5.11/unix
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include
  make 
  make install
fi
cd $ICI
if [[ ! -d tDOM-0.8.3 ]] ; then
  tar zxf tDOM-0.8.3.tar.gz
  cd tDOM-0.8.3
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include
  make 
  make install
fi
cd $ICI
if [[ ! -d  tcllib-1.13 ]] ; then
  tar zxf tcllib-1.13.tar.gz
  cd tcllib-1.13
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include
  make 
  make install
fi
cd $ICI
if [[ ! -d tklib-0.5 ]] ; then
  tar zxf tklib-0.5.tar.gz
  cd tklib-0.5
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include
  make 
  make install
fi
cd $ICI
if [[ ! -d bwidget-1.9.5 ]] ; then
  tar zxf bwidget-1.9.5.tar.gz
  cp -r bwidget-1.9.5 ${InstallPrefix}/lib
fi
cd $ICI
if [[ ! -d keynav1.0 ]] ; then
  tar zxf keynav1.0.tar.gz
  cp -r keynav1.0 ${InstallPrefix}/lib
fi
cd $ICI
if [[ ! -d tablelist5.5 ]] ; then
  tar zxf tablelist5.5.tar.gz
  cp -r tablelist5.5 ${InstallPrefix}/lib
fi
cd $ICI
if [[ ! -d Tktable2.10 ]] ; then
  tar zxf Tktable2.10.tar.gz
  cd Tktable2.10
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include \
              --with-tk=${InstallPrefix}/lib
  make 
  make install
fi
cd $ICI
if [[ ! -d tkimg1.4 ]] ; then
  tar zxf tkimg1.4.tar.gz
  cd tkimg1.4
  ./configure --enable-threads --enable-shared --prefix=${InstallPrefix} -with-tcl=${InstallPrefix}/lib --with-tclinclude=${InstallPrefix}/include \
              --with-tk=${InstallPrefix}/lib
  make 
  make install
fi

cd $ICI
echo === installation successful, cleaning up ===
find . -mindepth 1 -maxdepth 1  -type d -exec rm -rf {} \;


