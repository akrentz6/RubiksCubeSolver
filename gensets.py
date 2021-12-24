import rubikscube as rc

import numpy as np
import os
import random
import sys
import time

sets_dir = "datasets"
sets = {
    "train": [1_000_000 for _ in range(20)],
    "valid": [50_000],
    "test": [100_000]
}

r = (1, 10)
sol_base = np.eye(18)

if __name__ == "__main__":

    start = time.time()
    time_taken = 0
    total_sets = 0

    if not os.path.exists(sets_dir):
        os.makedirs(sets_dir)

    for dtype, sizes in sets.items():

        for i, size in enumerate(sizes):

            file = os.path.join(sets_dir, dtype + str(i) + ".npz")
            percent = size // 100

            print(f"Generating {file} data\n0%")

            t = time.time()

            cubes = np.empty((size, 1, 288), dtype=np.uint8)
            sols = np.empty((size, 18), dtype=np.uint8)

            for j in range(size):
                
                cube = rc.Cube()

                d = random.randint(*r)
                sols[j] = sol_base[cube.randomise(d)]
                cubes[j] = np.array(cube.hot_encode()).reshape(1, 288)

                if not (j + 1) % percent and j:
                    sys.stdout.write("\033[F")
                    print(f"{(j + 1) // percent}%")
            
            gen_taken = time.time()
            time_taken += gen_taken - t
            total_sets += size
            
            np.savez(file, cubes = cubes, sols = sols)
            
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[F")

            padding = ""
            if i < 10:
                padding += " "

            print(f"File: {padding}{file} | Gen Data Time: {(gen_taken - t):0.2f}s | Save Data Time: {(time.time() - gen_taken):0.2f}s")
    
    print(f"\nTotal Time Taken: {time.time() - start}s | Average Time Per Cube: {(time_taken / total_sets * 1_000_000):.3f}μs")

    input()
