# Resume Roast - React Frontend

A modern React TypeScript frontend for the Resume Roast AI-powered resume analysis system.

## Features

- 📄 Drag & drop resume upload (PDF, DOCX)
- 💼 Job input via LinkedIn URL or manual description
- 🤖 Real-time AI analysis with loading states
- 📊 Beautiful results visualization with score breakdown
- 🎯 Skills matching analysis
- ✅ Strengths and improvement areas
- 📱 Fully responsive design

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend server running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
# Copy .env file and update if needed
cp .env.example .env
```

3. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Environment Variables

- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## API Integration

The frontend connects to the FastAPI backend at `/resume/score` endpoint:

```typescript
POST /resume/score
Content-Type: multipart/form-data

FormData:
- resume: File (PDF/DOCX)
- job_url?: string (LinkedIn URL)
- job_description?: string (Manual job description)
```

## Component Structure

```
src/
├── components/
│   ├── FileUpload.tsx      # Resume file upload with drag & drop
│   ├── JobInput.tsx        # Job URL/description input
│   ├── LoadingSpinner.tsx  # Loading animation
│   └── ResultsDisplay.tsx  # Score and analysis results
├── App.tsx                 # Main application component
├── App.css                 # Global styles
└── index.tsx              # App entry point
```

## Styling

The app uses modern CSS with:
- CSS Grid and Flexbox layouts
- Gradient backgrounds
- Smooth animations and transitions
- Responsive design for mobile/tablet
- Color-coded score visualization

## Deployment

Build for production:
```bash
npm run build
```

The `build` folder contains the production-ready static files that can be served by any web server.
