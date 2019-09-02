"""
Aidan Redding - a1706124

Implementation of the A* algorithm in a CLI interface.
"""
import sys
import argparse
from os.path import exists
from collections import namedtuple


# Convenience data-type to hold cartesian coordinates
Vector2 = namedtuple("Vector2", ["x", "y"])


# Convenience function for displaying an error message without traceback and exiting with an error code
def err(msg):
    print(msg)
    sys.exit(1)


class PriorityQueue(object):
    """
    Could use queue.PriorityQueue, but where's the fun in that?
    Priority is ordered lowest first.
    """
    def __init__(self):
        self.data = []

    def empty(self):
        """
        Checks if the priority queue is empty.
        """
        if self.data:
            return False

        return True

    def put(self, data, priority):
        """
        Add value with associated priority to queue.
        """
        self.data.append((priority, data))

    def pop(self):
        if self.empty():
            return None

        # Sort the data in ascending order by priority
        self.data.sort(key=lambda x: x[0])

        # Return the item with the lowest priority number
        return self.data.pop(0)[1]


class World(object):
    def __init__(self, environment_data):
        # Split world data into a list of rows (where each row is a list of 1s and 0s)
        self.data = [row.split() for row in environment_data]

        self.width = len(self.data[0])
        self.height = len(self.data)

    def point_inside(self, the_point: Vector2):
        """
        If the point is within the dimensions of the world, return True otherwise False
        """
        if (0 <= the_point.x < self.width) and (0 <= the_point.y < self.height):
            return True

        return False

    def __getitem__(self, key):
        """
        If key is a tuple/Vector2 it selects a point, otherwise it selects a row.
        """
        try:
            x, y = key

        except TypeError:
            return self.data[key]

        else:
            return self.data[y][x]

    def is_empty(self, the_point: Vector2):
        """
        If the specified point contains a wall, returns False otherwise True.
        """
        if self[the_point] == "0":
            return True

        return False

    def neighbours(self, the_point: Vector2):
        """
        Find the points adjacent to the specified point.
        """
        the_neighbours = []

        potential = (Vector2(the_point.x-1, the_point.y), Vector2(the_point.x+1, the_point.y),
                     Vector2(the_point.x, the_point.y+1), Vector2(the_point.x, the_point.y-1))

        for neighbour in potential:
            if self.point_inside(neighbour):
                if self.is_empty(neighbour):
                    the_neighbours.append(neighbour)

        return the_neighbours


# Define the heuristic method to be used in the A* algorithm
def cartesian_distance(pos1: Vector2, pos2: Vector2):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def a_star(the_start, the_end, the_world):
    looking_at = PriorityQueue()
    looking_at.put(the_start, 0)

    parent = {the_start: None}
    cost = {the_start: 0}

    while not looking_at.empty():
        current = looking_at.pop()

        # Check if destination has been reached
        if current == the_end:
            break

        # Loop through valid neighbour cells and calculate their costs
        for new_point in the_world.neighbours(current):
            new_cost = cost[current] + 1
            if new_point not in cost or new_cost < cost[new_point]:
                cost[new_point] = new_cost
                # The priority is the sum of cost and distance from this point to the destination,
                # where the higher the value the lower the priority
                priority = new_cost + cartesian_distance(the_end, new_point)
                looking_at.put(new_point, priority)

                # Update the dictionary of parents to include the new point
                parent[new_point] = current

    the_point = the_end
    the_path = [the_end]

    try:
        # Follow the calculated path backwards
        while the_point != the_start:
            the_point = parent[the_point]
            the_path.append(the_point)

    except KeyError:
        err("No path could be found.")

    the_path.reverse()

    return the_path


def graphical_route(the_world, the_path):
    """
    Display route from start to end with ascii graphics.
    """
    print("""
Key:
@ - Origin
$ - Destination
X - Wall
o - Path
. - Empty space
""")

    to_display = ""
    for y in range(the_world.height):
        for x in range(the_world.width):
            the_point = Vector2(x, y)
            if the_point == the_path[0]:
                to_display += "@"

            elif the_point == the_path[-1]:
                to_display += "$"

            elif the_point in the_path:
                to_display += "o"

            elif the_world[x, y] == "1":
                to_display += "X"

            else:
                to_display += "."

        to_display += "\n"

    print(to_display, end="")


if __name__ == "__main__":
    # Add command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Uses A* algorithm to find path from origin to destination in the given environment.")

    parser.add_argument("--graphics", "-g", action="store_true", default=False, dest="graphics_enabled",
                        help="Enable graphical output.")
    parser.add_argument("filepath", action="store", help="The path to the input file")
    parser.add_argument("origin_x", action="store", type=int,
                        help="The origin x coordinate as an integer")
    parser.add_argument("origin_y", action="store", type=int,
                        help="The origin y coordinate as an integer")
    parser.add_argument("destination_x", action="store", type=int,
                        help="The destination x coordinate as an integer")
    parser.add_argument("destination_y", action="store", type=int,
                        help="The destination y coordinate as an integer")
    the_args = parser.parse_args()

    GRAPHICAL_ROUTE = the_args.graphics_enabled

    env_file = the_args.filepath
    if not exists(env_file):
        err("Specified environment file does not exist.")

    # Read in environment file as a list of lines
    with open(env_file, "r") as f:
        env_data = f.readlines()

    # Extract width and height from file
    env_size = env_data[0].split()
    env_size = (int(env_size[0]), int(env_size[1]))

    # Trim the data of the width/height line
    env_data = env_data[1:]

    world = World(env_data)

    start = Vector2(the_args.origin_x, the_args.origin_y)
    if not world.point_inside(start):
        err("Starting coordinates are out of world.")

    end = Vector2(the_args.destination_x, the_args.destination_y)
    if not world.point_inside(end):
        err("Ending coordinates are out of the world.")

    # Check that start and end points aren't on walls
    if not world.is_empty(start):
        err("Starting point is on a non-empty space.")

    if not world.is_empty(end):
        err("Ending point is on a non-empty space.")

    # Calculate route
    path = a_star(start, end, world)

    # If graphical display is enabled, display ascii art otherwise go through the route and output directional commands
    if GRAPHICAL_ROUTE:
        graphical_route(world, path)

    else:
        prev_point = None
        displayed = False
        for point in path:
            if prev_point is not None:
                if displayed:
                    to_print = " "
                else:
                    to_print = ""
                    displayed = True

                if point.x > prev_point.x:
                    to_print += "R"

                elif point.x < prev_point.x:
                    to_print += "L"

                elif point.y > prev_point.y:
                    to_print += "D"

                else:
                    to_print += "U"
                print(to_print, end="")

            prev_point = point

        print()
