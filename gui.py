import tkinter as tk
import os
import json
import random
import threading
import logging
from tkinter import ttk, filedialog, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
from fpdf import FPDF

from main import AICareerNavigator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_career_navigator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CareerNavigatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Career Navigator")
        self.root.geometry("1400x900")  # Increased window size
        self.root.minsize(1200, 800)    # Increased minimum size
        
        # Initialize settings variables before loading settings
        self.output_dir_var = tk.StringVar(value="output/")
        self.autosave_var = tk.BooleanVar(value=True)
        self.export_format_var = tk.StringVar(value="JSON")
        self.theme_var = tk.StringVar(value="Light")
        
        # Initialize translations before using them
        self.translations = {
            'English': {
                'main_title': 'AI Career Navigator',
                'dashboard': 'Dashboard',
                # ...other translations...
            },
            'Norwegian': {
                'main_title': 'AI Karriere Navigator',
                'dashboard': 'Oversikt',
                # ...other translations...
            }
        }
        
        # Set default language
        self.current_language = 'English'
        
        # Initialization
        self.check_data_files()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use one of the available themes: 'clam', 'alt', 'default', 'classic'
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.bg_color = "#f5f5f5"  # Light gray
        self.text_color = "#2c3e50"  # Dark blue
        self.accent_color = "#e74c3c"  # Red
        
        # Style configuration
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', font=('Helvetica', 10), background=self.primary_color)
        self.style.configure('TLabel', font=('Helvetica', 10), background=self.bg_color, foreground=self.text_color)
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), background=self.bg_color, foreground=self.primary_color)
        self.style.configure('Subheader.TLabel', font=('Helvetica', 12, 'bold'), background=self.bg_color, foreground=self.text_color)
        
        # Navigation button style
        self.style.configure('Nav.TButton', 
                           font=('Helvetica', 11, 'bold'),
                           padding=(0, 10),
                           background=self.primary_color,
                           foreground='white')
        self.style.map('Nav.TButton', 
                      background=[('active', self.secondary_color), ('pressed', self.accent_color)])
        
        # Initialize AI Career Navigator
        self.navigator = AICareerNavigator()
        
        # User data
        self.user_profile = {}
        self.recommendations = {}
        self.target_role = None
        
        # Set default language to English
        self.current_language = 'English'
        
        # Initialize language
        self.initialize_language()
        
        # Load saved settings before initializing UI components
        self.load_saved_settings()
        
        # Load icons and logo
        self.icons = {}
        self.load_icons()
        
        # Create interface
        self.create_menu()
        self.create_main_frame()
        
        # Show dashboard by default
        self.show_dashboard()
        
        # Apply translations
        self.apply_translations()
    
    def check_data_files(self):
        """Checks if required data files exist, if not - creates them with default data"""
        data_dirs = ["data", "ai_career_navigator/data"]
        data_files = {
            "skills_database.csv": "skill_id,skill_name,category,relevance_score,learning_difficulty\n1,Python,Programming,10,3\n2,Java,Programming,9,4",
            "job_market_data.csv": "date,skill,demand,avg_salary,num_openings\n2024-01-01,Python,10,15000,500\n2024-01-01,Java,8,14000,450",
            "roles_database.csv": "role_id,role_name,level,avg_salary,required_skills,experience_years\n1,Junior Python Developer,Junior,8000,1;3;4,0"
        }
        for data_dir in data_dirs:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            for filename, default_content in data_files.items():
                file_path = os.path.join(data_dir, filename)
                if not os.path.exists(file_path):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    print(f"Created file {file_path}")
    
    def create_menu(self):
        """Create the main menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CV", command=self.load_cv)
        file_menu.add_command(label="Load Profile", command=self.load_profile)
        file_menu.add_command(label="Save Profile", command=self.save_profile)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="CV Analysis", command=lambda: self.show_frame('cv_analysis'))
        analysis_menu.add_command(label="Career Path", command=lambda: self.show_frame('career_path'))
        analysis_menu.add_command(label="Career Simulation", command=lambda: self.show_frame('career_simulation'))
        analysis_menu.add_command(label="Market Trends", command=lambda: self.show_frame('market_trends'))
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Instructions", command=self.show_help)
    
    def create_main_frame(self):
        """Create the main container for frames"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        nav_buttons = [
            ("Dashboard", self.show_dashboard, 'dashboard'),
            ("User Profile", lambda: self.show_frame('user_profile'), 'user'),
            ("CV Analysis", lambda: self.show_frame('cv_analysis'), 'cv'),
            ("Career Path", lambda: self.show_frame('career_path'), 'path'),
            ("Career Simulation", lambda: self.show_frame('career_simulation'), 'simulation'),
            ("Market Trends", lambda: self.show_frame('market_trends'), 'trends'),
            ("Settings", lambda: self.show_frame('settings'), 'settings')
        ]
        # Nowoczesny układ: ikona nad tytułem, wszystko wyśrodkowane
        for text, command, icon_key in nav_buttons:
            btn_frame = ttk.Frame(self.nav_frame)
            btn_frame.pack(fill=tk.X, pady=8, padx=4)
            if self.icons.get(icon_key):
                icon_label = ttk.Label(btn_frame, image=self.icons[icon_key], anchor='center', background=self.bg_color)
                icon_label.pack(side=tk.TOP, pady=(0, 4))
            btn = ttk.Button(
                btn_frame,
                text=text,
                command=command,
                style='Nav.TButton',
                width=18
            )
            btn.pack(side=tk.TOP, anchor='center')
        # Ustaw stałą szerokość dla nav_frame, aby przyciski były równo
        self.nav_frame.update_idletasks()
        self.nav_frame.config(width=220)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.frames = {}
        self.create_dashboard_frame()
        self.create_user_profile_frame()
        self.create_cv_analysis_frame()
        self.create_career_path_frame()
        self.create_career_simulation_frame()
        self.create_market_trends_frame()
        self.create_settings_frame()
    
    def show_frame(self, frame_name):
        """Show the selected frame"""
        for frame in self.frames.values():
            frame.pack_forget()
        if frame_name in self.frames:
            self.frames[frame_name].pack(fill=tk.BOTH, expand=True)
    
    def create_dashboard_frame(self):
        """Create the dashboard frame with modern style and logo"""
        dashboard = ttk.Frame(self.content_frame, style='TFrame')
        self.frames['dashboard'] = dashboard
        
        # Logo and header
        header_frame = ttk.Frame(dashboard, style='TFrame')
        header_frame.pack(pady=(0, 20))
        if self.icons.get('logo'):
            logo_label = ttk.Label(header_frame, image=self.icons['logo'], background=self.bg_color)
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
        header = ttk.Label(header_frame, text="AI Career Navigator", style='Header.TLabel', font=('Helvetica', 22, 'bold'))
        header.pack(side=tk.LEFT)
        
        # Information about the system
        info_text = """
        Welcome to AI Career Navigator!
        
        This advanced system supports your career development through:
        • Comprehensive skill analysis
        • Predicting market trends
        • Generating personalized career paths
        • Simulating future career scenarios
        
        Start by loading your CV or creating a profile.
        """
        info_label = ttk.Label(dashboard, text=info_text, wraplength=700, justify='left', font=('Helvetica', 12), background=self.bg_color)
        info_label.pack(pady=10)
        
        # Stats cards (modern look)
        stats_frame = ttk.Frame(dashboard, style='TFrame')
        stats_frame.pack(fill=tk.X, pady=10)
        stats_frame.pack_propagate(False)
        stats_cards = [
            ("Skills", "0", "Number of identified skills", 'cv'),
            ("Market Trends", "15", "Skills with the highest demand growth", 'trends'),
            ("Earning Potential", "0", "Predicted salary growth over 5 years", 'simulation'),
            ("Skill Gaps", "0", "Number of skill gaps to fill", 'settings')
        ]
        for i, (title, value, desc, icon_key) in enumerate(stats_cards):
            card = tk.Frame(stats_frame, bg="white", bd=0, highlightthickness=0)
            card.grid(row=0, column=i, padx=0, pady=0, sticky="nsew")
            if self.icons.get(icon_key):
                icon_label = tk.Label(card, image=self.icons[icon_key], bg="white")
                icon_label.pack(pady=(10, 0))
            tk.Label(card, text=title, font=('Helvetica', 12, 'bold'), fg=self.primary_color, bg="white").pack(pady=(5, 0))
            tk.Label(card, text=value, font=('Helvetica', 24, 'bold'), fg=self.secondary_color, bg="white").pack(pady=5)
            tk.Label(card, text=desc, wraplength=150, justify='center', bg="white").pack(pady=(5, 10))
            card.config(highlightbackground=self.primary_color, highlightcolor=self.primary_color, highlightthickness=2, bd=0)
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Quick access buttons with icons
        quick_access = ttk.Frame(dashboard, style='TFrame')
        quick_access.pack(fill=tk.X, pady=10)
        quick_access.pack_propagate(False)
        quick_buttons = [
            ("Analyze CV", lambda: self.show_frame('cv_analysis'), 'cv'),
            ("Check Trends", lambda: self.show_frame('market_trends'), 'trends'),
            ("Generate Path", lambda: self.show_frame('career_path'), 'path'),
            ("Simulate Career", lambda: self.show_frame('career_simulation'), 'simulation')
        ]
        for i, (text, command, icon_key) in enumerate(quick_buttons):
            btn = ttk.Button(quick_access, text=text, command=command, style='Accent.TButton')
            if self.icons.get(icon_key):
                btn.config(image=self.icons[icon_key], compound=tk.LEFT)
            btn.grid(row=0, column=i, padx=0, pady=0, sticky="nsew")
        for i in range(4):
            quick_access.columnconfigure(i, weight=1)

        # Modernize style for Accent.TButton
        self.style.configure('Accent.TButton', 
                           font=('Helvetica', 11, 'bold'), 
                           foreground='white', 
                           background=self.primary_color, 
                           borderwidth=0, 
                           focusthickness=3, 
                           focuscolor=self.accent_color,
                           padding=(0, 12))
        self.style.map('Accent.TButton', background=[('active', self.secondary_color)])
    
    def create_user_profile_frame(self):
        """Create the user profile frame"""
        profile_frame = ttk.Frame(self.content_frame)
        self.frames['user_profile'] = profile_frame
        
        # Header
        header = ttk.Label(profile_frame, text="User Profile", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Help button
        help_button = ttk.Button(profile_frame, text="Instructions", command=self.show_profile_instructions)
        help_button.pack(pady=(0, 10))
        
        # Inicjalizacja zmiennych formularza
        self.firstname_var = tk.StringVar()  # Imię
        self.lastname_var = tk.StringVar()   # Nazwisko
        self.email_var = tk.StringVar()      # Email
        self.phone_var = tk.StringVar()      # Telefon
        self.location_var = tk.StringVar()   # Lokalizacja
        self.current_role_var = tk.StringVar() # Obecna rola
        self.experience_var = tk.StringVar(value="0") # Lata doświadczenia
        self.industry_var = tk.StringVar()   # Branża
        self.education_var = tk.StringVar()  # Wykształcenie
        self.new_skill_var = tk.StringVar()  # Nowa umiejętność
        self.salary_var = tk.StringVar(value="0")  # Oczekiwania płacowe
        
        # Główna ramka formularza
        form_frame = ttk.Frame(profile_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Personal data
        personal_frame = ttk.LabelFrame(form_frame, text="Personal Data")
        personal_frame.pack(fill=tk.X, pady=10)
        
        # Używaj tylko grid w tej sekcji
        personal_grid = ttk.Frame(personal_frame)
        personal_grid.pack(padx=10, pady=10, fill=tk.X)
        
        # Pierwsze imię
        ttk.Label(personal_grid, text="First Name:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        ttk.Entry(personal_grid, textvariable=self.firstname_var, width=30).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Nazwisko
        ttk.Label(personal_grid, text="Last Name:").grid(row=0, column=2, sticky='w', padx=10, pady=5)
        ttk.Entry(personal_grid, textvariable=self.lastname_var, width=30).grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # Email
        ttk.Label(personal_grid, text="Email:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        ttk.Entry(personal_grid, textvariable=self.email_var, width=30).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Telefon
        ttk.Label(personal_grid, text="Phone:").grid(row=1, column=2, sticky='w', padx=10, pady=5)
        ttk.Entry(personal_grid, textvariable=self.phone_var, width=30).grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # Lokalizacja
        ttk.Label(personal_grid, text="Location:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        ttk.Entry(personal_grid, textvariable=self.location_var, width=30).grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # Doświadczenie zawodowe
        experience_section = ttk.LabelFrame(form_frame, text="Work Experience")
        experience_section.pack(fill=tk.X, pady=10)
        
        experience_grid = ttk.Frame(experience_section)
        experience_grid.pack(padx=10, pady=10, fill=tk.X)
        
        # Obecna rola
        ttk.Label(experience_grid, text="Current Role:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        ttk.Entry(experience_grid, textvariable=self.current_role_var, width=30).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Lata doświadczenia
        ttk.Label(experience_grid, text="Experience (years):").grid(row=0, column=2, sticky='w', padx=10, pady=5)
        ttk.Spinbox(experience_grid, from_=0, to=50, textvariable=self.experience_var, width=5).grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # Branża
        ttk.Label(experience_grid, text="Industry:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        ttk.Entry(experience_grid, textvariable=self.industry_var, width=30).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Edukacja - używając grid w tej sekcji
        education_frame = ttk.LabelFrame(form_frame, text="Education")
        education_frame.pack(fill=tk.X, pady=10)
        
        education_grid = ttk.Frame(education_frame)
        education_grid.pack(padx=10, pady=10, fill=tk.X)
        
        # Tutaj używaj grid, ale w nowym kontenerze
        ttk.Label(education_grid, text="Education:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.education_var = tk.StringVar()
        self.education_combo = ttk.Combobox(education_grid, textvariable=self.education_var, width=30)
        self.education_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        self.education_combo['values'] = ('High School', 'Bachelor', 'Engineer', 'Master', 'Doctor')
        
        # Umiejętności
        skills_frame = ttk.LabelFrame(form_frame, text="Skills")
        skills_frame.pack(fill=tk.X, pady=10)
        
        skills_grid = ttk.Frame(skills_frame)
        skills_grid.pack(padx=10, pady=10, fill=tk.X)
        
        # Lista umiejętności
        ttk.Label(skills_grid, text="Skills List:").grid(row=0, column=0, sticky='nw', padx=10, pady=5)
        
        # Pole tekstowe na umiejętności
        self.skills_text = scrolledtext.ScrolledText(skills_grid, wrap=tk.WORD, width=40, height=5)
        self.skills_text.grid(row=0, column=1, rowspan=3, sticky='w', padx=10, pady=5)
        
        # Przyciski do zarządzania umiejętnościami (prawa strona)
        skills_buttons_frame = ttk.Frame(skills_grid)
        skills_buttons_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Dodawanie umiejętności
        ttk.Label(skills_buttons_frame, text="New Skill:").grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        add_skill_frame = ttk.Frame(skills_buttons_frame)
        add_skill_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Entry(add_skill_frame, textvariable=self.new_skill_var, width=20).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(add_skill_frame, text="Add", command=self.add_skill).grid(row=0, column=1, padx=5, pady=5)
        
        # Usuwanie umiejętności
        ttk.Button(skills_buttons_frame, text="Remove Selected", command=self.remove_skills).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Przyciski
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Save Profile", command=self.save_profile).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Analyze CV", command=lambda: self.show_frame('cv_analysis')).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Clear Form", command=self.clear_profile_form).pack(side=tk.LEFT, padx=10)
    
    def create_cv_analysis_frame(self):
        """Create the CV analysis frame"""
        analysis_frame = ttk.Frame(self.content_frame)
        self.frames['cv_analysis'] = analysis_frame
        
        # Header
        header = ttk.Label(analysis_frame, text="CV Analysis", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Help button
        help_button = ttk.Button(analysis_frame, text="Instructions", command=self.show_cv_instructions)
        help_button.pack(pady=(0, 10))
        
        # Ramka na CV i wyniki analizy (podział na lewą i prawą stronę)
        cv_content_frame = ttk.Frame(analysis_frame)
        cv_content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Lewa strona - wprowadzanie CV
        left_frame = ttk.Frame(cv_content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        cv_input_frame = ttk.LabelFrame(left_frame, text="Enter CV")
        cv_input_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cv_text = scrolledtext.ScrolledText(cv_input_frame, wrap=tk.WORD, width=50, height=20)
        self.cv_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        cv_buttons = ttk.Frame(left_frame)
        cv_buttons.pack(fill=tk.X, pady=10)
        
        ttk.Button(cv_buttons, text="Analyze", command=self.analyze_cv).pack(side=tk.LEFT, padx=5)
        ttk.Button(cv_buttons, text="Load from File", command=self.load_cv).pack(side=tk.LEFT, padx=5)
        ttk.Button(cv_buttons, text="Clear", command=self.clear_cv).pack(side=tk.LEFT, padx=5)
        
        # Prawa strona - wyniki analizy
        right_frame = ttk.Frame(cv_content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Ramka na wyniki analizy CV
        results_frame = ttk.LabelFrame(right_frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dodajemy scrolledText dla wyników analizy
        self.cv_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=50, height=20)
        self.cv_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Dodaj przycisk eksportu do PDF
        export_pdf_btn = ttk.Button(results_frame, text="Export to PDF", command=self.export_cv_analysis_to_pdf)
        export_pdf_btn.pack(pady=8)
        
        # Pozostałe komponenty (tabele, podsumowanie, rekomendacje)
        bottom_frame = ttk.Frame(analysis_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tabela umiejętności
        skills_frame = ttk.LabelFrame(bottom_frame, text="Detected Skills")
        skills_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Utworzenie Treeview dla umiejętności
        columns = ('skill', 'level')
        self.skills_tree = ttk.Treeview(skills_frame, columns=columns, show='headings')
        self.skills_tree.heading('skill', text='Skill')
        self.skills_tree.heading('level', text='Level')
        self.skills_tree.column('skill', width=150)
        self.skills_tree.column('level', width=100)
        self.skills_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Podsumowanie i rekomendacje
        summary_frame = ttk.Frame(bottom_frame)
        summary_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        summary_label = ttk.LabelFrame(summary_frame, text="Summary")
        summary_label.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.summary_text = scrolledtext.ScrolledText(summary_label, wrap=tk.WORD, width=40, height=5)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        recommendations_label = ttk.LabelFrame(summary_frame, text="Recommendations")
        recommendations_label.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.recommendations_text = scrolledtext.ScrolledText(recommendations_label, wrap=tk.WORD, width=40, height=10)
        self.recommendations_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_career_path_frame(self):
        """Create the career path generation frame"""
        path_frame = ttk.Frame(self.content_frame)
        self.frames['career_path'] = path_frame
        
        # Utworzenie głównej ramki
        main_frame = ttk.Frame(path_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = ttk.Label(main_frame, text="Career Path Generator", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Help button - dodajemy na górze formularza
        help_button = ttk.Button(main_frame, text="Instructions", command=self.show_path_instructions)
        help_button.pack(pady=(0, 10))
        
        # Cel zawodowy
        target_frame = ttk.LabelFrame(main_frame, text="Career Goal")
        target_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Kontener na elementy formularza (używamy tylko grid)
        target_grid = ttk.Frame(target_frame)
        target_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Obecna rola
        ttk.Label(target_grid, text="Current Role:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.path_current_role_combo = ttk.Combobox(target_grid, width=30)
        self.path_current_role_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Rola docelowa
        ttk.Label(target_grid, text="Target Role:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.target_role_var = tk.StringVar()
        target_roles = ["Senior Developer", "Tech Lead", "Solution Architect", "CTO", "Project Manager"]
        target_role_combo = ttk.Combobox(target_grid, textvariable=self.target_role_var, values=target_roles, width=30)
        target_role_combo.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Ramy czasowe
        ttk.Label(target_grid, text="Time Frame (years):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.time_frame_var = tk.StringVar(value="5")
        time_frame_spin = ttk.Spinbox(target_grid, from_=1, to=15, textvariable=self.time_frame_var, width=5)
        time_frame_spin.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # Priorytet kariery
        ttk.Label(target_grid, text="Priority:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.path_priority_combo = ttk.Combobox(target_grid, width=30)
        self.path_priority_combo.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        self.path_priority_combo['values'] = ('Salary', 'Speed', 'Work-life balance', 'Skill development')
        self.path_priority_combo.current(0)
        
        # Przycisk generowania
        ttk.Button(target_grid, text="Generate Career Path", command=self.generate_career_path).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Reszta kodu...
    
    def create_career_simulation_frame(self):
        """Create the career simulation frame"""
        simulation_frame = ttk.Frame(self.content_frame)
        self.frames['career_simulation'] = simulation_frame
        
        # Header
        header = ttk.Label(simulation_frame, text="Career Simulation", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Help button
        help_button = ttk.Button(simulation_frame, text="Instructions", command=self.show_simulation_instructions)
        help_button.pack(pady=(0, 10))
        
        # Ramka formularza
        form_frame = ttk.Frame(simulation_frame)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Parametry symulacji
        params_frame = ttk.LabelFrame(form_frame, text="Simulation Parameters")
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Rola docelowa
        target_frame = ttk.Frame(params_frame)
        target_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(target_frame, text="Target Role:").pack(side=tk.LEFT, padx=5)
        
        # Lista ról docelowych
        target_roles = ["Senior Java Developer", "Senior Python Developer", "Frontend Lead", 
                       "Backend Lead", "DevOps Engineer", "Data Scientist", "AI Engineer", 
                       "CTO", "Solution Architect", "Product Manager"]
        self.sim_target_role_var = tk.StringVar()
        target_combo = ttk.Combobox(target_frame, textvariable=self.sim_target_role_var, values=target_roles, width=30)
        target_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Intensywność nauki
        intensity_frame = ttk.Frame(params_frame)
        intensity_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(intensity_frame, text="Learning Intensity (1-10):").pack(side=tk.LEFT, padx=5)
        self.learning_intensity_var = tk.StringVar(value="5")
        ttk.Spinbox(intensity_frame, from_=1, to=10, textvariable=self.learning_intensity_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Strategia zmiany pracy
        strategy_frame = ttk.Frame(params_frame)
        strategy_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(strategy_frame, text="Job Change Strategy:").pack(side=tk.LEFT, padx=5)
        
        strategies = ["Frequent change (every 1-2 years)", "Moderate change (every 2-3 years)", "Long-term (every 4+ years)"]
        self.job_change_strategy_var = tk.StringVar(value=strategies[1])
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.job_change_strategy_var, values=strategies, width=30)
        strategy_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Horyzont czasowy
        time_frame = ttk.Frame(params_frame)
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(time_frame, text="Time Horizon (years):").pack(side=tk.LEFT, padx=5)
        self.sim_time_frame_var = tk.StringVar(value="5")
        ttk.Spinbox(time_frame, from_=1, to=15, textvariable=self.sim_time_frame_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Przyciski akcji
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Run Simulation", command=self.run_career_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_simulation_form).pack(side=tk.LEFT, padx=5)
        
        # Ramka na wyniki
        results_frame = ttk.LabelFrame(simulation_frame, text="Simulation Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Podziel wyniki na dwie części: wykres i szczegóły
        results_paned = ttk.PanedWindow(results_frame, orient=tk.HORIZONTAL)
        results_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Rama na wykres
        self.sim_chart_frame = ttk.Frame(results_paned)
        results_paned.add(self.sim_chart_frame, weight=3)
        
        # Ramka na szczegóły symulacji
        details_frame = ttk.Frame(results_paned)
        results_paned.add(details_frame, weight=2)
        
        # Tabela szczegółów
        columns = ('time', 'role', 'salary', 'skills', 'event')
        self.sim_tree = ttk.Treeview(details_frame, columns=columns, show='headings')
        
        # Definicja nagłówków
        self.sim_tree.heading('time', text='Time (years)')
        self.sim_tree.heading('role', text='Role')
        self.sim_tree.heading('salary', text='Salary')
        self.sim_tree.heading('skills', text='Skills')
        self.sim_tree.heading('event', text='Event')
        
        # Ustawienie szerokości kolumn
        self.sim_tree.column('time', width=80)
        self.sim_tree.column('role', width=150)
        self.sim_tree.column('salary', width=100)
        self.sim_tree.column('skills', width=150)
        self.sim_tree.column('event', width=150)
        
        # Dodanie drzewa i paska przewijania
        self.sim_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.sim_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sim_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_market_trends_frame(self):
        """Create the market trends analysis frame"""
        trends_frame = ttk.Frame(self.content_frame)
        self.frames['market_trends'] = trends_frame
        
        # Header
        header = ttk.Label(trends_frame, text="Market Trends", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Help button
        help_button = ttk.Button(trends_frame, text="Instructions", command=self.show_trends_instructions)
        help_button.pack(pady=(0, 10))
        
        # Ramka formularza
        form_frame = ttk.Frame(trends_frame)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Parametry analizy
        params_frame = ttk.LabelFrame(form_frame, text="Analysis Parameters")
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Kategoria umiejętności
        category_frame = ttk.Frame(params_frame)
        category_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(category_frame, text="Skill Category:").pack(side=tk.LEFT, padx=5)
        
        categories = ["Programming", "DevOps", "Data Science", "Frontend", "Backend", "Mobile", "UX/UI", "Soft Skills"]
        self.skill_category_var = tk.StringVar(value=categories[0])
        category_combo = ttk.Combobox(category_frame, textvariable=self.skill_category_var, values=categories, width=30)
        category_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Zakres czasowy
        time_frame = ttk.Frame(params_frame)
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(time_frame, text="Time Range:").pack(side=tk.LEFT, padx=5)
        
        time_ranges = ["Last year", "Last 2 years", "Last 5 years"]
        self.time_range_var = tk.StringVar(value=time_ranges[0])
        time_combo = ttk.Combobox(time_frame, textvariable=self.time_range_var, values=time_ranges, width=30)
        time_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Minimalna popularność
        popularity_frame = ttk.Frame(params_frame)
        popularity_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(popularity_frame, text="Minimum Popularity (1-10):").pack(side=tk.LEFT, padx=5)
        self.min_popularity_var = tk.StringVar(value="3")
        ttk.Spinbox(popularity_frame, from_=1, to=10, textvariable=self.min_popularity_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Przyciski akcji
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Analyze Trends", command=self.analyze_market_trends).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_trends_form).pack(side=tk.LEFT, padx=5)
        
        # Ramka na wyniki
        results_frame = ttk.LabelFrame(trends_frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Podziel wyniki na zakładki
        tab_control = ttk.Notebook(results_frame)
        tab_control.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zakładka z wykresem popytu
        self.demand_frame = ttk.Frame(tab_control)
        tab_control.add(self.demand_frame, text='Demand')
        
        # Zakładka z wykresem płac
        self.salary_frame = ttk.Frame(tab_control)
        tab_control.add(self.salary_frame, text='Salaries')
        
        # Zakładka z gorącymi umiejętnościami
        hot_skills_frame = ttk.Frame(tab_control)
        tab_control.add(hot_skills_frame, text='Hot Skills')
        
        # Tabela gorących umiejętności
        hot_skills_columns = ('skill', 'growth', 'demand', 'trend')
        self.hot_skills_tree = ttk.Treeview(hot_skills_frame, columns=hot_skills_columns, show='headings')
        
        # Definicja nagłówków
        self.hot_skills_tree.heading('skill', text='Skill')
        self.hot_skills_tree.heading('growth', text='Growth')
        self.hot_skills_tree.heading('demand', text='Demand')
        self.hot_skills_tree.heading('trend', text='Trend')
        
        # Ustawienie szerokości kolumn
        self.hot_skills_tree.column('skill', width=150)
        self.hot_skills_tree.column('growth', width=100)
        self.hot_skills_tree.column('demand', width=100)
        self.hot_skills_tree.column('trend', width=150)
        
        # Dodanie drzewa i paska przewijania
        self.hot_skills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(hot_skills_frame, orient=tk.VERTICAL, command=self.hot_skills_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hot_skills_tree.configure(yscrollcommand=scrollbar.set)
        
        # Zakładka z najlepiej płatnymi umiejętnościami
        top_paid_frame = ttk.Frame(tab_control)
        tab_control.add(top_paid_frame, text='Top Paid')
        
        # Tabela najlepiej płatnych umiejętności
        top_paid_columns = ('skill', 'salary', 'difficulty', 'market_size')
        self.top_paid_tree = ttk.Treeview(top_paid_frame, columns=top_paid_columns, show='headings')
        
        # Definicja nagłówków
        self.top_paid_tree.heading('skill', text='Skill')
        self.top_paid_tree.heading('salary', text='Average Salary')
        self.top_paid_tree.heading('difficulty', text='Difficulty (1-10)')
        self.top_paid_tree.heading('market_size', text='Market Size')
        
        # Ustawienie szerokości kolumn
        self.top_paid_tree.column('skill', width=150)
        self.top_paid_tree.column('salary', width=150)
        self.top_paid_tree.column('difficulty', width=100)
        self.top_paid_tree.column('market_size', width=100)
        
        # Dodanie drzewa i paska przewijania
        self.top_paid_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(top_paid_frame, orient=tk.VERTICAL, command=self.top_paid_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.top_paid_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_settings_frame(self):
        """Create the settings frame"""
        settings_frame = ttk.Frame(self.content_frame)
        self.frames['settings'] = settings_frame
        
        # Header
        header = ttk.Label(settings_frame, text="Settings", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # File Settings
        file_frame = ttk.LabelFrame(settings_frame, text="File Settings")
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        file_grid = ttk.Frame(file_frame)
        file_grid.pack(padx=10, pady=10, fill=tk.X)
        
        # Output directory
        ttk.Label(file_grid, text="Output Directory:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.output_dir_var = tk.StringVar(value="output/")
        output_entry = ttk.Entry(file_grid, textvariable=self.output_dir_var, width=40)
        output_entry.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        ttk.Button(file_grid, text="Browse", command=self.browse_output_dir).grid(row=0, column=2, padx=5)
        
        # Auto-save settings
        self.autosave_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(file_grid, text="Auto-save profile", variable=self.autosave_var).grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # File format
        ttk.Label(file_grid, text="Export Format:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.export_format_var = tk.StringVar(value="JSON")
        format_combo = ttk.Combobox(file_grid, textvariable=self.export_format_var, values=["JSON", "TXT", "CSV"], state="readonly", width=10)
        format_combo.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # Theme Settings (keep this section)
        theme_frame = ttk.LabelFrame(settings_frame, text="Theme Settings")
        theme_frame.pack(fill=tk.X, padx=20, pady=10)
        
        theme_grid = ttk.Frame(theme_frame)
        theme_grid.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(theme_grid, text="Select Theme:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.theme_var = tk.StringVar(value="Light")
        self.theme_combo = ttk.Combobox(theme_grid, textvariable=self.theme_var, values=["Light", "Dark", "Blue", "Green"], state="readonly", width=20)
        self.theme_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        self.theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(e, show_message=True))
        
        # Initialize theme without showing message
        self.change_theme(show_message=False)
        
        # Buttons
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Reset", command=self.reset_settings).pack(side=tk.LEFT, padx=10)
    
    def show_dashboard(self):
        """Show the dashboard"""
        self.show_frame('dashboard')
        
        # Aktualizuj statystyki jeśli dostępne
        if self.user_profile and 'skills' in self.user_profile:
            # Aktualizacja karty umiejętności
            skill_card = self.frames['dashboard'].winfo_children()[2].winfo_children()[0]
            skill_value = skill_card.winfo_children()[1]
            skill_value.configure(text=str(len(self.user_profile['skills'])))
        
        if self.recommendations and 'roi_analysis' in self.recommendations:
            # Aktualizacja karty potencjału zarobkowego
            potential_card = self.frames['dashboard'].winfo_children()[2].winfo_children()[2]
            potential_value = potential_card.winfo_children()[1]
            
            earnings_increase = self.recommendations['roi_analysis'].get('monthly_salary_increase', 0)
            potential_value.configure(text=f"{earnings_increase} PLN")
    
    def load_cv(self):
        """Loads CV from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select CV File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'windows-1250', 'iso-8859-2']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    cv_content = file.read()
                
                # Display content in the text field
                self.cv_text.delete(1.0, tk.END)
                self.cv_text.insert(tk.END, cv_content)
                
                # Show CV analysis frame
                self.show_frame('cv_analysis')
                return
                
            except UnicodeDecodeError:
                continue
        
        # If no encoding worked
        messagebox.showerror("Error", "Cannot load file: unsupported encoding. Try converting the file to UTF-8.")
    
    def load_profile(self):
        """Loads user profile from a file"""
        file_path = filedialog.askopenfilename(
            title="Select Profile File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                
            self.user_profile = profile_data
            self.update_profile_form()
            
            messagebox.showinfo("Success", "User profile has been loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load file: {e}")
    
    def save_profile(self):
        """Saves user profile to a file"""
        file_path = filedialog.asksaveasfilename(
            title="Save User Profile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.update_profile_from_form()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profile, f, indent=4)
                
            messagebox.showinfo("Success", "User profile has been saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file: {e}")
    
    def update_profile_form(self):
        """Updates the profile form with user data"""
        # Personal data
        if 'name' in self.user_profile:
            names = self.user_profile['name'].split()
            self.firstname_var.set(names[0] if names else '')
            self.lastname_var.set(names[1] if len(names) > 1 else '')
        if 'email' in self.user_profile:
            self.email_var.set(self.user_profile['email'])
        if 'phone' in self.user_profile:  # Add phone field
            self.phone_var.set(self.user_profile['phone'])
        if 'location' in self.user_profile:
            self.location_var.set(self.user_profile['location'])
        
        # Professional data
        if 'current_role' in self.user_profile:
            self.current_role_var.set(self.user_profile['current_role'])
        if 'experience_years' in self.user_profile:
            self.experience_var.set(str(self.user_profile['experience_years']))
        if 'industry' in self.user_profile:  # Add industry field
            self.industry_var.set(self.user_profile['industry'])
        if 'education' in self.user_profile:  # Add education field
            self.education_var.set(self.user_profile['education'])
            self.education_combo.set(self.user_profile['education'])
        
        # Skills
        if 'skills' in self.user_profile:
            self.skills_text.delete('1.0', tk.END)
            self.skills_text.insert(tk.END, ', '.join(self.user_profile['skills']))
    
    def update_profile_from_form(self):
        """Aktualizuje profil użytkownika na podstawie formularza"""
        # Osobowe
        self.user_profile['name'] = f"{self.firstname_var.get()} {self.lastname_var.get()}"
        self.user_profile['email'] = self.email_var.get()
        self.user_profile['location'] = self.location_var.get()
        self.user_profile['phone'] = self.phone_var.get()
        
        # Zawodowe
        self.user_profile['current_role'] = self.current_role_var.get()
        self.user_profile['experience_years'] = int(self.experience_var.get())
        self.user_profile['industry'] = self.industry_var.get()
        self.user_profile['education'] = self.education_var.get()
        
        # Oczekiwania płacowe - sprawdź czy istnieje zmienna
        if hasattr(self, 'salary_var'):
            self.user_profile['salary_expectation'] = int(self.salary_var.get())
        else:
            # Jeśli salary_var nie istnieje, ustaw domyślną wartość lub pomiń to pole
            self.user_profile.pop('salary_expectation', None)  # Usuń pole jeśli istnieje
        
        # Umiejętności
        skills_text = self.skills_text.get('1.0', tk.END).strip()
        if skills_text:
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            self.user_profile['skills'] = skills_list
        else:
            self.user_profile['skills'] = []
    
    def analyze_cv(self):
        """Analyzes CV and extracts skills"""
        cv_text = self.cv_text.get('1.0', tk.END).strip()
        
        if not cv_text:
            messagebox.showwarning("Warning", "Please enter CV text before analysis.")
            return
        
        # Inicjalizacja wyników analizy
        self.cv_analysis_results = {
            'skills': [],
            'skill_levels': {}
        }
        
        # Uruchom analizę w osobnym wątku
        def analysis_task():
            try:
                # Analizuj CV
                extracted_skills = self.navigator.skills_analyzer.extract_skills_from_cv(cv_text)
                
                # Analizuj poziomy umiejętności
                skill_levels = {}
                for skill in extracted_skills:
                    level = self.navigator.skills_analyzer.analyze_skill_level(cv_text, skill)
                    skill_levels[skill] = level
                
                # Zapisz wyniki
                self.cv_analysis_results = {
                    'skills': extracted_skills,
                    'skill_levels': skill_levels
                }
                
                # Aktualizuj UI po zakończeniu
                self.root.after(0, self.update_after_cv_analysis)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error during CV analysis: {e}"))
        
        # Uruchom analizę w nowym wątku
        threading.Thread(target=analysis_task, daemon=True).start()
        
        messagebox.showinfo("Information", "CV analysis started. Results will be displayed upon completion.")
    
    def update_after_cv_analysis(self):
        """Updates UI after CV analysis"""
        try:
            # Clear skills table
            for item in self.skills_tree.get_children():
                self.skills_tree.delete(item)
            
            # Fill skills table
            for skill in self.cv_analysis_results['skills']:
                level = self.cv_analysis_results['skill_levels'].get(skill, 1)
                level_text = ['Basic', 'Intermediate', 'Advanced', 'Expert'][min(level-1, 3)]
                
                self.skills_tree.insert('', 'end', values=(skill, level_text))
            
            # Update text summary
            summary = f"Detected {len(self.cv_analysis_results['skills'])} skills.\n\n"
            
            # Add skills by levels
            levels = {
                'Basic': [],
                'Intermediate': [],
                'Advanced': [],
                'Expert': []
            }
            
            for skill, level in self.cv_analysis_results['skill_levels'].items():
                level_text = ['Basic', 'Intermediate', 'Advanced', 'Expert'][min(level-1, 3)]
                levels[level_text].append(skill)
            
            for level, skills in levels.items():
                if skills:
                    summary += f"\n{level}: {', '.join(skills)}"
            
            # Display summary
            self.summary_text.delete('1.0', tk.END)
            self.summary_text.insert(tk.END, summary)
            
            # Display results in right window
            self.cv_results_text.delete('1.0', tk.END)
            self.cv_results_text.insert(tk.END, f"CV ANALYSIS RESULTS\n\n")
            self.cv_results_text.insert(tk.END, f"Detected {len(self.cv_analysis_results['skills'])} skills.\n\n")
            
            # List all skills with levels
            self.cv_results_text.insert(tk.END, "Detailed results:\n\n")
            for skill, level in self.cv_analysis_results['skill_levels'].items():
                level_text = ['Basic', 'Intermediate', 'Advanced', 'Expert'][min(level-1, 3)]
                self.cv_results_text.insert(tk.END, f"- {skill}: {level_text}\n")
            
            # Add recommendations
            self.cv_results_text.insert(tk.END, "\n\nRECOMMENDATIONS:\n\n")
            
            for skill in self.cv_analysis_results['skills'][:5]:  # Top 5 skills
                try:
                    resources = self.navigator.skills_analyzer.recommend_learning_resources(skill)
                    self.cv_results_text.insert(tk.END, f"For skill {skill}:\n")
                    for resource in resources[:3]:  # Top 3 resources
                        self.cv_results_text.insert(tk.END, f"- {resource}\n")
                except AttributeError:
                    self.cv_results_text.insert(tk.END, f"For skill {skill}:\n")
                    self.cv_results_text.insert(tk.END, f"- Online courses (e.g., Udemy, Coursera)\n")
                    self.cv_results_text.insert(tk.END, f"- Documentation and tutorials\n")
                    self.cv_results_text.insert(tk.END, f"- Practical projects\n")
                
                self.cv_results_text.insert(tk.END, "\n")
            
            # Generate recommendations for key skills
            recommendations = "Skill development recommendations:\n\n"
            
            for skill in self.cv_analysis_results['skills'][:5]:  # Top 5 skills
                try:
                    resources = self.navigator.skills_analyzer.recommend_learning_resources(skill)
                    recommendations += f"For skill {skill}:\n"
                    for resource in resources[:3]:  # Top 3 resources
                        recommendations += f"- {resource}\n"
                except AttributeError:
                    recommendations += f"For skill {skill}:\n"
                    recommendations += f"- Online courses (e.g., Udemy, Coursera)\n"
                    recommendations += f"- Documentation and tutorials\n"
                    recommendations += f"- Practical projects\n"
                recommendations += "\n"
            
            # Display recommendations
            self.recommendations_text.delete('1.0', tk.END)
            self.recommendations_text.insert(tk.END, recommendations)
            
            # Zaktualizuj profil użytkownika
            if 'skills' not in self.user_profile:
                self.user_profile['skills'] = []
            
            # Dodaj nowe umiejętności (bez duplikatów)
            for skill in self.cv_analysis_results['skills']:
                if skill not in self.user_profile['skills']:
                    self.user_profile['skills'].append(skill)
            
            # Aktualizuj formularz profilu
            self.update_profile_form()
            
            messagebox.showinfo("Success", "CV analysis has been completed.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating results: {str(e)}")
    
    def generate_career_path(self):
        """Generates a career path based on selected parameters"""
        try:
            # Sprawdź czy mamy wymaganą rolę docelową
            target_role = self.target_role_var.get()
            if not target_role:
                messagebox.showwarning("Warning", "Please select a target role.")
                return
            
            # Pobierz dane z formularza
            current_role = self.path_current_role_combo.get()
            if not current_role:
                messagebox.showwarning("Warning", "Please specify the current role.")
                return
            
            # Pobierz ramy czasowe
            try:
                time_frame = int(self.time_frame_var.get())
            except ValueError:
                messagebox.showwarning("Warning", "Invalid time frame value.")
                return
            
            # Priorytet
            priority = self.path_priority_combo.get()
            
            # Pokaż komunikat o przetwarzaniu
            messagebox.showinfo("Information", "Generating career path. Please wait...")
            
            # Uruchom generowanie w osobnym wątku, aby nie blokować interfejsu
            def generate_task():
                try:
                    # Utwórz zapytanie do generatora ścieżki
                    request = {
                        'current_role': current_role,
                        'target_role': target_role,
                        'time_frame': time_frame,
                        'priority': priority
                    }
                    
                    # Pobierz profil użytkownika
                    if hasattr(self, 'user_profile') and self.user_profile:
                        user_skills = self.user_profile.get('skills', [])
                        experience = self.user_profile.get('experience_years', 0)
                        request['user_skills'] = user_skills
                        request['experience_years'] = experience
                    
                    # Generuj ścieżkę kariery
                    self.path_results = self.navigator.career_path_generator.generate_path(request)
                    
                    # Aktualizuj UI w głównym wątku
                    self.root.after(0, self.display_career_path_results)
                except Exception as e:
                    error_msg = f"Error generating career path: {str(e)}"
                    self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            
            # Uruchom generowanie w nowym wątku
            threading.Thread(target=generate_task, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def display_career_path_results(self):
        """Displays the results of the career path generation"""
        if not hasattr(self, 'path_results') or not self.path_results:
            messagebox.showinfo("Information", "No results to display.")
            return
        
        try:
            # Create larger window for results
            results_window = tk.Toplevel(self.root)
            results_window.title("Career Path Results")
            results_window.geometry("1000x800")  # Increased size
            results_window.transient(self.root)
            
            # Create notebook with tabs
            notebook = ttk.Notebook(results_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Visualization tab
            viz_frame = ttk.Frame(notebook)
            notebook.add(viz_frame, text='Visualization')
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Chart data
            roles = [step['role'] for step in self.path_results['steps']]
            # Convert PLN to EUR (approximate exchange rate 1 EUR = 4.5 PLN)
            salaries = [step['salary'] / 4.5 for step in self.path_results['steps']]
            times = [step['time_months'] for step in self.path_results['steps']]
            
            # Bar chart
            bars = ax.bar(range(len(roles)), salaries, color=self.primary_color)
            
            # Labels
            ax.set_xlabel('Career Step')
            ax.set_ylabel('Salary (EUR)')
            ax.set_title('Career Development Path')
            ax.set_xticks(range(len(roles)))
            ax.set_xticklabels(roles, rotation=45, ha='right')
            
            # Add time duration info
            for i, (bar, time) in enumerate(zip(bars, times)):
                ax.text(i, bar.get_height() + 200, f"{time} months", 
                        ha='center', va='bottom', rotation=0)
            
            plt.tight_layout()
            
            # Add chart to Tkinter frame
            canvas = FigureCanvasTkAgg(fig, viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Details tab
            details_frame = ttk.Frame(notebook)
            notebook.add(details_frame, text='Details')
            
            # Career path table
            path_columns = ('role', 'level', 'salary', 'time', 'skills')
            path_tree = ttk.Treeview(details_frame, columns=path_columns, show='headings')
            
            # Define headers
            path_tree.heading('role', text='Role')
            path_tree.heading('level', text='Level')
            path_tree.heading('salary', text='Salary')
            path_tree.heading('time', text='Time (months)')
            path_tree.heading('skills', text='Required Skills')
            
            # Define column widths
            path_tree.column('role', width=150)
            path_tree.column('level', width=100)
            path_tree.column('salary', width=100)
            path_tree.column('time', width=100)
            path_tree.column('skills', width=300)
            
            # Fill table with data
            for i, step in enumerate(self.path_results['steps']):
                skills_str = ', '.join(step['required_skills'])
                path_tree.insert('', 'end', values=(
                    step['role'],
                    step['level'],
                    f"{step['salary'] / 4.5:.0f} EUR",  # Convert PLN to EUR
                    step['time_months'],
                    skills_str
                ))
            
            path_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Add scrollbar
            path_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=path_tree.yview)
            path_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            path_tree.configure(yscrollcommand=path_scrollbar.set)
            
            # Skills to Acquire tab
            skills_frame = ttk.Frame(notebook)
            notebook.add(skills_frame, text='Skills to Acquire')
            
            # Skills to acquire table
            skills_columns = ('skill', 'priority', 'difficulty', 'time')
            skills_tree = ttk.Treeview(skills_frame, columns=skills_columns, show='headings')
            
            # Define headers
            skills_tree.heading('skill', text='Skill')
            skills_tree.heading('priority', text='Priority')
            skills_tree.heading('difficulty', text='Difficulty')
            skills_tree.heading('time', text='Learning Time (months)')
            
            # Define column widths
            skills_tree.column('skill', width=150)
            skills_tree.column('priority', width=100)
            skills_tree.column('difficulty', width=100)
            skills_tree.column('time', width=150)
            
            # Priority translation dictionary
            priority_translation = {
                'Wysoki': 'High',
                'Średni': 'Medium',
                'Niski': 'Low'
            }
            
            # Fill table with data
            skills_to_learn = self.path_results.get('skills_to_learn', [])
            for skill in skills_to_learn:
                # Translate priority to English
                priority = priority_translation.get(skill['priority'], skill['priority'])
                skills_tree.insert('', 'end', values=(
                    skill['name'],
                    priority,
                    skill['difficulty'],
                    skill['learning_time_months']
                ))
            
            skills_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Add scrollbar
            skills_scrollbar = ttk.Scrollbar(skills_frame, orient=tk.VERTICAL, command=skills_tree.yview)
            skills_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            skills_tree.configure(yscrollcommand=skills_scrollbar.set)
            
            # Close button
            ttk.Button(results_window, text="Close", command=results_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying results: {str(e)}")

    def show_path_instructions(self):
        """Displays instructions for the career path generator"""
        instructions = """
INSTRUCTIONS FOR CAREER PATH GENERATOR:

1. ENTERING DATA:
   • Current Role: Select your current job position
   • Target Role: Specify the position you want to achieve
   • Time Frame: Enter the number of years you want to spend on development
   • Priority: Choose the most important aspect (salary, speed, balance)

2. GENERATING THE PATH:
   • Click the "Generate Career Path" button
   • Wait for the data to be processed and the optimal path to be generated

3. INTERPRETING RESULTS:
   • "Visualization" tab - graphical presentation of the career path
   • "Details" tab - table with a detailed description of each step
   • "Skills to Acquire" tab - list of skills to master

4. TIPS:
   • Fill in your user profile beforehand to include your existing skills
   • Experiment with different priorities and time frames
   • Note the required skills for each stage of the path
   
5. LIMITATIONS:
   • The generator takes into account current market trends and may not predict future changes
   • Actual career development may differ from the generated path
   • Regularly update your profile to receive more accurate recommendations
    """
        
        instruction_window = tk.Toplevel(self.root)
        instruction_window.title("Career Path Generator Instructions")
        instruction_window.geometry("600x500")
        instruction_window.transient(self.root)
        
        instruction_text = scrolledtext.ScrolledText(instruction_window, wrap=tk.WORD)
        instruction_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        instruction_text.insert(tk.END, instructions)
        instruction_text.config(state=tk.DISABLED)  # Tylko do odczytu
        
        ttk.Button(instruction_window, text="Close", command=instruction_window.destroy).pack(pady=10)
    
    def run_career_simulation(self):
        """Runs the career simulation"""
        # Walidacja danych
        target_role = self.sim_target_role_var.get()
        if not target_role:
            messagebox.showwarning("Warning", "Please select a target role.")
            return
        
        try:
            time_frame = int(self.sim_time_frame_var.get())
            learning_intensity = int(self.learning_intensity_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Please enter valid numeric values.")
            return
        
        job_change_strategy = self.job_change_strategy_var.get()
        
        # Komunikat o rozpoczęciu symulacji
        messagebox.showinfo("Information", "Career simulation started. Results will be displayed upon completion.")
        
        # Uruchom symulację w osobnym wątku
        threading.Thread(target=self._run_simulation_task, args=(
            target_role, time_frame, learning_intensity, job_change_strategy
        ), daemon=True).start()

    def _run_simulation_task(self, target_role, time_frame, learning_intensity, job_change_strategy):
        """Runs the career simulation in a separate thread"""
        try:
            # Pobierz obecną rolę z profilu użytkownika lub ustaw domyślną
            current_role = self.user_profile.get('current_role', 'Junior Developer')
            
            # Określ częstotliwość zmiany pracy na podstawie strategii
            if "częsta" in job_change_strategy.lower():
                job_change_rate = 1.5  # co 1.5 roku
            elif "umiarkowana" in job_change_strategy.lower():
                job_change_rate = 2.5  # co 2.5 roku
            else:  # długoterminowa
                job_change_rate = 4.0  # co 4 lata
            
            # Zainicjuj parametry symulacji
            events = []
            current_time = 0.0
            current_salary = self._get_salary_for_role(current_role)
            current_skills = self.user_profile.get('skills', [])
            if not current_skills:
                current_skills = ["Programming", "Basic IT"]  # domyślne umiejętności
            
            # Dodaj wydarzenie początkowe
            events.append({
                'time': 0,
                'role': current_role,
                'salary': current_salary,
                'skills': current_skills.copy(),
                'event': 'Start of simulation'
            })
            
            # Symuluj ścieżkę kariery
            while current_time < time_frame:
                # Postęp nauki zależy od intensywności
                learning_progress = learning_intensity / 10.0  # Od 0.1 do 1.0
                
                # Upływ czasu do następnego wydarzenia
                next_time_increment = min(0.5, time_frame - current_time)  # Maksymalnie pół roku
                current_time += next_time_increment
                
                # Dodaj nowe umiejętności z określonym prawdopodobieństwem
                if random.random() < learning_progress * next_time_increment:
                    new_skill = self._get_random_skill_for_career(target_role)
                    if new_skill and new_skill not in current_skills:
                        current_skills.append(new_skill)
                        events.append({
                            'time': round(current_time, 1),
                            'role': current_role,
                            'salary': current_salary,
                            'skills': current_skills.copy(),
                            'event': f'Acquired skill: {new_skill}'
                        })
                
                # Sprawdź możliwość zmiany pracy
                if len(events) > 1 and (current_time - events[0]['time']) >= job_change_rate and random.random() < 0.3:
                    old_role = current_role
                    current_role = self._get_next_career_step(current_role, target_role, current_time / time_frame)
                    new_salary = self._get_salary_for_role(current_role)
                    
                    # Dodaj wydarzenie zmiany pracy
                    current_salary = new_salary
                    events.append({
                        'time': round(current_time, 1),
                        'role': current_role,
                        'salary': current_salary,
                        'skills': current_skills.copy(),
                        'event': f'Job change: {old_role} → {current_role}'
                    })
            
            # Dodaj wydarzenie końcowe, jeśli ostatnie wydarzenie nie jest blisko końca symulacji
            if abs(events[-1]['time'] - time_frame) > 0.1:
                events.append({
                    'time': time_frame,
                    'role': current_role,
                    'salary': current_salary,
                    'skills': current_skills,
                    'event': 'End of simulation'
                })
            
            # Oblicz wzrost wynagrodzenia
            initial_salary = events[0]['salary']
            final_salary = events[-1]['salary']
            salary_growth = ((final_salary / initial_salary) - 1) * 100 if initial_salary > 0 else 0
            
            # Przygotuj wyniki
            results = {
                'events': events,
                'initial_role': events[0]['role'],
                'final_role': events[-1]['role'],
                'initial_salary': initial_salary,
                'final_salary': final_salary,
                'salary_growth': round(salary_growth, 1),
                'skills_acquired': len(events[-1]['skills']) - len(events[0]['skills'])
            }
            
            # Aktualizuj UI w głównym wątku
            self.root.after(0, lambda: self.display_simulation_results(results))
            
        except Exception as e:
            # Obsługa błędów
            error_msg = f"Error during simulation: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

    def _get_salary_for_role(self, role):
        """Returns an approximate salary for a given role"""
        # Podstawowe wynagrodzenia dla różnych poziomów
        base_salaries = {
            'Junior': 7000,
            'Mid': 12000,
            'Senior': 18000,
            'Lead': 22000,
            'Manager': 25000,
            'Architect': 28000,
            'Director': 35000,
            'CTO': 45000
        }
        
        # Sprawdź, czy rola zawiera któryś z kluczy
        role_lower = role.lower()
        for level, salary in base_salaries.items():
            if level.lower() in role_lower:
                # Dodaj losową wariację +/- 10%
                variation = random.uniform(0.9, 1.1)
                return int(salary * variation)
        
        # Domyślne wynagrodzenie, jeśli nie znaleziono dopasowania
        return 10000

    def _get_random_skill_for_career(self, target_role):
        """Returns a random skill useful for a given career path"""
        # Typowe umiejętności dla różnych ścieżek kariery
        skills_by_path = {
            'java': ["Java", "Spring", "Hibernate", "Maven", "JUnit", "SQL", "Design Patterns", "Microservices"],
            'python': ["Python", "Django", "Flask", "Pandas", "NumPy", "SQL", "REST API", "Git"],
            'frontend': ["HTML", "CSS", "JavaScript", "React", "Angular", "TypeScript", "Webpack", "UI/UX"],
            'backend': ["Design Patterns", "REST API", "Databases", "Caching", "Security", "Containerization", "Microservices"],
            'devops': ["Docker", "Kubernetes", "Jenkins", "AWS", "Terraform", "Ansible", "Linux", "Monitoring"],
            'data': ["SQL", "Python", "Data Analysis", "Data Visualization", "Statistics", "ETL", "Big Data"],
            'ai': ["Machine Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Statistics", "Deep Learning"],
            'architect': ["System Design", "Scalability", "Performance Optimization", "Security", "Cloud Architecture"],
            'manager': ["Team Leadership", "Project Management", "Agile", "Communication", "Budget Planning", "Risk Management"]
        }
        
        # Znajdź odpowiednią kategorię umiejętności na podstawie roli docelowej
        target_lower = target_role.lower()
        relevant_skills = []
        
        for path, skills in skills_by_path.items():
            if path in target_lower:
                relevant_skills.extend(skills)
        
        # Jeśli nie znaleziono specyficznych umiejętności, użyj wspólnych
        if not relevant_skills:
            relevant_skills = [
                "Communication", "Problem Solving", "Teamwork", "Git", 
                "HTTP", "REST API", "Documentation", "Testing", "Debugging"
            ]
        
        # Dodaj umiejętności miękkie
        soft_skills = [
            "Communication", "Teamwork", "Time Management", "Critical Thinking",
            "Presentation", "Negotiation", "Conflict Management", "Mentoring"
        ]
        
        # Połącz wszystkie umiejętności i wybierz losową
        all_skills = list(set(relevant_skills + soft_skills))
        return random.choice(all_skills) if all_skills else None

    def clear_simulation_form(self):
        """Clears the career simulation form"""
        self.sim_target_role_var.set("")
        self.learning_intensity_var.set("5")
        self.job_change_strategy_var.set("Moderate change (every 2-3 years)")
        self.sim_time_frame_var.set("5")
        
        # Wyczyść wyniki
        for item in self.sim_tree.get_children():
            self.sim_tree.delete(item)
        
        for widget in self.sim_chart_frame.winfo_children():
            widget.destroy()

    def display_simulation_results(self, results):
        """Displays the results of the career simulation"""
        # Wyczyść istniejące wyniki
        for item in self.sim_tree.get_children():
            self.sim_tree.delete(item)
        
        for widget in self.sim_chart_frame.winfo_children():
            widget.destroy()
        
        # Wypełnij tabelę szczegółów
        for event in results['events']:
            salary_eur = round(event['salary'] / 4.5, 2)  # Convert PLN to EUR
            self.sim_tree.insert('', 'end', values=(
                event['time'],
                event['role'],
                f"{salary_eur:.2f} EUR",
                ", ".join(event['skills'][:3]) + ("..." if len(event['skills']) > 3 else ""),
                event['event']
            ))
        
        # Create larger chart frame
        chart_frame = ttk.Frame(self.sim_chart_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Adjust figure size and spacing
        fig, ax = plt.subplots(figsize=(12, 8))  # Increased figure size
        
        # Prepare data - convert salary to EUR
        times = [event['time'] for event in results['events']]
        salaries = [event['salary'] / 4.5 for event in results['events']]  # Convert PLN to EUR
        roles = [event['role'] for event in results['events']]
        
        # Main plot
        ax.plot(times, salaries, marker='o', linestyle='-', color=self.primary_color, linewidth=2, markersize=8)
        
        # Add role labels with more spacing
        for i, (x, y, role) in enumerate(zip(times, salaries, roles)):
            ax.annotate(
                role,
                (x, y),
                xytext=(0, 20),  # Increased vertical offset
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=8,
                rotation=45  # Rotate labels to prevent overlap
            )
        
        ax.set_title('Career Development Simulation')
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Salary (EUR)')  # Changed to EUR
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Dodaj wykres do ramki
        canvas = FigureCanvasTkAgg(fig, master=self.sim_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Podsumowanie
        messagebox.showinfo("Simulation Summary", 
                           f"Simulation completed successfully.\n"
                           f"Simulation time: {results['events'][-1]['time']} years\n"
                           f"Final role: {results['events'][-1]['role']}\n"
                           f"Salary growth: {results['salary_growth']}%")

    def create_career_simulation_chart(self, results):
        """Creates a career simulation chart"""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Przygotuj dane do wykresu
        times = [event['time'] for event in results['events']]
        salaries = [event['salary'] for event in results['events']]
        roles = [event['role'] for event in results['events']]
        
        # Główny wykres
        ax.plot(times, salaries, marker='o', linestyle='-', color=self.primary_color, linewidth=2, markersize=8)
        
        # Dodaj etykiety dla punktów
        for i, (x, y, role) in enumerate(zip(times, salaries, roles)):
            ax.annotate(
                role,
                (x, y),
                xytext=(0, 10),
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=8
            )
        
        # Dodaj znaczniki dla ważnych wydarzeń
        for event in results['events']:
            if event['event'] != "Kontynuacja pracy":
                x = event['time']
                y = event['salary']
                ax.plot(x, y, 'o', color=self.accent_color, markersize=10)
        
        ax.set_title('Career Development Simulation')
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Salary (PLN)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Dodaj wykres do ramki
        canvas = FigureCanvasTkAgg(fig, master=self.sim_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def analyze_market_trends(self):
        """Analyzes market trends based on selected parameters"""
        category = self.skill_category_var.get()
        time_range = self.time_range_var.get()
        
        try:
            min_popularity = float(self.min_popularity_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid minimum popularity value.")
            return
        
        messagebox.showinfo("Information", "Market trends analysis started. Results will be displayed upon completion.")
        
        # Uruchom analizę w osobnym wątku
        threading.Thread(target=self._run_trends_analysis, args=(
            category, time_range, min_popularity
        ), daemon=True).start()

    def _run_trends_analysis(self, category, time_range, min_popularity):
        """Performs market trends analysis in a separate thread"""
        try:
            results = self.generate_market_trends(category, time_range, min_popularity)
            self.root.after(0, lambda: self.display_trends_results(results))
        except Exception as e:
            error_msg = f"Error during trends analysis: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

    def generate_market_trends(self, category, time_range, min_popularity):
        """Generates market trends data based on selected parameters"""
        try:
            # Convert time range to months
            months = {
                "Last year": 12,
                "Last 2 years": 24,
                "Last 5 years": 60
            }.get(time_range, 12)

            # Sample skills for each category
            skills_by_category = {
                "Programming": ["Python", "Java", "JavaScript", "C++", "Go", "Rust", "TypeScript", "PHP"],
                "DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "Jenkins", "Terraform", "Ansible"],
                "Data Science": ["Python", "R", "SQL", "TensorFlow", "PyTorch", "Pandas", "Scikit-learn"],
                "Frontend": ["React", "Angular", "Vue.js", "HTML5", "CSS3", "JavaScript", "TypeScript"],
                "Backend": ["Node.js", "Django", "Spring", "Flask", ".NET", "Express.js"],
                "Mobile": ["Flutter", "React Native", "Kotlin", "Swift", "Android SDK", "iOS"],
                "UX/UI": ["Figma", "Adobe XD", "Sketch", "UI Design", "User Research", "Prototyping"],
                "Soft Skills": ["Communication", "Leadership", "Project Management", "Agile", "Scrum"]
            }

            # Get skills for selected category
            selected_skills = skills_by_category.get(category, skills_by_category["Programming"])

            # Generate sample data
            from datetime import datetime, timedelta
            import random
            import numpy as np

            end_date = datetime.now()
            dates = [(end_date - timedelta(days=30*i)) for i in range(months)]
            dates.reverse()

            # Generate trends data
            hot_skills = []
            demand_trends = {}
            salary_trends = {}
            top_paid_skills = []

            for skill in selected_skills:
                # Generate demand trend
                base_demand = random.uniform(5, 10)
                growth_rate = random.uniform(0.02, 0.15)
                trend_type = random.choice(["Growing", "Stable", "High Demand"])
                
                demand_values = []
                salary_values = []
                
                for i, date in enumerate(dates):
                    # Calculate demand with some randomness
                    demand = base_demand * (1 + growth_rate * i/12) * random.uniform(0.95, 1.05)
                    demand_values.append((date, max(1, min(10, demand))))
                    
                    # Calculate salary with trend
                    base_salary = random.uniform(3000, 8000)  # Base salary in EUR
                    salary = base_salary * (1 + growth_rate * i/12) * random.uniform(0.98, 1.02)
                    salary_values.append((date, salary))

                # Store trends
                demand_trends[skill] = demand_values
                salary_trends[skill] = salary_values

                # Calculate growth percentage
                initial_demand = demand_values[0][1]
                final_demand = demand_values[-1][1]
                growth_percent = ((final_demand - initial_demand) / initial_demand) * 100

                if growth_percent >= min_popularity:
                    hot_skills.append({
                        'skill': skill,
                        'growth': growth_percent,
                        'demand': final_demand,
                        'trend': trend_type
                    })

                # Add to top paid skills
                top_paid_skills.append({
                    'skill': skill,
                    'salary': int(salary_values[-1][1]),
                    'difficulty': random.randint(5, 10),
                    'market_size': f"{random.randint(1000, 10000)}+ positions"
                })

            # Sort hot skills by growth
            hot_skills.sort(key=lambda x: x['growth'], reverse=True)
            
            # Sort top paid skills by salary
            top_paid_skills.sort(key=lambda x: x['salary'], reverse=True)

            return {
                'hot_skills': hot_skills[:10],  # Top 10 hot skills
                'top_paid_skills': top_paid_skills[:10],  # Top 10 paid skills
                'demand_trends': demand_trends,
                'salary_trends': salary_trends
            }

        except Exception as e:
            print(f"Error generating market trends: {str(e)}")
            # Return default structure to avoid NoneType errors
            return {
                'hot_skills': [
                    {'skill': 'Python', 'growth': 15.0, 'demand': 9.5, 'trend': 'Growing'},
                    {'skill': 'JavaScript', 'growth': 12.0, 'demand': 9.0, 'trend': 'Stable'}
                ],
                'top_paid_skills': [
                    {'skill': 'Python', 'salary': 5000, 'difficulty': 7, 'market_size': '5000+ positions'},
                    {'skill': 'JavaScript', 'salary': 4500, 'difficulty': 6, 'market_size': '4000+ positions'}
                ],
                'demand_trends': {'Python': [(datetime.now(), 9.5)]},
                'salary_trends': {'Python': [(datetime.now(), 5000)]}
            }

    def show_trends_instructions(self):
        """Displays instructions for market trends analysis"""
        instructions = """
INSTRUCTIONS FOR MARKET TRENDS ANALYSIS:

1. SELECT ANALYSIS PARAMETERS:
   • Skill Category: Choose the category you are interested in (e.g., Programming, Marketing)
   • Time Range: Specify the period for which you want to see trends
   • Minimum Popularity: Choose the popularity threshold for skills

2. RUNNING THE ANALYSIS:
   • Click the "Analyze Trends" button
   • Wait for the data to be fetched and analyzed
   • Results will be displayed on charts and tables

3. INTERPRETING RESULTS:
   • Demand Chart: Shows changes in skill demand over time
   • Salary Chart: Displays salary trends for skills
   • Hot Skills Table: List of skills with the fastest demand growth
   • Top Paid Skills Table: Skills with the highest salaries

4. USING THE RESULTS:
   • Identify skills worth developing
   • Plan your career path based on market trends
   • Adjust your job search strategy to current trends
    """
    
        self.show_instructions_window("Market Trends Analysis Instructions", instructions)

    def show_instructions_window(self, title, instructions_text):
        """Displays an instructions window"""
        instruction_window = tk.Toplevel(self.root)
        instruction_window.title(title)
        instruction_window.geometry("600x500")
        instruction_window.transient(self.root)
        
        instruction_text = scrolledtext.ScrolledText(instruction_window, wrap=tk.WORD)
        instruction_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        instruction_text.insert(tk.END, instructions_text)
        instruction_text.config(state=tk.DISABLED)  # Tylko do odczytu
        
        ttk.Button(instruction_window, text="Close", command=instruction_window.destroy).pack(pady=10)

    def display_trends_results(self, results):
        """Displays the results of the trends analysis"""
        # Wyczyść istniejące wyniki
        for item in self.hot_skills_tree.get_children():
            self.hot_skills_tree.delete(item)
        
        for item in self.top_paid_tree.get_children():
            self.top_paid_tree.delete(item)
        
        for widget in self.demand_frame.winfo_children():
            widget.destroy()
        
        for widget in self.salary_frame.winfo_children():
            widget.destroy()
        
        # Wypełnij tabelę gorących umiejętności
        for skill in results['hot_skills']:
            self.hot_skills_tree.insert('', 'end', values=(
                skill['skill'],
                f"{skill['growth']:.1f}%",
                f"{skill['demand']:.1f}",
                skill['trend']
            ))
        
        # Convert salaries to EUR in top paid skills table
        for skill in results['top_paid_skills']:
            salary_eur = round(skill['salary'] / 4.5, 2)  # Convert PLN to EUR
            self.top_paid_tree.insert('', 'end', values=(
                skill['skill'],
                f"{salary_eur:.2f} EUR",
                skill['difficulty'],
                skill['market_size']
            ))
        
        # Utwórz wykres popytu
        self.create_trends_chart(self.demand_frame, results['demand_trends'], 
                               'Skill Demand Trends', 'Demand (1-10)', 
                               figsize=(12, 8))  # Larger chart
        
        # Convert salary values to EUR and create chart
        salary_trends_eur = {
            skill: [(date, value/4.5) for date, value in data] 
            for skill, data in results['salary_trends'].items()
        }
        self.create_trends_chart(self.salary_frame, salary_trends_eur,
                               'Salary Trends for Skills', 'Salary (EUR)',
                               figsize=(12, 8))  # Larger chart
        
        # Podsumowanie
        messagebox.showinfo("Analysis Summary", 
                           f"Analyzed {len(results['hot_skills'])} skills.\n"
                           f"Fastest growing: {results['hot_skills'][0]['skill']} ({results['hot_skills'][0]['growth']:.1f}%)\n"
                           f"Highest paid: {results['top_paid_skills'][0]['skill']} ({results['top_paid_skills'][0]['salary']} EUR)")

    def create_trends_chart(self, parent_frame, trends_data, title, y_label, figsize=(12, 8)):
        """Creates a trends chart with specified size"""
        fig, ax = plt.subplots(figsize=figsize)  # Use specified figure size
        
        # Wybierz maksymalnie 5 najważniejszych umiejętności do pokazania
        top_skills = sorted(trends_data.items(), key=lambda x: x[1][-1][1], reverse=True)[:5]
        
        for skill, data in top_skills:
            dates, values = zip(*data)
            # If this is a salary chart (checking y_label), convert values to EUR
            if 'Salary' in y_label:
                values = [val / 4.5 for val in values]  # Convert PLN to EUR
            ax.plot(dates, values, marker='o', linestyle='-', label=skill)
        
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel(y_label)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Obróć etykiety osi X dla lepszej czytelności
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Dodaj wykres do ramki
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_trends_form(self):
        """Clears the trends analysis form"""
        self.skill_category_var.set("Programming")
        self.time_range_var.set("Last year")
        self.min_popularity_var.set("3")
        
        # Wyczyść wyniki
        for item in self.hot_skills_tree.get_children():
            self.hot_skills_tree.delete(item)
        
        for item in self.top_paid_tree.get_children():
            self.top_paid_tree.delete(item)
        
        for widget in self.demand_frame.winfo_children():
            widget.destroy()
        
        for widget in self.salary_frame.winfo_children():
            widget.destroy()

    def clear_simulation_form(self):
        """Clears the career simulation form"""
        self.sim_target_role_var.set("")
        self.learning_intensity_var.set("5")
        self.job_change_strategy_var.set("Moderate change (every 2-3 years)")
        self.sim_time_frame_var.set("5")
        
        # Wyczyść wyniki
        for item in self.sim_tree.get_children():
            self.sim_tree.delete(item)
        
        for widget in self.sim_chart_frame.winfo_children():
            widget.destroy()

    def display_simulation_results(self, results):
        """Displays the results of the career simulation"""
        # Wyczyść istniejące wyniki
        for item in self.sim_tree.get_children():
            self.sim_tree.delete(item)
        
        for widget in self.sim_chart_frame.winfo_children():
            widget.destroy()
        
        # Wypełnij tabelę szczegółów
        for event in results['events']:
            salary_eur = round(event['salary'] / 4.5, 2)  # Convert PLN to EUR
            self.sim_tree.insert('', 'end', values=(
                event['time'],
                event['role'],
                f"{salary_eur:.2f} EUR",
                ", ".join(event['skills'][:3]) + ("..." if len(event['skills']) > 3 else ""),
                event['event']
            ))
        
        # Create larger chart frame
        chart_frame = ttk.Frame(self.sim_chart_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Adjust figure size and spacing
        fig, ax = plt.subplots(figsize=(12, 8))  # Increased figure size
        
        # Prepare data - convert salary to EUR
        times = [event['time'] for event in results['events']]
        salaries = [event['salary'] / 4.5 for event in results['events']]  # Convert PLN to EUR
        roles = [event['role'] for event in results['events']]
        
        # Main plot
        ax.plot(times, salaries, marker='o', linestyle='-', color=self.primary_color, linewidth=2, markersize=8)
        
        # Add role labels with more spacing
        for i, (x, y, role) in enumerate(zip(times, salaries, roles)):
            ax.annotate(
                role,
                (x, y),
                xytext=(0, 20),  # Increased vertical offset
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=8,
                rotation=45  # Rotate labels to prevent overlap
            )
        
        ax.set_title('Career Development Simulation')
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Salary (EUR)')  # Changed to EUR
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Dodaj wykres do ramki
        canvas = FigureCanvasTkAgg(fig, master=self.sim_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Podsumowanie
        messagebox.showinfo("Simulation Summary", 
                           f"Simulation completed successfully.\n"
                           f"Simulation time: {results['events'][-1]['time']} years\n"
                           f"Final role: {results['events'][-1]['role']}\n"
                           f"Salary growth: {results['salary_growth']}%")

    def create_career_simulation_chart(self, results):
        """Creates a career simulation chart"""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Przygotuj dane do wykresu
        times = [event['time'] for event in results['events']]
        salaries = [event['salary'] for event in results['events']]
        roles = [event['role'] for event in results['events']]
        
        # Główny wykres
        ax.plot(times, salaries, marker='o', linestyle='-', color=self.primary_color, linewidth=2, markersize=8)
        
        # Dodaj etykiety punktów
        for i, (time, salary, role) in enumerate(zip(times, salaries, roles)):
            if i == 0 or i == len(times) - 1 or results['events'][i]['event'].startswith('Zmiana pracy'):
                ax.annotate(
                    role, 
                    (time, salary),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    fontsize=9
                )
        
        # Dodaj linie poziome dla lepszej czytelności
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ustaw tytuł i etykiety
        ax.set_title('Career Development Simulation')
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Salary (PLN)')
        
        # Dodatkowe informacje
        stats_text = (
            f"Initial role: {results['initial_role']}\n"
            f"Final role: {results['final_role']}\n"
            f"Salary growth: {results['salary_growth']}%\n"
            f"Skills acquired: {results['skills_acquired']}"
        )
        
        plt.figtext(0.02, 0.02, stats_text, wrap=True, fontsize=9)
        plt.tight_layout()
        
        # Dodaj do ramki
        canvas = FigureCanvasTkAgg(fig, master=self.sim_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def simulate_career_progress(self, target_role, time_frame, learning_intensity, job_change_strategy):
        """Simulates career progress based on given parameters"""
        import random
        
        # Określenie strategii zmiany pracy w miesiącach
        if "częsta" in job_change_strategy.lower():
            job_change_interval = random.randint(12, 24)  # co 1-2 lata
        elif "umiarkowana" in job_change_strategy.lower():
            job_change_interval = random.randint(24, 36)  # co 2-3 lata
        else:  # długoterminowa
            job_change_interval = random.randint(36, 60)  # co 3-5 lat
        
        # Pobierz dane użytkownika, jeśli są dostępne
        current_role = "Junior Developer"  # domyślnie
        current_salary = 6000  # domyślnie
        current_skills = ["Programming", "Problem Solving"]  # domyślnie
        
        if hasattr(self, 'user_profile') and self.user_profile:
            current_role = self.user_profile.get('current_role', current_role)
            current_salary = self.user_profile.get('salary_expectation', current_salary)
            current_skills = self.user_profile.get('skills', current_skills)
        
        # Dostosuj współczynnik nauki na podstawie intensywności
        learning_factor = learning_intensity / 10.0  # 0.1 - 1.0
        
        # Rezultaty symulacji
        events = []
        current_time = 0.0  # w latach
        
        # Dodaj początkowe wydarzenie
        events.append({
            'time': current_time,
            'role': current_role,
            'salary': current_salary,
            'skills': current_skills.copy(),
            'event': "Start of simulation"
        })
        
        # Symuluj w czasie
        while current_time < time_frame:
            # Czas do następnego wydarzenia (w latach)
            next_event_time = random.uniform(0.25, 0.5)  # co 3-6 miesięcy
            current_time += next_event_time
            current_time = round(current_time, 2)  # zaokrąglenie do 2 miejsc po przecinku
            
            if current_time > time_frame:
                current_time = time_frame
            
            # Czy to czas na zmianę pracy?
            months_passed = int(current_time * 12)
            job_change = (months_passed % job_change_interval) < 3  # Jeśli jesteśmy blisko interwału zmiany pracy
            
            # Nauka nowych umiejętności
            if random.random() < learning_factor:
                new_skill = self.generate_random_skill(current_skills)
                current_skills.append(new_skill)
                
                events.append({
                    'time': current_time,
                    'role': current_role,
                    'salary': current_salary,
                    'skills': current_skills.copy(),
                    'event': f"Acquired skill: {new_skill}"
                })
            
            # Zmiana pracy
            elif job_change and current_time > 1.0:  # Nie zmieniaj pracy w pierwszym roku
                # Nowa rola i płaca
                new_role = self.generate_next_role(current_role, target_role, current_time / time_frame)
                salary_increase = random.uniform(0.10, 0.25)  # 10-25% podwyżki
                new_salary = int(current_salary * (1 + salary_increase))
                
                # Aktualizuj stan
                current_role = new_role
                current_salary = new_salary
                
                events.append({
                    'time': current_time,
                    'role': current_role,
                    'salary': current_salary,
                    'skills': current_skills.copy(),
                    'event': "Job change"
                })
            
            # Podwyżka w obecnej pracy
            elif random.random() < 0.3 and (current_time - events[-1]['time']) > 0.8:  # 30% szans na podwyżkę po 10 miesiącach
                salary_increase = random.uniform(0.03, 0.08)  # 3-8% podwyżki
                current_salary = int(current_salary * (1 + salary_increase))
                
                events.append({
                    'time': current_time,
                    'role': current_role,
                    'salary': current_salary,
                    'skills': current_skills.copy(),
                    'event': "Salary increase"
                })
            
            # Awans
            elif random.random() < 0.2 and (current_time - events[-1]['time']) > 1.5:  # 20% szans na awans po 1.5 roku
                if "Senior" not in current_role and "Lead" not in current_role:
                    if "Junior" in current_role:
                        current_role = current_role.replace("Junior", "Mid")
                    elif "Mid" in current_role:
                        current_role = current_role.replace("Mid", "Senior")
                    else:
                        current_role = "Senior " + current_role
                    
                    salary_increase = random.uniform(0.15, 0.20)  # 15-20% podwyżki
                    current_salary = int(current_salary * (1 + salary_increase))
                    
                    events.append({
                        'time': current_time,
                        'role': current_role,
                        'salary': current_salary,
                        'skills': current_skills.copy(),
                        'event': "Promotion"
                    })
            
            # Jeśli osiągnięto cel przed końcem symulacji
            if current_role == target_role and current_time < time_frame:
                events.append({
                    'time': current_time,
                    'role': current_role,
                    'salary': current_salary,
                    'skills': current_skills.copy(),
                    'event': "Achieved target role"
                })
                break
        
        # Dodaj końcowe wydarzenie, jeśli potrzeba
        if events[-1]['time'] < time_frame:
            events.append({
                'time': time_frame,
                'role': current_role,
                'salary': current_salary,
                'skills': current_skills.copy(),
                'event': "End of simulation"
            })
        
        # Oblicz wzrost wynagrodzenia
        initial_salary = events[0]['salary']
        final_salary = events[-1]['salary']
        salary_growth = round(((final_salary / initial_salary) - 1) * 100)
        
        return {
            'events': events,
            'salary_growth': salary_growth
        }

    def generate_random_skill(self, current_skills):
        """Generates a random skill not yet on the list"""
        # Comprehensive list of programming skills
        all_skills = {
            "Programming Languages": [
                "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP", "Swift", 
                "Kotlin", "Go", "Rust", "TypeScript", "Scala", "R", "MATLAB", "Perl",
                "Haskell", "Lua", "Dart", "Groovy", "Assembly", "COBOL", "Fortran",
                "Visual Basic", "ObjectiveC", "Delphi"
            ],
            "Web Technologies": [
                "HTML5", "CSS3", "SASS/SCSS", "JavaScript", "TypeScript", "WebGL",
                "WebAssembly", "PWA", "Web Components", "Web Sockets", "Web Workers",
                "Service Workers"
            ],
            "Frontend Frameworks": [
                "React", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", 
                "Gatsby", "jQuery", "Bootstrap", "Tailwind CSS", "Material-UI",
                "Chakra UI", "Redux", "MobX", "Ember.js"
            ],
            "Backend Frameworks": [
                "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
                "Laravel", "Ruby on Rails", "ASP.NET Core", "Phoenix", "NestJS",
                "Strapi", "Symfony", "CodeIgniter"
            ],
            "Databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
                "Microsoft SQL Server", "Cassandra", "DynamoDB", "Neo4j", "CouchDB",
                "Elasticsearch", "MariaDB", "Firebase"
            ],
            "Cloud & DevOps": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
                "GitLab CI/CD", "Travis CI", "CircleCI", "Terraform", "Ansible",
                "Puppet", "Chef", "Vagrant", "ECS", "EKS", "OpenShift"
            ],
            "AI & Machine Learning": [
                "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "OpenCV",
                "NLTK", "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
                "XGBoost", "LightGBM", "Hugging Face", "Fast.ai", "MLflow"
            ],
            "Mobile Development": [
                "React Native", "Flutter", "Xamarin", "Ionic", "Android SDK",
                "iOS SDK", "SwiftUI", "Kotlin Multiplatform", "Capacitor",
                "PhoneGap", "Unity Mobile"
            ],
            "Tools & Version Control": [
                "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Mercurial",
                "JIRA", "Confluence", "Trello", "Notion", "VS Code", "IntelliJ IDEA",
                "Eclipse", "PyCharm", "WebStorm"
            ],
            "Testing & QA": [
                "Jest", "Mocha", "Cypress", "Selenium", "JUnit", "PyTest",
                "TestNG", "Karma", "Jasmine", "Robot Framework", "Postman",
                "SoapUI", "LoadRunner", "JMeter"
            ],
            "Architecture & Patterns": [
                "Microservices", "REST API", "GraphQL", "SOAP", "MVC", "MVVM",
                "Clean Architecture", "Domain-Driven Design", "Event-Driven Architecture",
                "Serverless", "SOA", "Design Patterns"
            ],
            "Methodologies & Practices": [
                "Agile", "Scrum", "Kanban", "XP", "TDD", "BDD", "DevOps",
                "CI/CD", "Code Review", "Pair Programming", "Clean Code",
                "SOLID Principles"
            ]
        }
        
        # Flatten the skills dictionary into a single list
        all_skills_list = [skill for category in all_skills.values() for skill in category]
        
        # Remove skills user already has
        available_skills = [skill for skill in all_skills_list if skill not in current_skills]
        
        # If all skills are taken, return advanced message
        if not available_skills:
            return "Advanced professional skills"
        
        return random.choice(available_skills)

    def generate_next_role(self, current_role, target_role, progress_factor):
        """Generates the next role on the career path"""
        # Ścieżki kariery dla różnych specjalizacji
        career_paths = {
            "Developer": ["Junior Developer", "Mid Developer", "Senior Developer", "Lead Developer", "Software Architect"],
            "Frontend": ["Junior Frontend Dev", "Frontend Developer", "Senior Frontend Dev", "Frontend Lead", "UI/UX Architect"],
            "Backend": ["Junior Backend Dev", "Backend Developer", "Senior Backend Dev", "Backend Lead", "System Architect"],
            "Data": ["Data Analyst", "Data Engineer", "Senior Data Engineer", "Data Scientist", "Head of Data"],
            "DevOps": ["DevOps Engineer", "Senior DevOps", "DevOps Lead", "Cloud Architect", "Head of Infrastructure"]
        }
        
        # Określ ścieżkę kariery na podstawie obecnej roli
        path_key = None
        for key in career_paths:
            if key.lower() in current_role.lower() or key.lower() in target_role.lower():
                path_key = key
                break
        
        if not path_key:
            path_key = "Developer"  # domyślna ścieżka
        
        path = career_paths[path_key]
        
        # Znajdź obecną pozycję na ścieżce
        current_index = -1
        for i, role in enumerate(path):
            if role.lower() in current_role.lower():
                current_index = i
                break
        
        if current_index == -1:
            current_index = 0  # jeśli nie znaleziono, zacznij od początku
        
        # Znajdź docelową pozycję
        target_index = len(path) - 1  # domyślnie koniec ścieżki
        for i, role in enumerate(path):
            if role.lower() in target_role.lower():
                target_index = i
                break
        
        # Oblicz następny indeks na podstawie postępu
        next_index = min(current_index + 1, target_index)
        
        # Jeśli jesteśmy blisko końca symulacji, daj szansę na osiągnięcie celu
        if progress_factor > 0.8 and random.random() > 0.5:
            next_index = target_index
        
        return path[next_index]

    def on_closing(self):
        """Handle window closing event"""
        try:
            # Save settings
            self.save_settings()
            
            # Save profile if auto-save is enabled
            if hasattr(self, 'autosave_var') and self.autosave_var.get():
                try:
                    output_dir = self.output_dir_var.get()
                    os.makedirs(output_dir, exist_ok=True)
                    profile_path = os.path.join(output_dir, 'last_profile.json')
                    
                    if hasattr(self, 'user_profile') and self.user_profile:
                        with open(profile_path, 'w', encoding='utf-8') as f:
                            json.dump(self.user_profile, f, indent=4)
                except Exception as e:
                    logger.error(f"Error saving profile: {e}")
            
            # Destroy the window and quit the application
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during closing: {e}")
            # Force quit if there's an error
            self.root.quit()
            self.root.destroy()

    def browse_output_dir(self):
        """Opens dialog to select output directory"""
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        if dir_path:
            self.output_dir_var.set(dir_path)
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create directory: {e}")

    def load_saved_settings(self):
        """Loads previously saved application settings"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # Apply loaded settings
                    self.output_dir_var.set(settings.get('output_dir', "output/"))
                    self.autosave_var.set(settings.get('autosave', True))
                    self.export_format_var.set(settings.get('export_format', "JSON"))
                    self.theme_var.set(settings.get('theme', "Light"))
                    
                    # Apply theme immediately
                    self.change_theme(show_message=False)
                    
                    logger.info("Settings loaded successfully")
            else:
                logger.info("No saved settings found, using defaults")
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            messagebox.showwarning("Settings Load Error", 
                                 "Could not load saved settings. Using defaults.")

    def initialize_language(self):
        """Initializes translation dictionaries"""
        self.translations = {
            'English': {
                'main_title': 'AI Career Navigator',
                'dashboard': 'Dashboard',
                'user_profile': 'User Profile',
                'cv_analysis': 'CV Analysis',
                'career_path': 'Career Path',
                'career_simulation': 'Career Simulation',
                'market_trends': 'Market Trends',
                'settings': 'Settings',
                'file': 'File',
                'load_cv': 'Load CV',
                'load_profile': 'Load Profile',
                'save_profile': 'Save Profile',
                'exit': 'Exit',
                'analysis': 'Analysis',
                'help': 'Help',
                'about': 'About',
                'instructions': 'Instructions',
                'personal_data': 'Personal Data',
                'first_name': 'First Name:',
                'last_name': 'Last Name:',
                'email': 'Email:',
                'phone': 'Phone:',
                'current_role': 'Current Role:',
                'experience_years': 'Experience (years):',
                'industry': 'Industry:',
                'education': 'Education:',
                'save': 'Save',
                'clear': 'Clear',
                'creator': 'Creator: Adrian Lesniak',
            },
            'Norwegian': {
                'main_title': 'AI Karriere Navigator',
                'dashboard': 'Oversikt',
                'user_profile': 'Brukerprofil',
                'cv_analysis': 'CV-analyse',
                'career_path': 'Karrierevei',
                'career_simulation': 'Karrieresimulering',
                'market_trends': 'Markedstrender',
                'settings': 'Innstillinger',
                'file': 'Fil',
                'load_cv': 'Last inn CV',
                'load_profile': 'Last inn profil',
                'save_profile': 'Lagre profil',
                'exit': 'Avslutt',
                'analysis': 'Analyse',
                'help': 'Hjelp',
                'about': 'Om',
                'instructions': 'Instruksjoner',
                'personal_data': 'Personopplysninger',
                'first_name': 'Fornavn:',
                'last_name': 'Etternavn:',
                'email': 'E-post:',
                'phone': 'Telefon:',
                'current_role': 'Nåværende rolle:',
                'experience_years': 'Erfaring (år):',
                'industry': 'Bransje:',
                'education': 'Utdanning:',
                'save': 'Lagre',
                'clear': 'Tøm',
                'creator': 'Skaper: Adrian Lesniak',
            }
        }

    def change_theme(self, event=None, show_message=True):
        """Changes the application theme"""
        theme = self.theme_var.get()
        try:
            if theme == "Dark":
                self.primary_color = "#2980b9"  # Darker blue
                self.secondary_color = "#27ae60"  # Darker green
                self.bg_color = "#2c3e50"  # Dark blue-gray
                self.text_color = "#ecf0f1"  # Light gray
                self.accent_color = "#c0392b"  # Darker red
            elif theme == "Blue":
                self.primary_color = "#4a90e2"  # Sky blue
                self.secondary_color = "#5bd1d7"  # Turquoise
                self.bg_color = "#f0f8ff"  # Light blue
                self.text_color = "#2c3e50"  # Dark blue
                self.accent_color = "#ff6b6b"  # Coral
            elif theme == "Green":
                self.primary_color = "#2ecc71"  # Green
                self.secondary_color = "#f1c40f"  # Yellow
                self.bg_color = "#f0fff0"  # Light green
                self.text_color = "#27ae60"  # Dark green
                self.accent_color = "#e74c3c"  # Red
            else:  # Light theme
                self.primary_color = "#3498db"  # Blue
                self.secondary_color = "#2ecc71"  # Green
                self.bg_color = "#f5f5f5"  # Light gray
                self.text_color = "#2c3e50"  # Dark blue
                self.accent_color = "#e74c3c"  # Red

            # Update styles
            self.style.configure('TFrame', background=self.bg_color)
            self.style.configure('TButton', font=('Helvetica', 10), background=self.primary_color)
            self.style.configure('TLabel', font=('Helvetica', 10), background=self.bg_color, foreground=self.text_color)
            self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), background=self.bg_color, foreground=self.primary_color)
            self.style.configure('Subheader.TLabel', font=('Helvetica', 12, 'bold'), background=self.bg_color, foreground=self.text_color)
            
            if show_message:
                messagebox.showinfo("Theme Changed", f"Applied {theme} theme successfully!")
                
        except Exception as e:
            logger.error(f"Error changing theme: {e}")
            if show_message:
                messagebox.showerror("Error", "Failed to change theme")

    def show_about(self):
        """Shows the about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About AI Career Navigator")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'+{x}+{y}')
        
        # Content frame
        content_frame = ttk.Frame(about_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(content_frame, text="AI Career Navigator", style='Header.TLabel')
        title.pack(pady=(0, 10))
        
        # Version
        version = ttk.Label(content_frame, text="Version 1.0.0", style='Subheader.TLabel')
        version.pack(pady=(0, 20))
        
        # Description
        description = """
        AI Career Navigator is an intelligent career planning 
        and development tool that helps users make informed 
        decisions about their professional future.
        
        Created by Adrian Lesniak
        Copyright © 2024
        """
        desc_label = ttk.Label(content_frame, text=description, wraplength=350, justify='center')
        desc_label.pack(pady=10)
        
        # Close button
        ttk.Button(content_frame, text="Close", command=about_window.destroy).pack(pady=20)

    def show_help(self):
        """Shows the help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("AI Career Navigator - Help")
        help_window.geometry("600x400")
        help_window.transient(self.root)
        
        help_text = """
        GETTING STARTED:
        
        1. User Profile:
           • Create your profile or load your CV
           • Fill in your personal and professional details
           • Add your skills and experience
        
        2. CV Analysis:
           • Upload your CV for automatic analysis
           • Review detected skills and competencies
           • Get personalized recommendations
        
        3. Career Planning:
           • Set your career goals
           • Generate career path options
           • View market trends and opportunities
        
        4. Career Simulation:
           • Run career simulations
           • Test different scenarios
           • Analyze potential outcomes
        
        5. Market Analysis:
           • Check current job market trends
           • View salary ranges
           • Identify in-demand skills
        
        For more detailed information, visit our documentation.
        """
        
        help_scroll = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_scroll.insert(tk.END, help_text)
        help_scroll.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)

    def show_profile_instructions(self):
        """Displays instructions for the user profile section"""
        instructions = """
INSTRUCTIONS FOR USER PROFILE:

1. PERSONAL INFORMATION:
   • Fill in your basic personal details
   • Provide contact information
   • Enter your current location

2. PROFESSIONAL DETAILS:
   • Specify your current role
   • Enter years of experience
   • Select your industry
   • Choose your education level

3. SKILLS MANAGEMENT:
   • Add your professional skills
   • Remove outdated skills
   • Skills can be comma-separated
   • Add new skills as you learn them

4. SAVING & LOADING:
   • Save your profile regularly
   • Load existing profile from file
   • Profile data is used for analysis

5. TIPS:
   • Keep your profile updated
   • Be specific with skill names
   • Include certification details
   • Add relevant experience
        """
        self.show_instructions_window("User Profile Instructions", instructions)

    def show_cv_instructions(self):
        """Displays instructions for CV analysis"""
        instructions = """
INSTRUCTIONS FOR CV ANALYSIS:

1. PREPARING YOUR CV:
   • Use clear formatting
   • List skills explicitly
   • Include experience details
   • Mention relevant projects

2. UPLOADING:
   • Choose a text-based CV file
   • Or paste CV content directly
   • Supported formats: TXT, PDF (text)

3. ANALYSIS PROCESS:
   • System will extract skills
   • Experience levels detected
   • Projects analyzed
   • Technologies identified

4. REVIEWING RESULTS:
   • Check detected skills
   • Verify experience levels
   • Review recommendations
   • Export analysis if needed

5. USING THE RESULTS:
   • Update your profile
   • Focus on gaps
   • Plan skill development
   • Track progress
        """
        self.show_instructions_window("CV Analysis Instructions", instructions)

    def show_simulation_instructions(self):
        """Displays instructions for career simulation"""
        instructions = """
INSTRUCTIONS FOR CAREER SIMULATION:

1. SETTING PARAMETERS:
   • Choose target role
   • Set learning intensity
   • Select job change strategy
   • Define time horizon

2. RUNNING SIMULATION:
   • Click 'Run Simulation'
   • Wait for processing
   • Review results carefully

3. INTERPRETING RESULTS:
   • Salary progression
   • Skill acquisition
   • Career milestones
   • Potential challenges

4. ADJUSTING SIMULATION:
   • Try different scenarios
   • Modify parameters
   • Compare outcomes
   • Save interesting results

5. USING INSIGHTS:
   • Plan career moves
   • Set learning goals
   • Adjust timeline
   • Track progress
        """
        self.show_instructions_window("Career Simulation Instructions", instructions)

    def add_skill(self):
        """Adds a new skill to the skills list"""
        new_skill = self.new_skill_var.get().strip()
        
        if not new_skill:
            messagebox.showwarning("Warning", "Please enter a skill name.")
            return
            
        # Get current skills
        current_skills = self.skills_text.get('1.0', tk.END).strip()
        skills_list = [s.strip() for s in current_skills.split(',') if s.strip()]
        
        # Check if skill already exists
        if new_skill in skills_list:
            messagebox.showwarning("Warning", "This skill is already in the list.")
            return
        
        # Add new skill
        skills_list.append(new_skill)
        
        # Update skills text
        self.skills_text.delete('1.0', tk.END)
        self.skills_text.insert(tk.END, ', '.join(skills_list))
        
        # Clear entry
        self.new_skill_var.set('')

    def remove_skills(self):
        """Removes selected skills from the skills list"""
        try:
            # Get selection
            selection_start = self.skills_text.tag_ranges("sel")
            if not selection_start:
                messagebox.showwarning("Warning", "Please select the skills to remove.")
                return
            
            # Get selected text
            selected_text = self.skills_text.get(selection_start[0], selection_start[1])
            selected_skills = [s.strip() for s in selected_text.split(',')]
            
            # Get all skills
            current_skills = self.skills_text.get('1.0', tk.END).strip()
            skills_list = [s.strip() for s in current_skills.split(',') if s.strip()]
            
            # Remove selected skills
            updated_skills = [s for s in skills_list if s not in selected_skills]
            
            # Update skills text
            self.skills_text.delete('1.0', tk.END)
            self.skills_text.insert(tk.END, ', '.join(updated_skills))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error removing skills: {str(e)}")

    def clear_profile_form(self):
        """Clears all fields in the profile form"""
        self.firstname_var.set('')
        self.lastname_var.set('')
        self.email_var.set('')
        self.phone_var.set('')
        self.location_var.set('')
        self.current_role_var.set('')
        self.experience_var.set('0')
        self.industry_var.set('')
        self.education_var.set('')
        self.new_skill_var.set('')
        self.skills_text.delete('1.0', tk.END)
        
        if hasattr(self, 'salary_var'):
            self.salary_var.set('0')

    def clear_cv(self):
        """Clears the CV text area and analysis results"""
        # Clear CV text area
        self.cv_text.delete('1.0', tk.END)
        
        # Clear results text areas
        self.cv_results_text.delete('1.0', tk.END)
        self.summary_text.delete('1.0', tk.END)
        self.recommendations_text.delete('1.0', tk.END)
        
        # Clear skills tree
        for item in self.skills_tree.get_children():
            self.skills_tree.delete(item)
        
        # Reset any analysis results
        if hasattr(self, 'cv_analysis_results'):
            self.cv_analysis_results = {
                'skills': [],
                'skill_levels': {}
            }

    def save_settings(self):
        """Saves application settings to file"""
        try:
            settings = {
                'output_dir': self.output_dir_var.get(),
                'autosave': self.autosave_var.get(),
                'export_format': self.export_format_var.get(),
                'theme': self.theme_var.get()
            }
            
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
                
            messagebox.showinfo("Success", "Settings saved successfully!")
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")

    def reset_settings(self):
        """Resets settings to default values"""
        try:
            # Set default values
            self.output_dir_var.set("output/")
            self.autosave_var.set(True)
            self.export_format_var.set("JSON")
            self.theme_var.set("Light")
            
            # Apply theme
            self.change_theme(show_message=False)
            
            # Save defaults
            self.save_settings()
            
            messagebox.showinfo("Success", "Settings have been reset to defaults.")
            logger.info("Settings reset to defaults")
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            messagebox.showerror("Error", f"Could not reset settings: {str(e)}")

    def apply_translations(self):
        """Applies translations to all UI elements based on current language"""
        try:
            if self.current_language not in self.translations:
                logger.warning(f"Language {self.current_language} not found in translations")
                return

            current_trans = self.translations[self.current_language]

            # Update window title
            self.root.title(current_trans.get('main_title', 'AI Career Navigator'))

            # Update navigation buttons
            for child in self.nav_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    button_text = child.cget('text').lower().replace(' ', '_')
                    translated_text = current_trans.get(button_text, child.cget('text'))
                    child.configure(text=translated_text)

            # Update menu items if they exist
            if hasattr(self, 'menubar'):
                for menu in self.menubar.winfo_children():
                    if isinstance(menu, tk.Menu):
                        menu_label = menu.cget('label').lower()
                        translated_label = current_trans.get(menu_label, menu.cget('label'))
                        menu.configure(label=translated_label)

            # Update frame labels
            for frame_name, frame in self.frames.items():
                for child in frame.winfo_children():
                    if isinstance(child, ttk.Label):
                        if 'Header.TLabel' in child.cget('style'):
                            label_text = child.cget('text').lower().replace(' ', '_')
                            translated_text = current_trans.get(label_text, child.cget('text'))
                            child.configure(text=translated_text)

            logger.info(f"Applied translations for language: {self.current_language}")

        except Exception as e:
            logger.error(f"Error applying translations: {str(e)}")
            messagebox.showerror("Error", "Failed to apply translations")

    def _get_next_career_step(self, current_role, target_role, progress):
        """Determines the next career step based on current role and target role"""
        # Career progression paths
        career_paths = {
            'developer': ['Junior Developer', 'Mid Developer', 'Senior Developer', 'Lead Developer', 'Solution Architect'],
            'frontend': ['Junior Frontend', 'Frontend Developer', 'Senior Frontend', 'Frontend Lead', 'UI/UX Architect'],
            'backend': ['Junior Backend', 'Backend Developer', 'Senior Backend', 'Backend Lead', 'System Architect'],
            'data': ['Junior Data Analyst', 'Data Analyst', 'Data Engineer', 'Senior Data Engineer', 'Data Architect'],
            'devops': ['Junior DevOps', 'DevOps Engineer', 'Senior DevOps', 'DevOps Lead', 'Cloud Architect'],
            'manager': ['Team Lead', 'Project Manager', 'Senior PM', 'Program Manager', 'Director'],
        }

        # Determine the relevant career path
        path_key = None
        for key in career_paths:
            if key in current_role.lower() or key in target_role.lower():
                path_key = key
                break

        if not path_key:
            # Use default developer path if no specific path is found
            path_key = 'developer'

        career_path = career_paths[path_key]

        # Find current position in the path
        current_index = -1
        for i, role in enumerate(career_path):
            if role.lower() in current_role.lower():
                current_index = i
                break

        if current_index == -1:
            current_index = 0  # Start from beginning if current role not found

        # Find target position
        target_index = len(career_path) - 1  # Default to end of path
        for i, role in enumerate(career_path):
            if role.lower() in target_role.lower():
                target_index = i
                break

        # Calculate next step based on progress
        if progress > 0.8 and random.random() > 0.7:  # Chance for bigger jump near end
            next_index = min(current_index + 2, target_index)
        else:
            next_index = min(current_index + 1, target_index)

        return career_path[next_index]

    def load_icons(self):
        """Load icons from local files or URLs"""
        # Create simple text-based icons as fallback
        def create_text_icon(text, size=(24, 24)):
            img = Image.new('RGBA', size, (0, 0, 0, 0))
            return ImageTk.PhotoImage(img)
        
        icon_urls = {
            'dashboard': 'https://cdn-icons-png.flaticon.com/512/1828/1828859.png',
            'user': 'https://cdn-icons-png.flaticon.com/512/747/747376.png',  # minimalistyczna czarna sylwetka
            'cv': 'https://cdn-icons-png.flaticon.com/512/1828/1828925.png',  # ikona książki mono
            'path': 'https://cdn-icons-png.flaticon.com/512/25/25694.png',
            'simulation': 'https://cdn-icons-png.flaticon.com/512/3524/3524659.png',
            'trends': 'https://cdn-icons-png.flaticon.com/512/1828/1828919.png',
            'settings': 'https://cdn-icons-png.flaticon.com/512/2099/2099058.png',
            'logo': 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',
        }
        
        for key, url in icon_urls.items():
            try:
                with urllib.request.urlopen(url, timeout=5) as u:
                    raw_data = u.read()
                image = Image.open(BytesIO(raw_data)).resize((24, 24), Image.Resampling.LANCZOS)
                self.icons[key] = ImageTk.PhotoImage(image)
                print(f"Loaded icon: {key}")
            except Exception as e:
                print(f"Failed to load icon {key}: {e}")
                # Create a simple colored square as fallback
                img = Image.new('RGBA', (24, 24), self.primary_color)
                self.icons[key] = ImageTk.PhotoImage(img)

    def export_cv_analysis_to_pdf(self):
        """Eksportuje wyniki analizy CV do pliku PDF"""
        from tkinter import filedialog, messagebox
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "CV Analysis Results", ln=True, align='C')
        pdf.ln(10)
        # Pobierz tekst z okna wyników
        text = self.cv_results_text.get('1.0', tk.END)
        for line in text.split('\n'):
            pdf.multi_cell(0, 8, line)
        # Zapisz plik
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                pdf.output(file_path)
                messagebox.showinfo("Success", f"PDF exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CareerNavigatorGUI(root)
    root.mainloop()