# Weather Application - Module 6 Lab

## Student Information
- **Name**: Francis Gabriel F. Nonato
- **Student ID**: 231002327
- **Course**: CCCS 106
- **Section**: 3A

## Project Overview
My weather app is a simple desktop application that lets users check the current weather and a five-day forecast for any city. It connects to the OpenWeatherMap API to get real-time data like temperature, humidity, wind speed, and weather conditions. Users can type in a city or select one from their search history, and the app displays the information in a clean interface with icons and text. It also allows switching between Celsius and Fahrenheit and has a light and dark theme for better visibility. The app saves the search history and user settings so that everything is ready the next time it is opened.

## Features Implemented
1. **Dark Mode Support**
2. **Search History**
3. **Temperature Unit Toggle**
4. **5-Day Weather Forecast**

### Base Features
- [✓] City search functionality
- [✓] Current weather display
- [✓] Temperature, humidity, wind speed
- [✓] Weather icons
- [✓] Error handling
- [✓] Modern UI with Material Design

### Enhanced Features
1. **Search History**
   - It saves the last ten cities I searched so I can quickly check them again.
   - I chose this feature to make the app more convenient for frequent users.
   - The challenge was updating the dropdown without losing the list, and I solved it by managing the history separately from the input field.

2. **Temperature Unit Toggle**
   - It lets users switch between Celsius and Fahrenheit for all weather data.
   - I chose this feature because people use different units depending on their location.
   - The challenge was converting both temperature and wind speed correctly, and I solved it by applying the proper formulas and updating all related controls.

3. **5-Day Weather Forecast**
   - It shows the forecast for the next five days with highs, lows, and weather icons.
   - I chose this feature to give users a better idea of upcoming weather conditions.
   - The challenge was organizing the data by day, and I solved it by grouping the forecast items using their dates.

## Screenshots
![Main Weather Display](<screenshots/main weather display.png>)
![5-Day Weather Forecast](<screenshots/5-day forecast.png>)
![Search History Dropdown](<screenshots/search history.png>)
![Temperature Unit Toggle](<screenshots/temperature unit toggle.png>)
![Dark Mode View](<screenshots/dark mode.png>)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/frnonato-lgtm/cccs106-projects.git
cd cccs106-projects/mod6_labs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OpenWeatherMap API key to .env
