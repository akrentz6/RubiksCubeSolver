import rubikscube as rc

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import keras.models
import matplotlib.pyplot as plt
import numpy as np
import sys

colours = ["O", "G", "W", "B", "Y", "R"]

cubes = 100
percent = cubes // 100
ranges = [1, 11]

if __name__ == "__main__":

    model = keras.models.load_model("model")
    model.summary()
    
    accuracy = []

    for depth in range(*ranges):

        print(f"Testing at depth: {depth}\n0%")
        
        solved_count = 0

        for i in range(cubes):

            cube = rc.Cube()
            cube.randomise(depth)

            copy_solved = False

            for j in range(-1, 18):

                if copy_solved:
                    break

                copy = cube.copy()

                if j != -1:
                    copy.parse_int_move(j)

                for _ in range(20):

                    inp = np.array(copy.hot_encode()).reshape(1, 1, 288)
                    m = model.predict(inp)
                    
                    move = np.argmax(m)
                    copy.parse_int_move(move)

                    if copy.is_solved():

                        solved_count += 1
                        copy_solved = True
                        break
            
            if not (i + 1) % percent and i:
                sys.stdout.write("\033[F")
                print(f"{(i + 1) // percent}%")

        accuracy.append(solved_count / cubes * 100)
        
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[F")
        print(f"Depth: {depth:2.0f} | Solved: {solved_count:4.0f} | Accuracy: {(solved_count / cubes * 100):6.2f}%")
    
    plt.title("Rubiks Cube Solver")
    plt.xlabel("Depth")
    plt.ylabel("Accuracy")

    plt.ylim((0, 100))
    plt.xlim((1, depth))

    plt.plot(list(range(*ranges)), accuracy)
    plt.savefig('accuracy.pdf')
    plt.show()