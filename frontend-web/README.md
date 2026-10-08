# AI Financial Analyst - Web Application

A modern React-based web application for AI-powered financial analysis.

## Features

- 📊 **Dashboard**: Overview of financial metrics and portfolio performance
- 🏢 **Company Management**: Add, view, and manage company financial data
- 📤 **Data Upload**: Import financial statements (CSV, Excel)
- 📈 **KPI Analysis**: Key Performance Indicators with industry benchmarks
- ⚠️ **Risk Analysis**: Comprehensive risk assessment and scoring
- 🔮 **Forecasting**: AI-powered financial forecasting
- 🤖 **AI Insights**: GPT/Gemini-powered financial analysis
- 📊 **Benchmarking**: Compare performance against industry standards
- 💬 **Chat Analyst**: Interactive AI financial assistant
- 📑 **Reports**: Generate and view detailed analysis reports
- 👤 **Profile**: User settings and preferences

## Quick Start

### Prerequisites

- Node.js v18+ and npm
- Python 3.10+
- OpenAI API key or Google Gemini API key

### Installation

1. **Install frontend dependencies:**
```bash
cd frontend-web
npm install
```

2. **Configure environment variables:**
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_key_here
# OR
GEMINI_API_KEY=your_gemini_key_here
```

3. **Start the backend server:**
```bash
# From project root
py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Start the frontend dev server:**
```bash
cd frontend-web
npm run dev
```

5. **Open your browser:**
Navigate to `http://localhost:5173`

## Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Navigation
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Framer Motion** - Animations
- **React Hot Toast** - Notifications

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - Database ORM
- **OpenAI/Gemini** - LLM integration
- **Pandas** - Data processing
- **NumPy** - Numerical computing

## Project Structure

```
frontend-web/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Layout.jsx   # Main app layout with navigation
│   │   └── ui.jsx       # UI component library
│   ├── pages/           # Route pages
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Companies.jsx
│   │   ├── Upload.jsx
│   │   ├── KpiAnalysis.jsx
│   │   ├── RiskAnalysis.jsx
│   │   ├── Forecasting.jsx
│   │   ├── AiInsights.jsx
│   │   ├── Benchmarking.jsx
│   │   ├── ChatAnalyst.jsx
│   │   ├── Reports.jsx
│   │   └── Profile.jsx
│   ├── context/
│   │   └── AuthContext.jsx  # Authentication state management
│   ├── api.js           # API client configuration
│   ├── App.jsx          # Main app component with routing
│   └── main.jsx         # App entry point
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## API Endpoints

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /companies` - List companies
- `POST /companies` - Create company
- `POST /upload` - Upload financial data
- `GET /analysis/kpi/{company_id}` - KPI analysis
- `GET /analysis/risk/{company_id}` - Risk assessment
- `POST /analysis/forecast` - Generate forecast
- `POST /analysis/insights` - AI insights
- `POST /chat` - Chat with AI analyst
- `GET /reports` - List reports

## Development Notes

- The app uses JWT authentication with tokens stored in localStorage
- All API calls include the auth token in the Authorization header
- Protected routes redirect to login if not authenticated
- The backend auto-reloads on code changes
- Vite HMR provides instant frontend updates

## Deployment

### Build for Production

```bash
cd frontend-web
npm run build
```

The production build will be in the `dist/` folder.

### Environment Variables for Production

Update `.env` with production values:
```
APP_ENV=production
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key-here
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

## Troubleshooting

### Backend not accessible
- Ensure backend is running on port 8000
- Check CORS settings in `backend/config.py`

### Authentication errors
- Verify JWT secret key is consistent
- Check token expiration settings

### Missing dependencies
```bash
cd frontend-web
npm install
```

## License

MIT License - See LICENSE file for details
