# To run this agent

1. Python3 installed

2. Go to meld/calma directory, set up and activate virtual python3 environment; e.g.:

        cd ~/workspace/github/oerc-music/meld-calma/  # (E.g.)
        virtualenv mcenv -p python3
        . mcenv/bin/activate

3. Install additional libraries

    (This step can be skipped if using a previously created `mcenv`)

        pip install rdflib
        pip install requests
        pip install SPARQLwrapper
        pip install progressbar2

4. Activate Python environment for agents (if not already done), and set CONTAINER and MELD_USERNAME environment variables:

        cd ~/workspace/github/oerc-music/meld-calma/  # (E.g.)
        . mcenv/bin/activate        # Python environment for agents
        export CONTAINER=
        export MELD_USERNAME=

(These ensure that the agent coder (a) uses the default https://localhost:8443/public/ as the top level container for testing against, and (b) does not attempt to autheticate against the Solid server.)

5. In a separate shell, start Solid server with `webid=false` in config.json file.  E.g.:

        . ~/.nvm/nvm.sh             # Activate required node version
        . ~/.nvm/bash_completion
        cd ~/solid/                 # Wherever Solid is installed
        cat config.json             # Check webid setting
        DEBUG=solid:* ./node_modules/solid-server/bin/solid-test start

6. Back in the original shell environment, run the agent; e.g.:


        # cd ~/workspace/github/oerc-music/meld-calma/src/agents/song-to-signal/        
        python3 key-distribution-per-recording.py "recording_workset/Acid_Food_by_Mogwai/"


<!--
        # cd ~/workspace/github/oerc-music/meld-calma/src/agents/song-to-signal/        
        python3 song_to_signal.py Mogwai "acid food"

 -->
