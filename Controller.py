import re
import pygame as pygame


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def get_planets(self):
        return self.model.filteredPlanets

    def start_algorithm(self):
        selected_planet = self.get_selected_planet()
        self.model.run_algorithm(self, selected_planet)

    # function to restore the planet selection list to the original DataSet included at initialization.
    def clear_filters(self):

        # reset the filter planet list to the original state
        self.model.filteredPlanets = self.model.planets
        # reset the efficiency index of the application
        self.model.efficiency_index = 1
        # reset the efficiency slider to default position
        self.view.efficiency_slider.set(1)

        # reset the output window text, include welcome message and filter message
        self.view.console_text_output.configure(state='normal')
        self.view.console_text_output.delete(1.0, 'end')
        self.view.console_text_output.insert('end', 'Welcome to SandGlass!\n')
        self.view.console_text_output.insert('end', 'All filters have been removed, Original planet list restored\n')
        self.view.console_text_output.configure(state='disabled')

        # set the option values of the dropdown list
        self.view.selection_dropdown['values'] = self.model.filteredPlanets

        self.view.planet_selection.set("Select a planet")

    # function to parse out the planet names from dataset to be used in selection menu on interface
    def get_planets_names(self):
        selection_dropdown_planet_names = []
        for planet in self.model.filteredPlanets:
            name = planet.name
            selection_dropdown_planet_names.append(name)

    # function to validate planet selection drop down and pass a valid planet selection to the algorithmic module
    def get_selected_planet(self):

        # grab string value from selection drop down menu
        selected_planet = self.view.selection_dropdown.get()

        if selected_planet == "Select a planet":
            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end', 'Invalid selection, please choose planet from drop down!\n')
            self.view.console_text_output.configure(state='disabled')
            return

        elif selected_planet == "No results found":
            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end',
                                                 'Invalid selection, No planets are available in the current list, '
                                                 'please clear filters and start again\n')
            self.view.console_text_output.configure(state='disabled')
            return

        else:
            for planet in self.model.planets:
                if planet.name == selected_planet:
                    selected_planet = planet
                    return selected_planet

    def get_efficiency_index(self):
        return self.model.efficiency_index

    # function to set the efficiency index of the model for calculations and output a client message to console
    def submit_efficiency(self):
        efficiency_value = self.view.efficiency_slider.get()

        self.model.efficiency_index = efficiency_value

        # reset the output window text, include welcome message and filter message
        self.view.console_text_output.configure(state='normal')
        self.view.console_text_output.insert('end',
                                             'Efficiency index of calculation set to ' + str(efficiency_value) +
                                             '% factor of calculation increments\n')
        self.view.console_text_output.configure(state='disabled')

    def filter_by_mass(self):
        self.inputted_mass = 0
        self.filtered_mass = []
        self.filtered_mass_planet = []

        try:
            self.inputted_mass_string = self.view.mass_input.get()
            self.inputted_mass = float(self.view.mass_input.get())

            if self.inputted_mass <= 0:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end',
                                                     'ERROR: Mass value must be greater than zero \n')
                self.view.console_text_output.configure(state='disabled')
                return

            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end', 'SUCCESS: Mass filter applied \n')
            self.view.mass_input.delete(0, 'end')

            for planet in self.model.filteredPlanets:
                if hasattr(planet, 'mass') and float(planet.mass) < self.inputted_mass:
                    self.filtered_mass.append(planet)
                    self.filtered_mass_planet.append(planet.name)

            if len(self.filtered_mass) == 0:
                self.view.console_text_output.insert('end', 'No results found with mass less than ' + str(
                    self.inputted_mass) + '\n')
                self.view.console_text_output.configure(state='disabled')
                self.view.name_input.delete(0, 'end')
                self.view.selection_dropdown.configure(values=self.filtered_mass_planet)
                self.view.planet_selection.set("No results found")
                return

            self.model.filteredPlanets = self.filtered_mass
            self.view.console_text_output.insert('end', str(len(
                self.filtered_mass)) + ' results found with mass less than ' + str(self.inputted_mass) + '\n')
            self.view.console_text_output.configure(state='disabled')
            self.view.name_input.delete(0, 'end')
            self.view.selection_dropdown.configure(values=self.filtered_mass_planet)
            self.view.planet_selection.set("Select a planet")

        except ValueError:
            if not self.inputted_mass_string:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end', 'ERROR: Mass filter value cannot be empty \n')
                self.view.console_text_output.configure(state='disabled')
            else:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end',
                                                     'ERROR: Please enter a valid number for the mass filter \n')
                self.view.console_text_output.configure(state='disabled')

    def filter_by_distance(self):
        self.filtered_distance = []
        self.filtered_distance_string = []

        try:
            self.inputted_distance_string = self.view.range_input.get()
            self.inputted_distance = float(self.view.range_input.get())

            if self.inputted_distance <= 0:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end',
                                                     'ERROR: Range value must be greater than zero\n')
                self.view.console_text_output.configure(state='disabled')
                return

            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end', 'SUCCESS: Range filter applied\n')
            self.view.range_input.delete(0, 'end')

            for planet in self.model.filteredPlanets:
                if hasattr(planet, 'distance') and float(planet.distance) < self.inputted_distance:
                    self.filtered_distance_string.append(planet)
                    self.filtered_distance.append(planet.name)

            if len(self.filtered_distance_string) == 0:
                self.view.console_text_output.insert('end', 'No results found with distance less than ' + str(
                    self.inputted_distance) + ' Parsecs from Earth.\n')
                self.view.console_text_output.configure(state='disabled')
                self.view.name_input.delete(0, 'end')
                self.view.selection_dropdown.configure(values=self.filtered_distance)
                self.view.planet_selection.set("No results found")
                return

            self.model.filteredPlanets = self.filtered_distance_string
            self.view.console_text_output.insert('end', str(len(
                self.filtered_distance_string)) + ' results found with distance less than ' + str(
                self.inputted_distance) + ' Parsecs from Earth.\n')
            self.view.console_text_output.configure(state='disabled')
            self.view.name_input.delete(0, 'end')
            self.view.selection_dropdown.configure(values=self.filtered_distance)
            self.view.planet_selection.set("Select a planet")

        except ValueError:
            if not self.inputted_distance_string:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end', 'ERROR: Range filter value cannot be empty \n')
                self.view.console_text_output.configure(state='disabled')
            else:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end',
                                                     'ERROR: Please enter a valid number for the range filter \n')
                self.view.console_text_output.configure(state='disabled')

    def filter_by_name(self):
        # Get the name that the user wants to search for
        searchName = self.view.name_input.get().strip().lower()

        # If the user submits without entering a name
        if searchName == "":
            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end', 'ERROR: Name filter value cannot be empty \n')
            self.view.console_text_output.configure(state='disabled')
            # Clear the input field
            self.view.name_input.delete(0, 'end')
            return

        # Input cannot exceed 30 characters
        if len(searchName) > 30:
            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end', 'Error: Name filter value cannot exceed 30 characters \n')
            self.view.console_text_output.configure(state='disabled')
            # Clear the input field
            self.view.name_input.delete(0, 'end')
            return

        # Check the dataset for the specified string
        else:
            tempPlanets = []

            for planet in self.model.filteredPlanets:
                if hasattr(planet, 'name') and searchName in planet.name.lower():
                    tempPlanets.append(planet)

            if len(tempPlanets) == 0:
                self.view.console_text_output.configure(state='normal')
                self.view.console_text_output.insert('end',
                                                     'SUCCESS: Name filter applied \n no results containing "' + searchName + '" found\n')
                self.view.console_text_output.configure(state='disabled')
                # Clear the input field
                self.view.name_input.delete(0, 'end')
                # Set the drop-down list to the filtered list
                self.view.selection_dropdown.configure(values=tempPlanets)
                self.view.planet_selection.set("No results found")
                return
            else:
                self.model.filteredPlanets = tempPlanets
                self.view.console_text_output.configure(state='normal')
                if len(tempPlanets) == 1:
                    self.view.console_text_output.insert('end', 'SUCCESS: Name filter applied \n ' + str(
                        len(tempPlanets)) + ' result containing "' + searchName + '" found, selection set to "' + searchName + '"\n')
                    # If there is only one result, set the selected planet to that result
                    self.view.planet_selection.set(tempPlanets[0])
                else:
                    self.view.console_text_output.insert('end', 'SUCCESS: Name filter applied \n' + str(
                        len(tempPlanets)) + ' results containing "' + searchName + '" found\n')
                    self.view.planet_selection.set("Select a planet")
                self.view.console_text_output.configure(state='disabled')
                # Clear the input field
                self.view.name_input.delete(0, 'end')
                # Set the drop-down list to the filtered list
                self.view.selection_dropdown.configure(values=tempPlanets)

    # Function that creates a window with the "about" information of the application
    def about_app(self, w, h):

        try:
            pygame.init()

            # define the window
            # Define the parent frame size in relation to application display specifications
            WIDTH = w - 200
            HEIGHT = h

            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("About the Sandglass Application")
            clock = pygame.time.Clock()

            # Load the background image and scale it to match the screen size
            background_image = pygame.image.load("images/visualization_background.jpg").convert()
            background_picture = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

            # Function that will send text to the next line when it finds a \n (since pygame can't process them)
            def process_newlines(text_to_split):
                # Create a list where every element is a line of text up to a newline character. Deletes the newline character
                split_text = text_to_split.split('\n')

                # Create a list of surfaces, where each surface in the list is one line of text
                surfaces = []
                for sentence in split_text:
                    new_surface = font.render(sentence, True, (255, 255, 255))
                    surfaces.append(new_surface)
                return surfaces

            # load each frame of the gif image into array
            frames = []
            for i in range(61):
                frames.append(pygame.image.load(f"images/frames/frame ({i + 1}).gif").convert_alpha())

            # Define the text to display
            header_font = pygame.font.SysFont("Times New Roman", 60)
            sub_header_font = pygame.font.SysFont("Times New Roman", 35)
            font = pygame.font.SysFont("Times New Roman", 25)

            # define the text to be placed above the gif image
            header_text = "Welcome to SandGlass!"
            sub_header_text = "SandGlass has been created for the NASA SpaceApps 2023 Competition!"
            text1 = "\n\nSandGlass is an interactive application for interfacing with the NASA Exoplanet archives " \
                    "database in order to determine the point when an\nindividual planet will leave the currently " \
                    "viewable universe. Sandglass allows you to filter and select from all known Exoplanets " \
                    "classified\nby NASA based on the planet's title, current distance from Earth in parsecs (pc), and "\
                    "planetary mass in relation to Earth.\n\nUsing the current Hubble constant, a planet's distance from "\
                    "earth, and the maximum distance viewable by the hubble telescope, Sandglass\nis able to determine "\
                    "how many years it will take for a planet to reach the edge of the viewable universe, and therefore disappear "\
                    "from the night\nsky, based on universal expansion theory."

            # define the text to be placed below the gif image
            text2 = "Filter your selection from over 5000 classified exo-planets while using the efficiency index to " \
                    "adjust the accuracy and speed of your calculation.\nOnce your selection has been made, Sandglass " \
                    "will perform a series of calculations using the Hubble constant and your planet's initial distance from\n" \
                    "Earth to determine the exponential velocity of that planet's expansion away from Earth's galaxy " \
                    "and to predict the number of years the planet will be\nviewable by the Hubble telescope. " \
                    "Sandglass will then present the data to you with our galactic visualizer."


            # Create the arrays that will store the lines that fit into the window
            formatted_text1 = process_newlines(text1)
            formatted_text2 = process_newlines(text2)

            # Pygame loop
            running = True
            current_frame = 0
            while running:

                # draw the background
                screen.blit(background_picture, (0, 0))

                y_position = 20
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # draw header texts
                header_surface = header_font.render(header_text, True, (255, 255, 255))
                screen.blit(header_surface, (500, y_position))
                y_position += 75

                # draw sub header texts
                sub_header_surface = sub_header_font.render(sub_header_text, True, (255, 255, 255))
                screen.blit(sub_header_surface, (250, y_position))
                y_position += 25

                # print the first block of text
                for surface in formatted_text1:
                    screen.blit(surface, (75, y_position))
                    y_position += 25  # Increment the y position for blit so each surface prints on a new line

                # display each frame of the gif as an animated image
                y_position += 30
                screen.blit(frames[current_frame], (350, y_position))
                current_frame += 1  # go to the next frame
                current_frame %= len(frames)

                y_position += 500

                # Print the second block of text
                for surface in formatted_text2:
                    screen.blit(surface, (75, y_position))
                    y_position += 25  # Increment the y position for blit so each surface prints on a new line
                pygame.display.flip()
                clock.tick(8)  # set the frame rate for smooth animation of the gif image

            pygame.quit()

        except Exception as e:
            self.view.console_text_output.configure(state='normal')
            self.view.console_text_output.insert('end', 'EXCEPTION: An Error was encountered opening the info window,'
                                                        'Please try again or restart the application. \n')
            self.view.console_text_output.configure(state='disabled')
            pygame.quit()
