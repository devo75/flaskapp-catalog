# Catalog Project for Udacity's Full Stack Web Developer Nanodegreee Program
Using python and flask it was the goal of this project to develop a web application that creates a list of items for a category.  Utiliziting Google authentication, authorization and CRUD operations, the user has the ability to create, read, update and delete the categories or the items they create. 

##Initial Setup
In order to be able to run this project, you will have to have a VirtualBox and Vagrant installed on your system.
To install VirtualBox visit (https://www.virtualbox.org/) 
To install Vagrant visit(https://www.vagrantup.com/)

##Running the Application
Once you have completed the initial setup you will need to run the virtual machine. Inside the terminal you need the change into the directory where you have stored the project using the cd command and then in the vagrant directory. Now type vagrant up to start your virtual machine.

Once your virtual machine is running, you need to log in by typing vagrant ssh.

Next, you need to cd /vagrant and then using cd command to change in the project directory.

From here, create the database using python database_setup.py

Populate the database using python campgrounds.py

Run the application using python application.py

With the application running, in your browser go to (localhost:5000) to see the application in action.

##Closing the Appl;ication
To exit out of vagrant, you need to first CRTL C to stop the application, then type exit and when prompted type vagrant halt.





