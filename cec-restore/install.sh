#!/usr/bin/env bash
# Restore libCEC-only CEC architecture (pre-Bazzite inputattach stack).
# Run on the NUC: sudo bash install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="${SUDO_USER:-brandon}"
USER_HOME="$(getent passwd "$USER_NAME" | cut -d: -f6)"
UDEV_DIR="/etc/udev/rules.d"
SYSTEMD_USER_DIR="${USER_HOME}/.config/systemd/user"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Run as root: sudo bash install.sh" >&2
    exit 1
fi

echo "==> Restoring libCEC-only CEC stack for ${USER_NAME} (${USER_HOME})"

# --- Block Bazzite kernel inputattach path ---
echo "==> Masking pulse8-cec-inputattach@.service"
systemctl mask pulse8-cec-inputattach@.service 2>/dev/null || true
systemctl stop 'pulse8-cec-inputattach@*.service' 2>/dev/null || true

# --- Udev: block auto-inputattach, restore ttyACM access, optional cec0 symlink ---
echo "==> Installing udev rules"
install -Dm644 "${SCRIPT_DIR}/udev/99-pulse8-cec.rules" "${UDEV_DIR}/99-pulse8-cec.rules"
install -Dm644 "${SCRIPT_DIR}/udev/10-cec-wakeup.rules" "${UDEV_DIR}/10-cec-wakeup.rules"

# Neutralize stale Bazzite bluetooth->cec-control hook if present in /usr
if [[ -f /usr/lib/udev/rules.d/99-cec-bluetooth.rules ]]; then
    install -Dm644 "${SCRIPT_DIR}/udev/99-cec-bluetooth.rules" "${UDEV_DIR}/99-cec-bluetooth.rules"
fi

udevadm control --reload-rules
udevadm trigger --subsystem-match=tty --action=add

# --- User in dialout for ttyACM0 (Bazzite default is 660) ---
echo "==> Adding ${USER_NAME} to dialout group"
usermod -aG dialout "${USER_NAME}" 2>/dev/null || true

# --- Application files ---
echo "==> Installing remote.sh and cec-bridge.service"
install -Dm755 "${SCRIPT_DIR}/remote.sh" "${USER_HOME}/remote.sh"
install -Dm644 "${SCRIPT_DIR}/cec-bridge.service" "${SYSTEMD_USER_DIR}/cec-bridge.service"
chown "${USER_NAME}:${USER_NAME}" "${USER_HOME}/remote.sh" "${SYSTEMD_USER_DIR}/cec-bridge.service"

# --- Disable legacy Bazzite cec-control services if still present ---
for svc in cec-onboot cec-onsleep cec-onpoweroff; do
    systemctl disable "${svc}.service" 2>/dev/null || true
    systemctl stop "${svc}.service" 2>/dev/null || true
done

# --- Unload kernel pulse8 driver if it grabbed the port ---
modprobe -r pulse8_cec 2>/dev/null || true

# --- Enable user bridge ---
echo "==> Enabling cec-bridge user service"
sudo -u "${USER_NAME}" XDG_RUNTIME_DIR="/run/user/$(id -u "${USER_NAME}")" \
    systemctl --user daemon-reload
sudo -u "${USER_NAME}" XDG_RUNTIME_DIR="/run/user/$(id -u "${USER_NAME}")" \
    systemctl --user enable cec-bridge.service
sudo -u "${USER_NAME}" XDG_RUNTIME_DIR="/run/user/$(id -u "${USER_NAME}")" \
    systemctl --user restart cec-bridge.service

echo ""
echo "Done. Verify with:"
echo "  systemctl is-masked pulse8-cec-inputattach@.service"
echo "  ls -la /dev/ttyACM0"
echo "  echo scan | sudo cec-client -d 8 -o bazzite -t p"
echo "  systemctl --user status cec-bridge.service"
echo "  tail -f ${USER_HOME}/cec_log.txt"
echo ""
echo "Log out and back in (or reboot) so dialout group membership applies."
