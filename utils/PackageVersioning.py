from datetime import datetime
from watchdog.observers import Observer

import hashlib
import os

from flask import json
from json import JSONDecodeError

from utils.PackageFinder import InvalidPackageName
from utils.Tools import file_as_blockiter, hash_bytestr_iter
from watchdog.events import FileSystemEventHandler


class PackageVersioning(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.__update_directory()

    def on_deleted(self, event):
        if not event.is_directory:
            self.__update_directory()

    def on_created(self, event):
        if not event.is_directory:
            self.__update_directory()

    def __enter__(self):
        event_handler = self
        for p in self.__repos_json_conf:
            observer = Observer()
            observer.schedule(event_handler, path=p['directory_path'], recursive=False)
            observer.start()
            self.__repos_obs.append(observer)
        return self

    def __exit__(self, type, value, traceback):
        for o in self.__repos_obs:
            o.stop()
        for o in self.__repos_obs:
            o.join()

    def __init__(self, package_finder, repos_json_conf, prefix_url_download="/download"):
        self.__repos_public = {}
        self.__repos_private = {}
        self.__package_finder = package_finder
        self.__repos_json_conf = repos_json_conf
        self.__repos_obs = []
        self.__prefix_url_download = prefix_url_download

        self.__update_directory()

    def __update_directory(self):
        for p in self.__repos_json_conf:
            self.__version_directory(p['directory_path'], p['name'], p['description'])

    def __version_directory(self, directory_path, repo_name, repo_description):
        repo_public = {"repo_description": repo_description}
        repo_private = {"directory_path": os.path.abspath(directory_path)}

        for filename in self.__package_finder.find_packages(directory_path):
            package_path = os.path.join(directory_path, filename)

            package_name = self.__package_finder.get_package_name(filename)
            version_major = self.__package_finder.get_version_major(filename)
            version_minor = self.__package_finder.get_version_minor(filename)
            version_release = self.__package_finder.get_version_release(filename)
            version = (version_major, version_minor, version_release)
            package_url = os.path.join(self.__prefix_url_download, repo_name, filename)
            pacakage_sha256 = hash_bytestr_iter(file_as_blockiter(open(package_path, "rb")), hashlib.sha256(),
                                                ashexstr=True)
            package_md5 = hash_bytestr_iter(file_as_blockiter(open(package_path, "rb")), hashlib.md5(), ashexstr=True)
            package_sig_url = "{}.sig".format(package_path)
            version_info_path = "{}.json".format(package_path)

            if os.path.isfile(version_info_path):
                with open(version_info_path) as data_file:
                    try:
                        version_info = json.load(data_file)
                    except JSONDecodeError:
                        print("Error decoding info version file {}".format(version_info_path))
                        version_info = None
            else:
                version_info = None

            if not os.path.isfile(package_sig_url):
                package_sig_url = None
            else:
                package_sig_url = "{}.sig".format(package_url)

            if package_name not in repo_public:
                repo_public[package_name] = {}
            else:
                if str(version) in repo_public[package_name]:
                    raise Exception("Conflict name package {} version {} ! Version already exist !"
                                    .format(package_name, str(version)))

            repo_public[package_name][str(version)] = {
                "version_major": version_major,
                "version_minor": version_minor,
                "version_release": version_release,
                "version_info": version_info,
                "url": package_url,
                "sha256": pacakage_sha256,
                "md5": package_md5,
                "signature_url": package_sig_url,
                "modification_date": datetime.fromtimestamp(os.path.getmtime(package_path)).isoformat(),
                "modification_timestamp": os.path.getmtime(package_path),
            }

        self.__repos_public[repo_name] = repo_public
        self.__repos_private[repo_name] = repo_private

    def get_all_packages(self, package_name=None, repo_name=None):
        if repo_name is None:
            return self.__repos_public
        repo_name, repo_public, _ = self.__get_repo(repo_name)
        try:
            return repo_public[package_name] if \
                package_name is not None else repo_public
        except KeyError:
            raise PackageDoNotExist

    def get_last_version_package(self, package_name, repo_name=None):
        _, repo_public, _ = self.__get_repo(repo_name)

        try:
            package = repo_public[package_name]
        except KeyError:
            raise PackageDoNotExist

        last_version = max(package,
                           key=lambda i: (package[i]["version_major"],
                                          package[i]["version_minor"],
                                          package[i]["version_release"])
                           )

        return package[str(last_version)]

    def get_path_package(self, filename, repo_name=None):
        if not self.__package_finder.is_valid_filename(filename):
            raise InvalidPackageName
        _, _, repo_private = self.__get_repo(repo_name)
        return os.path.join(repo_private['directory_path'], filename)

    def __get_repo(self, repo_name):
        try:
            return repo_name, self.__repos_public[repo_name], self.__repos_private[repo_name]
        except KeyError:
            raise RepoDoNotExist

    def get_version_package(self, package_name, repo_name=None, version_major=None, version_minor=None,
                            version_release=None):
        _, repo_public, _ = self.__get_repo(repo_name)

        try:
            package = repo_public[package_name]
        except KeyError:
            raise PackageDoNotExist

        try:
            if None not in (version_major, version_minor, version_release):
                return package[str((version_major, version_minor, version_release))]
            elif None not in (version_major, version_minor):
                version = \
                    max(
                        filter(
                            lambda i: package[i]["version_major"] == version_major
                                      and package[i]["version_minor"] == version_minor, package
                        ),
                        key=lambda i: (
                            package[i]["version_major"],
                            package[i]["version_minor"],
                            package[i]["version_release"]
                        )
                    )
                return package[str(version)]
            elif version_major is not None:
                version = \
                    max(
                        filter(
                            lambda i: package[i]["version_major"] == version_major, package
                        ),
                        key=lambda i: (
                            package[i]["version_major"],
                            package[i]["version_minor"],
                            package[i]["version_release"]
                        )
                    )
                return package[str(version)]
            else:
                raise VersionDoNotExist
        except (ValueError, KeyError):
            raise VersionDoNotExist


class VersionDoNotExist(Exception):
    pass


class RepoDoNotExist(Exception):
    pass


class PackageDoNotExist(Exception):
    pass