#!/bin/bash
TCL_ROOT=`pwd -P`

set -e

cd $TCL_ROOT

export PATH=${TCL_ROOT}/bin:$PATH


cd ${TCL_ROOT}/bin
rm -f wish tclsh 
ln -sf wish8.5 wish
ln -sf tclsh8.5 tclsh
ln -sf wish8.5 maestro_wish8.5
ln -sf tclsh8.5 maestro_tclsh8.5



function configure_and_make() {
    cd $1
    ./configure --enable-threads --enable-shared --prefix=${TCL_ROOT} $2
    make 
    make install
    cd ..
}

MAKE_ARGS1="-with-tcl=${TCL_ROOT}/lib --with-tclinclude=${TCL_ROOT}/include"
MAKE_ARGS2=$MAKE_ARGS1" --with-tk=${TCL_ROOT}/lib"

configure_and_make tcl8.5.11/unix
configure_and_make thread2.6.7 "$MAKE_ARGS1"
configure_and_make tk8.5.11/unix "$MAKE_ARGS1"
configure_and_make tDOM-0.8.3 "$MAKE_ARGS1"
configure_and_make tcllib-1.13 "$MAKE_ARGS1"
configure_and_make tklib-0.5 "$MAKE_ARGS1"
configure_and_make Tktable2.10 "$MAKE_ARGS2"
configure_and_make tkimg1.4 "$MAKE_ARGS2"
