"""
   :synopsis: File
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from os import path, remove


def remove_file(file_):
    if path.exists(file_):
        remove(file_)
