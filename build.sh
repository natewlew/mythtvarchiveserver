#!/bin/bash


function build_deb {

    python setup.py --command-packages=stdeb.command sdist_dsc
    cp deb_dist/*.orig.tar.gz ../
    rm -rf deb_dist/
    dpkg-buildpackage

}

function clean {

    rm -rf build/
    rm -rf deb_dist/
    rm -rf ./*.egg-info/
    find . -name '*.pyc' -delete
    rm -rf ../mythtvarchiveserver_*

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

