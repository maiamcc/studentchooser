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
roster_master_list = "all_rosters"

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
        reg_output = "%s: chosen %d time(s)" % (self.name, self.times_picked)
        absence_output = " (absent)"
        if self.absent:
            return reg_output + absence_output
        else:
            return reg_output
    def to_file(self):
        # for file storage
        return "%s; %f; %d; %d" % (self.name, self.prob, self.times_picked, self.absent)

class Roster(dict):
    ### CREATION, SAVING, PRINTING ###
    def __init__(self, name, new=True):
        # note; expects 'name' to be same as filename
        super(Roster,self).__init__()
        self.name = name
        self.new = new
        if new:
            """Makes a new roster (names the roster; asks for list of students; populates roster)."""
            students = make_student_list()
            for name in students:
                self[name] = Student(name)
            self.scale()
        else:
            """Populate roster with the data in a given file.
            Each line of data should be in format: 'name; prob; times_picked; absent'."""

            with open(self.name) as infile:
                for line in infile:
                    this_line = line.split("; ") # make each line into list

                    name = this_line[0]
                    prob = float(this_line[1])
                    times_picked = int(this_line[2])
                    absent = bool(int(this_line[3]))

                    self[name] = Student(name, prob, times_picked, absent)

            # prints students who were absent last time the program was run
            self.last_absent()

    def __str__(self):
        """Prints contents of roster in user-friendly format."""
        output = ["Current roster: %s" % self.name]
        output.extend(["\t%s" % self[kid] for kid in self])
        return "\n".join(output)

    def save_to_disk(self):
        """Saves the roster to disk, in a text file with its same name. If the roster is new,
        also adds it to the master list of rosters."""

        # write this roster to corresponding text file
        with open(self.name, "w") as outfile:
            for kid in self:
                outfile.write(self[kid].to_file())
                outfile.write("\n")

        # if this is a newly created roster, add the file name to the list of
            # roster files in the "config" file
        if self.new:
            roster_list = get_all_rosters() # list of all roster files
            roster_list.append(self.name) # add this roster to list
            roster_list.sort(key=string.lower) # alphabetize list

            with open(roster_master_list, "w") as outfile:
                # write list of all roster files to the master list of rosters
                for roster in roster_list:
                    outfile.write(roster)
                    outfile.write("\n")

    def add_to_roster(self, input_list):
        for kid in input_list:
            if self.get(kid):
                # if student is already in the roster, don't add a duplicate, print an error instead
                print "ERROR: '%s' is already in your roster." % kid
            else:
                # create a new Student object in the roster
                self[kid] = Student(kid)

    ### CHOOSING ###
    def pick_a_kid(self):
        """Return a student picked from roster according to probability distribution.
        (Each student's probabibility is adjusted according to number of times picked.)"""
        value = random() * 100 # random value between 0 and 100
        startpoint = 0
        endpoint = 0

        present_students = [kid for kid in self if not self[kid].absent]

        for kid in present_students:
            # increase endpoint by this student's probability
            endpoint += self[kid].prob

            if (startpoint <= value <= endpoint):
                chosen = kid
                break
            else:
                # increase startpoint by this student's probability
                startpoint += self[kid].prob

        return chosen

    def scale(self):
        """Adjust all students' probabilities, scale to sum to 100."""
        # set all prob's back to scale to 100
        for kid in self:
            self[kid].prob = 100 * prob_change ** (self[kid].times_picked)

        # for all kids who are present, adjust prob. by # of times picked, then scale
        total = 0
        present_students = [kid for kid in self.values() if not kid.absent]

        for kid in present_students:
            total += kid.prob
        for kid in present_students:
            kid.prob *= 100.0 / total

    def choose(self):
        """The entire student selection process, including confirmation and output."""
        while True:
            # pick a student
            the_student = self.pick_a_kid()

            # ask for confirmation
            confirmation = confirm(the_student + " was selected. OK? y/n")

            if confirmation: # if the user confirms
                self[the_student].times_picked += 1 # adjust student's "times_picked" counter
                break
            elif not(confirmation): # if user does not confirm
                print "OK, choosing again." # run the loop again (i.e. pick again)

        self.scale()

        print "Selected:", the_student
        return the_student

    ### ATTENDANCE ###
    def take_attendance(self):
        """Asks user to input absent students, passes these students to mark_absent()
        to change their status to "absent"""
        # reset all students to "present"
        for kid in self.itervalues():
            kid.absent = False

        # ask user to input absent students
        print "Input absent students one at a time, hitting RETURN after each. For example:"
        print "\tAbraham \n\tBeelzebub \n\tCain"
        print "Remember, you must input your students' names exactly as the appear on the roster."
        print "As a reminder, your roster is:"
        for kid in self:
            print "\t", kid
        print "When you're done (or if no one is absent), just press 'RETURN'"

        absent_list = []

        while True:
            answer = ask()
            if answer != "": # if answer is not a blank line
                if self.get(answer): # if answer is in the roster (i.e. valid student name)
                    absent_list.append(answer) # add to absent list
                else:
                    print "Not a vaild student name, please try again."
            else: # if the user enters a blank line, end the loop
                break

        # show the user-entered list, ask for confirmation
        print "You said the following students are absent:"
        print "\t", "; ".join(absent_list)

        confirmation = confirm()

        if confirmation:
            # if user confirms, set specified students to "absent"
            for kid in absent_list:
                self[kid].absent = True
            self.scale()
        elif not(confirmation):
            # if user does not confirm, ask again
            self.take_attendance()

    def last_absent(self):
        """Print names of the students who are absent.
        (Because this is called when the roster is first loaded, it assumes it is displaying those
        students who were absent last time user ran the program.)"""

        absent_students = "; ".join(sorted([kid for kid in self if self[kid].absent], key=string.lower))

        print "Students absent last time:"
        print "\t", absent_students


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
def get_all_rosters():
    """"Return a list of all of the roster filenames in the config file."""
    with open(roster_master_list) as all_rosters_file:
        return sorted([line.strip() for line in all_rosters_file], key=string.lower)

###### RAW-INPUT / STATE-CHANGE FUNCTIONS ######

### ATTENDANCE ###

### CHOOSING ###

### ROSTERS (MAKING AND UPDATING) ###

def make_student_list():
    """Return a list of students according to user input."""

    print "Input students one at a time, hitting RETURN after each. For example:"
    print "\tAbraham \n\tBeelzebub \n\tCain"
    print "Remember, you must input your students' names exactly as the appear/as you wish them to appear on the roster."
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
    print "\t", "; ".join(temp_students_list)

    confirmation = confirm()

    if confirmation: # if user confirms
        return temp_students_list # return the list
    elif not(confirmation): # if user does not confirm
        return make_student_list() # ask again for input

def make_new_roster():
    while True:
        # name the text file in which this roster will be stored
        print "Enter a name for this class."
        class_name = ask()

        try:
            all_rosters_list = get_all_rosters()
        except IOError:
            # the roster_master_list file doesn't exist yet, so we should make it.
                # (It contains nothing, so the list of all rosters is empty.)
            open(roster_master_list, 'a').close()
            all_rosters_list = []

        if class_name in all_rosters_list:
            print "ERROR! This class name already exists. Please try again."
        else:
            return Roster(name=class_name, new=True)

### DATA ###

##### LARGE-SCALE FUNCTIONS #####

def new_or_load():
    """Ask the user if they want to make a new roster of load an existing one."""

    while True:
        print "1. make new roster, 2. load existing roster"
        answer = ask()

        if answer == "1":
            return make_new_roster()

        elif answer == "2":
            # set "current roster" equal to roster loaded by user
            return load_roster_from_disk()

        else: # if user input invalid, run loop again
            print "Sorry, I didn't get that. Try again."

def load_roster_from_disk():
    """Load a roster from file."""
    # make list of all rosters in config file
    roster_list = get_all_rosters()

    if len(roster_list) == 0: # if list is empty, make a new roster instead
        print "No rosters available to load. Make a new one instead."
        return make_new_roster()

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
                roster_to_load = roster_list[index]
                print "File to load:", roster_to_load

                return Roster(name=roster_to_load, new=False)
            else: # if user input isn't in range or isn't an integer
                print "Sorry, I didn't get that. Try again."

def add_students(current_roster):
    students_to_add = make_student_list()
    current_roster.add_to_roster(students_to_add)

def exit(current_roster):
    current_roster.save_to_disk()
    sys.exit()

def main():
    """Main user interface function from which all other functions are called."""
    print "Hello, and welcome to Student Chooser."

    cur_roster = new_or_load()

    # Does user want to take attendance?
    answer = confirm("Take attendance now? y/n")
    if answer:
        cur_roster.take_attendance()

    while True:
        print "1. pick, 2. input absences, 3. view roster, 4. add student(s), 5. switch classes, 6. exit"
        answer = ask()
        if answer == "1":
            cur_roster.choose()
        elif answer == "2":
            cur_roster.take_attendance()
        elif answer == "3":
            print cur_roster
        elif answer == "4":
            add_students(cur_roster)
        elif answer == "5":
            cur_roster.save_to_disk()
            cur_roster = new_or_load()
        elif answer == "6":
            exit(cur_roster)
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