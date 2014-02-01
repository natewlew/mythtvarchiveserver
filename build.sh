#!/bin/bash


function build_deb {
    dpkg-buildpackage

}

function clean {

    rm -rf deb_dist/
	rm -rf build/
	rm -rf ./*.egg-info/
	find . -name '*.pyc' -delete
	rm -rf ../mythtvarchiveserver_*
	rm -rf ../mythtvarchiveservermedia_*
	dh_clean

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

