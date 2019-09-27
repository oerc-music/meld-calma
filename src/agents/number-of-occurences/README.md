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

    Change to the "agents" directory in the current repository (e.g. `/Users/graham/workspace/github/oerc-music/meld-calma/src/agents`)

        python3 song-to-signal/song_to_signal.py Mogwai "acid food"   # (if not already run)
        python3 number-of-occurences/number_of_occurences.py Mogwai "acid food"


At this point, expect to be able to see something like this:

    $ node $MELD_TOOL ls /public/
    List container /public/
    https://localhost:8443/public/artists_songs/
    https://localhost:8443/public/artists/
    https://localhost:8443/public/song_number_of_occurrences/
    https://localhost:8443/public/song_to_recording/

    $ node $MELD_TOOL ls https://localhost:8443/public/song_number_of_occurrences/
    List container https://localhost:8443/public/song_number_of_occurrences/
    https://localhost:8443/public/song_number_of_occurrences/song_occurrence_7e0e515fd10c481c9a21345936153cb0.ttl

