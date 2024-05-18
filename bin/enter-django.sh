#!/bin/bash

# case "$(uname -s)" in    
#     CYWGWIN*|MSYS*|MINGW*)
#         echo 'Windows'
#         winpty docker exec -it card_django bash    
#     ;;

#     *)
#         echo 'Linux'
#         docker exec -it card_django bash
#     ;;
# esac

source ./bin/commands.sh

CMD_PREFIX=$(detectar_os)

${CMD_PREFIX} docker exec -it flask sh

