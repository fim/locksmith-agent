import os
import re
import StringIO

class ConfigParser(object):

    def __init__(self, filename, separator="=", multiple_values=True, empty_values=True):
        self.conf = {}
        self.filename = filename
        self.separator = separator
        self.multiple_values = multiple_values
        self.empty_values = empty_values

        if os.path.isfile(filename):
            self.parse()
        else:
            self._load_defaults()
            self.export_file(self.filename)

    def __getitem__(self, key):
        """
        Return val for key
        """
        val = self.conf[self._normalize_key(key)]
        return self._denormalize_val(val)

    def __setitem__(self, key, val):
        """
        Set val for key
        """
        self.conf[self._normalize_key(key)] = self._normalize_val(val)

    def __delitem__(self, key):
        """
        Delete key from conf
        """
        del self.conf[self._normalize_key(key)]

    def __str__(self):
        buf = StringIO.StringIO()

        for k in self.conf.keys():
            buf.write('{0}="{1}"\n'.format(k, self[k]))

        return buf.getvalue()

    def keys(self):
        return self.conf.keys()

    def _compile(self):
        """
        Create make.conf
        """
        return self.__str__()

    def _load_defaults(self, conf={}):
        for k,v in conf.iteritems():
            self[k] = v

    def _normalize_key(self, key):
        return key

    def _denormalize_key(self, key):
        return key

    def _normalize_val(self, val):
        if self.multiple_values:
            if ' ' in val:
                return val.split(' ')

        return val

    def _denormalize_val(self, val):
        if self.multiple_values:
            if not isinstance(val, basestring):
                return ' '.join(val)

        return val

    def get(self, *args):
        """
        Get dict of values
        """
        conf = {}
        if not args:
            conf = self.conf
        else:
            for key in args:
                conf[self._normalize_key(key)] = self[key]

        return conf

    def set(self, **kwargs):
        """
        Set conf directives from input dict
        """
        for k,v in kwargsiteritems():
            self[k] = v

    def parse(self):
        with open(self.filename, 'r') as f:
            self._parse(f.readlines())

    def _parse(self, lines):
        values = {}
        cur_array = []

        trailing_comment=re.compile('\s*#.*$')
        white_space=re.compile('\s+')

        for x, myline in enumerate(lines):
            myline = myline.strip()

            # Force the line to be clean
            # Remove Comments ( anything following # )
            myline = trailing_comment.sub("", myline)

            # Skip any blank lines
            if not myline: continue

            # Look for separator
            msearch = myline.find(self.separator)

            # If separator found assume its a new key
            if msearch != -1:
                # Split on the first occurence of the separator creating two strings in the array mobjs
                mobjs = myline.split(self.separator, 1)
                mobjs[1] = mobjs[1].strip().strip('"')

                # Start a new array using the first element of mobjs
                cur_array = [mobjs[0]]
                if mobjs[1]:
                    if self.multiple_values:
                        subarray = mobjs[1].split()
                        cur_array += subarray
                    else:
                        cur_array += [mobjs[1]]

            # Else add on to the last key we were working on
            else:
                if self.multiple_values:
                    cur_array += myline.split()
                else:
                    raise Exception, "Syntax error: " + x

            if len(cur_array) == 2:
                values[cur_array[0]] = cur_array[1]
            else:
                values[cur_array[0]] = cur_array[1:]

        if not self.empty_values:
            for x in values.keys():
                # Delete empty key pairs
                if not values[x]:
                    print "\n\tWARNING: No value set for key " + x + "...deleting"
                    del values[x]

        self.conf = values

    def save(self):
        self.export_file(self.filename)

    def import_file(self, filename):
        """
        Import conf file
        """
        with open(filename, 'r') as f:
            self._parse(f.readlines())

    def export_file(self, filename):
        """
        Export conf to file
        """
        with open(filename, 'w') as f:
            f.write(self._compile())

LOCKSMITH_DEFAULTS = {
    'register_url': 'register/',
    'base_url': 'json/',
}

class LocksmithConf(ConfigParser):

    def _load_defaults(self):
        for k,v in DABUS_DEFAULTS.iteritems():
            self[k] = v
