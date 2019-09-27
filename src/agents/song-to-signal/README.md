# To run this agent

1. Python3 installed
2. Set up and activate virtual python3 environment; e.g.:

        virtualenv mcenv -p python3
        . mcenv/bin/activate

3. Install additional libraries

    (This step can be skipped if using a previously created `mcenv`)

        pip install rdflib
        pip install requests
        pip install SPARQLwrapper

4. Set CONTAINER and MELD_USERNAME environment variables

        export CONTAINER=
        export MELD_USERNAME=

5. Start Solid server with `webid=false` in config.json file

6. Run agent:

        python3 song_to_signal.py Mogwai "acid food"

