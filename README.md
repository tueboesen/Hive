# Hive Neural network

This project is my attempt at coding up a simple neural network trained to play [hive](https://boardgamegeek.com/boardgame/2655/hive)

## Structure

Representation of pieces:

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
