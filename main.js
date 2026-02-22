// the main Skill-Link - AI-Driven Campus Placement Platform
// Team Arena

const API_BASE = '/api';

// ==================== AUTH UTILITIES ====================

const Auth = {
    // Get token from localStorage
    getToken: () => localStorage.getItem('skilllink_token'),
    
    // Get user role
    getRole: () => localStorage.getItem('skilllink_role'),
    
    // Get user data
    getUser: () => {
        const user = localStorage.getItem('skilllink_user');
        return user ? JSON.parse(user) : null;
    },
    
    // Set auth data
    setAuth: (token, user, role) => {
        localStorage.setItem('skilllink_token', token);
        localStorage.setItem('skilllink_user', JSON.stringify(user));
        localStorage.setItem('skilllink_role', role);
    },
    
    // Clear auth data
    logout: () => {
        localStorage.removeItem('skilllink_token');
        localStorage.removeItem('skilllink_user');
        localStorage.setItem('skilllink_role', 'guest');
        window.location.href = '/';
    },
    
    // Check if logged in
    isLoggedIn: () => !!localStorage.getItem('skilllink_token'),
    
    // Redirect based on role
    redirectByRole: () => {
        const role = Auth.getRole();
        if (role === 'hr') {
            window.location.href = '/dashboard/hr';
        } else if (role === 'student') {
            window.location.href = '/dashboard/student';
        }
    }
};

// ==================== API HELPERS ====================

const API = {
    // Make authenticated request
    async request(endpoint, options = {}) {
        const token = Auth.getToken();
        
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };
        
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // GET request
    get: (endpoint) => API.request(endpoint, { method: 'GET' }),
    
    // POST request
    post: (endpoint, data) => API.request(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    // PUT request
    put: (endpoint, data) => API.request(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    // DELETE request
    delete: (endpoint) => API.request(endpoint, { method: 'DELETE' })
};

// ==================== UI UTILITIES ====================

const UI = {
    // Show toast notification
    showToast: (message, type = 'info') => {
        const container = document.querySelector('.toast-container') || UI.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    // Create toast container
    createToastContainer: () => {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    },
    
    // Show loading spinner
    showLoading: (element) => {
        element.innerHTML = '<div class="spinner"></div>';
    },
    
    // Hide loading
    hideLoading: (element) => {
        element.innerHTML = '';
    },
    
    // Format date
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Get status badge class
    getStatusClass: (status) => {
        const classes = {
            'Applied': 'status-applied',
            'Shortlisted': 'status-shortlisted',
            'Rejected': 'status-rejected',
            'Interview': 'status-interview',
            'Selected': 'status-selected'
        };
        return classes[status] || 'status-applied';
    },
    
    // Get match score class
    getMatchClass: (score) => {
        if (score >= 70) return 'match-high';
        if (score >= 40) return 'match-medium';
        return 'match-low';
    }
};

// ==================== HR AUTH ====================

const HRAuth = {
    // Register HR
    async register(data) {
        try {
            const result = await API.post('/hr/register', data);
            Auth.setAuth(result.access_token, result.hr, 'hr');
            UI.showToast('Registration successful!', 'success');
            Auth.redirectByRole();
            return result;
        } catch (error) {
            UI.showToast(error.message, 'error');
            throw error;
        }
    },
    
    // Login HR
    async login(email, password) {
        try {
            const result = await API.post('/hr/login', { email, password });
            Auth.setAuth(result.access_token, result.hr, 'hr');
            UI.showToast('Login successful!', 'success');
            Auth.redirectByRole();
            return result;
        } catch (error) {
            UI.showToast(error.message, 'error');
            throw error;
        }
    }
};

// ==================== STUDENT AUTH ====================

const StudentAuth = {
    // Register Student
    async register(data) {
        try {
            const result = await API.post('/students/register', data);
            Auth.setAuth(result.access_token, result.student, 'student');
            UI.showToast('Registration successful!', 'success');
            Auth.redirectByRole();
            return result;
        } catch (error) {
            UI.showToast(error.message, 'error');
            throw error;
        }
    },
    
    // Login Student
    async login(email, password) {
        try {
            const result = await API.post('/students/login', { email, password });
            Auth.setAuth(result.access_token, result.student, 'student');
            UI.showToast('Login successful!', 'success');
            Auth.redirectByRole();
            return result;
        } catch (error) {
            UI.showToast(error.message, 'error');
            throw error;
        }
    }
};

// ==================== HR DASHBOARD ====================

const HRDashboard = {
    // Get analytics
    async getAnalytics() {
        return await API.get('/hr/analytics');
    },
    
    // Get HR jobs
    async getJobs() {
        return await API.get('/hr/jobs');
    },
    
    // Create job
    async createJob(data) {
        const result = await API.post('/hr/jobs', data);
        UI.showToast('Job created successfully!', 'success');
        return result;
    },
    
    // Get applicants for job
    async getApplicants(jobId) {
        return await API.get(`/hr/jobs/${jobId}/applicants`);
    },
    
    // Shortlist candidate
    async shortlistCandidate(appId) {
        const result = await API.post(`/hr/applications/${appId}/shortlist`);
        UI.showToast('Candidate shortlisted!', 'success');
        return result;
    },
    
    // Reject candidate
    async rejectCandidate(appId) {
        const result = await API.post(`/hr/applications/${appId}/reject`);
        UI.showToast('Candidate rejected', 'info');
        return result;
    },
    
    // Send interview
    async sendInterview(appId, message) {
        const result = await API.post('/hr/send-interview', { application_id: appId, message });
        UI.showToast('Interview invitation sent!', 'success');
        return result;
    },
    
    // Get AI recommendations
    async getRecommendations(jobId) {
        return await API.get(`/hr/jobs/${jobId}/recommended`);
    },
    
    // Bulk shortlist
    async bulkShortlist(jobId, count) {
        const result = await API.post(`/hr/jobs/${jobId}/shortlist-bulk`, { count });
        UI.showToast(`${result.shortlisted_count} candidates shortlisted!`, 'success');
        return result;
    },
    
    // Add HR note
    async addNote(appId, note) {
        const result = await API.post(`/hr/applications/${appId}/note`, { note });
        UI.showToast('Note added!', 'success');
        return result;
    }
};

// ==================== STUDENT DASHBOARD ====================

const StudentDashboard = {
    // Get dashboard data
    async getDashboard() {
        return await API.get('/students/dashboard');
    },
    
    // Get profile
    async getProfile() {
        return await API.get('/students/profile');
    },
    
    // Update profile
    async updateProfile(data) {
        const result = await API.put('/students/profile', data);
        UI.showToast('Profile updated!', 'success');
        return result;
    },
    
    // Get skills
    async getSkills() {
        return await API.get('/students/skills');
    },
    
    // Add skills
    async addSkills(skills) {
        const result = await API.post('/students/skills', { skills });
        UI.showToast('Skills updated!', 'success');
        return result;
    },
    
    // Get profile strength
    async getProfileStrength() {
        return await API.get('/students/profile-strength');
    },
    
    // Get skill gap
    async getSkillGap(jobId) {
        return await API.get(`/students/skill-gap/${jobId}`);
    },
    
    // Get role suggestions
    async getRoleSuggestions() {
        return await API.get('/students/role-suggestions');
    },
    
    // Get skill demand
    async getSkillDemand() {
        return await API.get('/students/skill-demand');
    },
    
    // Get recommended jobs
    async getRecommendedJobs() {
        return await API.get('/students/jobs/recommended');
    },
    
    // Get applications
    async getApplications() {
        return await API.get('/students/applications');
    },
    
    // Apply for job
    async applyJob(jobId) {
        const result = await API.post(`/students/jobs/apply/${jobId}`);
        UI.showToast('Job applied successfully!', 'success');
        return result;
    },
    
    // Save job
    async saveJob(jobId) {
        const result = await API.post(`/students/saved-jobs/${jobId}`);
        UI.showToast('Job saved!', 'success');
        return result;
    },
    
    // Get saved jobs
    async getSavedJobs() {
        return await API.get('/students/saved-jobs');
    },
    
    // Unsave job
    async unsaveJob(jobId) {
        const result = await API.delete(`/students/saved-jobs/${jobId}`);
        UI.showToast('Job removed from saved', 'info');
        return result;
    },
    
    // Get internships
    async getInternships() {
        return await API.get('/students/internships');
    },
    
    // Get business jobs
    async getBusinessJobs() {
        return await API.get('/students/business-jobs');
    }
};

// ==================== RESUME ====================

const Resume = {
    // Upload resume
    async upload(file, jobRequirements = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (jobRequirements) {
            formData.append('job_requirements', JSON.stringify(jobRequirements));
        }
        
        const token = Auth.getToken();
        const response = await fetch(`${API_BASE}/resume/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }
        
        UI.showToast('Resume uploaded!', 'success');
        return data;
    },
    
    // Get resume score
    async getScore() {
        return await API.get('/resume/score');
    },
    
    // Get resume score for job
    async getScoreForJob(jobId) {
        return await API.get(`/resume/score/${jobId}`);
    },
    
    // Delete resume
    async delete() {
        const result = await API.delete('/resume/delete');
        UI.showToast('Resume deleted', 'info');
        return result;
    }
};

// ==================== SKILL TAGS INPUT ====================

const SkillTags = {
    // Initialize skill tags input
    init(containerId, onChange) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'skill-input';
        input.placeholder = 'Type skill and press Enter';
        
        container.appendChild(input);
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const value = input.value.trim().replace(',', '');
                if (value) {
                    SkillTags.addTag(container, value, onChange);
                    input.value = '';
                }
            }
        });
        
        // Make container focusable
        container.addEventListener('click', () => input.focus());
    },
    
    // Add skill tag
    addTag(container, skill, onChange) {
        const existingTags = container.querySelectorAll('.skill-tag span');
        for (let tag of existingTags) {
            if (tag.textContent.toLowerCase() === skill.toLowerCase()) {
                return;
            }
        }
        
        const tag = document.createElement('div');
        tag.className = 'skill-tag';
        tag.innerHTML = `
            <span>${skill}</span>
            <span class="remove" onclick="SkillTags.removeTag(this, '${skill}', ${onChange})">×</span>
        `;
        
        container.insertBefore(tag, container.querySelector('.skill-input'));
        
        if (onChange) onChange();
    },
    
    // Remove skill tag
    removeTag(element, skill, onChange) {
        element.parentElement.remove();
        if (onChange) onChange();
    },
    
    // Get all skills
    getSkills(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return [];
        
        const tags = container.querySelectorAll('.skill-tag span:not(.remove)');
        return Array.from(tags).map(tag => tag.textContent);
    },
    
    // Set skills
    setSkills(containerId, skills, onChange) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing tags
        const existingTags = container.querySelectorAll('.skill-tag');
        existingTags.forEach(tag => tag.remove());
        
        // Add new tags
        skills.forEach(skill => SkillTags.addTag(container, skill, onChange));
    }
};

// ==================== FILE UPLOAD ====================

const FileUpload = {
    // Initialize drag and drop
    init(dropZoneId, onFileSelect) {
        const dropZone = document.getElementById(dropZoneId);
        if (!dropZone) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        // Highlight drop zone
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('dragover');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('dragover');
            });
        });
        
        // Handle drop
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                onFileSelect(files[0]);
            }
        });
        
        // Handle click
        dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.pdf,.docx,.doc';
            input.onchange = (e) => {
                if (e.target.files.length > 0) {
                    onFileSelect(e.target.files[0]);
                }
            };
            input.click();
        });
    },
    
    // Validate file
    validate(file) {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        if (!allowedTypes.includes(file.type)) {
            throw new Error('Only PDF and DOCX files are allowed');
        }
        
        if (file.size > maxSize) {
            throw new Error('File size must be less than 16MB');
        }
        
        return true;
    }
};

// ==================== CAREERBOT ====================

const CareerBot = {
    // Toggle chatbot
    toggle() {
        const box = document.querySelector('.chatbot-box');
        if (box) {
            box.classList.toggle('show');
        }
    },
    
    // Send message
    async sendMessage(message) {
        const messagesContainer = document.querySelector('.chatbot-messages');
        if (!messagesContainer) return;
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.textContent = message;
        messagesContainer.appendChild(userMsg);
        
        // Get bot response
        const response = await CareerBot.getResponse(message);
        
        // Add bot response
        const botMsg = document.createElement('div');
        botMsg.className = 'message bot';
        botMsg.textContent = response;
        messagesContainer.appendChild(botMsg);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    },
    
    // Get AI response
    async getResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Check for greetings
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
            return "Hello! I'm CareerBot, your AI career assistant. How can I help you today?";
        }
        
        // Check for job help
        if (lowerMessage.includes('job') || lowerMessage.includes('job')) {
            return "I can help you find jobs! Go to the Dashboard and check 'Recommended Jobs' section. Make sure your profile is complete and resume is uploaded!";
        }
        
        // Check for resume help
        if (lowerMessage.includes('resume') || lowerMessage.includes('cv')) {
            return "To improve your resume:\n1. Upload your resume in the Resume section\n2. Add your skills using the skill tags\n3. Keep your profile updated\n4. A good resume scores 70+ for better job matches!";
        }
        
        // Check for skills help
        if (lowerMessage.includes('skill')) {
            return "Adding relevant skills increases your job match percentage! Add skills like Python, Java, React, SQL, AWS, Machine Learning, etc. to get better job recommendations.";
        }
        
        // Check for interview help
        if (lowerMessage.includes('interview')) {
            return "To prepare for interviews:\n1. Practice common questions\n2. Research the company\n3. Review your resume\n4. Prepare questions to ask the interviewer\n5. Dress professionally!";
        }
        
        // Check for application status
        if (lowerMessage.includes('application') || lowerMessage.includes('status')) {
            return "Check your application status in the 'My Applications' section of your dashboard. You'll see if you're Applied, Shortlisted, or have interview calls!";
        }
        
        // Default response
        return "I'm here to help! You can ask me about:\n- Finding jobs\n- Improving your resume\n- Adding skills\n- Interview preparation\n- Application status\n\nWhat would you like to know?";
    }
};

// ==================== DARK MODE ====================

const DarkMode = {
    // Toggle dark mode
    toggle() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('skilllink_darkmode', document.body.classList.contains('dark-mode'));
    },
    
    // Initialize
    init() {
        if (localStorage.getItem('skilllink_darkmode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    }
};

// ==================== EXPORT TO CSV ====================

const Export = {
    // Download CSV
    toCSV(data, filename) {
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }
};

// ==================== FORM VALIDATION ====================

const Validation = {
    // Validate email
    email(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Validate password
    password(password) {
        return password.length >= 6;
    },
    
    // Validate required
    required(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },
    
    // Validate form
    validateForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return true;
        
        const inputs = form.querySelectorAll('[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!Validation.required(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
            
            // Email validation
            if (input.type === 'email' && !Validation.email(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            }
            
            // Password validation
            if (input.type === 'password' && !Validation.password(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        });
        
        return isValid;
    }
};

// ==================== INITIALIZE ====================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize dark mode
    DarkMode.init();
    
    // Add logout handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });
    }
    
    // Add chatbot toggle handler
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', CareerBot.toggle);
    }
    
    // Add dark mode toggle handler
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', DarkMode.toggle);
    }
});
