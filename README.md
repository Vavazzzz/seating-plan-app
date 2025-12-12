# Seating Plan Application

## Overview
The Seating Plan Application is a GUI-based tool designed to help users create and manage seating arrangements for various events. Users can create seating plans, define sections, add seats, and export or import seating plans in JSON format.

## Features
- Create and manage seating plans
- Add, delete, and rename sections
- Add and delete individual seats or ranges of seats
- Clone sections
- Change row and seat numbers
- Export seating plans to JSON
- Import existing seating plans from JSON

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd seating-plan-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python -m src.ui.main_window
```

## Project Structure
```
seating-plan-app
├── src
│   ├── ui
│   │   ├── __init__.py     # UI module initialization
│   │   ├── main_window.py   # Main window layout and event handling
│   │   └── section_view.py  # Detailed view of a section
│   ├── models
│   │   ├── __init__.py     # Models module initialization
│   │   ├── seating_plan.py  # SeatingPlan model
│   │   ├── section.py       # Section model
│   │   └── seat.py          # Seat model
│   └── utils
│       ├── __init__.py          # Utils module initialization
|       ├── alphanum_handler.py  # Handling of alphanumeric ranges
│       └── json_io.py           # Project import/export functions
├── examples
│   └── seating_plan_example.json  # Example seating plan
├── tests
│   ├── test_seating_plan.py  # Unit tests for SeatingPlan
│   └── test_section.py       # Unit tests for Section
├── requirements.txt           # Project dependencies
├── pyproject.toml            # Project configuration
├── .gitignore                 # Files to ignore in version control
└── README.md                  # Project documentation
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.