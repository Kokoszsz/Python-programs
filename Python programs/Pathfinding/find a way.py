import pygame
import random
pygame.font.init()


## setting up window size (can be modified)
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Pathfinding')

## declaring colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
ORANGE = (255,128,0)

MY_FONT = pygame.font.SysFont("monospace", 12)

FPS = 60

## higher the number, program is slower
SPEED = 12 

ALL_COLORS = [] 

## size of rect
BLOCK_SIZE = 15

BOTTOM_PANEL_HEIGHT = 200

### number of rows and collumns
ROWS = (HEIGHT - BOTTOM_PANEL_HEIGHT)//BLOCK_SIZE
COLS = (WIDTH)//BLOCK_SIZE
BG_COLOR = (WHITE)

OPTION_RECT_SIZE = 50


IMPASSABLE_BLOCK_PROPABILITY = 35   #%


BLOCK_COLORS = [BLACK, WHITE]



## blocks used for changing colors
class ColorBlock:
    def __init__(self,x,y,color):
        self.color = color
        self.pos_x = x
        self.pos_y = y
        self.color_block = pygame.Rect(self.pos_x, self.pos_y, OPTION_RECT_SIZE, OPTION_RECT_SIZE)


## blocks that would be traversed during path search
class Node:
    def __init__(self, position, current_cost, parent, estimate_distance):
        self.position = position
        self.current_cost = current_cost
        self.parent = parent
        self.estimate_distance = estimate_distance

    def __str__(self) -> str:
        return f"position: {self.position[0]}, {self.position[1]} cost: {self.current_cost} parent: {self.parent} estimate_distance: {self.estimate_distance}"


## draws bord
def draw_window(all_colors, grid, random_block, clear_block, erease_block, proper_way):


    screen.fill(WHITE)
    for colors in all_colors:
        pygame.draw.rect(screen, colors.color, colors.color_block)
        pygame.draw.rect(screen, BLACK, colors.color_block, 2)

    pygame.draw.rect(screen, BLACK, random_block, 2)
    text_random = MY_FONT.render('random', 1, (0, 0, 0,))
    screen.blit(text_random, (OPTION_RECT_SIZE + 3, (HEIGHT - BOTTOM_PANEL_HEIGHT//2) + OPTION_RECT_SIZE//3))

    pygame.draw.rect(screen, BLACK, clear_block, 2)
    text_clear_path = MY_FONT.render('clear', 1, (0, 0, 0,))
    screen.blit(text_clear_path, (OPTION_RECT_SIZE*2.5 + 7, (HEIGHT - BOTTOM_PANEL_HEIGHT//2) + OPTION_RECT_SIZE//3))

    pygame.draw.rect(screen, BLACK, erease_block, 2)
    text_erase = MY_FONT.render('erase', 1, (0, 0, 0,))
    screen.blit(text_erase, (OPTION_RECT_SIZE*4 + 7, (HEIGHT - BOTTOM_PANEL_HEIGHT//2) + OPTION_RECT_SIZE//3))
    
    for i, row in enumerate(grid):
        for j, pixel in enumerate(row):
            pygame.draw.rect(screen, pixel, (j*BLOCK_SIZE,i*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))

    for i in range(ROWS+1):
         pygame.draw.line(screen, BLACK, (0,i*BLOCK_SIZE), (COLS * BLOCK_SIZE,i*BLOCK_SIZE), width=1)  ### if you want lines

    for i in range(COLS):
        pygame.draw.line(screen, BLACK, (i*BLOCK_SIZE,0), (i*BLOCK_SIZE,ROWS * BLOCK_SIZE), width=1)  ### if you want lines

    if proper_way == None:
        this_font = pygame.font.SysFont("arialblack", 25)
        text_clear = this_font.render('NO WAY TO GET TO THIS POINT', 1, (0, 0, 0,))                          
        screen.blit(text_clear, (WIDTH//3, (HEIGHT - BOTTOM_PANEL_HEIGHT//2 - BOTTOM_PANEL_HEIGHT//8)))


    pygame.display.update()



## initializes a grid
def init_grid(color):
    grid  = []
    for x in range(ROWS):
        grid.append([])
        for _ in range(COLS):
            grid[x].append(color)
    return grid

## gets row and col of a grid where user clicked
def get_grid_pos(mouse_position):
    x,y = mouse_position
    row = x//BLOCK_SIZE
    col = y//BLOCK_SIZE
    return row, col

## allows to change color by selecting rect with certain color. 
def change_color(mouse_position, drawing_color):
    x,y = mouse_position
    for colors in ALL_COLORS:
        if x >= colors.pos_x and x <= colors.pos_x + OPTION_RECT_SIZE and y >= colors.pos_y and y <= colors.pos_y + OPTION_RECT_SIZE:
            drawing_color = colors.color
    return drawing_color

## clears board
def erase(grid, start_chosen, end_chosen):
    for i in range(ROWS):
        for j in range(COLS):
            grid[i][j] = WHITE
    start_chosen, end_chosen = False, False
    return grid, start_chosen, end_chosen

## clears current path 
def clear_path(grid):
    for i in range(ROWS):
        for j in range(COLS):
            if grid[i][j] == RED or grid[i][j] == PURPLE or grid[i][j] == GREEN:
                grid[i][j] = WHITE
    return grid

## sets up random maze
def random_maze(grid):
    for i in range(ROWS):
        for j in range(COLS):
            if random.randrange(100) >= IMPASSABLE_BLOCK_PROPABILITY:
                grid[i][j] = WHITE
            else:
                grid[i][j] = BLACK



    start_pos = random.randrange(COLS), random.randrange(ROWS)
    end_pos = random.randrange(COLS), random.randrange(ROWS)
    while end_pos == start_pos:
        end_pos = random.randrange(COLS), random.randrange(ROWS)

    grid[start_pos[1]][start_pos[0]] = ORANGE
    grid[end_pos[1]][end_pos[0]] = BLUE
    return grid, start_pos, end_pos

## sets up a certain color of a cell in grid
def insert(row, col, grid, start_chosen, end_chosen, drawing_color, start_pos, end_pos):
    if start_chosen == False:
        grid[col][row] = ORANGE
        start_pos = row, col
        start_chosen = True
    elif end_chosen == False:
        if grid[col][row] == ORANGE:
            pass
        else:
            grid[col][row] = BLUE
            end_pos = row, col
            end_chosen = True
    else:
        draw_pos = row, col
        if draw_pos != start_pos and draw_pos != end_pos:
            grid[col][row] = drawing_color

    return start_chosen, end_chosen, start_pos, end_pos, grid



## checks how away is cur point from end point
def estimate_distance_f(point, end):
    x = abs(point[0] - end[0])
    y = abs(point[1] - end[1])
    return x + y 

## sets one of nodes as current from those that are Open(those green) (the one with lowest cost is set as current)
def set_current_and_remove_from_open(Open):
    
    current = Open[0]
    for pos in Open[1:]:
        if pos.current_cost + pos.estimate_distance < current.current_cost + current.estimate_distance:
            current = pos

    Open.remove(current)
    return current

## checks and return all neighbours of current
def check_neighbour(Current, grid):
    for_open_pos = []
    neighbours_to_check = [[0,1],[1,0],[0,-1],[-1,0]]
    cur_x = Current.position[0]
    cur_y = Current.position[1]
    for x,y in neighbours_to_check:
        if cur_x + x < COLS and cur_y + y < ROWS and cur_x + x >= 0 and cur_y + y >= 0 and grid[cur_y + y][cur_x + x] != BLACK:
            neighbour_pos = cur_x + x, cur_y + y
            for_open_pos.append(neighbour_pos)


    return for_open_pos  


## if node with same position as new_open is already in Closed or Open and its cost is bigger then cost of new_open node, it is beeing removed.
## else new_open is added to Open(those green)
def check_cheaper_way(new_open, Open, Closed, grid):
    for node in Open:
        if new_open.position == node.position: 
            if new_open.current_cost < node.current_cost:
                Open.remove(node)
                Open.append(new_open)
            return Open, Closed, grid

    for node in Closed:
        if new_open.position == node.position:
            if new_open.current_cost < node.current_cost:
                node.parent == new_open.position
                Closed.remove(node)
                Open.append(new_open)
            return Open, Closed, grid

    
    Open.append(new_open)
    grid[new_open.position[1]][new_open.position[0]] = GREEN
    pygame.draw.rect(screen, grid[new_open.position[1]][new_open.position[0]], (new_open.position[0]*BLOCK_SIZE,new_open.position[1]*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))

    return Open, Closed, grid



## tries to find shortest path from starting point to end point
def find_a_way(start_pos, end_pos, grid):
    Open = [Node(start_pos, 0, 0, estimate_distance_f(start_pos,end_pos))]  ## position, current cost, parent element, estimate cost
    Closed = []
    while True:
        ## if there are no more Open nodes, it means that path was not found
        if Open == []:
            return None, grid
        
        ## sets Current node. Node with lowest cost is chosen
        Current = set_current_and_remove_from_open(Open)


        ## pauses program, thx to this, algorithm is slower and more visible
        pygame.time.delay(SPEED) 
        


        ## checks for all neighbouring cells of Current
        new_open_pos = check_neighbour(Current, grid)
        
        ## creates a Node for every neighbour 
        for element in new_open_pos:
            new_open = Node(element, Current.current_cost+1, Current.position, estimate_distance_f(element, end_pos))

            Open, Closed, grid = check_cheaper_way(new_open, Open, Closed, grid)

        ## sets color of Current to red and moves it to Closed
        grid[Current.position[1]][Current.position[0]] = RED
        Closed.append(Current)

        ## if position of Current is same as end point position path was found
        if Current.position == end_pos:
            return Closed, grid

        ## sets color of starting point to orange (it gets overridden by red)
        grid[start_pos[1]][start_pos[0]] = ORANGE
        
        ## draws Current rect
        pygame.draw.rect(screen, grid[Current.position[1]][Current.position[0]], (Current.position[0]*BLOCK_SIZE,Current.position[1]*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))
        for i in range(ROWS):
            pygame.draw.line(screen, BLACK, (0,i*BLOCK_SIZE), (COLS * BLOCK_SIZE,i*BLOCK_SIZE), width=1)  ### if you want lines
        for i in range(COLS):
            pygame.draw.line(screen, BLACK, (i*BLOCK_SIZE,0), (i*BLOCK_SIZE,ROWS * BLOCK_SIZE), width=1)  ### if you want lines

        #for element in Closed:
            #text_cost = MY_FONT.render(str(element.current_cost + element.estimate_distance), 1, (0, 0, 0,))
            #screen.blit(text_cost, (element.position[0]*BLOCK_SIZE, element.position[1]*BLOCK_SIZE )) ### if you want cost
        #for element in Open:
            #text_cost = MY_FONT.render(str(element.current_cost + element.estimate_distance), 1, (0, 0, 0,))
            #screen.blit(text_cost, (element.position[0]*BLOCK_SIZE, element.position[1]*BLOCK_SIZE )) ### if you want cost  

        pygame.display.update()

## shows shortest path (purple)
def show_proper_way(proper_way, grid):
    end_element = proper_way[-1]
    while True:
        for element in proper_way:
            if end_element.parent == element.position:
                grid[element.position[1]][element.position[0]] = PURPLE
                end_element = element
        if end_element.parent == 0:
            return grid
    
## main function
def main():

    x = OPTION_RECT_SIZE 
    y = HEIGHT - BOTTOM_PANEL_HEIGHT//1.2
    for color in BLOCK_COLORS:
        ALL_COLORS.append(ColorBlock(x,y,color))
        x += OPTION_RECT_SIZE*1.5

    random_block = pygame.Rect(OPTION_RECT_SIZE, HEIGHT - BOTTOM_PANEL_HEIGHT//2, OPTION_RECT_SIZE, OPTION_RECT_SIZE)
    clear_block = pygame.Rect(OPTION_RECT_SIZE * 2.5, HEIGHT - BOTTOM_PANEL_HEIGHT//2, OPTION_RECT_SIZE, OPTION_RECT_SIZE)
    erase_block = pygame.Rect(OPTION_RECT_SIZE * 4, HEIGHT - BOTTOM_PANEL_HEIGHT//2, OPTION_RECT_SIZE, OPTION_RECT_SIZE)
    drawing_color = BLACK

    grid = init_grid(BG_COLOR)

    start_chosen = False
    end_chosen = False

    start_pos = None
    end_pos = None

    proper_way = 'nothing for now'



    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            draw_window(ALL_COLORS, grid, random_block, clear_block, erase_block, proper_way)

            if event.type == pygame.QUIT:
                run = False
            elif pygame.mouse.get_pressed()[0]:
                m_pos = pygame.mouse.get_pos()
                try:
                    row, col = get_grid_pos(m_pos)
                    drawing_color = change_color(m_pos, drawing_color)
                    x,y = m_pos

                    if x >= random_block.x and x <= random_block.x + OPTION_RECT_SIZE and y >= random_block.y and y <= random_block.y + OPTION_RECT_SIZE:
                        grid, start_pos, end_pos = random_maze(grid)
                        start_chosen, end_chosen = True, True
                    elif x >= clear_block.x and x <= clear_block.x + OPTION_RECT_SIZE and y >= clear_block.y and y <= clear_block.y + OPTION_RECT_SIZE:
                        grid = clear_path(grid)
                        start_chosen, end_chosen = True, True
                    elif x >= erase_block.x and x <= erase_block.x + OPTION_RECT_SIZE and y >= erase_block.y and y <= erase_block.y + OPTION_RECT_SIZE:
                        grid, start_chosen, end_chosen = erase(grid, start_chosen, end_chosen)

                    start_chosen, end_chosen, start_pos, end_pos, grid = insert(row, col, grid, start_chosen, end_chosen, drawing_color, start_pos, end_pos)

                except IndexError:
                        pass
            elif event.type == pygame.KEYDOWN:
                if start_chosen == True and end_chosen == True:
                    if event.key == pygame.K_SPACE:
                        proper_way, grid = find_a_way(start_pos, end_pos, grid) 

                        if proper_way != None:
                            show_proper_way(proper_way, grid)
                            grid[end_pos[1]][end_pos[0]] = BLUE
                            grid[start_pos[1]][start_pos[0]] = ORANGE

                    
    pygame.quit()

if __name__ == '__main__':
    main()