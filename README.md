Materials for collaborative project with tryg denmark about seasonal prediction of storm damages

The project is organized as an installable conda package. To get setup, first pull the directory from github to your local machine:

``` bash
$ git clone https://github.com/edunnsigouin/cf-trygdanmarkstormpred
```

Then install the conda environment:

``` bash
$ conda env create -f environment.yml
```

Then install the project package:

``` bash
$ python setup.py develop
```

Finally change the project directory in cf-trygdanmarkstormpred/config.py to your local project directory
