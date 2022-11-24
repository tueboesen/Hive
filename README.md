# Hive Neural network

This project is my attempt at coding up a simple neural network trained to play [hive](https://boardgamegeek.com/boardgame/2655/hive)

## Neural network symmetries
The game contains certain symmetries that the neural network should incorporate.

- The nn should be 60 degree rotational invariant.
- The nn should be translational invariant.
- The nn should be permutation equivariant. 
- The nn should be mirror invariant.

## Neural network structure
Overall the neural network should try to predict the best possible move in any given situation, and give an estimate of how likely it is to be winning the game.
There should be some markov tree decision incorporated somehow.

## Representation of pieces

### Queen
Input = (x,y,Type,InPlay) 

Output moves = (6)

### Beetle
Input = (x,y,Type,InPlay,Level) 

Output moves = (6)

### Grasshopper
Input = (x,y,Type,InPlay) 

Output moves = (6)

### Spider
Input = (x,y,Type,InPlay) 

Output moves = (All places within 3 spaces = 37)

### Ant
Input = (x,y,Type,InPlay) 

Output moves = (6 moves around each other piece = 21*6=126)
