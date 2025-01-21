# Developer Productivity Monitoring Platform Architecture

## Overview
The platform consists of a microservices-based backend written in Python/Flask and a React/TypeScript frontend. It provides comprehensive developer productivity monitoring, including DORA metrics, value stream analysis, security scanning, and real-time collaboration features.

## Backend Services

### Core Services
1. **Task Service** (`task_service.py`)
   - Task management and tracking
   - Status updates and assignments
   - Integration with external task systems

2. **Monitoring Service** (`monitoring_service.py`)
   - Focus time tracking
   - Activity monitoring
   - Productivity metrics calculation

3. **Git Service** (`git_service.py`)
   - Repository traffic analytics
   - Commit and merge tracking
   - Deployment event recording

### Analytics Services
1. **DORA Service** (`dora_service.py`)
   - Deployment frequency tracking
   - Lead time calculation
   - Change failure rate monitoring
   - Mean time to recovery (MTTR)

2. **Value Stream Service** (`value_stream_service.py`)
   - End-to-end cycle time tracking
   - Value stream mapping
   - Process bottleneck identification

3. **AI Service** (`ai_service.py`)
   - Code review scoring
   - Readability analysis
   - Productivity suggestions

### Security & Authentication
1. **Security Service** (`security_service.py`)
   - GitHub code scanning integration
   - Security advisory tracking
   - Vulnerability management

2. **SSO Service** (`sso_service.py`)
   - Single Sign-On support
   - Okta integration
   - Azure AD integration

3. **Auth Service** (`auth_service.py`)
   - Role-Based Access Control (RBAC)
   - Permission management
   - Token handling

### Collaboration Features
1. **Collaboration Service** (`collaboration_service.py`)
   - Team activity tracking
   - Code review analytics
   - Contribution insights

2. **WebSocket Service** (`websocket_service.py`)
   - Real-time updates
   - Live collaboration
   - Mindmap synchronization

### Support Services
1. **Notifications Service** (`notifications_service.py`)
   - Email notifications
   - Slack integration
   - Achievement alerts

2. **Report Service** (`report_service.py`)
   - Data export (PDF, Excel, CSV)
   - Custom report generation
   - Metrics aggregation

3. **Achievements Service** (`achievements_service.py`)
   - Gamification system
   - Badge management
   - Progress tracking

## Frontend Architecture

### Core Components
1. **Dashboard Pages**
   - Main dashboard
   - Security dashboard
   - Value stream analysis
   - Team collaboration
   - Organization metrics

2. **Visualization Components**
   - Contribution charts
   - Traffic analytics
   - Focus time breakdown
   - Meeting analytics

3. **Real-time Features**
   - WebSocket integration
   - Live collaboration tools
   - Instant notifications

### UI Components
- Responsive design
- Dark/light theme support
- Mobile-first approach
- Accessible components

## Configuration

### Environment Variables
Required environment variables for backend services:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=devin_tasks

# GitHub Integration
GITHUB_TOKEN=your_github_token

# Security
SECRET_KEY=your_secret_key

# Okta SSO
OKTA_CLIENT_ID=your_okta_client_id
OKTA_CLIENT_SECRET=your_okta_client_secret
OKTA_ORG_URL=https://your-org.okta.com
OKTA_REDIRECT_URI=http://localhost:5000/sso/callback/okta

# Azure AD SSO
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
AZURE_REDIRECT_URI=http://localhost:5000/sso/callback/azure
```

### Security Considerations
- All sensitive configuration is loaded from environment variables
- Example configuration template provided in `config.example.py`
- Sensitive files excluded via `.gitignore`
- Data anonymization for user and repository information

## API Documentation

### Core Endpoints
1. **Task Management**
   - `POST /tasks` - Create new task
   - `GET /tasks/<id>` - Get task details
   - `PUT /tasks/<id>` - Update task

2. **Monitoring**
   - `GET /monitoring/focus-metrics/current` - Get current focus metrics
   - `POST /monitoring/events` - Record monitoring event

3. **Value Stream**
   - `GET /value-stream/metrics/<engineer_id>` - Get value stream metrics
   - `POST /value-stream/events/<engineer_id>` - Record value stream event

4. **Security**
   - `GET /security/alerts` - Get security alerts
   - `POST /security/sync` - Sync security advisories

5. **Collaboration**
   - `GET /collab/activity` - Get activity feed
   - `GET /collab/stats` - Get collaboration statistics

### WebSocket Events
1. **Mindmap Collaboration**
   - `join_mindmap` - Join collaborative session
   - `node_added` - New node creation
   - `node_updated` - Node update
   - `edge_added` - New edge creation

2. **Real-time Updates**
   - `user_joined` - User joined notification
   - `user_left` - User left notification
   - `mindmap_state` - Full state sync

## Development Setup

### Backend Setup
1. Create virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `config.example.py` to `config.py`
4. Set required environment variables
5. Run development server: `python run.py`

### Frontend Setup
1. Install dependencies: `npm install`
2. Set up environment variables
3. Run development server: `npm run dev`

## Testing
- Backend tests: `pytest`
- Frontend tests: `npm run test`
- End-to-end tests: (Coming soon)
