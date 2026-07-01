#!/usr/bin/env bash
# Revert custom libCEC bridge and restore Bazzite-managed CEC.
# Run: sudo bash revert-to-bazzite.sh [dgpu|native]

set -euo pipefail

USER_NAME="${SUDO_USER:-brandon}"
USER_HOME="$(getent passwd "$USER_NAME" | cut -d: -f6)"
MODE="${1:-}"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Run as root: sudo bash revert-to-bazzite.sh [dgpu|native]" >&2
    exit 1
fi

echo "==> Stopping custom cec-bridge for ${USER_NAME}"

sudo -u "${USER_NAME}" XDG_RUNTIME_DIR="/run/user/$(id -u "${USER_NAME}")" \
    systemctl --user disable --now cec-bridge.service 2>/dev/null || true

if [[ -f "${USER_HOME}/.config/systemd/user/cec-bridge.service" ]]; then
    mv "${USER_HOME}/.config/systemd/user/cec-bridge.service" \
        "${USER_HOME}/.config/systemd/user/cec-bridge.service.bak.$(date +%s)"
fi

if [[ -f "${USER_HOME}/remote.sh" ]]; then
    mv "${USER_HOME}/remote.sh" "${USER_HOME}/remote.sh.bak.$(date +%s)"
fi

echo "==> Removing custom udev overrides"
rm -f /etc/udev/rules.d/99-pulse8-cec.rules
rm -f /etc/udev/rules.d/99-cec-bluetooth.rules
# Keep 10-cec-wakeup.rules if you added it yourself before; remove for fully stock:
# rm -f /etc/udev/rules.d/10-cec-wakeup.rules

udevadm control --reload-rules
udevadm trigger --subsystem-match=tty --action=add
udevadm trigger --subsystem-match=usb --action=add

echo "==> Unmasking Bazzite inputattach units"
systemctl unmask pulse8-cec-inputattach@.service rainshadow-cec-inputattach@.service 2>/dev/null || true

echo "==> Hand off to ujust cec-mode"
if [[ -n "${MODE}" ]]; then
    sudo -u "${USER_NAME}" ujust cec-mode "${MODE}"
else
    echo "Run as ${USER_NAME}: ujust cec-mode"
    echo "  Pulse-Eight USB/internal adapter -> choose dGPU"
    echo "  Kernel/GPU CEC (cecd)            -> choose Native"
fi

echo ""
echo "Verify:"
echo "  ujust cec-mode status"
echo "  systemctl status pulse8-cec-inputattach@ttyACM0.service"
echo "  ls -la /dev/ttyACM0 /dev/cec* 2>/dev/null"
echo "  echo scan | cec-client -d 8 -t p -o bazzite"
