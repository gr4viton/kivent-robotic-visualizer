# kivent-robotic-visualizer
Visualisation of 2D robotic movement in map using kivent game loop python module


## install via playbook

Use the `scripts/playbook.yml`

## Install manually

### clone kivent and install its python dependencies
```
git clone https://github.com/kivy/kivent /srv/kivent
cd /srv/kivent
python3 -m pip install -r requirements.txt
```
If you get an error you can try run the install command for the second time.

### then install individual kivent modules which are needed
Follow individual dependencies mentioned in the following section: https://github.com/kivy/kivent#dependencies
#### kivent_core
```
cd /srv/kivent/modules/core
python3 setup.py build_ext install
```

#### kivent_cymunk
```
# First install pymunk
python3 -m pip install pymunk

# then clone and install the cython wrapper = cymunk
git clone https://github.com/kivy/cymunk /srv/cymunk
cd /srv/cymunk
sudo python3 -m pip install pymunk
# I needed sudo otherwise I got `warning: build_py: byte-compiling is disabled, skipping.`

# and then install the kivent_cymunk module
cd /srv/kivent/modules/cymunk
python3 setup.py build_ext install
#
```
