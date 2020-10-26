
def is_xy_in_rect(x, y, rect):
    return x >= rect["min_x"] and y >= rect["min_y"] and x <= rect["max_x"] and y <= rect["max_y"]

def get_distance(x1, x2, y1, y2):
    "returns float cartesian distance between two points"
    x = abs(x1-x2)
    y = abs(y1-y2)
    return (x**2+y**2)**0.5