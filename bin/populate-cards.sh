#!/bin/bash

# Define el nombre de tu contenedor Django
CONTAINER_NAME=card_django

# Define los comandos de Django que quieres ejecutar dentro del contenedor
COMMANDS=(
    "python manage.py populate_cards"
)

# Detectar el sistema operativo y preparar el prefijo del comando
case "$(uname -s)" in    
    CYGWIN*|MSYS*|MINGW*)
        echo 'Detected Windows environment'
        CMD_PREFIX="winpty docker exec -it"
    ;;

    *)
        echo 'Detected Linux environment'
        CMD_PREFIX="docker exec -it"
    ;;
esac

# Ejecutar los comandos de Django en el contenedor
for cmd in "${COMMANDS[@]}"; do
    echo "Executing: $cmd"
    $CMD_PREFIX $CONTAINER_NAME bash -c "$cmd"
done
