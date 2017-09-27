import json

from Config import CURRENT_CONFIG

from flask import Flask
from flask_restful import Api
import api.Repo as repoApi
from api.Repo import BrowseRepo, InfoLast, InfoLastRepo, InfoLastPackage, DownloadLastPackage, DownloadPackage, DownloadPackageVersion, \
    BrowseRepoVersion
from utils.PackageVersioning import PackageVersioning

app = Flask(__name__)
app.config.from_object(CURRENT_CONFIG)
api = Api(app, catch_all_404s=True)

# Api resource
api.add_resource(
    BrowseRepo,
    '/',  # Retrieve available repos
    '/<string:repo_name>',  # Retrieve data from <repo_name>
    '/<string:repo_name>/<string:package_name>',  # Retrieve data from <repo_name> about <package_name>
)

api.add_resource(
    BrowseRepoVersion,
    '/<string:repo_name>/<string:package_name>/<int:version_major>',
    # Retrieve data version <package_name> from <repo_name>
    '/<string:repo_name>/<string:package_name>/<int:version_major>/<int:version_minor>',
    # Retrieve data version <package_name> from <repo_name>
    '/<string:repo_name>/<string:package_name>/<int:version_major>/<int:version_minor>/<int:version_release>',
    # Retrieve data version <package_name> from <repo_name>
)

api.add_resource(
    InfoLast,
    '/last'
)

api.add_resource(
    InfoLastRepo,
    '/<string:repo_name>/last'
)

api.add_resource(
    InfoLastPackage,
    '/<string:repo_name>/<string:package_name>/last',  # Info for last version <package_name> from <repo_name>
)

api.add_resource(
    DownloadLastPackage,
    '/download/<string:repo_name>/<string:package_name>/last',
    # Download last version <package_name> from  <repo_name>
)

api.add_resource(
    DownloadPackageVersion,
    '/download/<string:repo_name>/<string:package_name>/<int:version_major>',
    # Download version <package_name> from <repo_name>
    '/download/<string:repo_name>/<string:package_name>/<int:version_major>/<int:version_minor>',
    # Download version <package_name> from <repo_name>
    '/download/<string:repo_name>/<string:package_name>/<int:version_major>/<int:version_minor>/<int:version_release>',
    # Download version <package_name> from <repo_name>
)

api.add_resource(
    DownloadPackage,
    '/download/<string:repo_name>/<string:filename>',  # Download version <filename> from repo_name
)

@app.before_first_request
def setup():
    repoApi.package_versioning = PackageVersioning(json.load(open(app.config['REPOS_JSON_CONFIG_PATH'])))
    repoApi.package_versioning.__enter__()


if __name__ == '__main__':
    app.run(host="0.0.0.0")
