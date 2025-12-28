# 🚀 Quick Start Guide - Kwizy

## Setup & Installation

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 14+ (for frontend)
- Git

### Backend Setup

```bash
# Navigate to project directory
cd quiz-generate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
# Edit .env file with your Supabase credentials
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key

# Run Flask server
python app.py
```

**Backend runs on**: http://localhost:5000 (API only)

### Frontend Setup

```bash
# Navigate to frontend directory
cd quiz-generate/frontend

# Install dependencies
npm install

# Start React development server
npm start
```

**Frontend runs on**: http://localhost:3000 (UI)

## Usage

### 1. Access the Application
Open your browser and go to: **http://localhost:3000**

### 2. Create Account
- Click "Sign Up"
- Enter your details:
  - First Name & Last Name
  - Email address
  - Strong password (8+ chars, uppercase, numbers)
  - Company (optional)
- Click "Create Account"

### 3. Login
- Click "Login"
- Enter email and password
- Click "Log In"

### 4. Dashboard Overview
Once logged in, you'll see:
- **Statistics**: Quizzes completed, documents, scores
- **Quick Actions**: Upload documents or generate quizzes

### 5. Upload Document
1. Go to "Documents" tab
2. Drag & drop a file or click to browse
3. Supported formats: PDF, DOCX, PPTX, TXT, RTF, PNG, JPG
4. Document appears in your list

### 6. Generate Quiz
1. Go to "Generate Quiz" tab
2. Select a document from dropdown
3. Choose number of questions (1-50)
4. Select difficulty level (Easy, Medium, Hard)
5. Click "Generate Quiz"
6. Quiz appears in "My Quizzes" tab

### 7. View Quizzes
- Go to "My Quizzes" tab
- See all generated quizzes with:
  - Difficulty badge (color-coded)
  - Question count
  - Creation date
- Click "Take Quiz" to start answering

### 8. Logout
- Click "Logout" button in top-right corner

## API Endpoints

### Authentication
- **POST** `/api/auth/signup` - Create new account
- **POST** `/api/auth/login` - Login user
- **POST** `/api/auth/logout` - Logout
- **GET** `/api/auth/session` - Check session status
- **GET** `/api/user/me` - Get current user profile

### Documents
- **GET** `/api/documents` - List user documents
- **POST** `/api/documents/upload` - Upload document
- **DELETE** `/api/documents/<id>` - Delete document

### Quiz
- **POST** `/api/quiz/generate` - Generate quiz from document
- **GET** `/api/quiz/history` - Get quiz history
- **GET** `/api/quiz/<id>` - Get specific quiz
- **POST** `/api/quiz/<id>/attempt` - Submit quiz attempt

### Health
- **GET** `/api/health` - System status

## Features

### ✅ Authentication
- Secure signup with password strength meter
- Email validation
- Session management
- Logout functionality

### ✅ Document Management
- Upload various file formats
- Drag-and-drop upload area
- View all uploaded documents
- Delete documents

### ✅ Quiz Generation
- AI-powered quiz creation
- Select question count (1-50)
- Choose difficulty level
- View generation history

### ✅ User Dashboard
- Personal statistics
- Quiz management
- Document library
- Quick action buttons

### ✅ UI/UX
- Modern gradient design
- Responsive mobile design
- Smooth animations
- Professional color scheme
- Loading states
- Error handling

## Troubleshooting

### "Cannot connect to localhost:5000"
- Make sure Flask server is running: `python app.py`
- Check if port 5000 is not already in use

### "Cannot connect to localhost:3000"
- Make sure React dev server is running: `npm start`
- Check if you're in the `frontend` directory

### Supabase Connection Error
- Verify `.env` file has correct credentials
- Check Supabase URL and key are valid
- Ensure Supabase project is active

### npm command not found
- Install Node.js from nodejs.org
- Restart terminal after installation

### Module not found errors
- Delete `node_modules` folder
- Delete `package-lock.json`
- Run `npm install` again

## Project Structure

```
quiz-generate/
├── app.py                 # Main Flask app
├── auth_service.py        # Authentication logic
├── quiz_generator.py      # Quiz generation AI
├── rag_system.py          # Document processing
├── document_processor.py   # File processing
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── frontend/              # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth.jsx   # Login/signup page
│   │   │   └── Dashboard.jsx  # Main dashboard
│   │   ├── services/
│   │   │   └── api.js     # API client
│   │   ├── styles/        # CSS files
│   │   └── App.jsx        # Router setup
│   └── package.json       # Node dependencies
└── README.md
```

## Environment Variables

Create `.env` file in project root:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Optional
MISTRAL_API_KEY=your-mistral-key
```

## Development Notes

### Running Tests
```bash
pytest -v
```

### Generating Coverage Report
```bash
pytest --cov=. --cov-report=html
```

### Building Frontend for Production
```bash
cd frontend
npm run build
```

## Support & Documentation

- **Auth.jsx** - Login/signup component with validation
- **Dashboard.jsx** - Main app interface
- **api.js** - Backend API client
- **FRONTEND_IMPROVEMENTS.md** - Detailed improvement documentation
- **README.md** - Main project readme

## Next Steps

1. ✅ Start backend: `python app.py`
2. ✅ Start frontend: `cd frontend && npm start`
3. ✅ Open http://localhost:3000
4. ✅ Sign up and try generating a quiz!

## Performance Tips

1. **Document Upload**: Start with smaller files (< 10 MB)
2. **Quiz Generation**: Start with 10-20 questions for testing
3. **Browser Cache**: Clear cache if styles aren't updating
4. **Console Errors**: Check browser DevTools console for details

---

**Happy learning with Kwizy!** 🎓
