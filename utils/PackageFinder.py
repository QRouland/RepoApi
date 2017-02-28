import os
import re


class PackageFinder:
    def __init__(self, regex_package_name):
        self.pattern_package_name = re.compile(regex_package_name)

    def find_packages(self, directory_path):
        return [f for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f)) and self.is_valid_filename(f)]

    def get_package_name(self, filename):
        return self.pattern_package_name.match(filename).group("package_name")

    def get_version_major(self, filename):
        return self.__match_int("version_major", filename)

    def get_version_minor(self, filename):
        return self.__match_int("version_minor", filename)

    def get_version_release(self, filename):
        return self.__match_int("version_release", filename)

    def is_valid_filename(self, filename):
        return self.pattern_package_name.match(filename)

    def __match_int(self, group, filename):
        match = self.pattern_package_name.match(filename).group(group)
        if match is None:
            return 0
        return int(match)


class InvalidPackageName(Exception):
    pass
