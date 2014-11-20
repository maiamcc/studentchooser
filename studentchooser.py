from random import random
import sys
import string

### CONSTANTS & GLOBALS ###

# default text in "confirm" function
default_confirm_msg = "Is this correct? y/n"

roster = {}
students = []

# change this value to adjust by how much a student's prob changes when picked
prob_change = 3.0/4.0

# default name of config file (will contain all of the filenames of existing rosters)
config_file = "config"

# tells system whether this roster is new (and so needs to be written into config file on close)
new_roster = True

### CLASSES ###
class Student(object):
    def __init__(self, name, prob=1, times_picked=0, absent=False):
        self.name = name
        self.prob = prob
        self.times_picked = times_picked
        self.absent = absent
    def __repr__(self):
        # for debug
        return "<%s; %f; %d; %d>" % (self.name, self.prob, self.times_picked, self.absent)
    def __str__(self):
        # for user output
        reg_output = "%s: chosen %d times" % (self.name, self.times_picked)
        absence_output = " (absent)"
        if self.absent:
            return reg_output + absence_output
        else:
            return reg_output
    def to_file(self):
        # for file storage
        return "%s; %f; %d; %d" % (self.name, self.prob, self.times_picked, self.absent)


### USER INPUT FUNCTIONS ###

def ask():
    """Return user input."""
    return raw_input("> ")

def confirm(msg=default_confirm_msg):
    """"Convert user input into True or False, return a Boolean."""
    while True:
        print msg
        answer = ask()
        if answer.lower() in ["y", "yes"]:
            return True
        elif answer.lower() in ["n", "no"]:
            return False
        else:
            print "Sorry, I didn't get that. Try again."

### HELPER FUNCTIONS ###

def get_present_students():
    """Return a list of present students."""
    return {kid: roster[kid] for kid in roster if not roster[kid].absent}

def update_student_list():
    """Repopulate and alphabetize student list."""
    # clear student list
    del students[:]

    # populate list of student names and sort alphabetically
    for kid in roster:
        students.append(kid)
    students.sort(key=string.lower)

def display_roster():
    """Prints contents of roster in user-friendly format."""
    print "Current roster:", current_roster_name
    for kid in students:
        print "\t", roster[kid]

def get_all_rosters():
    """"Return a list of all of the roster filenames in the config file."""
    with open(config_file) as all_rosters_file:
        all_rosters_list = []
        for line in all_rosters_file:
            all_rosters_list.append(line.strip())
        all_rosters_list.sort(key=string.lower)

    return all_rosters_list

def student_from_line(line):
    """Returns a Student with the values from a given line of data.
    Data should be in format: 'name; prob; times_picked; absent'."""
    this_line = line.split("; ") # make each line into list

    name = this_line[0]
    prob = float(this_line[1])
    times_picked = int(this_line[2])
    absent = bool(int(this_line[3]))

    # for debug:
    # print "name = %r; prob = %r; times_picked = %r; absent = %r" % (name, prob, times_picked, absent)

    return Student(name, prob, times_picked, absent)

###### RAW-INPUT / STATE-CHANGE FUNCTIONS ######

### ATTENDANCE ###

def mark_absent(abs_list):
    """Mark all students in a given list as \"absent\"."""
    for kid in abs_list:
        if roster.get(kid):
            roster[kid].absent = True
        else:
            print "ERROR! One or more of your names was not recognized. Please try again.\n"
            # (note: this is a failsafe. Theoretically, take_attendance() controls
                #for unrecognized student names)
            take_attendance()

def last_absent():
    """Print names of the students who are absent.
    (Because this is called when the roster is first loaded, it assumes it is displaying those
    students who were absent last time user ran the program.)"""
    absent_list = []

    # iterate through roster, add absent students to (sorted) absent_list
    absent_list = sorted([kid for kid in roster if roster[kid].absent], key=string.lower)

    # make list into string
    absent_string = "; ".join(absent_list)

    # print results
    print "Students absent last time:"
    print "\t", absent_string

### CHOOSING ###

def pick_kid():
    """Return a student picked from roster according to probability distribution.
    (Each student's probabibility is adjusted according to number of times picked.)"""
    value = random() * 100 # random value between 0 and 100
    startpoint = 0
    endpoint = 0

    for kid in get_present_students():
        # increase endpoint by this student's probability
        endpoint += get_present_students()[kid].prob

        # for debug:
        # print "(%f, %f)" % (startpoint, endpoint)

        if (startpoint <= value <= endpoint):
            chosen = kid
            break
        else:
            # increase startpoint by this student's probability
            startpoint += get_present_students()[kid].prob

    return chosen

def scale():
    """Adjust all students' probabilities, scale to sum to 100."""
    # set all prob's back to scale to 100
    for kid in roster:
        roster[kid].prob = 100 * prob_change ** (roster[kid].times_picked)

    # for all kids who are present, adjust prob. by # of times picked, then scale
    total = 0

    for kid in get_present_students():
            total += get_present_students()[kid].prob
    for kid in get_present_students():
            get_present_students()[kid].prob *= 100.0 / total

### ROSTERS (MAKING AND UPDATING) ###

def new_student_list():
    """Return a list of students according to user input."""

    print "Input students one at a time, hitting RETURN after each. For example:"
    print "\tAbraham \n\tBeelzebub \n\tCain"
    print "Remember, you must input your students' names exactly as the appear on the roster."
    print "When you're done, just press 'RETURN'"

    temp_students_list = []

    while True:
        answer = ask()
        if answer != "": # if answer is not a blank line
            temp_students_list.append(answer) # append answer to list
        else: # if the user enters a blank line, end the loop
            break

    # remore duplicates and alphebetize list
    temp_students_list = list(set(temp_students_list))
    temp_students_list.sort(key=string.lower)

    # show the user-entered list, ask for confirmation
    print "You provided the following list of students:"
    student_string = "; ".join(temp_students_list)
    print "\t", student_string

    confirmation = confirm()

    if confirmation: # if user confirms
        return temp_students_list # return the list
    elif not(confirmation): # if user does not confirm
        return new_student_list() # ask again for input

def update_roster(input_list):
    """Given a list of students, add those students to the roster.
    (Can also be used to populate a roster for the first time)"""

    for kid in input_list:
        if roster.get(kid):
            # if student is already in the roster, don't add a duplicate, print an error instead
            print "ERROR: '%s' is already in your roster." % kid
        else:
            # create a new Student object in the roster
            roster[kid] = Student(kid)

def populate_roster(data_file):
    """Populate roster with the data in a given file."""

    # first, clear the roster
    roster.clear()

    with open(data_file) as roster_info:
        for line in roster_info:
            s = student_from_line(line)
            roster[s.name] = s

    # repopulate and alphabetize student list
    update_student_list()

### DATA ###

def save_data():
    """Save any data from the session into the corresponding text file."""
    # open the file associated with this roster
    with open(current_roster_name, "w") as roster_info:
        for kid in roster:
            roster_info.write(roster[kid].to_file())
            roster_info.write("\n")

    # if this is a newly created roster, add the file name to the list of
        # roster files in the "config" file
    global new_roster

    if new_roster:
        roster_list = get_all_rosters() # list of all roster files
        roster_list.append(current_roster_name) # add current file to list
        roster_list.sort(key=string.lower) # alphabetize list

        with open(config_file, "w") as all_rosters_file:
            # write list of all roster files to the document
            for file_name in roster_list:
                all_rosters_file.write(file_name)
                all_rosters_file.write("\n")

##### LARGE-SCALE FUNCTIONS #####

def new_or_load():
    """Ask the user if they want to make a new roster of load an existing one."""

    # clear roster and student list
    roster.clear()
    del students[:]

    while True:
        print "1. make new roster, 2. load existing roster"
        answer = ask()

        if answer == "1":
            return make_new_roster()

        elif answer == "2":
            # set "current roster" equal to roster loaded by user
            global current_roster_name
            current_roster_name = load_roster()

            # print list of students absent last time user accessed this roster
            last_absent()

            # returns name of the class (= name of the file) for display
            return current_roster_name

        else: # if user input invalid, run loop again
            print "Sorry, I didn't get that. Try again."

def make_new_roster():
    """Makes a new roster (names the roster; asks for list of students; populates roster)."""

    # name the text file in which this roster will be stored
    while True:
        print "Enter a name for this class."
        class_title = ask()

        # checks if the given filename already exists in config file
        all_rosters_list = get_all_rosters()
        if class_title in all_rosters_list:
            print "ERROR! This class name already exists. Please try again."
        else:
            # save the given filename as the 'current roster'
            global current_roster_name
            current_roster_name = class_title
            # Boolean saying that this is a new roster
                # i.e. when the program saves data, it will know to add a new
                # filename to the "config" file
            global new_roster
            new_roster = True

            # ask the user for student names, and then make a roster from them
            students = new_student_list()
            update_roster(students)
            update_student_list()
            scale()

            # returns name of the class (= name of the file) for display
            return class_title

def load_roster():
    """Load a roster from file."""

    # Boolean saying that this is NOT a new roster
        # i.e. when the program saves data, it will NOT edit the "config" file
    global new_roster
    new_roster = False

    # make list of all rosters in config file
    roster_list = get_all_rosters()

    if len(roster_list) == 0: # if list is empty, make a new roster instead
        print "No rosters available to load. Make a new one instead."
        make_new_roster()

    else: # if config file contains at least one roster to load...
        print "Which roster would you like to load? Enter a number."

        # print a list of available rosters from config file
        for class_name in roster_list:
            class_name_index = roster_list.index(class_name) + 1
            print "\t%d. %s" % (class_name_index, class_name)

        while True:
            answer = ask()

            # if possible, turn answer from a string into an int.
            try:
                answer_int = int(answer)
            except ValueError:
                answer_int = None

            # if the answer is an int. in the range of # items in the list...
            if answer_int in range(1, len(roster_list) + 1):
                index = answer_int - 1 # (b/c list as displayed is 1-indexed)

                # save the given filename as the 'current file'
                global current_roster_name
                current_roster_name = roster_list[index]
                print "File to load:", current_roster_name

                # populate the roster using the data in the selected file
                populate_roster(current_roster_name)

                # returns name of the class (= name of the file) for display
                return current_roster_name
            else: # if user input isn't in range or isn't an integer
                print "Sorry, I didn't get that. Try again." # run the loop again

def select():
    """The entire student selection process, including confirmation and output."""
    while True:
        # pick a student
        the_student = pick_kid()

        # ask for confirmation
        confirmation = confirm(the_student + " was selected. OK? y/n")

        if confirmation: # if the user confirms
            get_present_students()[the_student].times_picked += 1 # adjust student's "times_picked" counter
            break
        elif not(confirmation): # if user does not confirm
            print "OK, choosing again." # run the loop again (i.e. pick again)

    scale()

    print "Selected:", the_student
    return the_student

def take_attendance():
    """Asks user to input absent students, passes these students to mark_absent()
    to change their status to "absent"""
    # reset all students to "present"
    for kid in roster:
        roster[kid].absent = False

    # ask user to input absent students
    print "Input absent students one at a time, hitting RETURN after each. For example:"
    print "\tAbraham \n\tBeelzebub \n\tCain"
    print "Remember, you must input your students' names exactly as the appear on the roster."
    print "As a reminder, your roster is:"
    for kid in students:
        print "\t", kid
    print "When you're done (or if no one is absent), just press 'RETURN'"

    absent_list = []

    while True:
        answer = ask()
        if answer != "": # if answer is not a blank line
            if roster.get(answer): # if answer is in the roster (i.e. valid student name)
                absent_list.append(answer) # add to absent list
            else:
                print "Not a vaild student name, please try again."
        else: # if the user enters a blank line, end the loop
            break

    # show the user-entered list, ask for confirmation
    print "You said the following students are absent:"
    absent_string = "; ".join(absent_list)
    print "\t", absent_string

    confirmation = confirm()

    if confirmation:
        # if user confirms, set specified students to "absent"
        mark_absent(absent_list)
        scale()
    elif not(confirmation):
        # if user does not confirm, ask again
        take_attendance()

def take_attendance_now():
    """To be run when switching classes: asks user if they want to take attendance now."""
    answer = confirm("Take attendance now? y/n")
    if answer:
        print "Who is absent today?"
        take_attendance()

def add_students():
    new_students = new_student_list()
    update_roster(new_students)
    update_student_list()

def switch_classes():
    save_data()
    new_or_load()

def exit():
    save_data()
    sys.exit()

def main():
    """Main user interface function from which all other functions are called."""
    print "Hello, and welcome to Student Chooser."

    current_roster_name = new_or_load()

    update_student_list()

    take_attendance_now()

    while True:
        print "1. pick, 2. input absences, 3. view roster, 4. add student(s), 5. switch classes, 6. exit"
        answer = ask()
        if answer == "1":
            select()
        elif answer == "2":
            take_attendance()
        elif answer == "3":
            display_roster()
        elif answer == "4":
            add_students()
        elif answer == "5":
            switch_classes()
        elif answer == "6":
            exit()
        else:
            print "Sorry, I didn't get that. Try again."

### TROUBLESHOOTING/TESTING FUNCTIONS ###
def test_always(kid):
    for i in range(0,500):
        the_student = debug_select()
        print "%d: %s" % (i, the_student)
        if the_student != kid:
            print "PANIC!"
            break

def test_never(kid):
    for i in range(0,500):
        the_student = debug_select()
        print "%d: %s" % (i, the_student)
        if the_student == kid:
            print "PANIC!"
            break

def multi_test(x):
    for i in range(0,x):
        print "%d: %s" % (i, debug_select())
        #print roster
        #print "-----------"

def debug_select():
    """A version of the select function that doesn't ask for confirmation."""
    the_student = pick_kid()

    get_present_students()[the_student].times_picked += 1 # adjust student's "times_picked" counter

    scale()

    return the_student

### RUNNING THE PROGRAM ###
if __name__ == '__main__':
    main()