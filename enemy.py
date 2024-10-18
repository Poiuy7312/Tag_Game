from typing import Tuple, Set, List
import random
import heapq
import os
from pathlib import Path


class Node:
    def __init__(self, position, parent, g=0, h=0):
        self.position = position  # (x, y) coordinates of the node
        self.g = g  # Cost from the start node to this node
        self.h = h  # Heuristic cost from this node to the goal
        self.f = g + h  # Total cost (g + h)
        self.parent = parent  # Pointer to the parent node for path reconstruction

    def __lt__(self, other):
        # Comparison method for priority queue to sort nodes by f cost
        return self.f < other.f


class enemy:
    def __init__(self, location: Tuple[int]):
        self.location = location  # Current location of the enemy
        self.filename = "enemy_path.txt"  # File to save enemy path

    def distance_from_player(self, state: Tuple[int], goal: Tuple[int]):
        # Calculate Manhattan distance from the current state to the goal
        distance = abs(goal[0] - state[0]) + abs(goal[1] - state[1])
        return distance

    def possible_moves(self, location, obstacles: set) -> Set[Tuple[int]]:
        # Generate possible moves from the current location, avoiding obstacles
        moves = set()
        if self.location[0] > 0:
            moves.add((location[0] - 1, location[1]))  # Move left
        if self.location[0] < 40:
            moves.add((location[0] + 1, location[1]))  # Move right
        if self.location[1] > 0:
            moves.add((location[0], location[1] - 1))  # Move down
        if self.location[1] < 40:
            moves.add((location[0], location[1] + 1))  # Move up
        return moves.difference(
            obstacles
        )  # Return valid moves not blocked by obstacles

    def predict_player_destination(
        self, player_location, distance: int, direction: str
    ) -> Tuple[int, int]:
        # Predict the player's future position based on their direction and distance
        if direction == "Up" and player_location[0] - distance > 0:
            predicted_location = (player_location[0] - distance, player_location[1])
        elif direction == "Down" and player_location[0] + distance < 40:
            predicted_location = (player_location[0] + distance, player_location[1])
        elif direction == "Left" and player_location[1] - distance > 0:
            predicted_location = (player_location[0], player_location[1] - distance)
        elif direction == "Right" and player_location[1] + distance < 40:
            predicted_location = (player_location[0], player_location[1] + distance)
        else:
            return player_location  # If the predicted location is out of bounds, stay in place
        return predicted_location

    def reconstruct_path(self, node: Node) -> list:
        """Reconstruct the path from the goal node back to the start."""
        path = []
        while node:
            path.append(node.position)  # Add the current node's position to the path
            node = node.parent  # Move to the parent node
        return path  # Return the path in the order from start to goal

    def add_to_open(self, open_list: List[Node], node: Node):
        """Determine if a node should be added to the open list based on cost."""
        for open_node in open_list:
            if node.position == open_node.position and node.g >= open_node.g:
                return False  # Do not add if it's not a better path
        return True  # Node is better; add to open list

    def pathfinder(
        self, obstacles, start: Tuple[int], goal: Tuple[int]
    ) -> Tuple[int, int]:
        # A* pathfinding algorithm to find the best path from start to goal
        if not Path(self.filename).exists() or Path(self.filename).stat().st_size == 0:
            open_list = []  # List of nodes to explore
            closed_list = set()  # Set of explored nodes
            start_node = Node(start, None, 0, self.distance_from_player(start, goal))
            heapq.heappush(open_list, start_node)  # Add the start node to the open list

            while open_list:
                current_node = heapq.heappop(
                    open_list
                )  # Get the node with the lowest f cost
                if current_node.position == goal:
                    path = self.reconstruct_path(
                        current_node
                    )  # Reconstruct path if goal is reached
                    with open(self.filename, "w") as fh:
                        for p in path:
                            fh.write(f"{p}\n")  # Write path to file
                    break

                closed_list.add(
                    current_node.position
                )  # Mark the current node as explored
                neighbors = self.possible_moves(
                    current_node.position, obstacles
                )  # Get valid neighbors
                for next_position in neighbors:
                    if next_position in closed_list:
                        continue  # Skip if the neighbor has already been explored
                    assert (
                        next_position not in closed_list
                    )  # Ensure neighbor is not in closed list
                    g_cost = current_node.g + 1  # Increment cost from the start
                    h_cost = self.distance_from_player(
                        next_position, goal
                    )  # Heuristic cost
                    next_node = Node(next_position, current_node, g_cost, h_cost)

                    if self.add_to_open(open_list, next_node):
                        heapq.heappush(
                            open_list, next_node
                        )  # Add to open list if it's a better path

        # Read the last path from the file to determine the next move
        with open(self.filename, "r") as fh:
            results = fh.readlines()
            if results:
                last_path = results.pop().strip()  # Get last path
                x, y = map(int, last_path.strip("()").split(", "))  # Parse coordinates
        with open(self.filename, "w") as fh:
            fh.writelines(results)  # Write remaining paths back to file

        r = (x, y)  # Return the last position
        return r

    def move(
        self,
        player_location: Tuple[int],
        player_direction: str,
        obstacles: set,
        moving: bool,
    ):
        # Determine the enemy's movement based on player location and direction
        best_moves = set()  # Moves that bring the enemy closer to the player
        bad_moves = set()  # Moves that take the enemy away from the player
        state = self.location  # Current enemy position
        current_distance = self.distance_from_player(
            state, player_location
        )  # Distance to the player
        goal = player_location  # Set goal to player's current location

        # Predict the player's future position if they are moving
        if current_distance < 10 and current_distance > 2 and moving:
            goal = self.predict_player_destination(
                player_location, current_distance, player_direction
            )

        moves = self.possible_moves(self.location, obstacles)  # Get possible moves
        if self.location != goal:  # If the enemy is not at the goal
            for move in moves:
                new_dist = self.distance_from_player(
                    move, goal
                )  # Calculate new distance to goal
                if new_dist < current_distance:
                    current_distance = new_dist  # Update current distance if closer
                    best_moves.add(move)  # Add to best moves
                else:
                    bad_moves.add(move)  # Add to bad moves

            # Choose the best move if available
            if best_moves and moving:
                self.location = random.choice(list(best_moves))  # Move to a best move
                if os.path.exists(self.filename):
                    os.remove(self.filename)  # Remove path file
            elif moving:
                self.location = random.choice(
                    list(bad_moves)
                )  # Move to a random bad move if no best options
                if os.path.exists(self.filename):
                    os.remove(self.filename)  # Remove path file
            else:
                # If not moving, use pathfinding to determine the next position
                _loc = self.pathfinder(obstacles, self.location, goal)
                if _loc:
                    self.location = _loc  # Update location to pathfinding result
