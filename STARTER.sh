pwd
cd ~/NV3_CodeBase/STARTUP_CRON/
python3 utils/STARTUP_BEEPS.py
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export XDG_RUNTIME_DIR=/run/user/1000
/usr/bin/nmcli device wifi connect kz password Arvix@34560
python3 utils/STARTUP_BEEPS.py
sleep 20
sudo systemctl enable ssh
sudo systemctl start ssh
python3 utils/STARTUP_BEEPS.py
jupyter-notebook --no-browser
