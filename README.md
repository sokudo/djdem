# djdem
Generate and plot multiple data streams.

Generates streams of data items with fields. Fields are typed. 
What and when to generate is defined dogen/dogen_data.py:CHANNEL_CONFIG. May add
YAML config at some point.

JavaScript code is generated from Python. Google Visualization API is used to
plot data.

# How to run.
# Start MySQL.
# Start dev Django server.
python manage.py runserver

# Print data as a table.
http://127.0.0.1:8000/show/table/

# Show different plots.
http://127.0.0.1:8000/show/
http://127.0.0.1:8000/show/m/
http://127.0.0.1:8000/show/s/
