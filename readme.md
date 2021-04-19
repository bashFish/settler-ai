# TODO
- building config should contain production speed etc.
- man muss noch iwie nen gewinn kriterium und score festlegen -> fewest ticks/ most ressources left
- ui/game/state muessen gut getrennt sein, zum ai spiele generien
- game logging/transcript for ai training
- carrier and worker (cutter) should take longer for longer distances
- refactor everything (i.p. ui, state & factories)
- search for settler 2 projects/ graphics
- look into pygame
- debug/ logging
- TODO's in code
- delete needs to reduce settlers as well
- introduce worker class -> delete frees worker
- start/stop
- delete in keys

# AI Goal: 
## iteration 1:
- map contains only forest. buildings: woodcutter, sawmill, barack
- goal: cut off all wood
## iteration 2:
- get as much bread as possible within x minutes OR 
- get fastest x bread
## iteration 3:
- get as much coins as possible

# Gameplay:
- every building requires 1 settler 
- every settler requires 1 food / X ticks 
- every tick, storehouse + base can transport X ressources 
- othw: "normal settler" border can be extendes by baracks etc

# Source:
## game
contains game code 

## simulation
given ai, generates transcriptions of auto-played games

## training 
trains ai

- need something hierarchical 
  - -> ai should eg highlevel learn that woodcutter only makes sense near wood
- compose/ formulate a strategy, then look for moves
- do a hidden state for own reasoning
- learn one-time associations : placing a cutter -> gets associated with nearest wood once. 
- placing storehouse -> all get re-associated with nearest.