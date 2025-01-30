# todolist-flask-application
Developing a To-Do List Application using Python Flask Framework

- Description: 
	* This is a To-Do List web application built using the Flask framework which provides users with an easy-to-use platform. 
	* It allows users to manage their tasks by adding, updating, deleting, and searching for them. 
	* The application features user authentication, task categorization, task prioritization, and sends SMS reminders for tasks due the following day.
	* The purpose of the app is to help users keep track of their tasks while ensuring they don't forget important deadlines by sending automatic reminders.

- Features
	1. User Authentication:
		* Sign Up: Users can register with their email, mobile number, and password.
		* Login/Logout: Registered users can log in and log out of the system.
		* Profile Management: Users can view and update their profile information.

	2. Task Management:
		* Create Tasks: Users can create tasks with a title, category, priority, and due date.
		* Update Tasks: Users can mark tasks as completed.
		* Delete Tasks: Users can delete tasks they no longer need.
		* Search Tasks: Users can search for tasks by using keywords in the title
	3. Task Reminders:
		* Due Date Reminders: Users receive SMS reminders for tasks that are due the next day.
		* Twilio Integration: Reminders are sent via Twilio using the Twilio API.

- Explanation of Key Files:
	* app.py: Contains the main Flask application, routes for different pages and different functions used.
	* model.py: Contains the database models for the User and Task objects.
	* templates: Contains HTML templates for the front-end views of the application.
	* static: Contains static assets like CSS files and JavaScript.

- How the Application Works
	1. User Registration and Login
		* When a new user registers, their details are stored in the database. 
		* The application uses Flask-Login to manage the user session. 
		* If a user is logged in, they can create, edit, delete, and search tasks.

	2. Task Management
		* Users can create tasks by specifying a title, category, priority, and due date. 
		* Each task is tied to a specific user. 
		* Tasks can be marked as completed, deleted, or searched using keywords in the title.

	3. SMS Reminders
		* Once a task’s due date is the next day, the APScheduler checks at midnight to send a reminder to the user via Twilio. 
		* A background job uses Twilio's API to send an SMS to the user's registered mobile number.

- Technologies Used
	* Python 3.x: Main programming language.
	* Flask: Lightweight web framework for building the application.
	* Flask-SQLAlchemy: ORM for interacting with the PostgreSQL database.
	* PostgreSQL: Relational database management system for storing user and task data.
	* Twilio: API for sending SMS reminders.
	* APScheduler: For scheduling background tasks to send reminders.
	* Flask-Login: For user session management and authentication.
	* dotenv: For securely loading environment variables (e.g., database credentials, Twilio API keys).

