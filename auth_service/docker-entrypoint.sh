#!/bin/bash
export RUN_MODE

make migrate

case $RUN_MODE in
"prod-like")
echo $RUN_MODE
make run_with_gunicorn
  ;;
"dev")
echo $RUN_MODE
make run_with_uvicorn
  ;;
esac