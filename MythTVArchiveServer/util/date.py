"""
   :synopsis: Date
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

from datetime import datetime


class InValidDate(Exception):
    pass


def string_to_datetime(date_string):
    try:
        return datetime.strptime(date_string.replace('T', ' '), '%Y-%m-%d %H:%M:%S%Z')
    except ValueError:
        raise InValidDate()

def date_to_string(_date):
    try:
        return _date.strftime("%Y-%m-%d")
    except ValueError:
        raise InValidDate()

def mythdate_to_str(_date):
    return str(_date.utcisoformat()).replace('T', ' ')