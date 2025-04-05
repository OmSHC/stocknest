# Project Name

## Overview
Brief description of your project and its purpose.

## Features
- Three-panel layout with dynamic content management
- Left sidebar navigation with key sections (Dashboard, Watchlist, Portfolio, Market, Reports)
- Middle sidebar for secondary navigation
- Main content area for primary content display
- Responsive design for all screen sizes
- Dark mode support
- Real-time updates

## UI Components
The application features a three-panel layout design with interactive navigation flow:

### Navigation Flow
- Left Sidebar → Middle Sidebar → Main Content Area
- Each panel's content updates based on the previous panel's selection
- Interactive click behavior triggers content updates in subsequent panels

### 1. Left Sidebar
- Application logo at the top
- Static sidebar with fixed width
- Primary navigation menu with icons:
  - Dashboard: 
    - Icon: Diagonal arrow icon
    - Purpose: Access main dashboard
    - Selection: Slightly enlarges when active
  - Watchlist: 
    - Icon: Star icon
    - Purpose: Manage watchlists
    - Selection: Slightly enlarges when active
  - Portfolio: 
    - Icon: Briefcase icon
    - Purpose: View and manage portfolio
    - Selection: Slightly enlarges when active
  - Market: 
    - Icon: Chart/graph icon
    - Purpose: Access market data
    - Selection: Slightly enlarges when active
  - Reports: 
    - Icon: Document icon
    - Purpose: View reports
    - Selection: Slightly enlarges when active
  - Risk:
    - Icon: Shield icon
    - Purpose: Risk management
    - Selection: Slightly enlarges when active
- Bottom section:
  - User profile section
    - Icon: User avatar
    - Username: "test"
- Visual Features:
  - Dark theme design
  - Selected item appears slightly larger than others
  - Consistent icon-based navigation
  - Fixed position sidebar (non-collapsible)
  - Visual feedback on hover and selection

### 2. Middle Sidebar
- Dynamic content based on selected section from Left Sidebar
- Content updates instantly when left sidebar item is clicked
- For Watchlist section:
  - My Watchlists (Header)
    - Create New Watchlist button (Blue button)
      - Form includes:
        - Watchlist Name (required)
        - Description (optional)
        - Stock Search functionality
          - Search by name or symbol
          - Real-time search results
          - Add/remove stocks from selection
  - CREATED BY ME section
    - List of user-created watchlists with:
      - Star icon for favorites
      - Watchlist name
      - Creation date
      - Toggle button (blue)
    - Current watchlists:
      - test6 (Created Mar 30, 2025)
      - test5 (Created Mar 30, 2025)
      - test4 (Created Mar 30, 2025)
      - test2 (Created Mar 30, 2025)
      - Banking & Financial (Created Mar 29, 2025)
      - Tech Stocks (Created Mar 29, 2025)
      - Blue Chip Stocks (Created Mar 29, 2025)
  - SUBSCRIBED WATCHLISTS section
    - List of subscribed watchlists:
      - Market Leaders (by John Doe)
      - Growth Stocks (by Jane Smith)
    - Each watchlist includes:
      - User icon
      - Watchlist name
      - Creator name
      - Toggle button (blue)
  - Summary Statistics (Bottom panel):
    - Total Watchlists: 4
    - Subscribers: 12
    - Public Lists: 2
    - Private Lists: 2

### 3. Main Content Area
- Primary content display based on middle sidebar selection
- Content updates when middle sidebar item is clicked
- Dynamic content loading with loading indicators
- Interactive elements and data visualization
- Responsive layout adjustments
- Content examples:
  - When clicking a watchlist: Displays detailed watchlist with stocks and performance
  - When clicking dashboard items: Shows relevant dashboard widgets
  - When clicking portfolio items: Displays portfolio details and analysis
  - When clicking market items: Shows market data and charts
  - When clicking report items: Displays selected report data

### Interaction Examples
1. Watchlist Flow:
   - Click "Watchlist" in left sidebar → Loads watchlist management in middle sidebar
   - Click specific watchlist in middle sidebar → Loads detailed watchlist view in main content area

2. Portfolio Flow:
   - Click "Portfolio" in left sidebar → Loads portfolio categories in middle sidebar
   - Click specific portfolio in middle sidebar → Loads detailed portfolio view in main content area

3. Market Flow:
   - Click "Market" in left sidebar → Loads market categories in middle sidebar
   - Click specific market view in middle sidebar → Loads detailed market data in main content area

## Installation
```bash
# Installation commands
npm install
# or
yarn install
```

## Usage
Describe how to use your project, including any important commands or configurations.

## Project Structure
```
project/
├── src/                      # Source code directory
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Shared components
│   │   ├── layout/         # Layout components
│   │   └── forms/          # Form-related components
│   ├── pages/              # Page components
│   │   ├── home/          # Home page
│   │   ├── dashboard/     # Dashboard page
│   │   └── settings/      # Settings page
│   ├── services/          # API and service integrations
│   ├── utils/             # Utility functions and helpers
│   ├── hooks/             # Custom React hooks
│   ├── styles/            # Global styles and themes
│   └── types/             # TypeScript type definitions
├── public/                 # Static files
│   ├── images/            # Image assets
│   ├── fonts/             # Font files
│   └── icons/             # Icon assets
├── tests/                 # Test files
│   ├── components/        # Component tests
│   ├── pages/            # Page tests
│   └── utils/            # Utility tests
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── guides/           # User guides
│   └── examples/         # Code examples
├── scripts/              # Build and deployment scripts
├── config/               # Configuration files
├── .github/              # GitHub specific files
│   └── workflows/        # GitHub Actions workflows
├── .vscode/              # VS Code settings
├── .gitignore           # Git ignore rules
├── package.json         # Project dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── README.md            # Project documentation
└── LICENSE              # Project license
```

## Configuration
Explain any configuration options and environment variables.

## Development
Instructions for setting up the development environment.

## Contributing
Guidelines for contributing to the project.

## License
Specify the project's license.

## Contact
Your contact information or ways to reach out.

## Acknowledgments
Credits and acknowledgments for any third-party resources used.

---
*Last updated: [Current Date]*
include watchfolder
