# 🏨 Tourism India Analytics Platform

A comprehensive data analytics web application for tourism analysis across India, providing insights into destinations, hotels, pricing patterns, seasonal trends, and budget planning.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Data Format](#data-format)
- [Troubleshooting](#troubleshooting)
- [Screenshots](#screenshots)
- [License](#license)

## 🎯 Overview

This project analyzes tourism data across India, providing interactive dashboards, destination search, budget planning, and comprehensive reports. It helps travelers make informed decisions about their trips based on real data.

## ✨ Features

### 🔍 Smart Search
- Search by city or state name
- Auto-suggest popular destinations
- View detailed destination information
- Quick access to budget planning

### 📊 Interactive Dashboard
- Rating distribution charts
- Hotel price analysis
- Seasonal patterns visualization
- Geographic distribution maps
- Budget category analysis
- Value matrix (price vs rating)

### 💰 Budget Calculator
- Trip cost estimation
- Detailed cost breakdown (hotel, activities, food, transport)
- Savings tips and recommendations
- Per-person and per-day cost calculations

### 📈 Comprehensive Reports
- Executive summary
- Statistical analysis
- Destination directory
- Key findings and insights
- Travel recommendations

### 🎨 Modern UI/UX
- Responsive design for all devices
- Interactive charts with Plotly
- Glassmorphism design effects
- Smooth animations
- Print-friendly reports

## 🛠 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Backend logic |
| Flask | 2.3.3 | Web framework |
| Pandas | 2.0.3 | Data processing |
| NumPy | 1.24.3 | Numerical operations |
| Plotly | 5.15.0 | Interactive visualizations |
| Bootstrap | 5.1.3 | Frontend styling |
| Font Awesome | 6.0 | Icons |

## 📁 Project Structure

├── app.py # Main Flask application
├── run.py # Application launcher
├── requirements.txt # Python dependencies
├── README.md # Project documentation
│
├── data/ # Data files directory
│ ├── hotel.csv # Hotel dataset
│ └── places.csv # Places dataset
│
├── templates/ # HTML templates
│ ├── base.html # Base template
│ ├── index.html # Home page
│ ├── search.html # Search page
│ ├── dashboard.html # Analytics dashboard
│ ├── calculator.html # Budget calculator
│ └── report.html # Report page
│
├── static/ # Static files
│ └── css/
│ └── style.css # Custom styles
│
├── reports/ # Generated reports
├── logs/ # Application logs
└── data/processed/ # Processed data



## 💻 Requirements

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 500MB free space
- **Python**: Version 3.8 or higher

### Python Packages
Flask==2.3.3
pandas==2.0.3
numpy==1.24.3
plotly==5.15.0
