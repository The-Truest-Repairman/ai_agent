#!/usr/bin/env bash
# libCEC-only Samsung remote bridge (original architecture).
# cec-client on /dev/ttyACM0 -> ydotool key injection for 44: UI press frames.

set -euo pipefail

LOG="${HOME}/cec_log.txt"
CEC_CLIENT=(cec-client -d 8 -m -p 1 -t p -o bazzite)

log() {
    printf '%s %s\n' "$(date -Is)" "$*" >> "${LOG}"
}

ensure_ydotoold() {
    if ! pgrep -x ydotoold >/dev/null 2>&1; then
        log "starting ydotoold"
        systemd-run --user --scope -- ydotoold >> "${LOG}" 2>&1 || true
        sleep 1
    fi
}

send_key() {
    log "ydotool key $*"
    ydotool key "$@" >> "${LOG}" 2>&1 || log "ydotool key failed: $*"
}

handle_cec_key() {
    local hex="$1"
    case "${hex}" in
        01) send_key 103:1 103:0 ;;  # up
        02) send_key 108:1 108:0 ;;  # down
        03) send_key 105:1 105:0 ;;  # left
        04) send_key 106:1 106:0 ;;  # right
        00) send_key 28:1 28:0 ;;    # select / enter
        0d) send_key 1:1 1:0 ;;      # back / escape
        41) send_key 113:1 113:0 ;;  # volume up
        42) send_key 114:1 114:0 ;;  # volume down
        43) send_key 118:1 118:0 ;;  # mute
        *) log "unmapped 44:${hex}" ;;
    esac
}

log "cec-bridge starting: ${CEC_CLIENT[*]}"
ensure_ydotoold

# Warmup: brief scan helps libCEC claim address before monitor mode.
{
    echo scan
    sleep 3
} | cec-client -d 8 -o bazzite -t p >> "${LOG}" 2>&1 || true

exec "${CEC_CLIENT[@]}" 2>> "${LOG}" | while IFS= read -r line; do
    log "${line}"
    if [[ "${line}" =~ (^|[[:space:]]|>>[[:space:]]*[0-9a-fA-F]+:)44:([0-9a-fA-F]+) ]]; then
        handle_cec_key "${BASH_REMATCH[2],,}"
    fi
done
