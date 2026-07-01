# CEC libCEC-only restore (NUC11 / Bazzite)

Restores the original working architecture:

- **libCEC** talks directly to `/dev/ttyACM0` via `cec-client`
- **No** Bazzite `inputattach` / kernel `pulse8_cec` / `/dev/cec0` path
- User service `cec-bridge.service` runs `remote.sh` -> `ydotool`

## Install on the NUC

```bash
cd /path/to/cec-restore
sudo bash install.sh
```

Then log out and back in (dialout group), or reboot.

## What it changes

| Item | Action |
|------|--------|
| `pulse8-cec-inputattach@.service` | masked |
| `/etc/udev/rules.d/99-pulse8-cec.rules` | blocks auto-inputattach, symlinks `cec0` |
| `/etc/udev/rules.d/10-cec-wakeup.rules` | USB wakeup + `ttyACM0` mode 0666 |
| `~/remote.sh` | libCEC monitor + ydotool bridge |
| `~/.config/systemd/user/cec-bridge.service` | enabled user service |

## Verify

```bash
systemctl is-masked pulse8-cec-inputattach@.service
fuser -v /dev/ttyACM0          # should show cec-client when bridge runs
echo scan | cec-client -d 8 -o bazzite -t p
systemctl --user status cec-bridge.service
tail -f ~/cec_log.txt
```

## Roll back Bazzite defaults

```bash
sudo systemctl unmask pulse8-cec-inputattach@.service
sudo rm /etc/udev/rules.d/99-pulse8-cec.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
systemctl --user disable --now cec-bridge.service
```
