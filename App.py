import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas
import multiprocessing
from Controller import Controller
from Model import Model
from View import View


class Splash(tk.Toplevel):

    def __init__(self, root):
        super().__init__()

        # Hide the title bar for the splash window
        self.overrideredirect(True)

        # Define the splash screen frame size dynamically based on system specs
        screen_width = self.winfo_screenwidth()
        splash_width = screen_width - 100
        screen_height = self.winfo_screenheight()
        splash_height = screen_height - 100
        splash_xposition = (screen_width - splash_width) // 2
        splash_yposition = (screen_height - splash_height) // 2
        self.geometry(f"{splash_width}x{splash_height}+{splash_xposition}+{splash_yposition}")
        self.progress = 0

        # Set the background image for the splash screen
        self.splash_image = Image.open("images/Splash Screen.jpg")
        self.resized = self.splash_image.resize((splash_width - 100, splash_height - 100))
        self.splash_photo = ImageTk.PhotoImage(self.resized)
        self.splash_label = ttk.Label(self, image=self.splash_photo)
        self.splash_label.pack()

        # Add the progress bar to the splash screen
        self.my_progress = ttk.Progressbar(self, orient="horizontal", length=splash_width / 2,
                                           mode="determinate")
        self.my_progress.pack(pady=10)

        # Add the progress label to the splash screen
        self.progress_label = ttk.Label(self, text="0%")
        self.progress_label.pack()

    # Define the function to update the progress bar
    def update_progress(self):
        if self.progress <= 101:
            self.my_progress["value"] = self.progress
            self.progress_label.config(text=f"{self.progress}%")
            self.progress += 2
            self.after(1)

    def destroy_splash_screen(self):
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.splash = None
        self.start_up_app()

        self.title("SandGlass application")
        # locking the parent window since the layout does not properly resize with window
        self.resizable(False, False)

        self.mainloop()

    def start_up_app(self):
        self.show_splash_screen()

        # load db in separate process
        process_startup = multiprocessing.Process(target=App.startup_process(self))
        process_startup.start()

        while process_startup.is_alive():
            self.splash.update()
            self.splash.update_progress()

        self.splash.my_progress["value"] = 100
        self.splash.progress_label.config(text="100")
        self.after(1000)
        self.remove_splash_screen()

    def show_splash_screen(self):
        self.withdraw()
        self.splash = Splash(self)

    # function to initialize application on its own thread to prevent application data corruption
    @staticmethod
    def startup_process(self):

        # Function called if the CSV requires reformatting
        def cleanup_csv(nasa_data_frame):
            nasa_data_frame = pandas.read_csv(csvName)
            # Check the first 25 rows and columns for instances of the old column names or comments
            n_rows, n_cols = nasa_data_frame.shape
            for i in range(min(n_rows, 25)):
                for j in range(min(n_cols, 25)):
                    if nasa_data_frame.iloc[i, j] == 'pl_name':
                        nasa_data_frame.iloc[i, j] = 'name'
                    elif nasa_data_frame.iloc[i, j] == 'pl_bmasse' or nasa_data_frame.iloc[i, j] == 'pl_masse':
                        nasa_data_frame.iloc[i, j] = 'mass'
                    elif nasa_data_frame.iloc[i, j] == 'sy_dist':
                        nasa_data_frame.iloc[i, j] = 'distance'
                    elif '#' in str(nasa_data_frame.iloc[i, j]):
                        nasa_data_frame = nasa_data_frame.drop(i)
                    elif nasa_data_frame.columns[j] == 'name' and nasa_data_frame.iloc[i, j] == 'name':
                        nasa_data_frame = nasa_data_frame.drop(i)

            nasa_data_frame.to_csv(csvName, index=False)  # Write the changes into the CSV
            nasa_data_frame.reset_index(drop=True, inplace=True)
            return nasa_data_frame  # Function end

        # read all data from CSV
        # csvName = "testing/Dev_Test_Set.csv"  # un-comment for development testing
        csvName = "NASA_PRODUCTION.csv"  # un-comment for production
        nasa_data_frame = pandas.read_csv(csvName)

        # check if the name column is already in the correct location
        if 'name' in nasa_data_frame.columns:
            nasa_data_frame = pandas.read_csv(csvName)
        else:
            # Check if the first row contains "#", if it does, call cleanup function to remove it as comments remain from download
            if nasa_data_frame.iloc[0].str.contains("#").any():
                nasa_data_frame = cleanup_csv(nasa_data_frame)

        # The File can have header issues, especially when downloaded so accounting for column headers out of place is required
        header_row = None
        for i in range(len(nasa_data_frame)):  # parsing without modification has minimal effeciency impact
            row = nasa_data_frame.loc[i]
            if 'name' in row.values and 'mass' in row.values and 'distance' in row.values:
                header_row = i
                break

        # if the header row was found, set it as the column names and delete all previous rows
        if header_row is not None:
            nasa_data_frame.columns = nasa_data_frame.loc[header_row]

        # convert dataframe to data dictionary to be passed to model constructor
        planet_data = nasa_data_frame.to_dict('records')
        model = Model(planet_data)

        # initialize the parent ttk frame which will have our 3 frame layout attached
        view = View(self)

        # draw the view onto the Parent window to take up the full space
        view.grid(row=0, column=0, sticky="nsew")

        controller = Controller(model, view)

        # assign controller to the view
        view.set_controller(controller)

        # draw the GUI on top of the layout, Must come after the controller in oder to assign values to widgets from
        # model
        view.draw_widgets()

    def remove_splash_screen(self):
        self.splash.destroy_splash_screen()
        del self.splash
        self.deiconify()


if __name__ == '__main__':
    App()
