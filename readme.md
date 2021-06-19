# TODO
- check  training of dqn
- adjust score: cutting wood from distane = more score!
- check verlauf von predictions tensorboard
- log von loss scheint kaputt
  
- icm
- transformer
- battling agents
- iterated score function learning including coord models
  - alternate action/coord model training, only train, 
    if other one produced useful predictions 


- replay buffer/ target network 
  -> careful with loss etc
  -> need last n states -> encode memory later to do better planning! 
- annealing of random/ best player moves
- build proper architecture s.t. new building can be integrated
  -> split every (sub-) task, do a "model-distributed" normalisation of values s.t. they can be comparable
  -> only least possible should be retrained
  -> prioritized experience buffer paper
- difficulty with similar states -> highlight somehow discrimitive difference?
reward clipping
dqn is reactive -> need sth for more reward?
 deepmind.com/dqn he says more data efficient methods now!!
- use double dqn afterwards! need sth with long term rewards
- dueling network architectures for deep rl paper
- icm for inverse action selection paper
- exploration : noisy nets for exploration paper 
- target: good memory network, efficient architecture, auto ml-architecture, extendable
- attention later for explainability and for focusing decision on what is important  
- first memory approach: recurrent nets/ transformer
- warum braucht das netz die kompletten letzten 4 states, und nicht nur die letzten actions + aktuellen state?
- one bayes network with different priors? + UAI for explaining it
-> don't just put everything into a number! keep the structure you got!!! primitive discrimiation like ressources/mapping or different actors
- introduce text driven reasoning/ decision making (just for fun)
 
  HERE IAM state of art Fall 2017!
  What happened afterwards?
  
  

- do Policy iteration
- curiosity driven reward function
- replay buffer: prioritize "good samples"/ keep equal distribution of most discriminative data

- BOHB architecture finding
- memory/ strategy/ planning
  
- increase number working ticks for carrier/ woodcutter according to distance
- add productivity of buildings
- refactor game code
- add 'change statistic' e.g. produced wood, buildings etc
- use lstm/ transformer
- to gameover or not to gameover

- implement/ find reasoning/explainable network
- should be refactored/ environment?
  
- train 2 network model without old - state (and look at old state)
- one network per building -> one network for composition -0 LSTM like convergance 


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
- construction shouldn't be in buildings.json
- put score to config

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