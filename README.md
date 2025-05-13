# CITS3403_PROJECT

# 📈 Productivity Tracker

### _Track. Analyze. Improve._

#### Description

**Productivity Tracker** is a web application designed to help students and professionals optimize their learning and productivity by tracking their study/work hours and task goals. Users can input data manually, and the system provides insightful analysis on focus trends, peak productivity times, and areas for improvement.

The dashboard highlights:
- Daily/weekly/monthly study durations
- Subject-wise efficiency
- Personalized productivity trends

This application motivates users by giving them clear visual feedback and enables sharing progress with peers or mentors.


| UWA ID     | Name          | GitHub Username   |
|------------|----------------|-------------------|
| 23718161   | Tiselle Rayawang    | TiselleWang       |
| 24215747   | Trisha Santillan     | ToriCodie          |
| 23808253   | Kai Fletcher  | k-train-money        | 
| 23236855   | Ruben ho Ho	  |  Rbho10       |

A user.db database has been created to store user's credentials in a secure manner. Passwords are stored in the form of hash (password + salt) in the database.

The code will be stored in a zip folder. Unzipping the folder will decompress the contents of the folder. 

Steps to reproduce/run the code:
1. Create and activate a virtual environment by running the command: `python3 -m venv protrackenv` 
Then access the virtual environment On Mac: `source protrackenv/bin/activate` On Windows: `protrackenv\Scripts\activate`
2. Install the dependencies by running the command: `pip install -r requirements.txt`.
3. Set up the flask environment by `export FLASK_APP=run:app` and `export FLASK_ENV=development` for development or `export FLASK_ENV=testing` for testing to run the flask app instance later.
Make sure `python-dotenv` is installed in your virtual environment. This will automatically load the .env file which contains your OpenAI API Key and secret key. This has been safely ignored through .gitignore file so that the key won't be exposed to the public repository.
5. Create an OpenAI Account via https://platform.openai.com/
6. Follow prompts and create an API key by entering API Key Name, and enter a project name. Copy the API Key once generated.
7. Create an empty `.env` file in the project's root directory. 
8. In the `.env` file, paste the line `OPENAI_API_KEY=sk-...{your api key}`. Also,create a `SECRET_KEY={your secret key}` for taking user input through flask-WTF forms. After these two variables have been inserted, save the file. The `python-dotenv` that has been installed in your virtual environment will automatically treat this as environment variables of the os and will then be used in the respective python codes (i.e. generate_insights.py, addSession.html).
9. Run the application: `flask run`. This will only work if you set up the `FLASK_APP` environment variable to point to your flask application instance.


