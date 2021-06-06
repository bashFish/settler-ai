 # it's approximated moves! actually: 10*20=200 ticks! # can't be just one, othw always starts with barack


#TODO: alle 10 zuege auf einmal trainierne -> vlt werden dann die abhaengigkeiten klarer, die 10 "code" auch mit trainiert

#TODO: try tensorboard

#TODO: find/ store top game moves!
#           train towards that one
#   eg: move[1] sawmill [pos1 pos2] or sawmill -> [pos1/2, pos3/4,...], randomly pick out of
#      building prediciton at move 1 sawmill ->  second network trained towards pos1/2
#   best game strategy: sawmill,  woodcutter -> predict that
#                   ALREADY predict multiple moves in the begining?
#
#   -> 30% exchange a move, then 30% exchange a coordinate
# TODO: dropout, L1 norm?
#
# TODO: make player playing against each other
#    -> lstd maessig 1/0 rating?
#



# open research problems AI
#   - NLP
#   - auto-mapping and more precise output (no one-hot encode/ hand-crafted lstm etc.)
#   -

# TODO : abort game when gameover!! -> penalty on all moves that led there.
# TODO: 1) invalid move -> penalty! auch bei action (eg keine bretter mehr da)
#       2)   mehr als 5 ticks in vorraus schauen! vielleicht in 5 und in 10! (erst da wird produktion anfangen)

# 0 0 TODO: owned land doch schon mitgeben?
#           heatmap, nicht 2 koordinaten ausgeben!(?)
#0) FIRST THING TO EXCHANGE: internal state needs to be trained separatedly!

#1) learn valid moves
#2) learn basic objectives: wood->cutter around/ wood -> sawmill -> plank/ barack extends
#3) learn strategies: all needs planks -> need pipeline/  -> find all wood + reach all area = top score
#4) elements should be exchangeable -> don't want to retrain everything just cuz i changed a building

#5) in my mind, i already have a map/target state, that gets refined every now and then.
#       so have a network learning that one, and then one ordering the needed moves.

# HANDCRAFTED EXPERT MODELS PERFORM WORSE!
# NEED AN EVOLUTIONARY ALGORITHM UNDERNEATH THAT CONSTRUCT AND FINDS ITS PATH
#
# First try one network!
# Later: one network per move and one per strategy and find a path thru the networks "compiling" a move.
#            get much more efficient!
#
#
# INPUT:
# - current state - complete
# - last 15 states - encoded    << should be lstm lateron?
# OUTPUT:
# - code
# - current move decision       << one hot or not?

#TODO: try an all-in-one-model and all-split-model as well!


#First: train for games that last only 150 ticks. should resolve in some ai (that doesnt abort immediate :D)
#LATER: let them battle against each other


# learn each valid move
# - eg construction works only within range, delete only on buildings
# - woodcutter only produces wood if around wood, sawmill only planks if wood available
# - carrier needs to be there
# - need to expand area
# - "more planks" -> "need sawmill, but also more wood"
# - detect areas on map to be used eventually, eg with wood etc

"""
def prediction_to_coords(preds):
    coords = preds*10
    cell = (int(min(round(abs(coords[0]), -1) / 10, 49)), int(min(round(abs(coords[1]), -1) / 10, 49)))
    return cell
"""



#TODO: construction needs to be more clear
# # # # -> currently it can be forgotten what building is being constructed (?)
# # # #    unless mystical hidden state keeps it
def state_representation(state):
    #state.owned_terrain, can be inherited from map
    #state.buildings, # can be inherited from occupation map
    # TODO: include demand on carrier and wood/sawmill
    # TODO: later include productivity of buildings
    # TODO: later include history of states/ lstm?