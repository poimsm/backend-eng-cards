#!/bin/bash

source ./bin/commands.sh

CMD_PREFIX=$(detectar_os)

${CMD_PREFIX} docker exec -it card_django bash

