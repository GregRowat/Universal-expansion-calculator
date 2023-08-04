from Planet import Planet
import time
import requests
import json


class Model:

    def __init__(self, planet_data):
        self.planets = []

        # URL for the TAP API endpoint
        url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

        # Construct the query to select all planets that
        query = "SELECT pl_name, pl_bmasse, sy_dist FROM pscomppars WHERE sy_dist IS NOT NULL AND pl_bmasse IS NOT NULL ORDER BY pl_name"

        # Parameters for the API call
        params = {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "json",
            "QUERY": query
        }
        # Make the API call
        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data_list = json.loads(response.text)

                for data in data_list:
                    planet = Planet(name=data['pl_name'], mass=data['pl_bmasse'], distance=data['sy_dist'])
                    self.planets.append(planet)

                # Print the number of planets loaded
                print("Planets Loaded from NASA Exoplanet Archive:", len(self.planets))

            else:
                print("Error: Unable to fetch data from the API.")
                print("Loading Existing Data:")
                # instantiate planet objects to add to the Model list via the CSV data dictionary on initialization
                for data in planet_data:
                    if data['name'] != 'name':
                        planet = Planet(name=data['name'], mass=data['mass'], distance=data['distance'])
                        self.planets.append(planet)
                # Print the number of planets loaded
                print("Planets Loaded from NASA_PRODUCTION.csv:", len(self.planets))

        except requests.exceptions.RequestException as e:
            # Connection error occurred (e.g., no internet connection)
            print(f"Connection Error: {e}\n Loading Existing Data:")
            for data in planet_data:
                if data['name'] != 'name':
                    planet = Planet(name=data['name'], mass=data['mass'], distance=data['distance'])
                    self.planets.append(planet)
            # Print the number of planets loaded
            print("Planets Loaded from NASA_PRODUCTION.csv:", len(self.planets))

        ##
        # create a duplicate list so the original data can be filtered or retrieved without harm
        self.filteredPlanets = []
        self.filteredPlanets = self.planets

        self.selected_planet = None
        self.efficiency_index = 1

    # function that takes in the selected planet
    # calls convert_time_unit in controller to clean up algorithm results
    # calls create_visualization in the view with algorithm results to display
    def run_algorithm(self, controller_reference, selected_planet):
        hubble_constant = 69.8  # Current value for hubble constant
        max_distance = 439999652819071048e+23  # Distance to Observable Universe Edge in KM
        distance = selected_planet.distance  # Distance to selected planet in Parsecs
        # Converted distances to planet being observed#
        distanceKM = distance * (3.0857 * 10 ** 13)  # Convert distance from PC to KM for loop
        distanceMPC = distance / 1000000  # Convert distance from PC to MPC for velocity calculations

        numCalc = 0  # This is the number of calculations performed by the algorithm

        velocity = hubble_constant * distanceMPC  # Calculate the starting velocity
        starting_velocity = velocity  # save initial velocity for display

        max_distance = max_distance - distanceKM  # get just the distance from the planet to obervational universe edge, ignoring distance from earth to the planet

        # Step size in km for how long the planet will travel before each recalculation
        step = (max_distance / 2000000 / (
                self.efficiency_index * 0.1))  # Divides by index to lower km for recalculations the larger the index

        t = 0  # this is to count years for the final result
        start_time = time.time()  # Start the timer
        data = []  # This is a list to store algorithm results for visualization

        #  loop that increments of distance equal to step, calculates the time that was taken to reach the next increment
        #  Then recalculate the new velocity and repeat. The speed will increase with distance.
        while distanceKM < max_distance:
            distanceKM += step  # Planet moves step KM away from earth
            delta_t = 0
            delta_t = step / velocity  # Time taken to reach the next increment
            # recalculate as the distance increases, thus its expansion rate must increase
            velocity = hubble_constant * (
                    distanceKM * 3.2407792896664E-20)  # since distanceKM contains current distance, this is used and converted to mpc as appropriate
            t += delta_t  # Add the time taken for the current step to the total elapsed time

            #  The data is being stored in a list for later visualization.
            #  This will also be passed to the view
            data.append({
                'distance': distance,
                'velocity': velocity,
            })
            numCalc += 1
        end_time = time.time()  # Stop the timer
        t = '{:.5g}'.format(t)  # format scientific notation of time to be limited to 5 digits
        t = str(t) + " years"
        end_time = time.time()  # Stop the timer
        calc = end_time - start_time

        step = '{:.5g}'.format(step)  # format scientific notation representing step size to be limited to 5 digits
        step = str(step)

        #  Send formatted value to view
        controller_reference.view.create_visualization_screen(t, calc, starting_velocity, numCalc, step)
