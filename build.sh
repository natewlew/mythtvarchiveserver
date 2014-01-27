#!/bin/bash


function build_deb {

    #python setup.py --command-packages=stdeb.command sdist_dsc
    #cp deb_dist/*.orig.tar.gz ../
    #rm -rf deb_dist/
    dpkg-buildpackage

}

function clean {

    #rm -rf deb_dist/
    rm -rf build/
    rm -rf ./*.egg-info/
    find . -name '*.pyc' -delete
    rm -rf ../mythtvarchiveserver_*
    rm -rf ../mythtvarchiveservermedia_*

    rm -rf debian/mythtvarchiveserver/
    rm -rf debian/mythtvarchiveservermedia/
    rm -rf debian/tmp/
    rm -rf debian/*debhelper*
    rm -rf debian/*substvars

}

case "$1" in
    deb)
        build_deb
        ;;
    clean)
        clean
        ;;
    *)
        echo "deb or clean"
        ;;
esac

