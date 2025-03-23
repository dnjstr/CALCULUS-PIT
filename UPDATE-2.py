import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sympy as sp
from scipy.integrate import quad
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile

class FunctionVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x750")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 750) // 2
        self.root.geometry(f'900x750+{x}+{y}')

        # icon diri
        self.root.title("DerivaPlot")
        
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DerivaPlot.ico")

            if os.path.isfile(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"Icon file not found at: {icon_path}")
        except Exception as e:
            print(f"Error setting icon: {e}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # DEFAULT THEME
        self.appearance_mode = "light"
        ctk.set_appearance_mode(self.appearance_mode)
        ctk.set_default_color_theme("blue")
        self.default_button_color = "#3B8ED0" 
        self.default_hover_color = "#3B8ED0"
        self.reset_button_color = "#FF5A5A"
        self.reset_hover_color = "#E04A4A" # for reset plot hehe   
        
        self.graph_path = None
        self.fig = None
        
        self.create_widgets()
        
    def create_widgets(self):
        self.top_bar = ctk.CTkFrame(self.root)
        self.top_bar.pack(fill="x", padx=10, pady=(5, 0))

        ctk.CTkLabel(self.top_bar, text="Function Plotter & Derivative Visualizer", font=("Arial", 16, "bold")).pack(side="left", padx=5)

        self.theme_button = ctk.CTkButton(
            self.top_bar, 
            text="☀️ Light" if self.appearance_mode == "dark" else "🌙 Dark",
            width=80,
            height=28,
            command=self.toggle_theme
        )
        self.theme_button.pack(side="right", padx=5, pady=5)

        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(padx=10, pady=5, fill="x")
        
        self.graph_frame = ctk.CTkFrame(self.root)
        self.graph_frame.pack(padx=10, pady=(0, 5), fill="both", expand=True)
        
        # Function input
        function_row = ctk.CTkFrame(self.input_frame)
        function_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(function_row, text="Function:", width=80).pack(side="left", padx=5)
        self.entry_func = ctk.CTkEntry(function_row, width=300, placeholder_text="e.g., sin(x) + 0.5*x**4")
        self.entry_func.pack(side="left", padx=5, fill="x", expand=True)
        
        # Range input
        range_row = ctk.CTkFrame(self.input_frame)
        range_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(range_row, text="X Range:", width=80).pack(side="left", padx=5)
        self.entry_xmin = ctk.CTkEntry(range_row, width=80, placeholder_text="Min")
        self.entry_xmin.pack(side="left", padx=5)
        ctk.CTkLabel(range_row, text="to", width=20).pack(side="left")
        self.entry_xmax = ctk.CTkEntry(range_row, width=80, placeholder_text="Max")
        self.entry_xmax.pack(side="left", padx=5)

        # Help button
        self.help_button = ctk.CTkButton(
            self.top_bar, 
            text="❓ Help",
            width=80,
            height=28,
            command=self.show_help
        )
        self.help_button.pack(side="right", padx=5, pady=5)

        # Derivative
        ctk.CTkLabel(range_row, text="Derivative:", width=80).pack(side="left", padx=(15, 5))
        self.entry_order = ctk.CTkEntry(range_row, width=50, placeholder_text="Order")
        self.entry_order.insert(0, "1")  # Default Valuer
        self.entry_order.pack(side="left", padx=5)
        
        # Action buttons
        button_row = ctk.CTkFrame(self.input_frame)
        button_row.pack(fill="x", pady=(5, 3))
        
        # Buttons
        button_width = 120
        button_height = 30
        button_padding = 3
        
        self.btn_plot = ctk.CTkButton(
            button_row, 
            text="Plot Functions", 
            command=self.on_plot,
            width=button_width,
            height=button_height
        )
        self.btn_plot.pack(side="left", padx=button_padding)
        
        self.btn_save = ctk.CTkButton(
            button_row, 
            text="Save Image", 
            command=self.on_save_image, 
            state="disabled",
            width=button_width,
            height=button_height
        )
        self.btn_save.pack(side="left", padx=button_padding)
        
        self.btn_receipt = ctk.CTkButton(
            button_row, 
            text="Save Receipt", 
            command=self.on_save_receipt, 
            state="disabled",
            width=button_width,
            height=button_height
        )
        self.btn_receipt.pack(side="left", padx=button_padding)
        
        # Graph placeholder
        self.canvas_frame = ctk.CTkFrame(self.graph_frame)
        self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status bar with link guthib
        status_bar_frame = ctk.CTkFrame(self.root)
        status_bar_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Status (left)
        self.status_var = ctk.StringVar(value="Ready to plot")
        self.status_bar = ctk.CTkLabel(status_bar_frame, textvariable=self.status_var, anchor="w", height=20)
        self.status_bar.pack(side="left", fill="x", expand=True)

        self.updates_link = ctk.CTkLabel(
            status_bar_frame, 
            text="Updates", 
            cursor="hand2",
            font=("Arial", 12, "underline"),
            text_color="#0000FF"
        )
        self.updates_link.pack(side="right", padx=10)
        self.updates_link.bind("<Button-1>", lambda e: self.open_updates_link())
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        if self.appearance_mode == "dark":
            self.appearance_mode = "light"
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="🌙 Dark")
        else:
            self.appearance_mode = "dark"
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="☀️ Light")
            
        # Update plot colors if it exists
        if self.fig is not None:
            self.update_plot_theme()
    
    def update_plot_theme(self):
        """Update the plot theme to match the app theme"""
        if self.fig is not None:
            background_color = "#242424" if self.appearance_mode == "dark" else "white"
            text_color = "white" if self.appearance_mode == "dark" else "black"
            
            self.fig.patch.set_facecolor(background_color)
            axes = self.fig.get_axes()
            for ax in axes:
                ax.set_facecolor(background_color)
                ax.tick_params(colors=text_color)
                ax.xaxis.label.set_color(text_color)
                ax.yaxis.label.set_color(text_color)
                ax.title.set_color(text_color)
                for spine in ax.spines.values():
                    spine.set_edgecolor(text_color)
            # Update legend
            legend = ax.get_legend()
            if legend is not None:
                frame = legend.get_frame()
                frame.set_facecolor(background_color)
                frame.set_edgecolor(text_color)

                for text in legend.get_texts():
                    text.set_color(text_color)
            
            self.canvas.draw()

    def show_help(self):
        """Display a help popup with information about the application"""
        text_color = "white" if self.appearance_mode == "dark" else "black"
        
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("DerivaPlot Help")
        help_window.geometry("500x400")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        help_window.geometry(f'500x400+{x}+{y}')

        help_window.grab_set()

        help_frame = ctk.CTkFrame(help_window)
        help_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_text = ctk.CTkTextbox(help_frame, wrap="word")
        help_text.pack(fill="both", expand=True, padx=5, pady=5)

        help_text.configure(text_color=text_color)

        help_content = """DerivaPlot - Function Visualization Tool

    How to use:
    1. Enter a mathematical function using x as the variable
    Examples: sin(x), x**2, cos(x) + 0.5*x

    2. Set the X Range for plotting (min and max values)
    Example: -10 to 10

    3. Set the derivative order (1 for first derivative, 2 for second, etc.)

    4. Click "Plot Functions" to visualize:
    - The original function
    - The specified derivative
    - The integral of the function

    5. Use the navigation toolbar to zoom, pan, or save the plot

    6. Click "Save Image" to export just the graph
    
    7. Click "Save Receipt" to create a complete report with the graph
    and function details

    Supported mathematical functions:
    - Basic: +, -, *, /, **
    - Trigonometric: sin, cos, tan
    - Others: exp, log, sqrt
    - Constants: pi, e

    Tips:

    For complex functions, use parentheses to ensure proper order of operations
    The derivative is calculated numerically, so very steep functions might show
    some approximation errors
    Toggle between light and dark themes using the theme button
    
    **Group Members:**  
    📌 Anino, Glenn  
    📌 Antonio, Den  
    📌 Casia, Jaybird  
    📌 Espina, Cyril  
    📌 Flores, Sophia  
    📌 Lacanaria, Lorenz  
    """
        
        help_text.insert("1.0", help_content)
        help_text.configure(state="disabled") 

        close_button = ctk.CTkButton(
            help_window, 
            text="Close", 
            command=help_window.destroy
        )
        close_button.pack(pady=10)
        
    def validate_inputs(self):
        """Validate all user inputs and check for empty fields."""
        expr = self.entry_func.get().strip()
        x_min = self.entry_xmin.get().strip()
        x_max = self.entry_xmax.get().strip()
        order = self.entry_order.get().strip()
        
        # Check for empty fields
        if not expr:
            messagebox.showerror("Input Error", "Function expression cannot be empty")
            return False, None, None, None
        
        if not x_min:
            messagebox.showerror("Input Error", "Minimum x value cannot be empty")
            return False, None, None, None
            
        if not x_max:
            messagebox.showerror("Input Error", "Maximum x value cannot be empty")
            return False, None, None, None
            
        if not order:
            messagebox.showerror("Input Error", "Derivative order cannot be empty")
            return False, None, None, None
            
        try:
            x = sp.symbols('x')
            # Convert the expression into a sympy function
            sympy_expr = sp.sympify(expr, locals={"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, 
                                                "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt,
                                                "pi": sp.pi, "e": sp.E})
            # Convert to a lambda function that NumPy can evaluate
            f = sp.lambdify(x, sympy_expr, 'numpy')
            
            # Ensure numerical validity
            x_min_val = float(x_min)
            x_max_val = float(x_max)
            order_val = int(order)
            
            if x_min_val >= x_max_val:
                raise ValueError("Min x must be less than Max x")
            
            if order_val < 1:
                raise ValueError("Derivative order must be at least 1")
                
            # Test the function with a sample value to catch potential errors
            test_x = np.array([0.5])
            try:
                f(test_x)
            except Exception:
                raise ValueError("Function cannot be evaluated. Check your syntax.")
            
            return True, f, (x_min_val, x_max_val), order_val
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return False, None, None, None
            
    def numerical_derivative(self, f, x_vals, order=1):
        """Compute the numerical derivative of a function."""
        if order == 1:
            dx = x_vals[1] - x_vals[0]
            return np.gradient(f(x_vals), dx)
        else:
            # implementation for higher order derivatives
            result = f(x_vals)
            for _ in range(order):
                dx = x_vals[1] - x_vals[0]
                result = np.gradient(result, dx)
            return result

    def numerical_integral(self, f, x_vals):
        """Compute the numerical integral of a function."""
        return np.array([quad(f, x_vals[0], x)[0] for x in x_vals])
        
    def on_plot(self):
        """Handle the plot button click."""
        try:
            # Clear previous plot if exists
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'toolbar'):
                self.toolbar.destroy()
            if hasattr(self, 'toolbar_frame'):
                self.toolbar_frame.destroy()

            # maintain size
            self.canvas_frame.pack_forget()
            self.canvas_frame = ctk.CTkFrame(self.graph_frame)
            self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)  
            
            # Validate inputs
            is_valid, f, x_range, order_val = self.validate_inputs()
            if not is_valid:
                return
            
            self.status_var.set("Calculating and plotting...")
            self.root.update()
            
            # Create plot
            x_vals = np.linspace(x_range[0], x_range[1], 400)
            
            try:
                y_vals = f(x_vals)
                dydx_vals = self.numerical_derivative(f, x_vals, order_val)
                integral_vals = self.numerical_integral(f, x_vals)
                
                # Create figure
                plt.style.use('default')
                self.fig, ax = plt.subplots(figsize=(8, 5))
                
                # Set colors based on theme
                background_color = "#242424" if self.appearance_mode == "dark" else "white"
                text_color = "white" if self.appearance_mode == "dark" else "black"
                self.fig.patch.set_facecolor(background_color)
                ax.set_facecolor(background_color)
                
                # Plot data
                ax.plot(x_vals, y_vals, label=f'Function: {self.entry_func.get()}', linewidth=2)
                ax.plot(x_vals, dydx_vals, label=f'{order_val}-Order Derivative', linestyle='dashed', linewidth=2)
                ax.plot(x_vals, integral_vals, label='Integral', linestyle='dotted', linewidth=2)
                
                # Set labels and appearance
                ax.set_xlabel('x', color=text_color)
                ax.set_ylabel('y', color=text_color)
                ax.set_title('Function, Derivative, and Integral', color=text_color)
                ax.tick_params(colors=text_color)
                for spine in ax.spines.values():
                    spine.set_edgecolor(text_color)
                
                # Update legend
                legend = ax.legend()
                if legend is not None:
                    frame = legend.get_frame()
                    frame.set_facecolor(background_color)
                    frame.set_edgecolor(text_color)
                    for text in legend.get_texts():
                        text.set_color(text_color)
                        
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # Display in UI
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill="both", expand=True)
                
                # navigation toolbar
                self.toolbar_frame = ctk.CTkFrame(self.canvas_frame)
                self.toolbar_frame.pack(side="bottom", fill="x")
                self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
                self.toolbar.update()
                
                # Enable save buttons
                self.btn_save.configure(state="normal")
                self.btn_receipt.configure(state="normal")
                
                # Store data for receipt
                self.current_data = {
                    "expr": self.entry_func.get(),
                    "x_range": x_range,
                    "order": order_val
                }

                # reset
                self.btn_plot.configure(
                    text="Reset Plot", 
                    command=self.on_reset_plot, 
                    fg_color=self.reset_button_color,
                    hover_color=self.reset_hover_color
                )
                
                self.status_var.set("Plot completed successfully")
            except Exception as e:
                messagebox.showerror("Calculation Error", f"Error calculating results: {e}")
                self.status_var.set("Error in calculation")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_var.set("Error occurred")

    def on_reset_plot(self):
        """Reset the plot and input fields."""
        # Clear input fields
        self.entry_func.delete(0, "end")
        self.entry_xmin.delete(0, "end")
        self.entry_xmax.delete(0, "end")
        self.entry_order.delete(0, "end")
        self.entry_order.insert(0, "1") 
        
        # Clear the plot
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'toolbar'):
            self.toolbar.destroy()
        if hasattr(self, 'toolbar_frame'):
            self.toolbar_frame.destroy()
        
        # Recreate the canvas frame
        self.canvas_frame.pack_forget()
        self.canvas_frame = ctk.CTkFrame(self.graph_frame)
        self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Reset the plot button
        self.btn_plot.configure(
            text="Plot Functions", 
            command=self.on_plot, 
            fg_color=self.default_button_color,
            hover_color=self.default_button_color
        )
        
        # Disable save buttons
        self.btn_save.configure(state="disabled")
        self.btn_receipt.configure(state="disabled")
        
        # Reset status
        self.status_var.set("Ready to plot")

        self.fig = None
    
    def on_save_image(self):
        """Save the current plot as an image."""
        if self.fig is None:
            messagebox.showerror("Error", "No plot to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Image saved to {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Image saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving image: {e}")
    
    def on_save_receipt(self):
        """Save a receipt with function details and the graph."""
        if self.fig is None or not hasattr(self, 'current_data'):
            messagebox.showerror("Error", "No data to save")
            return
            
        receipt_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG files", "*.png")]
        )
        
        if not receipt_path:
            return
        
        temp_path = None

        try:
            # Create receipt image
            receipt_width, receipt_height = 600, 630
            image = Image.new('RGB', (receipt_width, receipt_height), 'white')
            draw = ImageDraw.Draw(image)

            try:
                font_title = ImageFont.truetype("arial", 24)
                font_text = ImageFont.truetype("arial", 16)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
            
            # Add header
            draw.text((30, 30), "Function Visualizer Receipt", fill="black", font=font_title)
            draw.text((30, 80), f"Function: {self.current_data['expr']}", fill="black", font=font_text)
            draw.text((30, 110), f"X Range: [{self.current_data['x_range'][0]}, {self.current_data['x_range'][1]}]", 
                    fill="black", font=font_text)
            draw.text((30, 140), f"Derivative Order: {self.current_data['order']}", fill="black", font=font_text)
            draw.text((30, 170), f"Date: {np.datetime64('today')}", fill="black", font=font_text)
            
            # temp file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                self.fig.savefig(temp_path, dpi=150, bbox_inches='tight')
            
            # graph to receipt
            graph_img = Image.open(temp_path)
            graph_img = graph_img.resize((520, 380), Image.LANCZOS)
            image.paste(graph_img, (40, 200))
            
            # Footer
            footer_text = "Thank you for using DerivaPlot"

            draw.text((30, 600), footer_text, fill="black", font=font_text)

            
            # Save receipt
            image.save(receipt_path)
            
            self.status_var.set(f"Receipt saved to {os.path.basename(receipt_path)}")
            messagebox.showinfo("Success", f"Receipt saved successfully to:\n{receipt_path}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving receipt: {e}")
        finally:
            # temp file cleannerr
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def open_updates_link(self):
        """Open the updates webpage in the default browser"""
        import webbrowser
        webbrowser.open("https://github.com/dnjstr/CALCULUS-PIT/tree/masterglen")  
    
    def on_closing(self):
        """Handle window closing."""
        plt.close('all')  # Close all matplotlib
        self.root.destroy()

def main():
    """Main function to run the application."""
    root = ctk.CTk()
    app = FunctionVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()