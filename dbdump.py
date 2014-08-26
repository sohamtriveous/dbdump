__author__ = 'sohammondal'

import sys
import commands
import re

# helper functions
def exec_cmd(cmd):
    '''
    execute the given command
    :param cmd: the command to be execute
    :return:
    '''
    (status, output) = commands.getstatusoutput(cmd)
    if status:
        print 'Could not execute', cmd, sys.stderr
        return False
    return True


def find_all(pat, string):
    '''
    Finds a regular expression match within a string
    :param pat: the regex pattern to be matched
    :param string: the string where to search
    :return: the first group match within ()
    '''
    matches = re.findall(pat, string)
    if matches:
        return matches
    else:
        return None


def find(pat, string):
    '''
    Finds a regular expression match within a string
    :param pat: the regex pattern to be matched
    :param string: the string where to search
    :return: the first group match within ()
    '''
    match = re.search(pat, string)
    if match:
        return match.group(1)
    else:
        return None


def find_basic(pat, string):
    '''
    Finds a regular expression match within a string
    :param pat: the regex pattern to be matched
    :param string: the string where to search
    :return: the first group match within ()
    '''
    match = re.search(pat, string)
    if match:
        return match
    else:
        return None


def add_adb_device(devicename=None):
    '''
    Adds a -s device param to the delete commandline in case the devicename is none
    :param devicename: the name/id of the device
    :return:
    '''
    cmd = 'adb '
    if devicename:
        cmd = cmd + '-s ' + devicename + ' '
    return cmd

def del_folder(devicename, path):
    '''
    delete files at a particular path
    :param devicename: device
    :param path: path to be deleted
    :return:
    '''
    # add device whenever necessary
    cmd = add_adb_device(devicename)
    # command for deleting the file
    cmd = cmd + 'shell rm -r '
    new_cmd = cmd + path
    (status, output) = commands.getstatusoutput(new_cmd)
    if status:
        print 'Could not delete', path, sys.stderr
        return False
    else:
        return True


def pull_files(to_path='', from_path='', devicename=None):
    '''
    copies the given files to a given path
    :param to_path: the destination path
    :param from_path: the source path
    :param devicename: the device
    :return:
    '''
    # add device whenever necessary
    cmd = add_adb_device(devicename)
    # command for pulling a file
    cmd = cmd + 'pull '
    new_cmd = cmd + from_path + ' ' + to_path
    (status, output) = commands.getstatusoutput(new_cmd)
    if status:
        print 'Could not copy', from_path, sys.stderr
        return False
    return True


# App specific parse functions
def parse_app_package_name(argv=[]):
    '''
    Parses the app package name
    :param argv:
    :return:
    '''
    return argv[0]


def parse_destination_dir(argv=[]):
    '''
    Parses the destination folder
    :param argv:
    :return:
    '''
    if argv[0] == '--file' or argv[0] == '--device':
        return '.'
    else:
        return argv[0]


def parse_db_files(argv=[]):
    '''
    Parses the db files
    :param argv:
    :return:
    '''
    db_files = []
    for idx, arg in enumerate(argv):
        if arg == '--db':
            try:
                db_files.append(argv[idx + 1])
            except Exception:
                pass
    if db_files:
        return db_files


def parse_device(argv=[]):
    '''
    Parses the device name
    :param argv:
    :return:
    '''
    for idx, arg in enumerate(argv):
        if arg == '--device':
            try:
                return argv[idx + 1]
            except Exception:
                pass


# actual script specific methods
def db_files_list(path, db_files=None, devicename=None):
    '''
    Lists the db files
    :param path: path to carry out the list
    :param db_files: the db file params, if passed
    :param devicename: device name
    :return:
    '''
    cmd = add_adb_device(devicename)
    cmd = cmd + 'shell ls ' + path
    (status, output) = commands.getstatusoutput(cmd)
    output = str.splitlines(output)
    filenames = []
    if status:
        print 'Could not execute', cmd, sys.stderr
        return False
    else:
        for line in output:
            if db_files:
                for db_file in db_files:
                    filename = find_basic(db_file + '$', line)
                    if filename:
                        filenames.append(db_file)
                        break
                continue
            else:
                filename = find(r'(\w*.db$)', line)
                if filename:
                    filenames.append(filename)
        return filenames

def db_pull(temp_path, to_path, filenames=[], devicename=None):
    '''
    Pulls individual files from the device to the computer directory
    :param temp_path: temp directory where the files are stored
    :param to_path: destination directory on the laptop
    :param filenames: list of file names
    :param devicename: device name
    :return:
    '''
    for filename in filenames:
        print 'Pulling', filename, '-->', to_path
        pull_files(to_path, temp_path + '/' + filename, devicename)


def begin_dump(app_package_name, destination_dir, devicename=None, db_files=[]):
    '''
    Begins the db dump procedure
    :param app_package_name: app package name
    :param destination_dir: destination directory
    :param devicename: device name
    :param db_files: the list of specific db_files to be copied
    :return:
    '''
    database_base_path = '/data/data/'
    database_path = database_base_path + app_package_name + '/databases'

    filenames = db_files_list(database_path, db_files, devicename)
    db_pull(database_path, destination_dir, filenames, devicename)
    print 'Done!'
    return


def parse_agrs_and_start(argv=[]):
    '''
    Parses the arguments and sends them for further processing
    :param argv:
    :return:
    '''
    length = len(argv)
    if length < 2:
        print 'usage: python dbdump.py app_packagename [destination_dir] [--device devicename] [--db my_dbfile.db]'
        return

    app_package_name = parse_app_package_name(argv[1:])
    destination_dir = '.'
    devicename = None
    db_files = []
    if length > 2:
        destination_dir = parse_destination_dir(argv[2:])
        devicename = parse_device(argv[2:])
        db_files = parse_db_files(argv[2:])

    begin_dump(app_package_name, destination_dir, devicename, db_files)

    return


parse_agrs_and_start(sys.argv)
