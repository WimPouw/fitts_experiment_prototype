from psychopy import visual, core
import random
from psychopy import event, visual, core
from psychopy.event import Mouse
import csv

############################ how many trials?
ppn = input('participant number')
tr = input('how many trials do you want to do?')
trials = range(0, int(tr))

############################ key experiment settings
perturbationrange = [1, 10] #this means that we are going to apply perturbation between x1 and x2 pixels
radiusrange = [10, 80]      #this means we are going to vary the radius size with a lower and higher range


# Create a function that gives two psychopy circle objects that we can draw on the screen
def createcircleset(location2y = 0, location2x = 700, size1 = 50, size2 = 50):
    circle1 = visual.Circle(
        win=win,
        radius=size1,
        pos=[-700, 0],
        fillColor=[1, 0, 0],
        fillColorSpace="rgb",
        lineColor=[1, 1, 1],
        lineColorSpace="rgb"
    )
    circle2 = visual.Circle(
        win=win,
        radius=size2,
        pos=[location2x, location2y],
        fillColor=[1, 0, 0],
        fillColorSpace="rgb",
        lineColor=[1, 1, 1],
        lineColorSpace="rgb"
    )
    return circle1, circle2
#######################################################TRIALSTRUCTURE
# how often is there a perturbation? Now we just have 50% percent chance that the trial has a perturbation
perturbations = []
for i in trials:
    perturbation = random.randint(0, 1)
    if perturbation == 1:
        perturbation = random.randint(perturbationrange[0], perturbationrange[1])*[-1,1][random.randint(0, 1)] #here set the perturbation either in the upward or downward motion, with a value between 1-10 pixels
         #random upward or downward
    perturbations.append(perturbation)

# how are we going to vary te radius size which is crucial for the fitts task
radii = []
for i in trials:
    radii.append(random.randint(radiusrange[0], radiusrange[1])) #we now just randomly vary between 10, 80

####################################################################

# set up a wind
win = visual.Window(
    size=[800, 600],
    units="pix",
    color=[1, 1, 1],
    colorSpace="rgb",
    fullscr = True
)

# Create text stimuli for the Yes and No options, and a text function that your can use to draw free texts
task_text = visual.TextStim(
    win=win,
    text='Did you see the circle move during your approach?',
    pos=[0, 300],
    color=[1, 0, 0],
    height=70,
    units='pix'
)

yes_text = visual.TextStim(
    win=win,
    text='Yes',
    pos=[0, -100],
    color=[1, 0, 0],
    height=70,
    units='pix'
)

no_text = visual.TextStim(
    win=win,
    text='No',
    pos=[0, 100],
    color=[1, 0, 0],
    height=70,
    units='pix'
)

def free_text(text, win):
    frt = visual.TextStim(
        win=win,
        text=text,
        pos=[0, 0],
        color=[1, 0, 0],
        height=70,
        units='pix')
    return frt

##############################################set variables to collect_dataset
cnames = ['trialindex', 'radiustr', 'perturbation_yn', 'perturbation_correct', 'perturbation_values']
trailindex                  = []
radius_tr                   = []
perturbation_yn             = []
perturbation_correct        = []

#set up a mouse
mouse1 = Mouse(visible=True, newPos=None, win=win)

#we are now going to loop over trials
for i in trials:
    #we want save the mouse/touchscreen information continuously, so we can later do trajectory analyses
    mouse_time          = []
    mouse_time_series_x = []
    mouse_time_series_y = []
    #preset some variables
    response = None
    next = False
    #set radius based on triallist
    radius2 = radii[i]
    #now set circles as start
    circle1, circle2 = createcircleset(size1= radius2, size2= radius2)
    # Draw the circles
    circle1.draw()
    circle2.draw()
    # Update the windowd
    win.flip()

    # to start again the first circle needs to be pressed
    while True:
        if mouse1.isPressedIn(circle1):
            break

    if mouse1.isPressedIn(circle1):
        start_time = core.getTime()
        #check if we neeed to perturb
        perturbapplied = False # is the perturbation applied?
        while True:
            mouse_pos = mouse1.getPos()              # get the current position of the mouse
            mouse_time_series_x.append(mouse_pos[0]) #get the x position of the mouse and save in list
            mouse_time_series_y.append(mouse_pos[1]) #get the y position of the mouse and save in list
            mouse_time.append(core.getTime() - start_time) #get the time and append to list

            #buttons = mouse1.getPressed() #only left clicks now allowed
            #do perturbation
            if (perturbations[i]) != 0 & (perturbapplied == False):
                if(mouse_pos[0]>0):
                    circle1, circle2 = createcircleset(location2y = perturbations[i], size1=radius2, size2=radius2)
                    circle1.draw()
                    circle2.draw()
                    win.flip()
                    perturbapplied = True
            if mouse1.isPressedIn(circle2):
                next = True
                buttons, times = mouse1.getPressed(getTime=True)
                # write time series data
                with open('./data/time_series/ppn_' + str(ppn) + '_trial'+str(i)+ '.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['time', 'x', 'y'])
                    writer.writerows([mouse_time, mouse_time_series_x, mouse_time_series_y])

            if (next == True):
                # Draw the stimuli to the window
                task_text.draw()
                yes_text.draw()
                no_text.draw()
                win.flip()
                # Wait for a response
                response = None
                correct = False
                while response is None:
                    if mouse1.isPressedIn(yes_text):
                        response = True
                        if response & perturbapplied:
                            correct = True
                    elif mouse1.isPressedIn(no_text):
                        response = False
                    perturbation_correct.append(correct)
                break

    #collect data
    perturbation_yn.append(perturbapplied)
    trailindex.append(i)
    radius_tr.append(radius2)


#end screen with some statistics
endtext = 'there were ' + str(sum(perturbation_yn)) +' perturbations: ' + ' \n and you catched ' + str(sum(perturbation_correct)) + '\n \n saving your data now'
ft = free_text(endtext, win=win)
ft.draw()
win.flip()
core.wait(5)
win.close()

#also write the data to a dataset
with open('./data/'+ppn + '.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(cnames)
    writer.writerows([trailindex, radius_tr, perturbation_yn, perturbation_correct,perturbations])
