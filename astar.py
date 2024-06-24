import pygame, sys
from queue import PriorityQueue

pygame.init()

BOARD_PIXEL_WIDTH = 800
WINDOW = pygame.display.set_mode((BOARD_PIXEL_WIDTH, BOARD_PIXEL_WIDTH))
pygame.display.set_caption("A* Pathfinding Visualization")
game_font = pygame.font.SysFont("Trebuchet", 36)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

instructions = [
    "A* Pathfinder Visualization",
    "Instructions:",
    "1. Left-mouse click a square to set start point, again for end.",
    "2. Then, left-mouse click to place black obstacle blocks.",
    "3. Right-mouse click to reset any block to white.",
    "4. Press 'Space' to start the pathfinder.",
    "5. When done, press 'c' to reset the board or 'q' to quit.",
    "",
    "Click anywhere on the board to begin."
]


class Node:
    def __init__(self, row, col, node_width, total_rows):
        self.row = row
        self.col = col
        self.x = row * node_width
        self.y = col * node_width
        self.color = WHITE
        self.neighbors = []
        self.width = node_width
        self.total_rows = total_rows

    def get_pos(self) -> tuple:
        return self.row, self.col

    def is_closed(self) -> bool:
        return self.color == RED

    def is_open(self) -> bool:
        return self.color == GREEN

    def is_barrier(self) -> bool:
        return self.color == BLACK

    def is_start(self) -> bool:
        return self.color == ORANGE

    def is_end(self) -> bool:
        return self.color == TURQUOISE

    def reset(self) -> None:
        self.color = WHITE

    def make_closed(self) -> None:
        self.color = RED

    def make_open(self) -> None:
        self.color = GREEN

    def make_barrier(self) -> None:
        self.color = BLACK

    def make_start(self) -> None:
        self.color = BLUE

    def make_end(self) -> None:
        self.color = TURQUOISE

    def make_path(self) -> None:
        self.color = PURPLE

    def draw_node(self, window: pygame.display, color1=None, color2=None) -> None:
        """
        Node draws itself to board
        :param window: pygame.display object
        :param color1: optional: if present, draw checkerboard.  If absent, draw node.color
        :param color2: optional: only present if color1 supplied. second checkerboard color
        :return: None
        """
        checkerboard_scale = 4

        def swap_color(current_color):
            if current_color == color1:
                current_color = color2
            else:
                current_color = color1
            return current_color

        if not color1:  # simple draw
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))
        else:  # checkerboard draw
            color = color1
            for i in range(checkerboard_scale):
                for j in range(checkerboard_scale):
                    pygame.draw.rect(window, color, (self.x + (i * self.width // checkerboard_scale),
                                                     self.y + (j * self.width // checkerboard_scale),
                                                     self.width // checkerboard_scale,
                                                     self.width // checkerboard_scale))
                    color = swap_color(color)
                if not checkerboard_scale%2: # if the checkerboard is even x even, perform manual swap at end of column
                    color = swap_color(color)

    def update_neighbors(self, grid):
        """
        Scan for valid NSEW neighbors for each node, save results on each node itself
        :param grid:
        :return: None
        """
        self.neighbors = []
        # check down:(row + 1,col), up:(row - 1,col), right:(row,col + 1), and left:(row,col - 1)
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # left
            self.neighbors.append(grid[self.row][self.col - 1])


def h(node_coord1: tuple, node_coord2: tuple) -> int:
    """
    Manhattan heuristic distance calculation
    :param node_coord1: current node (x, y)
    :param node_coord2: end node (x, y)
    :return:
    """
    x1, y1 = node_coord1
    x2, y2 = node_coord2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, lambda_draw) -> None:
    """
    Pathfinding complete, work from endpoint back along the came_from list to draw the shortest path to the start point
    :param came_from: list of nodes in path
    :param current: begins at end point, crawls back the came_from list
    :param lambda_draw: lambda-packaged call to draw()
    :return:
    """
    while current in came_from:
        current = came_from[current]
        current.make_path()
        lambda_draw()


def astar(lambda_draw, grid, start_pos, end_pos) -> bool:
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start_pos))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start_pos] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start_pos] = h(start_pos.get_pos(), end_pos.get_pos())

    open_set_hash = {start_pos}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end_pos:
            reconstruct_path(came_from, end_pos, lambda_draw)
            end_pos.make_end()
            start_pos.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end_pos.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        lambda_draw()

        if current != start_pos:
            current.make_closed()

    return False


def make_grid(rows: int, board_pixel_width: int) -> list:
    """
    Generate the grid data structure: a list of lists of Nodes
    :param rows:
    :param board_pixel_width:
    :return: grid structure
    """
    grid = []
    node_size = board_pixel_width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, node_size, rows)
            grid[i].append(node)

    return grid


def draw_grid_lines(window: pygame.display, rows: int, board_pixel_width: int) -> None:
    """
    Draw grid lines for node blocks on pygame board
    :param window: pygame.display
    :param rows: int
    :param board_pixel_width: int
    :return: None
    """
    gap = board_pixel_width // rows

    for i in range(rows):
        pygame.draw.line(window, GRAY, (0, i * gap), (board_pixel_width, i * gap))
        pygame.draw.line(window, GRAY, (i * gap, 0), (i * gap, board_pixel_width))


def draw(window, grid, rows, board_pixel_width, start_pos, end_pos, update=True) -> None:
    """
    Draw board from scratch (per pygame tick)
    :param window: pygame.display
    :param grid:
    :param rows:
    :param board_pixel_width:
    :param start_pos: Node
    :param end_pos: Node
    :param update: bool (defaults to true, disable to blit extra info post-draw, update manually later)
    :return: None
    """
    window.fill(WHITE)
    for row in grid:
        for node in row:
            if node is start_pos:
                node.draw_node(window, GREEN, WHITE)
            elif node is end_pos:
                node.draw_node(window, BLACK, WHITE)
            else:
                node.draw_node(window)

    draw_grid_lines(window, rows, board_pixel_width)

    if update:
        pygame.display.update()


def get_clicked_pos(pos, rows, board_pixel_width) -> tuple:
    """
    Take pixel (x, y) and return (row, col)
    :param pos: (x, y) tuple
    :param rows:
    :param board_pixel_width:
    :return: (row, col) tuple
    """
    gap = board_pixel_width // rows

    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def get_node_from_mouseclick(board_pixel_width, grid, rows) -> Node:
    """
    Receives basic board info, queries pygame as to mouse position, returns node block associated with that position
    :param board_pixel_width:
    :param grid:
    :param rows:
    :return: Node
    """
    pos = pygame.mouse.get_pos()
    row, col = get_clicked_pos(pos, rows, board_pixel_width)
    node = grid[row][col]
    return node


def reset_board(board_pixel_width, rows) -> tuple:
    """
    Reset all grid values, set start and end pos to none
    :param board_pixel_width:
    :param rows:
    :return: tuple
    """
    grid = make_grid(rows, board_pixel_width)
    return None, None, grid


def main(window, board_pixel_width) -> None:
    rows = 50
    start_pos, end_pos, grid = reset_board(board_pixel_width, rows)

    # 1. begin by displaying instructions
    run = True

    while run:
        draw(window, grid, rows, board_pixel_width, start_pos, end_pos, False)

        y_offset = 50
        for line in instructions:
            text_surface = game_font.render(line, True, BLACK)
            window.blit(text_surface, (50, y_offset))
            y_offset += 40

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    # 2. Enter the game loop
    run = True

    while run:
        draw(window, grid, rows, board_pixel_width, start_pos, end_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # left click: set node as start position, end position, or barrier
                node = get_node_from_mouseclick(board_pixel_width, grid, rows)

                if not start_pos and node != end_pos:
                    start_pos = node
                    start_pos.make_start()
                elif not end_pos and node != start_pos:
                    end_pos = node
                    end_pos.make_end()
                elif node != start_pos and node != end_pos:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right click: reset node identity to unset
                node = get_node_from_mouseclick(board_pixel_width, grid, rows)
                node.reset()

                if node == start_pos:
                    start_pos = None
                elif node == end_pos:
                    end_pos = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start_pos and end_pos:  # Space bar: begin pathfinding
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    astar(lambda: draw(window, grid, rows, board_pixel_width, start_pos, end_pos), grid, start_pos,
                          end_pos)

                if event.key == pygame.K_c:  # c key: clear board
                    start_pos, end_pos, grid = reset_board(board_pixel_width, rows)

                if event.key == pygame.K_q:  # q key: quit
                    run = False

    pygame.quit()


main(WINDOW, BOARD_PIXEL_WIDTH)
