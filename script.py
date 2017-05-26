import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """

frames_pres = False
basename_pres = False
vary_pres = False
frames = 1
basename = "defaultVal"
knobs = []


def first_pass( commands ):
    global frames_pres
    global basename_pres
    global vary_pres
    global frames
    global basename

    for command in commands:
        # print command
        c = command[0]
        args = command[1:]

        if c == 'frames':
            frames = int(args[0])
            frames_pres = True
            
        elif c == 'basename':
            basename = args[0]
            basename_pres = True

        elif c == 'vary':
            vary_pres = True

    if vary_pres and not frames_pres:
        # exit program
        print "frames not present"
        exit()

    if frames_pres and not basename_pres:
        # set basename to default val, print
        print "basename not present.\nbasename has been set to: defaultVal"
        

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a separate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    global knobs

    knobs = [{} for f in range(num_frames)]

    for command in commands:
        print command
        c = command[0]
        args = command[1:]

        if c == 'vary':
            name = args[0]
            start_f = int(args[1])
            end_f = int(args[2])
            start_val = float(args[3])
            end_val = float(args[4])

            frame_cnt = end_f - start_f
            if frame_cnt < 0 or start_f < 0 or end_f >= frames:
                print "invalid frame range"
                return

            start_knob = (end_val - start_val) / frame_cnt
            step = 1
            curr = start_val

            if start_knob < 0:
                tmp = start_f
                start_f = end_f
                end_f = tmp

                start_knob *= -1
                step *= -1

                curr = end_val
                end_val = start_val

            for f in range(start_f, end_f + step, step):
                knobs[f][name] = curr
                if curr < end_val:
                    curr += start_knob
    return knobs


# if increment < 0:
#                 increment *= -1.0
#                 currentFrame = endValue #change the start
#                 for frame in range(endFrame, startFrame - 1, -1):
#                     knobs[frame][name] = currentFrame
#                     if currentFrame < startValue:
#                         currentFrame += increment
#             else:
#                 for frame in range(startFrame,endFrame + 1, 1):
#                     knobs[frame][name] = currentFrame
#                     if currentFrame < endValue:
#                         currentFrame += increment




def run(filename):
    """
    This function runs an mdl script
    """
    global frames 
    global frames_pres
    global basename
    global knobs


    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )
    screen = new_screen()
    step = 0.1
    

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    # run first_pass
    first_pass(commands)
    if frames_pres:
        knobs = second_pass(commands, frames)


    for f in range(frames):
        step = .1

        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        tmp = []

        for command in commands:
            print command
            c = command[0]
            args = command[1:]

            if c =='set':
                symbols[args[0]][1] = float(args[1])

            elif c == 'setknobs':
                for i in symbols:
                    if symbols[i][0] == 'knob':
                        symbols[i][1] = float(args[0])

            elif c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if args[3] != None:
                    one = knobs[f][args[3]] * args[0]
                    two = knobs[f][args[3]] * args[1]
                    three = knobs[f][args[3]] * args[2]
                    args = (one, two, three ,args[3])

                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[3] != None:
                    one = knobs[f][args[3]] * args[0]
                    two = knobs[f][args[3]] * args[1]
                    three = knobs[f][args[3]] * args[2]
                    args = (one, two, three ,args[3])

                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if args[2] != None:
                    one = knobs[f][args[2]] * args[1]
                    args = (args[0], one, args[2])

                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

        img_name = 'anim/' + basename + (3-len(str(f)))*'0' + str(f) + '.ppm'
        #print img_name
        save_ppm(screen, img_name)
        clear_screen(screen)

        #print f 
        #print frames

        print vary_pres
        print knobs

    make_animation(basename)
    print symbols
    # {'spinny': ['knob', 0], 'bigenator': ['knob', 0]}

