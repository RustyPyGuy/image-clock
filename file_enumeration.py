#!/usr/bin/env python3

# The Image Clock, a python clock that displays artwork to tell the time, and its
# component and supporting files (analog clock, file parser, and others)
# Copyright (C) 2021 github user: RustyPyGuy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# To contact the author: send a message to RustyPyGuy on Github.


"""
This enumerates the files and prepares data structures for clock_main.py

"""
import os
import stat

class FileRecord:
    """
    The file_catalog class creates a data storage and enumeration construct for
    parsing the input files. This class is called by FileCatalog2.
    """
    def __init__(self, clock4 :int, image_filepath :str, description :str):
        self.clock4 = int(clock4) #time in four digits e.g. 1615 is 4:15 PM
        self.image_filepath = str(image_filepath)
        self.height = int()
        self.width = int()
        self.description = str(description)
    def __iter__(self): #makes this class object iterable
        pass

class FileCatalog2:
    """
    The file_catalog class creates a data storage and enumeration construct for
    parsing the input files. It contains the filename text parsing logic
    """
    def __init__(self,image_filepath :str):
        self.image_file_list: list[FileRecord] = list()
        self.error_file_list: list[FileRecord] = list()
        self.image_filepath = image_filepath

    def tag_file(self, file :str):
        f = os.path.split(file)[1]
        temp_file_record=list()
        temp_file_record.append(FileRecord(-1, "", ""))
        clock4 = int() #time in four digits e.g. 1615 is 4:15 PM
        if f[0] in ["a","A"] and int(f[1:3]) == 12 \
        and int(f[3:5]) <= 59:
            temp_file_record[0].clock4 = 0000 + int(f[3:5])
        elif f[0] in ["p","P"] and int(f[1:3]) == 12 \
        and int(f[3:5]) <= 59:
            temp_file_record[0].clock4 = 1200  + int(f[3:5])
            # AM Time entries
        elif f[0] in ["a","A"] and int(f[1:3]) < 12 and int(f[1:3]) >= 0 \
        and int(f[3:5]) <= 59:
            temp_file_record[0].clock4 = int(f[1:5])
            # PM time entries
        elif f[0] in ["p","P"] and int(f[1:3]) <= 24 and int(f[1:3]) > 0 \
        and int(f[3:5]) <= 59:
            if int(f[1:3]) < 12 and int(f[1:3]) > 0:
                temp_file_record[0].clock4 = 1200 + int(f[1:5])
            elif int(f[1:3]) > 12 and int(f[1:3]) <= 24:
                temp_file_record[0].clock4 = int(f[1:5])
        # Either Time entries.  PROBLEM - the case can't double itself?
        elif f[0] in ["e","E"] and int(f[1:3]) == 12 \
        and int(f[3:5]) <= 59: # this should return 00 and 12 as the hour
            temp_file_record[0].clock4 = int(f[1:5])
            temp_file_record.append(FileRecord(-1, "", ""))
            temp_file_record[1].clock4 = 0000+ int(f[3:5])
            temp_file_record[1].description = str(f[5:])
            temp_file_record[1].image_filepath = str(file)
        elif f[0] in ["e","E"] and int(f[1:3]) > 0 and int(f[1:3]) <= 12 \
        and int(f[3:5]) <= 59:
            temp_file_record[0].clock4 = int(f[1:5])
            temp_file_record.append(FileRecord(-1, "", ""))
            temp_file_record[1].clock4 = int(f[1:5])+1200
            temp_file_record[1].description = str(f[5:])
            temp_file_record[1].image_filepath = str(file)
        else:
            temp_file_record[0].clock4 = -1
        temp_file_record[0].description = str(f[5:])
        temp_file_record[0].image_filepath = str(file)
        return temp_file_record


    def walktree(self, top: str, callback):
        """
        recursively descend the directory tree rooted at top, calling the
        callback function for each regular file. Taken from the module-stat
        example at: http://docs.python.org/lib/module-stat.html
        """
        for f in os.listdir(top):
            pathname = os.path.join(top, f)
            mode = os.stat(pathname)[stat.ST_MODE]
            if stat.S_ISDIR(mode):
                # It's a directory, recurse into it
                self.walktree(pathname, callback)
            elif stat.S_ISREG(mode):
                # It's a file, call the callback function
                callback(pathname)
            else:
                # Unknown file type, print a message
                print ('Skipping %s' % pathname)


    def addtolist(self, file, extensions=['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
        """
        evaulates the file type and naming format and, if compliant,
        creates a new class instance in a list.

        """
        filename, ext = os.path.splitext(file)
        e = ext.lower()
            # Only add common image types to the list.
        if e in extensions:
            new_record = self.tag_file(file)
            if new_record[0].clock4 >= 0:
                self.image_file_list = self.image_file_list + new_record
            else:
                self.error_file_list = self.error_file_list + new_record

    def catalog_files(self):
        """ This method is called externally.
        """
        self.walktree(self.image_filepath,self.addtolist)
        self.image_file_list = sorted(self.image_file_list, key=lambda image_file_list: image_file_list.clock4) # Thank you stackoverflow

    def clear_catalog_files(self):
        """ This method is called externally.
        """
        self.image_file_list.clear()
        self.error_file_list.clear()

    def return_missing(self, hour=-1):
        """ This method is called externally.
            Returns all the missing clocks as a string.  If the hour is defined
            as 24, then then only from that particular hour.
        """
        def time4_to_str(input: int):
            """ outputs a properly formatted string for a time input as an integer """
            if input//100 < 10:
                timestring = '0' + str(input//100)
            else:
                timestring = str(input//100)
            if input%100 < 10:
                timestring = timestring + ':' + '0' + str(input%100)
            else:
                timestring = timestring + ':' + str(input%100)
            return timestring

        def minute_search(hour: int):
            """ returns a list of minutes that are not cataloged in image file list """
            # Churn through all the minutes and all the files to find matches. Not efficient, but so what.
            # NOTE: Consider optimizing loop entries and exits to reduce loops - more important with more compound loops.
            missing_minutes_list = []
            hour=hour*100
            for minute in range(0, 60):
                for obj in self.image_file_list:
                    search_minute = hour + minute
                    if obj.clock4 == search_minute:
                        break # if a matching minute is found, then immediately break out of the first level loop.
                    elif self.image_file_list.index(obj) != len(self.image_file_list) -1:
                        continue
                    else:
                        missing_minutes_list.append(search_minute)
                        # if a matching minute was not found, add it to the missing list.
            return missing_minutes_list

        """ end of function definitions for this method """
        # run the search on a particular hour or loop over all hours
        if hour == 24:
            # loop through all hours and add to list
            missing_minutes =[]
            for hr in range(0,24):
                missing_minutes.extend(minute_search(hr))
        elif hour  >= 0 and  hour <= 23:
            # search for one hour
            missing_minutes = minute_search(hour)
        else:
            # If an hour outside of the range of hours is specfied, then error.
            return -1

        # string operations
        if hour == 24:
            missing_minutes_string = '\nTotal clocks missing for all times: ' + str(len(missing_minutes)) + '\n\nRanges of missing clocks\n'

        else:
            missing_minutes_string = '\nTotal clocks missing this hour: ' + str(len(missing_minutes)) + '\n\nRanges of missing clocks\n'
        run_start = 0
        for ind in range(0, len(missing_minutes)):
            # if the next indexed item is just one more integer than the
            # current item, then there is a run, otherwise set the end of the
            # run to the current index.
            if ind != len(missing_minutes)-1:
                if missing_minutes[ind]+1 == missing_minutes[ind+1]:
                    run_end = ind+1
                elif (missing_minutes[ind]-59)%100 == 0 and missing_minutes[ind+1]%100 == 0 \
                    and (missing_minutes[ind]-59)//100+1 == missing_minutes[ind+1]//100:
                    #check the bridge of the hour
                    run_end = ind+1
                else:
                    run_end = ind
            # if there is no run of a sequence, add that single time otherwise
            if run_end==run_start:
                timestring1 = time4_to_str(missing_minutes[ind])
                missing_minutes_string = missing_minutes_string + timestring1 + '\n'
                run_start = ind + 1
            elif run_end == ind:
                timestring1 = time4_to_str(missing_minutes[run_start])
                timestring2 = time4_to_str(missing_minutes[run_end])
                missing_minutes_string = missing_minutes_string + timestring1 + ' - ' + timestring2 + '\n'
                run_start = ind + 1
            else:
                pass
        missing_minutes_string += "\nFivers (good for analog clocks) \n"
        for ind in range(0, len(missing_minutes)):
            if missing_minutes[ind]%5 == 0:
                missing_minutes_string =  missing_minutes_string + time4_to_str(missing_minutes[ind]) +'\n'
        return missing_minutes_string


""" end of class definitions
Below is executed only when run directly from the command line. """

if __name__ == "__main__":
#    print("This file not intended to be run as a standalone script. Exiting.")
    print("Running test.")
    test = FileCatalog2("/var/lib/image-clock/images/")
    test.catalog_files()
    for x in range(0,len(test.image_file_list)):
        print(test.image_file_list[x].clock4, test.image_file_list[x].image_filepath, test.image_file_list[x].description )
    print("Entering debugging. If not needed, press c to continue.")
    breakpoint()
    print("End of test. Exiting.")
