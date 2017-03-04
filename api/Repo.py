from flask import json
from flask_restful import Resource, abort
from flask import redirect, send_file

from utils.PackageFinder import InvalidPackageName
from utils.PackageVersioning import VersionDoNotExist, RepoDoNotExist, PackageDoNotExist, PackageVersioning

package_versioning = None

class BrowseRepo(Resource):
    def get(self, repo_name=None, package_name=None):
        try:
            return package_versioning.get_all_packages(package_name=package_name, repo_name=repo_name), 200
        except (RepoDoNotExist, PackageDoNotExist) as e:
            print(type(e))
            abort(404)


class BrowseRepoVersion(Resource):
    def get(self, package_name, repo_name, version_major=None, version_minor=None, version_release=None):
        try:
            return package_versioning.get_version_package(
                package_name=package_name,
                repo_name=repo_name,
                version_major=version_major,
                version_minor=version_minor,
                version_release=version_release
            )
        except (RepoDoNotExist, PackageDoNotExist, VersionDoNotExist) as e:
            print(e)
            abort(404)


class InfoLastPackage(Resource):
    def get(self, package_name, repo_name):
        try:
            return package_versioning.get_last_version_package(package_name=package_name, repo_name=repo_name), 200
        except (RepoDoNotExist, PackageDoNotExist):
            abort(404)


class DownloadLastPackage(Resource):
    def get(self, package_name, repo_name):
        try:
            return redirect(
                package_versioning.get_last_version_package(package_name=package_name, repo_name=repo_name)['url']
            )
        except (RepoDoNotExist, PackageDoNotExist):
            abort(404)


class DownloadPackageVersion(Resource):
    def get(self, package_name, repo_name, version_major=None, version_minor=None, version_release=None):
        try:
            return redirect(
                package_versioning.get_version_package(
                    package_name=package_name,
                    repo_name=repo_name,
                    version_major=version_major,
                    version_minor=version_minor,
                    version_release=version_release
                )['url']
            )
        except VersionDoNotExist:
            abort(404)


class DownloadPackage(Resource):
    def get(self, filename, repo_name=None):
        try:
            return send_file(package_versioning.get_path_package(filename=filename, repo_name=repo_name))
        except InvalidPackageName:
            abort(404)
