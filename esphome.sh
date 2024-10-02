#!/usr/bin/sh

set -x

binding="--network=host"

while getopts "d:" opt; do
    case $opt in 
        d)
            binding="--device=$OPTARG"
            ;;
        \?)
            exit 1
            ;;
    esac
done

shift $((OPTIND - 1))

docker run --rm "$binding" -v "$PWD:/config" -i -t ghcr.io/esphome/esphome "$@"
