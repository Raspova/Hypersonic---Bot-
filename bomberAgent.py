import sys
import math

# WEIGHT
BOX_POS_W = -1000
WALL_POS_W = -1500
BOMB_THREAT = -2000 #ALL ABOVE COULD BE OBSTACLE_W = -2000 ;BUT FOR READABILITY  ... 
BOX_ATTRACTION_W = 100
BONNUS_W = 600
DISTANCE_W = 1
DISTANCE_B_W = 1
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
        def __init__(self, x , y , order, weight, print_Addon = ""):
            self.x = x
            self.y = y
            self.order = order
            self.weight = weight
            self.print = print_Addon

        def print_order(self):
            print( ("->> MOVE " if self.order == MOVE else "BOMB ") + str(self.x) + " " + str(self.y) + " " + self.print + '<', flush=True, file=sys.stderr)
            
        def __str__(self):
            return str(self.x) + " " + str(self.y) + " " + str(self.order)

        def __repr__(self):
            return str(self.x) + " " + str(self.y) + " " + str(self.order)

        def __eq__(self, other):
            return self.x == other.x and self.y == other.y and self.order == other.order

        def execute(self, x_player, y_player):
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
                    for _x in range(x + 1, x + self.range + 1) : # right
                        if _x >= self.map_w or (self.map[y][_x] != FREE and self.map[y][_x] != 'P'):
                            if _x < self.map_w and self.map[y][_x] in BOX :
                                ret[y][_x] = value
                            break
                        ret[y][_x] = value
                    for _x in range(x - 1, x - self.range - 1, -1) : # left
                        if _x < 0 or (self.map[y][_x] != FREE and self.map[y][_x] != 'P'): 
                            if _x >= 0 and self.map[y][_x] in BOX :
                                ret[y][_x] = value
                            break
                        ret[y][_x] = value
                    for _y in range(y + 1, y + self.range + 1) : # down
                        if _y >= self.map_h or (self.map[_y][x] != FREE and self.map[_y][x] != 'P'):
                            if _y < self.map_h and self.map[_y][x] in BOX :
                                ret[_y][x] = value
                            break
                        ret[_y][x] = value
                    for _y in range(y - 1, y - self.range - 1, -1) : # up
                        if _y < 0 or (self.map[_y][x] != FREE and self.map[_y][x] != 'P'): 
                            if _y >= 0 and self.map[_y][x] in BOX :
                                ret[_y][x] = value
                            break
                        ret[_y][x] = value
        return ret

    def update_info(self):
        self.bonnus_pos = []
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
                self.range = param_2 - 1 
                if (owner == self.my_id):
                    self.map[y][x] = 'P'
                else :
                    self.map[y][x] = 'E'
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
                        if _x >= self.map_w or buff_map[y][_x] in BOX or buff_map[y][_x] == WALL:
                            break
                        self.bombing_weighted_map[y][_x] += BOX_ATTRACTION_W
                    for _x in range(x - 1, x - self.range - 1, -1) : # left
                        if _x < 0 or buff_map[y][_x] in BOX or buff_map[y][_x] == WALL:
                            break
                        self.bombing_weighted_map[y][_x] += BOX_ATTRACTION_W
                    for _y in range(y + 1, y + self.range + 1) : # down
                        if _y >= self.map_h or buff_map[_y][x] in BOX or buff_map[_y][x] == WALL:
                            break
                        self.bombing_weighted_map[_y][x] += BOX_ATTRACTION_W
                    for _y in range(y - 1, y - self.range - 1, -1) : # up
                        if _y < 0 or buff_map[_y][x] in BOX or buff_map[_y][x] == WALL:
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
        #print 
        for y in range(self.map_h):
            for x in range(len(self.map[y])):
                if (self.map[y][x] != 'P'):
                    print("{:^5}".format(self.bombing_weighted_map[y][x]), file=sys.stderr, flush=False, end='|')
                else:
                    print("{:^5}".format("P"), file=sys.stderr, flush=False, end='|')
            print(file=sys.stderr, flush=True)

    def find_best_move(self)-> Order : 
        #if (self.best_moves != []) : 
        #    if (self.my_player_pos() == self.best_moves[0]):
        #        return self.best_moves.pop(0)
        #    else :
        #        return self.best_moves[0]
        max_weight = -1000
        best_move =  Order(-1, -1, MOVE, -1) # check that 
        x_p, y_p = self.my_player_pos()
        reachable =  self.find_all_reachable_cells(self.make_matrix_from_map(), x_p, y_p)
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
            # print("-----------------", file=sys.stderr, flush=True )
            # for y in range(self.map_h):
            #     for x in range(len(self.map[y])):
            #         print(reachable_with_bomb[y][x], file=sys.stderr, flush=False, end='')
            #     print("", file=sys.stderr, flush=False )
            # print("-----------------", file=sys.stderr, flush=True )
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
            #print("-----------------", file=sys.stderr, flush=True )
            #for y in range(self.map_h):
            #    for x in range(len(self.map[y])):
            #        print(reachable_with_bomb[y][x], file=sys.stderr, flush=False, end='')
            #    print("", file=sys.stderr, flush=False )
            ##reachable_with_bomb = self.find_all_reachable_cells(reachable_with_bomb,)  x_p, y_p
            for y in range(self.map_h):
                for x in range(self.map_w):
                    if (reachable_with_bomb[y][x] == 0 and ((abs(y_b - y) + abs(x_b - x)) < dist)):
                        dist = abs(y_b - y) + abs(x_b - x) 
                        best_move =  Order(x, y, MOVE, dist, print_Addon="SAVE LIFE")
                        #best_move.print_order()
            #print("-----------------", file=sys.stderr, flush=True )
            return best_move
     
            #if (best_move.x == -1):
            #    best_move = last_chance(x_b + 1, y_b, best_move)
            #    if best_move.x != -1:
            #        return best_move
            #    best_move = last_chance(x_b - 1, y_b, best_move)
            #    if best_move.x != -1:
            #        return best_move
            #    best_move = last_chance(x_b , y_b  + 1, best_move)
            #    if best_move.x != -1:
            #        return best_move
            #    best_move = last_chance(x_b , y_b - 1, best_move)
            #    if best_move.x != -1:
            #        return best_move
            #else :
            #    return best_move
        dist = 1000
        
        if (best_move.weight < 0 or best_move.x == -1):
            best_move = last_chance(x_p, y_p)
        if (best_move.x == -1):
            for y in range(self.map_h):
                for x in range(self.map_w):
                    buffer_move = last_chance(x, y)
                    print("Dist " + str( abs(y_p - y) + abs(x_p - x)) + " x:" + buffer_move.x, file=sys.stderr, flush=True)
                    if buffer_move.x != -1 and ((abs(y_p - y) + abs(x_p - x)) < dist) :
                        dist = abs(y_p - y) + abs(x_p - x)
                        best_move = Order(buffer_move.x, buffer_move.y, MOVE, dist, print_Addon="SAVE LIFE")
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
        # print("-----------------", file=sys.stderr, flush=True )
        # for y in range(self.map_h):
        #     for x in range(len(self.map[y])):
        #         print(matrix[y][x], file=sys.stderr, flush=False, end='')
        #     print("", file=sys.stderr, flush=False )
        # print("-----------------", file=sys.stderr, flush=True )
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
        # print("-----------------", file=sys.stderr, flush=True )
        # for y in range(self.map_h):
            # for x in range(len(self.map[y])):
                # print(reachable[y][x], file=sys.stderr, flush=False, end='')
            # print("", file=sys.stderr, flush=False )
        # print("-----------------", file=sys.stderr, flush=True )
        return reachable
    
    def update(self):
        self.update_info()
        self.create_weigth_map()
        order  = self.find_best_move()
        x ,y = self.my_player_pos()
        order.execute(x, y)
        self.print_map()
        
        
        
width, height, my_id = [int(i) for i in input().split()]
agent = Agent(width, height, my_id)
print(("Move 0 0"))

while True:
    agent.update()
        