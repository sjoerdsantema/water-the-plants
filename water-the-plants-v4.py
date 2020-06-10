import urllib.request, urllib.parse, urllib.error, json, ssl, logging, time
import RPi.GPIO as GPIO 
from time import sleep 

# add all gpio pins of relays in order(!) 
relay_pins = [16, 18]
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
for number in relay_pins:
    GPIO.setup(number, GPIO.OUT, initial=GPIO.LOW) 

# information on the pump capacity
litre_per_minute = 12
litre_per_second = litre_per_minute / 60

# set logging formatting
logging.basicConfig(filename='water-the-plants.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# values for the API
api_key = "4546b131d1"
service_url = "http://weerlive.nl/api/json-data-10min.php?"

# construct the url
parms = dict()
parms['locatie'] = "Amsterdam"
parms['key'] = api_key
url = service_url + urllib.parse.urlencode(parms)

# functions to set level
def run_pump(period):
    logging.info('watering the plants for %s seconds', period)
    total_water_pumped = litre_per_second * period
    print(f"pumping for {period} seconds")
    GPIO.output(16, GPIO.HIGH) 
    sleep(period)
    GPIO.output(16, GPIO.LOW) 

def calculate_period(temp):
    print(f"it is max {temp} celcius degrees today")
    pump_run_secs = 3
    if temp > 5:
        pump_run_secs += 3
    if temp > 18:
        pump_run_secs += 3
    if temp > 25:
        pump_run_secs += 3
    if temp > 35:
        pump_run_secs += 3
    if temp < 5:
        pump_run_secs = 0
        logging.warning('It could be freezing!')
    return pump_run_secs    
    
try:
   # get JSON
    uh = urllib.request.urlopen(url, context=ctx) # collect data
    data = uh.read().decode()
    js = json.loads(data)
    logging.info('Received JSON')  

    # setting the values
    max_temp_today = float(js['liveweer'][0]['d0tmax'])

    # calculate how long the pump runs
    period = calculate_period(max_temp_today)

    # run the pump
    run_pump(period)
except Exception as e:
    print('Oops! Something went wrong!')
    print(e)
    logging.warning(e) 
finally:
    print("job done, goodbye")


   
