#!/bin/sh

if [ "$DEBUG" = true ];
then
    python -m bytewax.run "tools.run_real_time:build_flow(debug=True)"
else
    # below var cfgd as env variable in docker-compose.yml
    if [ "$BYTEWAX_PYTHON_FILE_PATH" = "" ];
    then
        echo 'BYTEWAX_PYTHON_FILE_PATH is not set. Exiting....'
        exit 1
    fi
    echo 'BYTEWAX_PYTHON_FILE_PATH is set....'
    python -m bytewax.run $BYTEWAX_PYTHON_FILE_PATH
fi

echo 'Process ended.'

if [ "$BYTEWAX_KEEP_CONTAINER_ALIVE" = true ];
then
    echo 'Keeping container alive....';
    while :; do sleep 1; done
fi
