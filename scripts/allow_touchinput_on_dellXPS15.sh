sudo chmod 666 /dev/input/event10
sudo chmod 666 /dev/input/event19


echo "you must manually add these lines under section [input] into the config file `~/.kivy/config.init`"
echo "mtdev_%(name)s = probesysfs,provider=mtdev"
echo "hid_%(name)s = probesysfs,provider=hidinput"
echo "touch = probesysfs,match=E3 Finger,provider=linuxwacom,
    select_all=1,param=mode=touch"

