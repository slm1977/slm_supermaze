"""
Modulo che contiene la lista dei livelli di gioco.
Per aggiungere un nuovo livello è sufficiente aggiungere
un dizionario alla lista.
Si noti che tutti i parametri sono opzionali.
"""

levels = [


    # livello per testare le funzionalità di gioco
    {
        "ncols" : 11,
        "nrows" : 11,
        "greedy_enemies" : 1,
        "player_bullets" : [(2,20)],
        "invisibility_players" : [(3,20)],
        "maze_density": 0.1,
        "maze_complexity": 0.8,
        "background_image" : "Backgrounds/ydt89/Background_01.png"
      },


    # livello 1
    {
        "time" : 100,
        "ncols" : 11,
        "nrows" : 11,
        "scale" : 30,
        "clock" : 80,
        "enemies" : "Sprites/Animals/bear.png",
        "coin_color" : (255,255,255),
        "maze_density": 0.75,
        "maze_complexity": 0.5,
        "background_image" : "Backgrounds/ydt89/Background_02.png"

    },

    # livello 2
    {
        "num_enemies" : 1,
        "ncols" : 20,
        "nrows" : 20,
        "scale" : 30,
        "clock" : 80,
        "enemies" : "Sprites/Animals/bear.png",
        "time_reloaders" : 1,
        "coin_color" : (200,20,222),
        "maze_density": 0.75,
        "maze_complexity": 0.5,
        "background_image" : "Backgrounds/ydt89/Background_03.png"

    },

    # livello 3
    {
        "num_enemies" : 2,
        "time_reloaders" : 2,
        "bombs" : [(5,20)],
        "ncols" : 20,
        "nrows" : 20,
        "scale" : 40,
        "clock" : 80,
        "music" : "./Music/Soundimage/Funky-Gameplay_Looping.ogg",
        "wall" : "./Backgrounds/Dim/Chimeny.jpg",
        "background_image" : "Backgrounds/ydt89/Background_05.png"
    },

    # livello 4
    {
        "num_enemies": 6,
        "time_reloaders" : 3,
        "enemy_killers" : [(10,10)],
        "bombs" : [(5,20)],
        "wall_bombs" : [(3,10)],
        "ncols": 30,
        "nrows": 30,
        "scale": 40,
        "clock": 80,
        "enemies" : "Sprites/Animals/cow.png",
        "music" : "./Music/Soundimage/Racing-Menu.ogg",
        "wall" : "./Backgrounds/Dim/Dirt.jpg",
        "coin_color" : (0,20,200),
        "maze_density": 0.5,
        "maze_complexity": 0.8

    },

    # livello 5
    {
        "num_enemies": 8,
        "time_reloaders" : 3,
        "enemy_killers": [(6, 10)],
        "bombs": [(8, 20)],
        "wall_bombs" : [(3,25)],
        "ncols": 30,
        "nrows": 30,
        "scale": 40,
        "clock": 80,
        "enemies": "Sprites/Animals/elephant.png",
        "music": "./Music/Soundimage/Racing-Menu.ogg",
        "wall": "./Backgrounds/Dim/Dirt.jpg",
        "coin_color": (0, 255, 20),
        "maze_density": 0.2,
        "maze_complexity": 0.7,
        "invisibility_players" : [(3,10)],
        "player_bullets" : [(2,10)],

    },

    # livello 6
    {
        "num_enemies": 20,
        "time_reloaders": 5,
        "enemy_killers": [(10, 10)],
        "bombs": [(8, 20)],
        "wall_bombs": [(3, 25), (1,50)],
        "portals" : 5,
        "ncols": 30,
        "nrows": 30,
        "scale": 40,
        "clock": 120,
        "enemies": "Sprites/Animals/elephant.png",
        "music": "./Music/Soundimage/Grunge-Street-Game.ogg",
        "wall": "./Backgrounds/Dim/Dirt.jpg",
        "coin_color": (40, 70, 20),
        "maze_density": 0.5,
        "maze_complexity": 0.7,
        "player_bullets" : [(3,12)],

    },

    # livello 7
    {
        "num_enemies": 38,
        "num_shooters": [(2, 20)],
        "time_reloaders": 5,
        "enemy_killers": [(30, 10)],
        "invisibility_players" : [(5,8)],
        "bombs": [(3, 8)],
        "bombs": [(3, 25), (3, 20)],
        "portals": 5,
        "ncols": 50,
        "nrows": 18,
        "scale":28,
        "clock": 200,
        "enemies": "Sprites/Animals/crocodile.png",
        "music": "./Music/Soundimage/Surreal-Chase_Looping.ogg",
        "wall": "./Backgrounds/Dim/Grass.jpg",
        "coin_color": (40, 200, 20),
        "maze_density": 0.5,
        "maze_complexity": 0.7,
        "player_bullets" : [(2,5), (2,10),(1,15)],

    },

    # livello 8
    {
        "num_shooters" : [(5,50), (20,5)],
        "time_reloaders": 5,
        "enemy_killers": [(20, 10)],
        "invisibility_players": [(5, 8)],
        "bombs": [(3, 25), (3, 20)],
        "portals": 5,
        "ncols": 30,
        "nrows": 30,
        "scale": 28,
        "clock": 200,
        "shooters": "Sprites/Animals/giraffe.png",
        "music": "./Music/Soundimage/Car-Theft-101.ogg",
        "wall": "./Backgrounds/Dim/Roof1.jpg",
        "coin_color": (229,200, 20),
        "maze_density": 0.8,
        "maze_complexity": 0.8,
        "player_bullets": [(1, 30), (3, 20), (5, 25)],
        "greedy_enemies" : 2,
        "time_reloaders": 1,

    },

# livello 9
    {
        "num_shooters" : [(5,80), (20,35)],
        "time_reloaders": 5,
        "enemy_killers": [(20, 10)],
        "invisibility_players": [(5, 8)],
        "bombs": [(3, 25), (3, 20)],
        "portals": 5,
        "ncols": 30,
        "nrows": 25,
        "scale": 28,
        "clock": 200,
        "shooters": "Sprites/Animals/frog.png",
        "music": "./Music/Soundimage/Retro-Frantic_Looping.ogg",
        "wall": "./Backgrounds/Dim/AncientFlooring.jpg",
        "coin_color": (229,200, 220),
        "maze_density": 0.8,
        "maze_complexity": 0.4,
        "player_bullets": [(1, 30), (3, 20), (5, 25)],
        "greedy_enemies" : 2,
        "time_reloaders": 3,
        "wall_bombs" : [(3,10)],
        "wall_bombs" : [(4,10)],
    },

# livello 10
    {
        "num_shooters" : [(10, 120), (20,35)],
        "background_image" : "Backgrounds/ydt89/Background_07.png",
        "time_reloaders": 5,
        "enemy_killers": [(20, 10)],
        "invisibility_players": [(5, 8)],
        "bombs": [(3, 25), (3, 20)],
        "portals": 5,
        "ncols": 30,
        "nrows": 25,
        "scale": 25,
        "shooters": "Sprites/Animals/goat.png",
        "music": "./Music/Soundimage/Retro-Frantic_Looping.ogg",
        "wall": "./Backgrounds/Dim/Dirt.jpg",
        "coin_color": (229,80, 250),
        "maze_density": 0.8,
        "maze_complexity": 0.4,
        "player_bullets": [(1, 30), (3, 20), (5, 25)],
        "greedy_enemies" : 4,
        "time_reloaders": 3,
        "wall_bombs" : [(3,10)],
        "bombs" : [(4,10)],
    },

]