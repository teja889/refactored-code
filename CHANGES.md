Refactored the code

what i identified as a major issues

number 1:

--- security flaws --------

SQL injection: All database queries arre constructed using f-strings, which can be explioted if malicious input was passed

Plaintext password: A major security breach

sensitive data expose: endpoints returnned full user data, including password hashes

number 2:

--------- quality of code, and design issues--------------

Global DB connection: code used a single, global database connection (conn, cursor) for all requests this is not thread-safe

poor API responses: Responses weree returned as plain strings instead of JSON and status codes aree misused, even failed operations returned 200 OK

No Input Validation: code blindly trusting incoming JSON data

structure was not good: All logic was crammed into a single file with no modularization which hurts readability

       -------------changes i made and why-----------------

I focused on stabilizing the app, improving security, and making it more RESTful

----- security improvements -----

"Parameterized Queries": Replaced all f-string based SQL queries with parameterized queries (using ? placeholders), This is the standard, secure way to pass data to database, completely eliminated all SQL injection vulnerabilities

"Password Hashing": Implemented password hashing using werkzeug.security:
generate_password_hash() is used in the POST /users route to securely store new passwords
check_password_hash() is used in the POST /login route to safely compare the provided password against the stored hash without ever exposing the original

"Removed Password Hashes from Responses": Modified the SELECT queries in get_all_users, get_user, and search_users to explicitly request only id, name, and email, preventing the password hash from ever being sent to the client

------ best practices are: ---------
JSON Responses: All API responses are now correctly formatted as JSON using jsonify() this is the standard for REST APIs
Implemented appropriate status codes for all outcomes
Created a get_db_connection() helper function, each route now gets its own dedicated database connection and closes it when done
Routes now use request.get_json() with try...except to handle bad JSON and return 400 instead of crashing
improved readability by accessing database columns by name

------- Assumptions and Trade-offs ----------

Assumption: The goal was to refactor within the existing structure, so i kept everything in app.py but made it much more robust
trade-off: I avoided using Flask blueprints or SQLalchemy to keep things simple and meet the "Don't over-engineer" requirement

--------- what i would do with more time ------------
With more time, I’d use Blueprints for route separation, switch to SQLalchemy, externalize configs, and add tests with pytest

--------- this is where i used ai for help ----------
Standard HTTP Status Codes for REST APIs: I wanted to make sure I was using proper status codes for different outcomes (like 409 Conflict vs 400 Bad Request), and ChatGPT helped clarify which ones are correct for each scenario.

i have used chatgpt for password security best practices too, it recommended way to hash and verify passwords.
