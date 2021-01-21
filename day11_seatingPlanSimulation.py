import numpy as np
import moviepy.video.io.ImageSequenceClip
import seaborn as sns
import matplotlib.pyplot as plt

# Part one — task is to load and clean the seating plan, and run the "Game of Life" simulation until no more seats change state.
# The rules are:
# 1. if seat unoccupied and no adjacent seats occupied -> occupied
# 2. if seat occupied and 4 or more adjacent seats occupied -> unoccupied

# I have decided to use numpy arrays to tackle this problem. This is not the most efficient method, however, I have decided to do this such that I can create heatmaps from the data, with the overall aim of creating videos of the simulations, so that we can see the "Game of Life" (see: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)

# use a context manager to read lines from text file
with open('day11_input.txt', 'r') as f:
    file_contents = f.read()

# split by new line and remove any empty strings
data = file_contents.split('\n')
data = [row for row in data if row.split()]

# data loaded and cleaned, now define functions and run the simulation

def seat_plan_border_array(data):
    """
    Transform seating plan from a list into a numpy array with a border. The border makes dealing with edge cases easier later.
    """
    # define size of array
    num_rows = len(data)
    num_cols = len(data[0])
    seat_plan_b = np.zeros((num_rows+2, num_cols+2), dtype=int)

    # fill in the array. The floor is defined as 0, and an empty seat as -1. Later, filled seats will be 1.
    for i in range(num_rows):
        seats_str = data[i]
        for j in range(num_cols):
            seat_floor = seats_str[j]
            if seat_floor == "L":
                seat_plan_b[i+1,j+1] = int(-1)
            else:
                seat_plan_b[i+1,j+1] = int(0)

    return seat_plan_b

def apply_rules_border_simultaneously(sp):
    """
    Accepts array of seating plan with borders, applies the rules simultaneously, and return the updated seating plan with a record of seat changes.
    """
    # all rules are applied simultaneously, so need a copy of the input seating array
    spu = np.array(sp)

    # keep a record of those seats that change. This will later enable the tracking of simulation convergence/completion
    seat_change_list = []
    seat_change_stab = 0

    # array has borders so do not need to loop over these
    rr = sp.shape[0]-2
    cc = sp.shape[1]-2

    # iterate through all the seats, count number of occupied neighbouring seats, and apply the rules to update the seating plan
    for i in range(rr):
        for j in range(cc):

            # count occupied/unoccupied neighbours
            adj_sts = np.array([sp[i,j],  sp[i,j+1], sp[i,j+2], sp[i+1,j], sp[i+1,j+2], sp[i+2,j], sp[i+2,j+1], sp[i+2,j+2]])
            occs = len(adj_sts[adj_sts==1])
            unoccs = len(adj_sts[adj_sts==-1])

            # keep track of actual seat, i.e., considering the borders
            seat = sp[i+1,j+1]

            # apply the rules and update the copy of the seating plan array
            if (seat == -1) and (occs == 0): # if seat unoccupied and no adjs seats occupied -> occ
                spu[i+1, j+1] = 1
                seat_change_list.append([i+1, j+1])
                seat_change_stab += (i+1) + (j+1)
            elif (seat == 1) and (occs >= 4): # if seat occupied and 4 or more adjs occupied -> unocc
                spu[i+1, j+1] = -1
                seat_change_list.append([i+1, j+1])
                seat_change_stab += (i+1) + (j+1)
            else:
                continue

    return spu, seat_change_list, seat_change_stab


def count_occupied_seats(seating_plan):
    """Count number of occupied seats"""
    # count occupied seats
    rr = seating_plan.shape[0]
    cc = seating_plan.shape[1]
    occ_count = 0

    for i in range(rr):
        for j in range(cc):
            if seating_plan[i,j] == 1:
                occ_count += 1

    return occ_count

def run_simulation1(data):
    """
    Run the simulation until no more seats change state (simulation has converged),
    and return the final state of the seating plan with a record of seat changes (stab_list)
    """
    # transform data to numpy array
    sp_current = seat_plan_border_array(data)
    iteration = 0
    stab_list = []

    # run the simulation until no more seats change state
    pre_seat_stab = 0
    seat_stab = 1
    while pre_seat_stab != seat_stab:
        pre_seat_stab = seat_stab
        sp_current, seat_change_list, seat_stab = apply_rules_border_simultaneously(sp_current)
        stab_list.append(seat_stab)

    return sp_current, stab_list

# now run the simulation until no seats more seats change state, and count the occupied seats
sp_final_sim1, _ = run_simulation1(data)

# count the number of occupied seats in the final state
occ_seats_sim1 = count_occupied_seats(sp_final_sim1)
print(f'Part one: after converging, there are {occ_seats_sim1} occuied seats.')



# Part two — the rules have changed and we look in all 8 directions to the nearest seat, but not adjacent seats

# Now, we look from a seat in all directions (N, E, S, W and the four diagonals), to search for the first seat that we hit. Then we apply the rules.

# 8 functions, each returns the value of the first seat seen (i.e. occ, 1, or unocc, -1) in each direction. If no seat seen, return the value of the floor=0

def seeing_left(st_r, st_c, sp):
    """returns value of first seat seen to the left"""
    seats_list = sp[st_r, 0:st_c]
    seats_list_flipped = np.flip(seats_list)
    for s in seats_list_flipped:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_right(st_r, st_c, sp):
    """returns value of first seat seen to the right"""
    seats_list = sp[st_r, st_c+1:]

    for s in seats_list:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_down(st_r, st_c, sp):
    """returns value of first seat seen to going down"""
    seats_list = sp[st_r+1:, st_c]

    for s in seats_list:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_up(st_r, st_c, sp):
    """returns value of first seat seen to going up"""
    seats_list = sp[0:st_r:, st_c]
    seats_list_flipped = np.flip(seats_list)

    for s in seats_list_flipped:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_upleft(st_r, st_c, sp):
    """returns value of first seat seen diagonally up and left"""
    cs = [i for i in range(st_c)]
    rs = [i for i in range(st_r)]
    cs = cs[::-1]
    rs = rs[::-1]

    seats_list = []
    for r,c in zip(rs,cs):
        seats_list.append(sp[r,c])

    for s in seats_list:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_downleft(st_r, st_c, sp):
    """returns value of first seat seen diagonally down and left"""
    num_rows = sp.shape[0]

    cs = [i for i in range(st_c)]
    rs = [i for i in range(st_r+1, num_rows)]
    cs = cs[::-1]

    seats_list = []
    for r,c in zip(rs,cs):
        seats_list.append(sp[r,c])

    for s in seats_list:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_upright(st_r, st_c, sp):
    """returns value of first seat seen diagonally up and right"""
    num_cols = sp.shape[1]

    cs = [i for i in range(st_c+1, num_cols)]
    rs = [i for i in range(0, st_r)]
    rs = rs[::-1]

    seats_list = []
    for r,c in zip(rs,cs):
        seats_list.append(sp[r,c])

    for s in seats_list:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def seeing_downright(st_r, st_c, sp):
    """returns value of first seat seen diagonally down and right"""
    num_rows = sp.shape[0]
    num_cols = sp.shape[1]

    cs = [i for i in range(st_c+1, num_cols)]
    rs = [i for i in range(st_r+1, num_rows)]

    seats_list = []
    for r,c in zip(rs,cs):
        seats_list.append(sp[r,c])

    for s in seats_list:
        if s == -1:
            return -1
        elif s == 1:
            return 1
        else:
            continue

    return 0

def apply_rules_border_diag_new(sp):
    """
    Apply the new rules, i.e., looking for the first seat in each of the eight directions. Return the updated seating plan with record of changes.
    """
    # make a copy of plan coming in
    spu = np.array(sp)
    seat_change_list = []
    seat_change_stab = 0

    # define size of loop considering presence of borders
    rr = sp.shape[0]
    cc = sp.shape[1]

    # loop over all seats to apply the rules
    for i in range(rr-2):
        for j in range(cc-2):

            # define current seat, considering presence of borders
            seat_r = i+1
            seat_c = j+1
            st = sp[seat_r, seat_c]

            if (st==1) or (st==-1): # if a seat, find the values in the eight poss directions

                # find the eight seats
                upright = seeing_upright(seat_r, seat_c, sp)
                downright = seeing_downright(seat_r, seat_c, sp)
                upleft = seeing_upleft(seat_r, seat_c, sp)
                downleft = seeing_downleft(seat_r, seat_c, sp)
                up = seeing_up(seat_r, seat_c, sp)
                down = seeing_down(seat_r, seat_c, sp)
                left = seeing_left(seat_r, seat_c, sp)
                right = seeing_right(seat_r, seat_c, sp)

                # find number of occupied seats to apply the rules
                see_list = [left, upleft, up, upright, right, downright, down, downleft] # see is pun on seeing and the Holy See
                occ_list = [see for see in see_list if see==1]
                occ_number = sum(occ_list)

                # apply the rules
                if (st == -1) and (occ_number == 0): # if seat unoccupied and no adjs seats occupied -> occ
                    spu[seat_r, seat_c] = 1
                    seat_change_list.append([i+1, j+1])
                    seat_change_stab += (i+1) + (j+1)
                elif (st == 1) and (occ_number >= 5): # if seat occupied and 5 or more adjs occupied -> unocc
                    spu[seat_r, seat_c] = -1
                    seat_change_list.append([i+1, j+1])
                    seat_change_stab += (i+1) + (j+1)
                else:
                    continue

    return spu, seat_change_list, seat_change_stab

def run_simulation2(data):
    """
    Run the simulation until no more seats change state (simulation has converged),
    and return the final state of the seating plan with a record of seat changes (stab_list)
    """
    # transform data to numpy array
    sp_current = seat_plan_border_array(data)
    iteration = 0
    stab_list = []

    # run the simulation until no more seats change state
    pre_seat_stab = 0
    seat_stab = 1
    while pre_seat_stab != seat_stab:
        pre_seat_stab = seat_stab
        sp_current, seat_change_list, seat_stab = apply_rules_border_diag_new(sp_current)
        stab_list.append(seat_stab)

    return sp_current, stab_list

# now run the second simulation until no seats more seats change state, and count the occupied seats
sp_final_sim2, _ = run_simulation2(data)

# count the number of occupied seats in the final state
occ_seats_sim2 = count_occupied_seats(sp_final_sim2)
print(f'Part two: after converging, there are {occ_seats_sim2} occuied seats.')


# The simulation work, now this time let's run them again but saving out the heatmaps at each iteration, such that I can visualise them as videos

# set the fig size
sns.set(rc={'figure.figsize':(11,11)})

def run_sim1_saveImages(data, image_file_direct, file_name):
    """
    runs the first simulation, saving out each iteration as a heatmap, which can then be made into a video
    """
    # refresh the original seating plan and transform to numpy array
    sp_current = seat_plan_border_array(data)
    iteration = 0
    stab_list = []

    # run the simulation until no more seats change state
    pre_seat_stab = 0
    seat_stab = 1
    iteration = 0
    while pre_seat_stab!= seat_stab:
        pre_seat_stab = seat_stab
        sp_current, seat_change_list, seat_stab = apply_rules_border_simultaneously(sp_current)
        stab_list.append(seat_stab)
        iteration += 1

        # create the file name
        fig_file_name = image_file_direct + file_name + '_' + str(iteration) + '.png'
        # plot and save the heatmap
        sns.heatmap(sp_current, cbar=False, xticklabels=False, yticklabels=False, cmap="magma_r")
        plt.savefig(fig_file_name)

    return iteration

def run_sim2_saveImages(data, image_file_direct, file_name):
    """
    runs the second simulation, saving out each iteration as a heatmap, which can then be made into a video
    """
    # refresh the original seating plan and transform to numpy array
    sp_current = seat_plan_border_array(data)
    iteration = 0
    stab_list = []

    # run the simulation until no more seats change state
    pre_seat_stab = 0
    seat_stab = 1
    iteration = 0
    while pre_seat_stab!= seat_stab:
        pre_seat_stab = seat_stab
        sp_current, seat_change_list, seat_stab = apply_rules_border_diag_new(sp_current)
        stab_list.append(seat_stab)
        iteration += 1

        # create the file name
        fig_file_name = image_file_direct + file_name + '_' + str(iteration) + '.png'
        # plot and save the heatmap
        sns.heatmap(sp_current, cbar=False, xticklabels=False, yticklabels=False, cmap="magma_r")
        plt.savefig(fig_file_name)

    return iteration

def write_sim_video(image_files, fps, full_file_save):
    """create mp4 from series of heatmaps"""
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(full_file_save)

# set directory and file names for saving images
image_file_direct = '/Users/george.stanley/Documents/Content/adventCode_2020/day11_simulations_pngs_mp4s/'
file_name1 = 'simulation1_magma'
file_name2 = 'simulation2_magma'

# run both simulations, save the heatmaps from each iteration, and save the total iteration numbers
sim1_iterations = run_sim1_saveImages(data, image_file_direct, file_name1)
sim2_iterations = run_sim2_saveImages(data, image_file_direct, file_name2)

# generate list of image names to make videos
sim1_image_files = [image_file_direct + file_name1 + '_' + str(i) + '.png' for i in range(1,sim1_iterations+1)]
sim2_image_files = [image_file_direct + file_name2 + '_' + str(i) + '.png' for i in range(1,sim2_iterations+1)]

# create full file paths and names for saving the videos
full_file_video_save1 = image_file_direct + file_name1 + '.mp4'
full_file_video_save2 = image_file_direct + file_name2 + '.mp4'

# choose fps and make the movies
fps = 7
write_sim_video(sim1_image_files, fps, full_file_video_save1)
write_sim_video(sim2_image_files, fps, full_file_video_save2)
