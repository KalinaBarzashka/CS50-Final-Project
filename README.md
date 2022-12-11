## CS50-Final-Project
My final project for CS50 Harvard course.

### Table of Contents
- 1 National Monuments
  - 1.1 Overview
  - 1.2 Functionalities
- 2 Architecture
- 3 Technology Stack

# NationalLandmarks
  
The software is powered by flask library and supports SQLite database. The front-end part is implemented via pure HTML, CSS and Bootstrap. The project overview, functionalities, architecture and technology stack is reviewed bellow.  

## :pencil: Overview
The idea of the website is to contain the general information for all the USA's national monuments. Here all citizens and tourists can get familiar with the monuments, check their location and some other interesting information. If the digital visitor do not register, he/she will not be able to take a look of all the USA monuments and mark them as visited.
# How can you register?
Register online in a few simple steps by visiting the website page. Submit your:   
:pushpin: User Name  
:pushpin: Password  

After you register successfully, you will become a user and you will be able to:  
:pushpin: List all monuments  
:pushpin: List all states  
:pushpin: List all agencies  
:pushpin: Visit monuments  
:pushpin: Rate monuments  

## :computer: Functionalities  
#### :pushpin: Monuments Page  
On this page you can see the full list of the USA's national monument. Only admin can edit and delete monuments. Accessible only for registered users.  
#### :pushpin: Create Monument Page  
On this page you can submit new Monument objects to the database. Accessible only for admin users.  
#### :pushpin: Approve Monument Page  
Accessible only for admin users.  
#### :pushpin: Visited Monuments Page
On this page you can see the monuments, visited by the current user, his grade for the landmark and date of visit. Accessible only for registered users.  
#### :pushpin: Monuments Details Page  
On this page you can read summary for monument of your choise and some other details. Here, you can also rate and visit the place. Accessible only for registered users.  
#### :pushpin: Agencies Page  
On this page you can see the full list of the USA's agencies. Only admin can create, edit and delete agencies. Accessible only for registered users.  
#### :pushpin: States Page  
On this page you can see the full list of the USA's states. Only admin can create, edit and delete states. Accessible only for registered users.  

## :hammer: Architecture
The project architecture is accomplished using modern approaches in web development. The application is build using lightwight python framework - Flask, utilizing the folder-by-feature architecture for the html and css files.  
The authentication functionality is implemented via session storage, and the authorization is made via custom decorators.  

## :gear: Technology Stack
- Python, Flask, session storage  
- SQLAlchemy, WTforms  
- SQLite  
- HTML, CSS, Bootstrap  