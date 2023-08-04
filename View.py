import subprocess
import tkinter
from tkinter import ttk, PhotoImage, scrolledtext
import pygame as pygame
from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer
import cv2


# View class Main Layout and Widgets of GUI
class View(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # parent is the TK() root window of the app
        self.parent = parent

        # declare references to widgets that will need controller and model functionality
        # then build the widget on reference in the Build GUI method
        self.console_text_output = None
        self.selection_dropdown = None
        self.planet_selection = None
        self.name_input = None
        self.range_input = None
        self.mass_input = None
        self.name_submit_button = None
        self.range_submit_button = None
        self.mass_submit_button = None
        self.slider_submit_button = None
        self.efficiency_slider = None

        # empty reference will be set after controller is instantiated in APP
        self.controller = None

        # Define the parent frame size
        self.WIDTH = self.winfo_screenwidth() - 100
        self.HEIGHT = self.winfo_screenheight() - 100

        # define the layout frame sizes
        self.MENU_FRAME_WIDTH = self.WIDTH // 4
        self.CONSOLE_FRAME_HEIGHT = self.HEIGHT // 5
        self.FILTER_FRAME_WIDTH = self.WIDTH - self.MENU_FRAME_WIDTH
        self.FILTER_FRAME_HEIGHT = (self.HEIGHT - self.CONSOLE_FRAME_HEIGHT)
        self.MENU_FRAME_HEIGHT = (self.HEIGHT - self.CONSOLE_FRAME_HEIGHT)

        # image sizes for logo and mission statement
        self.LOGO_WIDTH = (self.MENU_FRAME_WIDTH // 4)
        self.LOGO_HEIGHT = (self.MENU_FRAME_HEIGHT // 8)
        self.MISSION_STATEMENT_WIDTH = (self.MENU_FRAME_WIDTH - self.LOGO_WIDTH)
        self.MISSION_STATEMENT_HEIGHT = self.MENU_FRAME_HEIGHT // 8

        # layout frames
        self.menu_frame = ttk.Frame(self, height=self.MENU_FRAME_HEIGHT, width=self.MENU_FRAME_WIDTH)
        self.filter_frame = ttk.Frame(self, height=self.FILTER_FRAME_HEIGHT, width=self.FILTER_FRAME_WIDTH)
        self.console_frame = ttk.Frame(self, height=self.CONSOLE_FRAME_HEIGHT, width=self.WIDTH)

        # Set menu background
        self.menu_image = Image.open("images/menu.jpg")
        self.menu_image = self.menu_image.resize((self.MENU_FRAME_WIDTH, self.MENU_FRAME_HEIGHT))
        self.menu_photo = ImageTk.PhotoImage(self.menu_image)
        self.menu_label = ttk.Label(self.menu_frame, image=self.menu_photo)
        # self.menu_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.menu_label.grid(row=0, column=0, sticky="nsew")

        # Set Menu Logo
        self.logo_image = Image.open("images/logo.jpg")
        self.logo_image = self.logo_image.resize((self.LOGO_WIDTH, self.LOGO_HEIGHT))
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self.menu_frame, image=self.logo_photo)
        self.logo_label.place(relx=0, rely=0, relwidth=0.26, relheight=0.128)

        # Set Mission statement background
        self.mission_statement_image = Image.open("images/mission.jpg")
        self.mission_statement_image = self.mission_statement_image.resize(
            (self.MISSION_STATEMENT_WIDTH, self.MISSION_STATEMENT_HEIGHT))
        self.mission_statement_photo = ImageTk.PhotoImage(self.mission_statement_image)
        self.mission_statement_label = ttk.Label(self.menu_frame, image=self.mission_statement_photo)
        self.mission_statement_label.place(relx=0.25, rely=0, relwidth=0.75, relheight=0.128)

        # set filter frame background
        self.filter_image = Image.open("images/galaxy.jpg")
        self.filter_image = self.filter_image.resize((self.FILTER_FRAME_WIDTH, self.FILTER_FRAME_HEIGHT))
        self.filter_photo = ImageTk.PhotoImage(self.filter_image)

        # using canvas for filter, so we can write text on it without background containers
        self.filter_canvas = tkinter.Canvas(self.filter_frame, width=self.FILTER_FRAME_WIDTH,
                                            height=self.FILTER_FRAME_HEIGHT)
        self.filter_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.filter_canvas.create_image(0, 0, image=self.filter_photo, anchor="nw")

        # place child frames
        self.menu_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.filter_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.console_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")

        # configure the grid layout of the parent tkk frame (this is the view frame not the root)
        self.grid_rowconfigure(0, weight=10)
        self.grid_rowconfigure(1, weight=10)
        self.grid_rowconfigure(2, weight=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=3)

        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=4)

        # further configure the console window to have its own grid
        self.console_frame.grid_columnconfigure(0, weight=8)
        self.console_frame.grid_columnconfigure(1, weight=0)
        self.console_frame.grid_columnconfigure(2, weight=2)

    # This method will draw all widgets onto the layout, must be called after instantiation and assignment of controller
    # in APP
    def draw_widgets(self):
        # ///////// CONSOLE WIDGETS ///////////////////////////////////////////////////////////////////////////////////

        # instantiate a read only not clickable text box to act as Console output
        self.console_text_output = scrolledtext.ScrolledText(self.console_frame, wrap='word', width=30, height=10,
                                                             bg='black',
                                                             fg='white',
                                                             bd=10,
                                                             relief='solid',
                                                             highlightbackground="white",
                                                             font=('Arial', 13),
                                                             takefocus=False)

        # the console text output needs to be enabled to edit the text and disabled to make it read only, This
        # will need to be done in all update methods for this widget. There may be better options then this out there
        # console_text_output.configure(state='enabled')
        self.console_text_output.insert('end', 'Welcome to SandGlass!\n')
        self.console_text_output.grid(row=0, column=0, sticky="nsew")
        self.console_text_output.configure(state='disabled')

        # create the clear filters button, stylize it and attach it to controller action
        clear_filter_button = tkinter.Button(self.console_frame, text="Clear filters", bg="#9A9AC0", fg="black",
                                             font=("Arial", 20),
                                             bd=3,
                                             relief="raised",
                                             borderwidth=3,
                                             highlightthickness=0,
                                             command=self.controller.clear_filters)

        clear_filter_button.grid(row=0, column=2, sticky="nsew")

        # ///////// MENU WIDGETS ///////////////////////////////////////////////////////////////////////////////////

        # define a variable value for the selection box
        self.planet_selection = tkinter.StringVar()
        self.planet_selection.set("Select a planet")

        # build scrollable combo box using Model data
        self.selection_dropdown = ttk.Combobox(self.menu_frame, textvariable=self.planet_selection,
                                               values=self.controller.get_planets(),
                                               height=20, state="readonly")
        self.selection_dropdown.config(font=('Arial', 12), background="white", justify='center')
        self.selection_dropdown.place(relx=0.5, rely=0.30, relwidth=0.9, relheight=0.05, anchor='n')

        # create quit button
        quit_button = tkinter.Button(self.menu_frame, text="Quit", bd=3, relief="raised",
                                     borderwidth=5, highlightthickness=0,
                                     highlightbackground="blue",
                                     font=("Arial", 20, "bold"),
                                     background="red",
                                     command=self.parent.destroy)

        quit_button.place(relx=0.05, rely=0.18, relwidth=0.25, relheight=0.08)

        # create about button
        about_button = tkinter.Button(self.menu_frame, text="About", bd=3, relief="raised",
                                      borderwidth=5, highlightthickness=0,
                                      highlightbackground="blue",
                                      font=("Arial", 20, "bold"),
                                      background="green",
                                      command=lambda: self.controller.about_app(self.WIDTH, self.HEIGHT))
        about_button.place(relx=0.35, rely=0.18, relwidth=0.25, relheight=0.08)

        # create tutorial button
        tutorial_button = tkinter.Button(self.menu_frame, text="Tutorial", bd=3, relief="raised",
                                         borderwidth=5, highlightthickness=0,
                                         highlightbackground="blue",
                                         font=("Arial", 20, "bold"),
                                         background="green",
                                         command=self.play_tutorial
                                         )
        tutorial_button.place(relx=0.65, rely=0.18, relwidth=0.3, relheight=0.08)

        # create calculate button
        calculate_button = tkinter.Button(self.menu_frame, text="Calculate", bd=3, relief="raised",
                                          borderwidth=5, highlightthickness=0,
                                          highlightbackground="blue",
                                          font=("Arial", 20, "bold"),
                                          background="green",
                                          command=self.controller.start_algorithm
                                          )

        calculate_button.place(relx=0.05, rely=0.85, relwidth=0.9, relheight=0.05)

        # //// FILTER WIDGETS /////////////////////////////////////////////////////////////////////////////////////////

        # this is spaced due to pythons desire to ratio everything, the spacing will line up the labels
        planet_name_label = "Planet Name"
        planet_mass_label = "       Planet Max Mass"
        planet_range_label = "         Planet Max Range"
        efficiency_label = "Efficiency      "

        string_height = 150
        input_width = 30
        input_font = ("Arial", 16)
        submit_font = ("Arial", 28, "bold")
        canvas_font = ("Arial", 36, "bold")
        canvas_text_color = "white"

        # spacing for filter labels
        y1 = self.FILTER_FRAME_HEIGHT / 2 - string_height
        y2 = self.FILTER_FRAME_HEIGHT / 2
        y3 = self.FILTER_FRAME_HEIGHT / 2 + string_height
        y4 = self.FILTER_FRAME_HEIGHT / 2 + (string_height * 1.8)
        input_y1 = y1 - 5
        input_y2 = y2 - 5
        input_y3 = y3 - 5

        # draw labels on canvas
        self.filter_canvas.create_text(self.FILTER_FRAME_WIDTH / 5, y1, text=planet_name_label, font=canvas_font,
                                       fill=canvas_text_color, justify="left")
        self.filter_canvas.create_text(self.FILTER_FRAME_WIDTH / 5, y2, text=planet_range_label, font=canvas_font,
                                       fill=canvas_text_color, justify="left")
        self.filter_canvas.create_text(self.FILTER_FRAME_WIDTH / 5, y3, text=planet_mass_label, font=canvas_font,
                                       fill=canvas_text_color, justify="left")
        self.filter_canvas.create_text(self.FILTER_FRAME_WIDTH / 5, y4, text=efficiency_label, font=canvas_font,
                                       fill=canvas_text_color, justify="left")

        # draw all input boxes
        self.name_input = tkinter.Entry(self.filter_canvas, font=input_font, width=input_width, justify="center")
        # self.name_input.place(x=self.FILTER_FRAME_WIDTH / 2.5 + 10, y=input_y1, anchor="w", height=40)  # Exact place
        self.name_input.place(relx=0.4, rely=0.29, relheight=0.05, relwidth=0.3)  # relative placing

        self.range_input = tkinter.Entry(self.filter_canvas, font=input_font, width=input_width, justify="center")
        # self.range_input.place(x=self.FILTER_FRAME_WIDTH / 2.5 + 10, y=input_y2, anchor="w", height=40) # Exact place
        self.range_input.place(relx=0.4, rely=0.48, relheight=0.05, relwidth=0.3)  # relative placing

        self.mass_input = tkinter.Entry(self.filter_canvas, font=input_font, width=input_width, justify="center")
        # self.mass_input.place(x=self.FILTER_FRAME_WIDTH / 2.5 + 10, y=input_y3, anchor="w",height = 40)  # Exact place
        self.mass_input.place(relx=0.4, rely=0.67, relheight=0.05, relwidth=0.3)  # relative placing

        # draw the filter input submit buttons
        self.name_submit_button = tkinter.Button(self.filter_frame, text="Submit", background="green", relief="raised",
                                                 borderwidth=5, highlightthickness=0, highlightbackground="blue",
                                                 font=submit_font, justify="center",
                                                 command=self.controller.filter_by_name)
        self.name_submit_button.place(relx=0.725, rely=0.29, relwidth=0.2, relheight=0.05)

        self.range_submit_button = tkinter.Button(self.filter_frame, text="Submit", background="green", relief="raised",
                                                  borderwidth=5, highlightthickness=0, highlightbackground="blue",
                                                  font=submit_font, justify="center",
                                                  command=self.controller.filter_by_distance)
        self.range_submit_button.place(relx=0.725, rely=0.48, relwidth=0.2, relheight=0.05)

        self.mass_submit_button = tkinter.Button(self.filter_frame, text="Submit", background="green", relief="raised",
                                                 borderwidth=5, highlightthickness=0, highlightbackground="blue",
                                                 font=submit_font, justify="center",
                                                 command=self.controller.filter_by_mass)
        self.mass_submit_button.place(relx=0.725, rely=0.67, relwidth=0.2, relheight=0.05)

        self.slider_submit_button = tkinter.Button(self.filter_frame, text="Submit", background="green",
                                                   relief="raised",
                                                   borderwidth=5, highlightthickness=0, highlightbackground="blue",
                                                   font=submit_font, justify="center",
                                                   command=self.controller.submit_efficiency)
        self.slider_submit_button.place(relx=0.725, rely=0.82, relwidth=0.2, relheight=0.05)

        # draw the efficiency slider bar
        self.efficiency_slider = tkinter.Scale(self.filter_frame, from_=1, to=100, orient=tkinter.HORIZONTAL, bg="blue",
                                               font=("Arial", 12, "bold"))
        self.efficiency_slider.place(relx=0.4, rely=0.82, relwidth=0.3, relheight=0.05)

    # //// VIEW FUNCTIONS //////////////////////////////////////////////////////////////////////////////////////////////

    # assign controller value to view
    def set_controller(self, controller):
        self.controller = controller

    # instantiate a pygame window for the purposes of visualization. This could change over development time
    def create_visualization_screen(self, t, calc, starting_velocity, num_calc, step):
        # retrieve planet from model
        selected_planet = self.controller.get_selected_planet()
        efficiency_index = self.controller.get_efficiency_index()

        # ensure planet was passed, if object does not exist stop function and do not instantiate pygame        time_in_billions_of_years:.2f
        if selected_planet is None:
            return
        else:
            # Retrieve the parameters you want to send
            subprocess.Popen(['python', 'Planet_Simulation.py', str(selected_planet), str(efficiency_index),
                              str(selected_planet.mass), str(selected_planet.distance), str(t), str(calc),
                              str(starting_velocity), str(num_calc), str(step)])

    # View method to instantiate a media player and playback video capture / audio using the cv2 library for the
    # purposes of the SandGlass in application tutorial video
    @staticmethod
    def play_tutorial():

        # define pathing for the desired Mp4 video in project directory
        video_path = "videos/tutorial.mp4"

        # assign the file to the video capture class in order to pull frames of the video file
        video = cv2.VideoCapture(video_path)
        # instantiate ffpyplayer media player object for audio video playback
        player = MediaPlayer(video_path)

        # define the video player window parameters
        window_size = (1200, 800)
        cv2.namedWindow("SandGlass Tutorial", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("SandGlass Tutorial", window_size)

        # infinite loop for video playback
        while True:

            # select next video and audio frame from video file
            grabbed, frame = video.read()
            audio_frame, val = player.get_frame()

            # if no frames exist the video file is finished exit playback
            if not grabbed:
                break

            # define framerate of playback to synchronize audio and video frames
            if cv2.waitKey(39) & 0xFF == ord("q"):
                break

            # detection conditions for manual 'QUIT' of the tutorial video
            try:
                # if property returns -1 the window has closed this will throw a benign exception
                # so break the playback loop inside the exception catch
                if cv2.getWindowProperty("SandGlass Tutorial", 1) == -1:
                    break
            except Exception as e:
                break

            # display current frame to media player window frame
            cv2.imshow("SandGlass Tutorial", frame)

            if val != 'eof' and audio_frame is not None:
                img, t = audio_frame

        # release and close Video / Audio / Playback components
        video.release()
        player.close_player()
        cv2.destroyAllWindows()
