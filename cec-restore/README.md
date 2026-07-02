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

## Troubleshooting: ghost "Intel NUC" steals remote (dgpu / libCEC)

### Symptom

After `echo 'as' | cec-client`, scan may still show:

- **currently active source:** Playback 3 (11) Intel NUC @ `1.0.0.0`
- **bazzite** @ `1.0.7.8` — not active

Remote monitor only shows `>> 0b:44:...` (keys to Playback 3), never `>> 04:44:...` (bazzite).

### Cause

libCEC 7.x autodetects physical address from DRM (`card0-DP-2` → `1.0.7.8`). That wins over
`CEC_PORT_NUMBER=1` / `-p 1`. The Samsung TV keeps routing the remote to a cached ghost device at
the correct port address `1.0.0.0` (Playback 3 / "Intel NUC"), not to bazzite at `1.0.7.8`.

`as` broadcasts active source `10:78` but the TV ignores it in favor of the `1.0.0.0` device.

### Step 9 — force physical address, then retest

```bash
# 9a: override autodetect to 1.0.0.0, then claim active source (one session)
printf 'pa 10 00\nas\n' | sudo cec-client -s -t p -o bazzite

# 9b: scan — bazzite should now be at 1.0.0.0; note who is active source
echo scan | sudo cec-client -s -t p -o bazzite

# 9c: monitor with forced PA in the same session; press D-pad on Samsung remote
{ printf 'pa 10 00\n'; sleep 25; } | timeout 30 sudo cec-client -d 8 -t p -o bazzite -m 2>&1 | tee ~/cec-pa1000.txt

grep '>>' ~/cec-pa1000.txt | head -25
```

**Pass:** lines like `>> 04:44:...` and `>> 04:45`  
**Fail:** still only `>> 0b:44:...` → continue with TV-side steps below

### TV-side (if 9c still routes to 0b)

On Samsung S95D: Settings → Connection → Anynet+ (HDMI-CEC):

1. Turn Anynet+ off, unplug NUC HDMI ~30s, turn Anynet+ back on
2. In device list, remove stale **Intel NUC** if shown; select **bazzite**
3. Retest unplugged VIZIO soundbar if it is still on the bus

### Persistent boot fix (dgpu mode)

`cec-onboot` runs separate `cec-client -s` processes; each re-autodetects `1.0.7.8`. Until Bazzite
passes `pa 10 00` before `as`, override the onboot activate line:

```bash
sudo systemctl cat cec-onboot.service   # confirm ExecStart path
grep -A5 perform_activate /usr/bin/cec-control 2>/dev/null || true
```

Workaround — run activate with forced PA in one shot (test before making permanent):

```bash
printf 'on 0\npa 10 00\nas\n' | sudo cec-client -s -t p -o bazzite
```

For Kodi: set physical address `1000` in CEC adapter settings (disables autodetect in libCEC).
