#!/bin/bash

# https://docs.marimo.io/

# 기본값 설정
TASKSET_LIST="no input"
COMMAND="edit"
HOST="0.0.0.0"
PORT="8080"
PW="marimo"

# Command validation function
is_valid_command() {
  case "$1" in
    edit|run) return 0 ;;  # When valid. 
    *) return 1 ;;        # When invalid.
  esac
}

# Number validation function
is_valid_port() {
  if [[ "$1" =~ ^[0-9]+$ ]]; then
    return 0
  else
    return 1
  fi
}

# IP Address validation function
is_valid_host() {
  local ip="$1"
  local stat=1
  if [[ $ip =~ ^([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})$ ]]; then
    OIFS="$IFS"
    IFS='.'
    ip=($ip)
    IFS="$OIFS"
    if [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]; then
      stat=0
    fi
  fi
  return $stat
}

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --taskset|-t)
      TASKSET_LIST="$2"
      shift 2
      ;;
    --command|-c)
      COMMAND="$2"
      if ! is_valid_command "$COMMAND"; then
        echo "Error: command must be 'edit' or 'run'"
        exit 1
      fi
      shift 2
      ;;
    --port|-p)
      PORT="$2"
      if ! is_valid_port "$PORT"; then
        echo "Error: port must be a number"
        exit 1
      fi
      shift 2
      ;;
    --host|-h)
      HOST="$2"
      if ! is_valid_host "$HOST"; then
        echo "Error: host must be a valid IP address"
        exit 1
      fi
      shift 2
      ;;
    --passward|-pw)
      PW="$2"
      shift 2
      ;;
    *)
      echo "Unknown option $key"
      exit 1
      ;;
  esac
done

# Run
BASE_COMMAND=(marimo "$COMMAND" --headless --port "$PORT" --host "$HOST" --token --token-password="$PW")
if [ "$TASKSET_LIST" != "no input" ]; then
    RUN_COMMAND=(taskset -c "$TASKSET_LIST" "${BASE_COMMAND[@]}")
else
    RUN_COMMAND=("${BASE_COMMAND[@]}")
fi
echo "${RUN_COMMAND[@]}"
"${RUN_COMMAND[@]}"