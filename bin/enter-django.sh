#!/bin/bash

case "$(uname -s)" in    
    CYWGWIN*|MSYS*|MINGW*)
        echo 'Windows'
        winpty docker exec -it card_django bash    
    ;;

    *)
        echo 'Linux'
        docker exec -it card_django bash
    ;;
esac
