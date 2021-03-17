# kivent-robotic-visualizer
Visualisation of 2D robotic movement in map using kivent game loop python module

## install via pipenv
```
pipenv --three
pipenv shell
pip install kivy

# kivent-robotic-visualiser dependencies install
# nope: pip install -r scripts/requirements.txt
pip install -r svgwrite

# kivent install
git clone https://github.com/kivy/kivent /srv/kivent
cd /srv/kivent
pip install -r requirements.txt
./script/install_all.sh

```
Worked on ubuntu 20.04

## install via playbook
Did not work on ubuntu 20.04.

Use the `scripts/playbook.yml`

## Install manually
Did not work on ubuntu 20.04.


### clone kivent and install its python dependencies
```
git clone https://github.com/kivy/kivent /srv/kivent
cd /srv/kivent
python3 -m pip install -r requirements.txt
```
If you get an error you can try run the install command for the second time.

### build and install cymunk - kivent_cymunk module dependency
```
# clone and build the pymunk cython wrapper = cymunk
git clone https://github.com/kivy/cymunk /srv/cymunk
cd /srv/cymunk
sudo python3 setup build_ext --inplace -f
sudo python3 setup install
```
I needed `sudo` otherwise I got `warning: build_py: byte-compiling is disabled, skipping.`

### then install all kivent modules which are needed
Follow individual dependencies mentioned in the following section: https://github.com/kivy/kivent#dependencies

```
cd /srv/kivent
./scripts/install_all.sh
# you might need to change python -> python3 in the install_all.sh script first
```
