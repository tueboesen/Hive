# Hive Neural network

This project is my attempt at coding up a simple neural network trained to play [hive](https://boardgamegeek.com/boardgame/2655/hive)

## Neural network symmetries
The game contains certain symmetries that the neural network should incorporate.

The nn should be 60 degree rotational invariant.
The nn should be translational invariant.
The nn should be permutation equivariant. 
The nn should be mirror invariant.

## Neural network structure
Overall the neural network should try to predict the best possible move in any given situation, and give an estimate of how likely it is to be winning the game.
There should be some markov tree decision incorporated somehow.

## Representation of pieces

### Queen
Features: Type
Moves: 6

### Beetle
Features: Type, Level
Moves: 6

### Grasshopper
Features: Type
Moves: 6

### Spider
Features: Type
Moves: All places within 3 spaces = 37

### Ant
Features: Type
Moves: 6 moves around each other piece = 21*6=126
