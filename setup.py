from setuptools import setup
from setuptools.command.install import install
import subprocess
import tomli
import os


def get_version():
    with open("pyproject.toml", "rb") as f:
        pyproject_data = tomli.load(f)
    return pyproject_data["project"]["version"]


class PostInstallCommand(install):
    """Post-installation for installing Playwright browsers automatically."""
    def run(self):
        install.run(self)
        if not os.getenv("CI"):  # Skip Playwright install in GitHub Actions
            print("🔧 Running `playwright install` to set up browsers...")
            subprocess.run(["playwright", "install"], check=True)


setup(
    name="dr-web-engine",
    version=get_version(),
    cmdclass={
        "install": PostInstallCommand,
    },
)