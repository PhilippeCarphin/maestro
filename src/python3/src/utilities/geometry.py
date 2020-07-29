
def is_xy_in_rect(x, y, rect):
    return x >= rect["min_x"] and y >= rect["min_y"] and x <= rect["max_x"] and y <= rect["max_y"]
