# MythTVArchiveServer Install

Requirements: MythTV, Twisted, SqlAlchemy, MySQLdb, python-dateutil

- Run `build.sh deb` to build the debian package
- Install the packages
- Edit the config file: `/etc/mythtvarchiveserver/config.cfg`
- Restart the services: `sudo service mythtvarchiveserver restart` and `sudo service mythtvarchiveservermedia restart`
- Go to `http://archiveserver:7081` to see the web interface. The xmlrpc server should be running on port `7080`

- Create the MythTV [Userjob](http://www.mythtv.org/wiki/User_Jobs) (Optional)

    The user job will point to the [mythtvarchive.py](MythTVArchiveServer/client/mythtvarchive.py) file. Install this file to your MythTV Backend Server at `/opt/mythtv`. Make the file permissions executable. Then create the user job with this as the parameter: `/opt/mythtv/mythtvarchive.py %CHANID% %STARTTIMEISOUTC%`.
