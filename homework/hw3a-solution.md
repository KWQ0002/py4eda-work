# HW3A Solution - Git and Version Control
## Part 1: Repository Cloning
I successfully cloned the class repository from `https://github.com/olearydj/INSY6500` to
`~/insy6500/class_repo`.
6
### Key Commands Used
- `git clone <url>` - Create local copy of remote repository
- `git log` - View commit history
- `git remote -v` - Check remote repository connections
## Part 2: Portfolio Repository Creation
I created my personal course repository with:
- Professional README.md describing the project
- Proper .gitignore to exclude unnecessary files
- Organized directory structure for homework, projects, and notes
### Understanding Git Workflow
The three-stage workflow:
1. Working Directory: Where I edit files
2. Staging Area: Where I prepare commits with `git add`
3. Repository: Where commits are permanently stored with `git commit`
## Part 3: GitHub Publishing
Successfully published repository to GitHub:
- Used `git remote add origin` to connect local repo to GitHub
- Used `git push -u origin main` to upload commits
- Verified all files and commits are visible on GitHub
### The Remote Connection
My local repository is now connected to GitHub:
- `git remote -v` shows the remote URL
- `git push` will send my commits to GitHub
- `git pull` will get updates from GitHub (if changes are made on GitHub)
### Details
Complete this section with details from your setup:
- Repository URL: https://github.com/KWQ0002/py4eda-work
- Output of `git remote -v`:
origin  https://github.com/KWQ0002/py4eda-work.git (push)
origin  https://github.com/KWQ0002/py4eda-work.git (fetch)
- The output of `git log --oneline`:
56f9f53 (HEAD -> main, origin/main) Add hw3a solution document
c9d9ca3 Initial commit: Add README and .gitignore
### Reflections

Question 1: Git Workflow Benefits You’ve now experienced the basic Git workflow: edit
files, stage changes, commit with messages, and push to GitHub.

a) Before this assignment, how did you typically manage different versions of your work (e.g.,
assignments, code, documents)? Compare that approach to using Git. What are 2-3 specific
advantages Git provides?

Undergraduate school assignments were managed through classic copy and paste and put the date in the name methods. Professionally in medical device product development document control systems are used to track the version history of different documents.
Git provides:
1. A way to conveniently commit and store your versions without having to manually save a new version each time on your system
2. A way to roll back if something has gone wrong in your project
3. A standardized documentable workflow that people can be trained on and work collaboratively

b) Describe a situation from your academic or professional work where Git’s commit history
would have been valuable. What problem would it have solved?

Understanding what was changed at different times. I ran into an issue in my career before where a new set of deliverables were added to an SOP but the update to the SOP did not call out that they were included in the update in the change lot. It could have given more context provided someone puts in nice comments.

Question 2: Repository Organization You now work with two repositories that serve different
purposes:
• class_repo - cloned from the instructor, read-only reference
• my_repo - your own work, pushed to GitHub
a) Explain why it’s important to keep these separate. What would happen if you tried to put
everything in one repository?

The class repo should remain as a source material for the students to make sure we have the same ground level truth. Whereas the individual repos that the students are pushing is reflective of the work that we are doing. It would not be good if students could write to the class_repo and modify the original files. Git also does not allow for you to have 
multiple repositories tied to a single directory. 

b) Think about your future coursework or projects. Describe how you might organize multiple
repositories. For example, how would you handle a group project versus individual assignments versus reference materials?
Individual assignments make sense to keep in my project created in this assignment, a group project could benefit from being stored in a purpose set up project, references materials will probably stay in the class_repo and then be copied into my project created in this assignment for modification.

Question 3: Commit Messages and History Look at the commit messages you wrote during
this assignment (use git log --oneline if needed).
a) Compare these two commit messages:
• “update”
• “Add hw3a solution documenting Git workflow and repository structure”
Which is more useful? Why? When might you need to find this commit again in the future?
If you would like to learn more about best practices for these important messages, you might be
interested in:
• The Conventional Commits specification - a popular convention where commits start with
prefixes like feat:, fix:, docs: to enable automation
• How to Write a Git Commit Message - a comprehensive guide to writing effective commit
messages

The second comment is more useful. Innevitably when someone (which might be you) need to go back and determine what has happened they will appreciate the improved comments which also don't take much more effort.


b) Imagine you’re working on a data analysis project over several weeks. Describe how you would
decide when to make a commit. What makes a good “unit of work” for a single commit?

There are several factors that play into this, how much work are you willing to potentially lose to drive failures or other things. Have you completed a succint module or sub module of what you were trying to attempt. For example if you are trying to sanitize all of the data to be plotted into a particular type of chart maybe you have completed a function that does the plotting and you that would be a good point, same for completing the portion of sanitizing data. To give an extremely vague and nebulous answer if you are working on it consistently and nearly full time once or twice a week would be a minimum.

### Graduate Questions

Understanding Git Concepts (10 points, Graduate Only)
Graduate students: Add a sub-section titled “### Graduate Questions” with concise answers to
the following:
Question 1: The Three-Stage Model Git uses three stages: Working Directory → Staging
Area → Repository. Many version control systems skip the staging area and commit all changes
directly.
Without a staging area, you’d have to commit everything at once with a message like “various
updates” - making it hard to understand your history later. The staging area lets you review and
organize your changes before committing, creating a clean, understandable history where each
commit represents one logical change.
a) Think about the work you did in this assignment. You created README.md, .gitignore, and
hw3a-solution.md. Why was it valuable to commit the README and .gitignore together
first, then commit hw3a-solution.md separately later? What would have been lost if you’d
committed everything at once?

Some readability is lost with doing large commits. Doing the README and .gitignore together can be thought of as a "setup" of your repository, then the adding of the solutions document is the first task or deliverable that is being done. The multiple comment sections around the commits allows for you to be more thoughtful without having to find a way to visually separate between the different sections that were being worked on.

b) Imagine you’re working on a homework assignment over several days. You:
• Write code to load data
• Start working on a new analysis function (half-finished)
• Fix a typo in a comment
• Update your README
Which of these changes should you commit now, and which should you wait on? Why? How
does staging help you make this decision?

If I am working solo I would commit the code to load the data now and the others could wait. When the analysis function is completed I would commit it, unless it is extremely complex and can be neatly divided into sub functions then I may commit it sooner if I can get 6 out of 10 sub functions working (To a point where something is distinctly testable).  The typo and update to the README are things I'd likely batch together and commit at what feels like the right time. Maybe I just commited the analysis function in one commit it may be a good time to update the project documentation in a second distinct commit.

c) Explain how git status helps you make decisions about what to stage and commit. When
in your workflow should you use it?

git status is useful when you are getting ready to determine what should be in your next commit and want to view what has changed. With my limited experience status would be part of an overall "commit" workflow. Check which files you have in your directory now and make sure you want to add them, gitignore or delete as necessary.

Question 2: Local vs. Remote Repositories You experienced both local repositories (on
your computer) and remote repositories (on GitHub).
a) Git is described as a “distributed” version control system. Based on your experience with
class_repo and my_repo, explain what this means. How is it different from just storing files
in Google Drive or Dropbox?

The version control system allows for detailed notes and commits at a project level. If you were dealing with a series of files on a google drive you could see when last edited and I think it does have a history but it lacks comments and the intentionality of the version control system. You also have a complete and independent version of the project on your system with the version control system. Basic drive storage also doesn't have much in the way of merge functionality so you may accidentally blow away someone elses work.


b) You can work on your local repository (my_repo) even without an internet connection - making
commits, viewing history, etc. Then later you can git push to sync with GitHub. Explain
why this architecture is valuable for developers. What workflows does it enable?

It allows for asynchronous work. Each thing completed can be committed at different points throughout the day or whatever the logical time frame is for the commits, then pushed to GitHub later in a clean concise manner that allows for relevant people to consume the different commits that were done. A bugfix may be picked up by testers, whereas another developer may need to interface with a new function you have written etc.


c) Describe the relationship between git clone, git pull, and git push. Why can you pull
from class_repo but not push to it, while your my_repo allows both?

git clone is if you want to create a working copy of a directory without risking changing the original. git pull is grab updates. git push sends out the updates that you have made so others can consume them. If students were allowed to push to class_repo we may accidentally manipulate existing files and Dan would lose control over the files and have to spend more effort making sure people didn't touch anything they shouldn't have.

Question 3: Professional Portfolio You’ve created a public repository on GitHub that will
be visible to potential employers or collaborators.
a) Throughout the remainder of this course, you’ll add more work to this repository. What
should you consider when deciding what to commit? How do you balance showing your work
process (including mistakes and iterations) versus presenting polished final products?

Making sure not to commit so frequently that the value of the comments and changes are lost. It may be advantageous to show more of the individual thought process in this course than the professional world specifically to demonstrate how you think and work through problems. Hiring managers will have an opportunity to discuss this with you in the interview process but if there is already demonstrated work that can show your thought process that can add benefits. It also needs to be balanced with this is a coure I'm trying to complete for a degree this isn't my entire CV.

b) Your README.md is the first thing people see when they visit your repository. What makes
a README effective for a portfolio repository versus a README for an open-source project
someone might want to use?

If I am writing it for a professional environment I want it to reflect someone on who I am, why I'm doing what I'm doing and try to demonstrate a little bit of soft skills with overall communication not just technical communication. If I am working on something that is open-source and meant to be used by others I would write in a much more technical communication style and not feel the need to provide anything personal about myself. If I want to be contacted with questions/comments include an email address otherwise focus on here are the explicit functions, here are the inputs it needs, here are the outputs it provides etc. Maybe also lead with a TLDR section depending on complexity.

c) Reflect on the value of building this public portfolio during your coursework rather than
waiting until you’re job searching. What habits should you develop now to make this portfolio
valuable later?

Starting it at this point gives a direct demonstration of what was done, it should also show increasing complexity and adaptability instead of just dumping a final version of a school project out there. It should build the habit of being able to clearly communicate what I was working on and what I have changed and demonstrate that. It also gives different demonstrations on how I communicate through code and other things that aren't person to person communication.
