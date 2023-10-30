from setuptools import setup, find_packages
import platform

if platform.system() in ["Linux", "Darwin"]:
    path_sep = "/"
elif platform.system() == "Windows":
    path_sep = "\\"
else:
    raise EnvironmentError("Unsupported platform : " + platform.system())

setup(
    name="buildingdata",
    version=0.1,
    author="John Levy",
    author_email="",
    packages=find_packages(),
    url="",
    description="Scrap french open-data on buildings",
)
