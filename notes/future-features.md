# Future features

This file lists some features that may considered for futuire implementation in the MELD/CALMA work, after a basic end-to-end system for key typicality has been implemented.


## Filter out different recordings of same concert

Currebntly, when there are multiple recxiordings, they are all analyzed separately, and contribute independently to the typicality analysis.  In future, we may want to consider some way of combining and/or filtering them so each concert gets equal weight in this analysis.


## Features other than key typicality

Current focus is on key typicality, per the original rCALMA work.  But the value of the SOFA approach would be more convincingly dem,onstrated if we can add new features by adding new analysis agents.

Note: rCALMA captures info for key, chord and tempo.

## Filtering agent framework

Both SOFA fragment remixer andf MELD/CALMA have shown up requirements for creating worksets that are filtered down in some way from a raw corpus of available data.  This suggests a possibility for a gebneric filtering agent framework.

(cf. CALMA song selection, useful fragment worksets)

## Agent-activation: responding to updates to workset

Agent activation is currently by manual running of scripts.  A true agent-based system would trigger analyses automatically in response to updates in the input and intermediate data.

Solid notifications look appropriate (gives WebSocket notification when container contents change)

## Incremental agent design 

(respond to changes rather than rescanning everything)

Currently, the agents just process everything they are poinrted at each time they run.  It would probably be smarter if they could respond incrementally to changes in the input data.

(GK thought: possible use for ResourceSync designs here?  Could Solid server be enhanced to support ResourceSync?)

## Performance using Solid

Once the SOFA app is settled, we can start looking at optimizations for performance of the agent model.  Maybe also follow up links with Inrupt delelopment of an enterprise frade Solid server and try that for performance?

