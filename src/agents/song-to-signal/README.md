# To run this agent

1. Python3 installed
2. Set up and actiovate virtual python3 environment; e.g.:

        virtualenv mcenv -p python3
        . mcenv/bin/activate

3. Install additional libraries

        pip install rdflib
        pip install requests
        pip install SPARQLwrapper

4. Set CONTAINER environment variable

        export CONTAINER=

5. Start Solid server with `webid=false` in config.json file

6. Run agent:

        python3 song_to_signal.py Mogwai "acid food"

