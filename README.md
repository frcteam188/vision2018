# vision2018

temporary testing repo for vision, will delete sooner or later

# Requirements
This project is meant to be run with virtualenv it should work fine without it however it is reccomended you install it.
Easiest way is to follow the instructions [here](https://github.com/brainsik/virtualenv-burrito)
Or just run the line below.
```
curl -sL https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL
```

# Setup

- Clone the repo

- Setup virtualenv

```
cd vision2018
mkvirtualenv -p <PATH TO PYTHON 3> vision2018
```
You can get the path to Python3 using `which python3`

The above line should already activate the environment, in case it did not `workon vision2018`

- Install the requirements

```
pip install -r requirements.txt
```
