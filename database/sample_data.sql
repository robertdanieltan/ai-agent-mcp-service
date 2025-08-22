-- Sample data for Task Management Database
-- Insert sample projects and tasks for testing

-- Insert sample projects
INSERT INTO projects (name, description) VALUES 
('AI Development Project', 'A comprehensive AI development project using CrewAI and MCP'),
('Database Migration', 'Migrate legacy database to PostgreSQL'),
('Frontend Redesign', 'Complete redesign of the user interface');

-- Insert sample tasks for AI Development Project (project_id = 1)
INSERT INTO tasks (title, description, status, priority, project_id, assigned_to) VALUES 
('Setup MCP Service', 'Create and configure the MCP service with FastMCP', 'completed', 'high', 1, 'Developer'),
('Implement Database Models', 'Create database models for projects and tasks', 'in_progress', 'high', 1, 'Backend Dev'),
('Create CrewAI Agents', 'Implement Project Manager and Task Coordinator agents', 'pending', 'medium', 1, 'AI Engineer'),
('Write Documentation', 'Document the API and setup instructions', 'pending', 'low', 1, 'Technical Writer'),
('Add Unit Tests', 'Implement comprehensive unit tests', 'pending', 'medium', 1, 'QA Engineer');

-- Insert sample tasks for Database Migration (project_id = 2)
INSERT INTO tasks (title, description, status, priority, project_id, assigned_to) VALUES 
('Analyze Legacy Schema', 'Document current database structure', 'completed', 'critical', 2, 'Database Admin'),
('Design New Schema', 'Create optimized PostgreSQL schema', 'in_progress', 'critical', 2, 'Database Admin'),
('Data Migration Script', 'Write scripts to migrate existing data', 'pending', 'high', 2, 'Backend Dev'),
('Performance Testing', 'Test database performance with migrated data', 'pending', 'medium', 2, 'QA Engineer');

-- Insert sample tasks for Frontend Redesign (project_id = 3)
INSERT INTO tasks (title, description, status, priority, project_id, assigned_to) VALUES 
('User Research', 'Conduct user interviews and surveys', 'completed', 'high', 3, 'UX Designer'),
('Wireframe Creation', 'Create wireframes for new design', 'in_progress', 'high', 3, 'UX Designer'),
('Component Library', 'Build reusable UI components', 'pending', 'medium', 3, 'Frontend Dev'),
('Responsive Design', 'Ensure design works on all devices', 'pending', 'medium', 3, 'Frontend Dev'),
('Accessibility Audit', 'Ensure WCAG compliance', 'pending', 'low', 3, 'QA Engineer');