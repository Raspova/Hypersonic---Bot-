import sys
import math
from collections import deque

# WEIGHT
BOX_POS_W = -1000
WALL_POS_W = -1500
BOMB_THREAT = -2000 #ALL ABOVE COULD BE OBSTACLE_W = -2000 ;BUT FOR READABILITY  ... 
BOX_ATTRACTION_W = 100
BONNUS_W = 600
DISTANCE_W = 1
DISTANCE_B_W = 1
INSTANT_BOMB_WEIGHT = 196
# ORDER TYPE
MOVE = 0
BOMB = 1
# Entities Type 
PLAYER = 0
BOMB = 1 
ITEM = 2
# Entities Map Char
WALL = 'X'
BOX = "012"
BOMB_ = "AB"
FREE = '.'

def my_print(_str):
    print(_str, file=sys.stderr)
    

class Player_info():
    def __init__(self, id, x, y, nb_bombs, bomb_reach):
        self.id = id
        self.x = x
        self.y = y
        self.nb_bombs = nb_bombs
        self.bomb_reach = bomb_reach

    def update_info(self, x, y, nb_bombs, bomb_reach):
        self.x = x
        self.y = y
        self.nb_bombs = nb_bombs
        self.bomb_reach = bomb_reach - 1 # range fucked up 
        
class Bomb_info():
    def __init__(self, id, x, y, timer, bomb_reach):
        self.id = id
        self.x = x
        self.y = y
        self.timer = timer
        self.bomb_reach = bomb_reach

class Order:
        def __init__(self, x , y , order, weight, print_Addon = "", n_x  = 0, n_y = 0):
            self.x = x
            self.y = y
            self.order = order
            self.weight = weight
            self.print = print_Addon
            self.next_x = n_x
            self.next_y = n_y

        def print_order(self):
            print( ("->> MOVE " if self.order == MOVE else "BOMB ") + str(self.x) + " " + str(self.y) + " " + self.print + '<', flush=True, file=sys.stderr)
            
        def __str__(self):
            return str(self.x) + " " + str(self.y) + " " + str(self.order)

        def __repr__(self):
            return str(self.x) + " " + str(self.y) + " " + str(self.order)

        def __eq__(self, other):
            return self.x == other.x and self.y == other.y and self.order == other.order

        def execute(self, x_player, y_player, xn = 0, yn = 0):
            if (self.order == MOVE):
                print("MOVE " + str(self.x) + " " + str(self.y) + " MOVE (" + str(self.x) + "," + str(self.y) + ") " + str(self.weight) + self.print)
            elif (self.order == BOMB):
                if (x_player == self.x and y_player == self.y):
                    print("BOMB " + str(self.x) + " " + str(self.y) + " BOOM (" + str(self.x) + "," + str(self.y) + ") " + str(self.weight) + self.print)
                else:
                    print("MOVE " + str(self.x) + " " + str(self.y) + " BOMB-> (" + str(self.x) + "," + str(self.y) + ") " + str(self.weight) + self.print)

class Agent:
    def __init__(self, map_w, map_h, my_id):
        self.players = []
        self.bombs = []
        self.map_w = map_w
        self.map_h = map_h
        self.my_id = my_id
        self.map = []
        #Dessision weighted map
        self.bombing_weighted_map = []
        self.bonnus_weighted_map = []
        # maybe later a pathfinding one 
        self.reachable_buffer =  [[1 for j in range(map_w)] for i in range(map_h)]
        self.range = -1
        self.best_moves = [] #(int , int)
        self.bonnus_pos = []
        self.turn = 0
        self.map_history = []
        self.matrix_reachable = []
        self.__init_info()
        
    
    
    def my_player(self)  :
        return self.players[self.my_id]

    def my_player_pos(self) :
        return self.my_player().x, self.my_player().y
    
    def __init_info(self):
        map = []
        for i in range(self.map_h):
            row = [*input()] # unpacking 
            map.append(row)
            self.bombing_weighted_map.append([0] * self.map_w)
        self.map = map
        entity_nbr = int(input())
        for i in range(entity_nbr):
            entity_type, owner, x, y, param_1, param_2 = [int(j) for j in input().split()]
            if entity_type == PLAYER : 
                if owner == self.my_id:
                    self.range = param_2 - 1 # -1 because the range is fuck up ;need to check that again       
                self.players.append(Player_info(owner, x, y, param_1, param_2))
            #elif entity_type == BOMB:
            #    self.bombs.append(Bomb_info(owner, x, y, param_1, param_2))
        self.players.sort(key=lambda x: x.id)

    
    
    def simulate_explosion(self, map, value, change_orignal_pos = True, x_theoretical = -1, y_theoretical = -1):
        ret = [[map[y][x] for x in range(self.map_w)] for y in range(self.map_h)]
        for y in range(self.map_h):
            for x in range(len(ret[y])):
                if self.map[y][x] in BOMB_ or (y == y_theoretical and x == x_theoretical):
                    if (change_orignal_pos):
                        ret[y][x] = value
                    if (x == x_theoretical and y == y_theoretical):
                        bomb_range = self.range
                    else : 
                        for b in self.bombs:
                            if b.x == x and b.y == y:
                                bomb_range = b.bomb_reach - 1
                                break
                    for _x in range(x + 1, x + bomb_range + 1) : # right
                        if _x >= self.map_w or (self.map[y][_x] != FREE and self.map[y][_x] != 'P'):
                            if _x < self.map_w and self.map[y][_x] in BOX :
                                ret[y][_x] = value
                            break
                        ret[y][_x] = value
                    for _x in range(x - 1, x - bomb_range - 1, -1) : # left
                        if _x < 0 or (self.map[y][_x] != FREE and self.map[y][_x] != 'P'): 
                            if _x >= 0 and self.map[y][_x] in BOX :
                                ret[y][_x] = value
                            break
                        ret[y][_x] = value
                    for _y in range(y + 1, y + bomb_range + 1) : # down
                        if _y >= self.map_h or (self.map[_y][x] != FREE and self.map[_y][x] != 'P'):
                            if _y < self.map_h and self.map[_y][x] in BOX :
                                ret[_y][x] = value
                            break
                        ret[_y][x] = value
                    for _y in range(y - 1, y - bomb_range - 1, -1) : # up
                        if _y < 0 or (self.map[_y][x] != FREE and self.map[_y][x] != 'P'): 
                            if _y >= 0 and self.map[_y][x] in BOX :
                                ret[_y][x] = value
                            break
                        ret[_y][x] = value
        return ret

    def update_info(self):
        self.bonnus_pos = []
        self.turn += 1
        for i in range(self.map_h):
            self.map[i] = [*input()] # unpacking 
        entity_nbr = int(input())
        for i in range(entity_nbr):
            entity_type, owner, x, y, param_1, param_2 = [int(j) for j in input().split()]
            if entity_type == BOMB:
                self.bombs.append(Bomb_info(owner, x, y, param_1, param_2))
                if owner == self.my_id :
                    self.map[y][x] = 'A'
                else :
                    self.map[y][x] = 'B'      
            elif entity_type == ITEM:
                self.bonnus_pos.append((x, y))
            if entity_type == PLAYER : 
                self.players[owner].update_info(x, y, param_1, param_2) # range update
                if (owner == self.my_id):
                    self.range = param_2 - 1 
                    self.map[y][x] = 'P'
                else :
                    self.map[y][x] = 'E'
        if (self.turn > 10):
            self.map_history.append([[self.map[y][x] for x in range(self.map_w)] for y in range(self.map_h)])


    def print_map(self):
        for y in range(self.map_h):
            for x in range(len(self.map[y])):
                print(self.map[y][x], file=sys.stderr, flush=False, end='')
            print(file=sys.stderr, flush=True)
    
    def create_weigth_map(self):
        for y in range(self.map_h):
            for x in range(len(self.map[y])):
                if self.map[y][x] in  BOX :
                    self.bombing_weighted_map[y][x] = BOX_POS_W
                elif self.map[y][x] == WALL :
                    self.bombing_weighted_map[y][x] = WALL_POS_W
                else :
                    self.bombing_weighted_map[y][x] = 0
        self.bonnus_weighted_map = [[(-100 if self.bombing_weighted_map[y][x] == 0 else self.bombing_weighted_map[y][x])
                                    for x in range(self.map_w)] for y in range(self.map_h)]
        # ADD THE BOX WEIGHT
        buff_map = self.simulate_explosion(self.map, FREE, False)
        for y in range(self.map_h):
            for x in range(len(self.map[y])):
                if buff_map[y][x] in BOX:
                    for _x in range(x + 1, x + self.range + 1) : # right
                        if _x >= self.map_w or buff_map[y][_x] in BOX or buff_map[y][_x] == WALL or (_x, y) in self.bonnus_pos:
                            break
                        self.bombing_weighted_map[y][_x] += BOX_ATTRACTION_W
                    for _x in range(x - 1, x - self.range - 1, -1) : # left
                        if _x < 0 or buff_map[y][_x] in BOX or buff_map[y][_x] == WALL or (_x, y) in self.bonnus_pos:
                            break
                        self.bombing_weighted_map[y][_x] += BOX_ATTRACTION_W
                    for _y in range(y + 1, y + self.range + 1) : # down
                        if _y >= self.map_h or buff_map[_y][x] in BOX or buff_map[_y][x] == WALL or (x, _y) in self.bonnus_pos:
                            break
                        self.bombing_weighted_map[_y][x] += BOX_ATTRACTION_W
                    for _y in range(y - 1, y - self.range - 1, -1) : # up
                        if _y < 0 or buff_map[_y][x] in BOX or buff_map[_y][x] == WALL or (x, _y) in self.bonnus_pos:
                            break
                        self.bombing_weighted_map[_y][x] += BOX_ATTRACTION_W
        # SUB BOMB WEIGHT -> SIMULATION OF EXPLOSION 
        self.bombing_weighted_map =  self.simulate_explosion(self.bombing_weighted_map, BOMB_THREAT)
        # SUB DISTANCE MATRIX 
        x, y = self.my_player_pos()
        for i in range(self.map_h):
            for j in range(self.map_w):
                if (self.map[i][j] == FREE):
                    dist = abs(i - y) + abs(j - x) 
                    self.bombing_weighted_map[i][j] -= dist * DISTANCE_W
        #SET BONNUS WEIGHT
        for x_b, y_b in self.bonnus_pos:  
            dist = abs(y_b - y) + abs(x_b - x) 
            self.bonnus_weighted_map[y_b][x_b] = max(BONNUS_W - (dist * DISTANCE_B_W * 100), 0) 
        
        # Create reachable map
        reachable = self.find_all_reachable_cells(self.make_matrix_from_map(), x, y)
        self.matrix_reachable = self.simulate_explosion(reachable, 1)    
        #print 
        for y in range(self.map_h):
            for x in range(len(self.map[y])):
                if (self.map[y][x] != 'P'):
                    print("{:^5}".format(self.bombing_weighted_map[y][x]), file=sys.stderr, flush=False, end='|')
                else:
                    print("{:^5}".format("P"), file=sys.stderr, flush=False, end='|')
            print(file=sys.stderr, flush=True)

    def find_best_move(self)-> Order : 
        max_weight = -1000
        best_move =  Order(-1, -1, MOVE, -1) # check that 
        x_p, y_p = self.my_player_pos()
        matrix = self.make_matrix_from_map()
        matrix = self.simulate_explosion(matrix, 1) # <- over type of matrix explosion before
        reachable =  self.find_all_reachable_cells(matrix , x_p, y_p)
           
        if (self.look_for_afk() and reachable[y_p][x_p] == 0):
            best_move =  Order(x_p, y_p, MOVE, 42, "AFK BITCH DETECTECK")
        elif (self.bombing_weighted_map[y_p][x_p] > INSTANT_BOMB_WEIGHT and reachable[y_p][x_p] == 0):
            best_move =  Order(x_p, y_p, BOMB, self.bombing_weighted_map[y_p][x_p])
        else :
            for y in range(self.map_h):
                for x in range(self.map_w):
                    if (self.bombing_weighted_map[y][x] > max_weight and reachable[y][x] == 0):
                        max_weight = self.bombing_weighted_map[y][x]
                        best_move =  Order(x, y, BOMB, max_weight)
                    if (self.bonnus_weighted_map[y][x] > max_weight and reachable[y][x] == 0):
                        max_weight = self.bonnus_weighted_map[y][x]
                        best_move =  Order(x, y, MOVE, max_weight, print_Addon=" BONNUS")
        if (best_move.order == BOMB):
            reachable_with_bomb = self.simulate_explosion(reachable, 1, True)#, best_move.x, best_move.y
            reachable_with_bomb = self.find_all_reachable_cells(reachable_with_bomb,  x_p, y_p)
            reachable_with_bomb = self.simulate_explosion(reachable_with_bomb, 1, True, best_move.x, best_move.y)
            if sum(row.count(0) for row in reachable_with_bomb) == 0: #BAN CELL 
                x, y =  best_move.x, best_move.y
                self.bombing_weighted_map[y][x] = -3000
                self.bonnus_weighted_map[y][x] = -3000
                return self.find_best_move()
 
        def last_chance(x_b, y_b):
            best_move =  Order(-1, -1, MOVE, -1)
            if (x_b < 0 or x_b >= self.map_w or y_b < 0 or y_b >= self.map_h or (self.map[y_b][x_b] != FREE)):
                return best_move 
            dist = 1000
            reachable = self.find_all_reachable_cells(self.make_matrix_from_map(), x_b, y_b)
            reachable_with_bomb = self.simulate_explosion(reachable, 1)
            for y in range(self.map_h):
                for x in range(self.map_w):
                    if (reachable_with_bomb[y][x] == 0 and ((abs(y_b - y) + abs(x_b - x)) < dist)):
                        dist = abs(y_b - y) + abs(x_b - x)
                        best_move =  Order(x, y, MOVE, dist + 1 , print_Addon="SAVE LIFE")
            return best_move

        dist = 1000
        if (best_move.weight < 0 or best_move.x == -1):
            best_move = last_chance(x_p, y_p)
        if (best_move.x == -1):
            for y in range(self.map_h):
                for x in range(self.map_w):
                    buffer_move = last_chance(x, y)
                    #print("Dist " + str( abs(y_p - y) + abs(x_p - x)) + " x:" + str(buffer_move.x), file=sys.stderr, flush=True)
                    if buffer_move.x != -1 and ((abs(y_p - y) + abs(x_p - x)) < dist) :
                        dist = abs(y_p - y) + abs(x_p - x)
                        best_move = Order(buffer_move.x, buffer_move.y, MOVE, dist, print_Addon="LAST EXIT LIFE")
                        best_move.print_order()
                        #print("->Dist " + str(dist), file=sys.stderr, flush=True)
        if (best_move.x == -1):
            my_print("FUCK IT  " + str(best_move))
            best_move = Order(x_p, y_p, MOVE, -1, " ERROR")
        return best_move

    # DEFT FIRST ALGO -> REACHABLE CELLS 
    def make_matrix_from_map(self):
        matrix =  [[0 for j in range(self.map_w)] for i in range(self.map_h)] # check tha dnf work whit bomb too
        for y in range(self.map_h):
            for x in range(self.map_w):
                if self.map[y][x] == FREE or  self.map[y][x] == 'P'  : #or self.map[y][x] == 'A'
                    matrix[y][x] = 0
                else :
                    matrix[y][x] = 1
        return matrix
    
    def find_all_reachable_cells(self, matrix, x , y):
        reachable = [[self.reachable_buffer[i][j] for j in range(self.map_w)] for i in range(self.map_h)] # check tha dnf work whit bomb too
        def dfs(i, j):
            if i < 0 or i >= self.map_h or j < 0 or j >= self.map_w or matrix[i][j] == 1:
                return
            reachable[i][j] = 0
            matrix[i][j] = 1 # mark as visited
            dfs(i + 1, j)
            dfs(i - 1, j)
            dfs(i, j + 1)
            dfs(i, j - 1)
        dfs(y, x)
        return reachable
    

    def shortest_path(self, target):
        start = self.my_player_pos()
        queue = deque([start])
        visited = set()
        distance = {start: 0}
        prev = {start: None}
        min_distance = float('inf')
        closest_cell = None

        while queue:
            x, y = queue.popleft()
            if (x, y) == target:
                return self.construct_path(prev, start, target)
            
            d = abs(x - target[0]) + abs(y - target[1])
            if d < min_distance:
                min_distance = d
                closest_cell = (x,y)            
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.map_w and 0 <= new_y < self.map_h and self.matrix_reachable[new_y][new_x] == 0 and (new_x,new_y) not in visited:
                    visited.add((new_x,new_y))
                    queue.append((new_x,new_y))
                    distance[(new_x,new_y)] = distance[(x,y)] + 1
                    prev[(new_x,new_y)] = (x,y)
        return self.construct_path(prev, start, closest_cell)
    
    def construct_path(self, prev, start, target):
        path = []
        while target != start:
            path.append(target)
            target = prev[target]
        path.append(start)
        return path[::-1]

    
    def look_for_afk(self):
        if len(self.map_history) < 10:
            return False
        if sum(row.count('E') for row in self.map) == 0:
            return False
        e_positions = []
        for i in range(-1, -11, -1):
            current_map = self.map_history[i]
            current_e_positions = set()
            for row in range(len(current_map)):
                for col in range(len(current_map[row])):
                    if current_map[row][col] == 'E':
                        current_e_positions.add((row, col))
            if not current_e_positions:
                return False
            e_positions.append(current_e_positions)
        for i in range(len(e_positions)-1):
            if e_positions[i] != e_positions[i+1]:
                return False
        return True

    def better_path_findin(self, target):
        return True #TODO
                    
    
    def update(self):
        self.update_info()
        self.create_weigth_map()
        order  = self.find_best_move()
        x ,y = self.my_player_pos()
        if (order.order == BOMB and x  == order.x and y == order.y):
            print("BOMB ",x, y) # CHANGE That
              #    for i in range(4):
            #        if [up, down, left, right][i] == 0:
            #            
            #            print("BOMB ",x, y)
            #            break   
            
        else:
            route = self.shortest_path((order.x, order.y))
            print("->Route " + str(route), file=sys.stderr, flush=True)
            if len(route) > 1:
                x_,y_ = route[1]
                print(("Move " + str(x_) + " " + str(y_)) + " " + order.print)
            else:
                  # print(("Move " + str(x_) + " " + str(y_)) + " STAY;" + order.print)
                if self.matrix_reachable[y][x] == 0:
                    print(("Move " + str(x) + " " + str(y)) + " STAY;" + order.print)
                else:
                    order.execute(x, y) # hazardous behaviour <-
            
        self.print_map()
        
        
        
width, height, my_id = [int(i) for i in input().split()]
agent = Agent(width, height, my_id)
print(("Move 0 0"))

while True:
    agent.update()
        