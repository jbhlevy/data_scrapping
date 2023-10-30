Installation
============

To use this package for acquisation of open-data regarding French buildings, follow the instructions below.

Pre-requisites
--------------

* [Anaconda 3.8 distribution](https://www.anaconda.com/distribution/) or [Miniconda3 distribution](https://docs.conda.io/en/latest/miniconda.html)
* To clone buildindata's Gitlab repository, [Git](https://git-scm.com/downloads) (On Windows, [Git for Windows](https://git-for-windows.github.io/) is preferred)


### Creating the conda environment

Open a command line tool in the buildingdata root folder and then run the following :

```
conda env create -f conda_env.yml
```

Activate the environment we have just created :

```
conda activate buildingmodel
```

For more information on conda environments, please visit https://conda.io/docs/using/envs.html .


### Installing the package

Then, from the root folder of buildingmodel, run :

```
python setup.py install
```
### Compiling a local version of the documentation

The documentation is compiled using the sphinx, make sure you have the right dependencies installed if you wish to recompile it by running 

```
make html
```

after having `cd` into the docs folder (Be careful, Windows sometimes require make to be called as an executable i.e. `.\make html`). 
Otherwise you can acess the current documentation at the `docs/build.index.html` file.# data_scrapping
