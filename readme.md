# TODO

https://scikit-optimize.github.io/stable/modules/generated/skopt.gp_minimize.html

https://scikit-optimize.github.io/stable/auto_examples/strategy-comparison.html#sphx-glr-auto-examples-strategy-comparison-py

- copy all code per experiment

for strategy planning:
- let network  propose N solutions, trajectories, then do search on them  

R-CNN/ YOLO/ Selective Search:
1. Generate initial sub-segmentation, we generate many candidate     regions
2. Use greedy algorithm to recursively combine similar regions into larger ones 
3. Use the generated regions to produce the final candidate region proposals 


- META-REINFORCEMENT LEARNING
http://ai.stanford.edu/blog/meta-exploration/
  https://github.com/ezliu/dream
  
- todo: experimente mit parameter vor ausfuehrung kopieren speichern
- another split of networks:
  - explicit do/nothing + buildings + positions (one for each building) ?
  - next step: one for each building
  - agents fuer strategie, die kollaborativ entscheiden was zu tun
    - eine ki fuer rohstoffe, eine fuer militaer, decision making 
    - einen (paar) schritt in die zukunft simulieren/ projective simulation

- check  training of dqn
- adjust score: cutting wood from distane = more score!
- check verlauf von predictions tensorboard
- log von loss scheint kaputt
  
- ICM, SERENE
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

## DQN
- distribution epsilon greedy might be shitty?
- TODO: score function nur +1 bei holz gehackt, -1 bei gamover? 
- speedup wenn ich jeden state ordentlich reward (produced) geben wuerde!
- diverging scores -> reward scaling/ clipping?
- remodel into agent vs agent game -> just +1 for more score


# interesting findings:
## DQN 

(- can't continue training - just doesnt produce meaningful new gradients.[is that still happening?])
- building a consumable score function was aweful! every hint just became a trap
  
- training runs after 2.5k games

[(<GameEvent.CONSTRUCT_BUILDING: 2>, ((28, 29), 'Sawmill')), None, None, None, (<GameEvent.CONSTRUCT_BUILDING: 2>, ((22, 20), 'Woodcutter')), (<GameEvent.CONSTRUCT_BUILDING: 2>, ((30, 21), 'Woodcutter')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
[[1.7053597  1.0920347  0.98589194 1.5440711 ]
 [1.379065   1.3187199  1.4117165  3.152345  ]
 [1.9823706  1.955113   1.8049877  4.09019   ]
 [2.622465   2.4414034  2.0406258  4.4875298 ]
 [1.7825575  5.3060684  4.0746017  4.74598   ]] 
 [[1.6312919  1.0631025  0.97268116 1.4807291 ]
 [1.2228956  1.0987868  1.2329954  2.5383496 ]
 [1.8133109  1.7562737  1.6464466  3.5876846 ]
 [2.819293   2.7076058  2.207342   4.8793874 ]
 [1.6152792  4.9473386  4.10507    4.5945845 ]]