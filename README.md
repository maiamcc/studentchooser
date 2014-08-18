Student Chooser
===============
This program was written in my second week of (Hacker School)[https://www.hackerschool.com/], and is my first project in Python! I wrote it at the suggestion of a teacher friend of mine, who wanted a fair way to call on her students at random (for putting homework problems on the board, etc.).

Think of this as the high-tech version of drawing a popsicle stick with a student's name on it. The downside to popsicle sticks is that a student is either in the pile or out of the pile--they either have the same chance of being drawn as anyone else, or a 0% chance of being drawn. This program weights students' probability of being picked based on the number of times they have been picked previously, so a student who has been chosen before is _less_ likely to be chosen again, but still in the running. (This means that being called on once is no guarantee of not being called on again, which will hopefully throw the fear of god into the students and encourage them to keep up with their homework or what have you.)

Files Needed
------------
To run this code, you need the Python file *studentchooser.py*, plus an empty config file, *config.txt*. (Soon, code will be updated to create a config file for you if one doesn't exist, but for now, you need to make your own.)

About the Program
-----------------
### Objects and Data Storage

A *student* is a custom object with the following attributes:

	* `name` - the student's name
	* `prob` - the student's probability of being selected. All probabilites begin equivalent (set to 1, then scaled with `scale()`), and are decreased by the `prob_changed` factor each time the student is picked.
	* `times_picked` - the number of times the student has been picked. Used to calculate adjustments to each student's probability.
	* `absent` - a Boolean stating whether the student is absent. Absent students (`absent=True`) are not considered for selection until their absence status has changed.

A *roster* is simply a collection of students, stored in a dictionary for easy access.

The contents of each roster is stored in a text file (with a name defined by user on creation of the roster). A list of all the roster files is contained in the config.txt file.

### Mechanics: Choosing a Student
Recall that each student has an associated probability value, and that the probability values of all the students in a class are scaled to sum to 100.

The program selects a student by picking a random number between 0 and 100. The students, in the order that they appear in the dictionary, are each allocated a chunk of the number line according to their probability. The program selects the student who owns the section of the number line into which the randomly generated value falls.

E.g., suppose students A (prob=30), B (prob=40), C (prob = 15) and D (prob = 15). The break-down of the number line is as follows: 0-30 belongs to A, 30.0001-70 to B, 70.0001-85 to C, and 85.0001-100 to D. So, if the random number is 74, the program will select C.

Note that when a student is marked absent, they are not considered for selection. The probabilities of all other students are adjusted accordingly.

### Mechanics: Scaling
After action that alters the relative probabilities of students in consideration, the roster is scaled with `scale()`.

Recall that `prob_change` is a fraction by which probability is adjusted for each time selected. E.g., if `prob_change = 3/4`, a student selected once will only be 3/4 as likely to be selected again.

In the `scale()` function, all students' probabilities are set back to 100, and then multiplied by the `prob_change` factor for every time the student has been picked, as tracked in their `times_picked` attribute.  (So, `100 * prob_change ** (Student.times_picked)`). Then, the program looks at all of the present students, sums their probabilities, and multiplies each probability by `100/total` -- that is, scaling all of the present students' probabilites to sum to 100.

### Flowchart of Program Execution

Program started!
> 1. make new roster, 2. load existing roster"
	1. New roster: user inputs a title for the roster, and names of all students in the class). Initially, all students have equal probabilities of being
	2. Existing roster: program displays a list of existing rosters, as found in the config.txt file; user selects one to load)
		- When existing roster is loaded, program displays a list of students who were absent the last time the user ran the program.
- Option to take attendance (i.e. input names of absent students)
> 1. pick, 2. input absences, 3. view roster, 4. add student(s), 5. switch classes, 6. exit
	1. Pick: program selects a student with the method described above, asks the user for confirmation. If user does not confirm, program chooses again.
		- If user confirms, program returns the student's name and increases student's times_picked count, and scales the probabilities of all the present students.
	2. Input absences: user inputs all absent students, one at a time.
	3. View roster: program displays the roster, including number of times picked and an indicator of whether each student is absent.
	4. Add student(s): user inputs students to add to roster.
	5. Switch classes: user saves any changes to current roster and switches to a different one. (User is given the option to make a new roster or load an existing one.)

Next Steps
----------

* Currently, the program won't run if there isn't an existing config.txt file in the directory. This is puzzling, since `open(file, "w")` ought to create a new file if none exists.
* Streamline code by using `with filename as infile:` etc. rather than opening and closing files separately.
* Organize code with more custom objects, and custom methods within those objects--e.g. methods within a Roster object--to eliminate confusion over global/local variables when trying to change the state of the program.