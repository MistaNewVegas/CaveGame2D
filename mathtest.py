"""
leveling system:
    points are 100 or 250
    logarithmic growth
    level 0 -> level 1 = 100 points total
    level 1 -> level 2 = 200 points total
    level 2 -> level 3 = 400 points total
    level 3 -> level 4 = 800 points total
    level 4 -> level 5 = 1600 points total

    rewards:
    health regenerates 50 points every level
    level 0: base
    level 1: higher jump
    level 2: more health
    level 3: faster walk
    level 4: more health
    level 5: even higher jump
"""
level = int(input("level: "))
points = int(input("points: "))

points_needed = (100*(2**level)) - points

print(points_needed)
