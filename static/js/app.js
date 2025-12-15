/**
 * Quiz RAG Generator - Main Application JavaScript
 */

// =====================================================
// Global State
// =====================================================

const state = {
    uploadedFiles: [],
    currentQuiz: null,
    userAnswers: {},
    isLoading: false
};

// =====================================================
// Utility Functions
// =====================================================

function showLoading(message = 'Chargement en cours...') {
    const overlay = document.getElementById('loading-overlay');
    const messageEl = document.getElementById('loading-message');
    messageEl.textContent = message;
    overlay.classList.add('active');
    state.isLoading = true;
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('active');
    state.isLoading = false;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        pdf: 'fas fa-file-pdf',
        pptx: 'fas fa-file-powerpoint',
        ppt: 'fas fa-file-powerpoint',
        docx: 'fas fa-file-word',
        doc: 'fas fa-file-word',
        txt: 'fas fa-file-alt',
        rtf: 'fas fa-file-alt'
    };
    return icons[ext] || 'fas fa-file';
}

// =====================================================
// API Functions
// =====================================================

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

async function generateQuiz(options) {
    const response = await fetch('/api/generate-quiz', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(options)
    });
    
    return await response.json();
}

async function clearDocuments() {
    const response = await fetch('/api/documents/clear', {
        method: 'POST'
    });
    
    return await response.json();
}

async function getDocumentStats() {
    const response = await fetch('/api/documents');
    return await response.json();
}

// =====================================================
// Navigation
// =====================================================

function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            navigateToSection(section);
        });
    });
}

function navigateToSection(sectionName) {
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.section === sectionName);
    });
    
    // Update sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.toggle('active', section.id === `${sectionName}-section`);
    });
}

// =====================================================
// Upload Section
// =====================================================

function initUploadSection() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const clearAllBtn = document.getElementById('clear-all-btn');
    const proceedBtn = document.getElementById('proceed-btn');
    
    // Drag and drop handlers
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', async (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        await handleFiles(files);
    });
    
    // Click to upload
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        await handleFiles(files);
        fileInput.value = '';
    });
    
    // Clear all button
    clearAllBtn.addEventListener('click', async () => {
        if (confirm('Êtes-vous sûr de vouloir supprimer tous les documents ?')) {
            showLoading('Suppression des documents...');
            try {
                await clearDocuments();
                state.uploadedFiles = [];
                updateFilesList();
                showToast('Tous les documents ont été supprimés', 'success');
            } catch (error) {
                showToast('Erreur lors de la suppression', 'error');
            } finally {
                hideLoading();
            }
        }
    });
    
    // Proceed button
    proceedBtn.addEventListener('click', () => {
        navigateToSection('generate');
    });
}

async function handleFiles(files) {
    const validExtensions = ['pdf', 'pptx', 'ppt', 'docx', 'doc', 'txt', 'rtf'];
    
    for (const file of files) {
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (!validExtensions.includes(ext)) {
            showToast(`Format non supporté: ${file.name}`, 'error');
            continue;
        }
        
        showLoading(`Traitement de ${file.name}...`);
        
        try {
            const result = await uploadFile(file);
            
            if (result.success) {
                state.uploadedFiles.push({
                    name: file.name,
                    size: file.size,
                    ...result.data
                });
                showToast(`${file.name} chargé avec succès`, 'success');
            } else {
                showToast(result.error || 'Erreur lors du chargement', 'error');
            }
        } catch (error) {
            showToast(`Erreur: ${error.message}`, 'error');
        }
    }
    
    hideLoading();
    updateFilesList();
}

function updateFilesList() {
    const filesList = document.getElementById('files-list');
    const clearAllBtn = document.getElementById('clear-all-btn');
    const proceedBtn = document.getElementById('proceed-btn');
    
    if (state.uploadedFiles.length === 0) {
        filesList.innerHTML = '<p class="no-files">Aucun document chargé</p>';
        clearAllBtn.style.display = 'none';
        proceedBtn.style.display = 'none';
        return;
    }
    
    clearAllBtn.style.display = 'inline-flex';
    proceedBtn.style.display = 'inline-flex';
    
    filesList.innerHTML = state.uploadedFiles.map((file, index) => `
        <div class="file-item" data-index="${index}">
            <div class="file-info">
                <i class="${getFileIcon(file.name)} file-icon"></i>
                <div class="file-details">
                    <h4>${file.name}</h4>
                    <span>${formatFileSize(file.size)} • ${file.chunks_created || 0} chunks</span>
                </div>
            </div>
            <div class="file-status success">
                <i class="fas fa-check-circle"></i>
                <span>Traité</span>
            </div>
        </div>
    `).join('');
}

// =====================================================
// Generate Section
// =====================================================

function initGenerateSection() {
    const numQuestionsInput = document.getElementById('num-questions');
    const numQuestionsValue = document.getElementById('num-questions-value');
    const generateBtn = document.getElementById('generate-btn');
    
    // Update range value display
    numQuestionsInput.addEventListener('input', () => {
        numQuestionsValue.textContent = numQuestionsInput.value;
    });
    
    // Difficulty option selection
    document.querySelectorAll('.option-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
        });
    });
    
    // Generate button
    generateBtn.addEventListener('click', handleGenerateQuiz);
}

async function handleGenerateQuiz() {
    // Check if documents are loaded
    if (state.uploadedFiles.length === 0) {
        showToast('Veuillez d\'abord charger un document', 'error');
        navigateToSection('upload');
        return;
    }
    
    // Get options
    const numQuestions = parseInt(document.getElementById('num-questions').value);
    const topic = document.getElementById('topic').value;
    const difficulty = document.querySelector('input[name="difficulty"]:checked')?.value || 'moyen';
    
    const questionTypes = Array.from(document.querySelectorAll('input[name="question_type"]:checked'))
        .map(cb => cb.value);
    
    if (questionTypes.length === 0) {
        showToast('Veuillez sélectionner au moins un type de question', 'error');
        return;
    }
    
    showLoading('Génération du quiz en cours...\nCela peut prendre quelques instants.');
    
    try {
        const result = await generateQuiz({
            num_questions: numQuestions,
            difficulty: difficulty,
            question_types: questionTypes,
            topic: topic
        });
        
        if (result.success && result.data) {
            state.currentQuiz = result.data;
            state.userAnswers = {};
            displayQuiz(result.data);
            navigateToSection('quiz');
            showToast('Quiz généré avec succès!', 'success');
        } else {
            showToast(result.error || 'Erreur lors de la génération', 'error');
        }
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// =====================================================
// Quiz Section
// =====================================================

function initQuizSection() {
    const newQuizBtn = document.getElementById('new-quiz-btn');
    const checkAnswersBtn = document.getElementById('check-answers-btn');
    const exportBtn = document.getElementById('export-btn');
    
    newQuizBtn.addEventListener('click', () => {
        navigateToSection('generate');
    });
    
    checkAnswersBtn.addEventListener('click', checkAnswers);
    exportBtn.addEventListener('click', exportQuiz);
}

function displayQuiz(quiz) {
    const container = document.getElementById('quiz-container');
    const actions = document.getElementById('quiz-actions');
    const results = document.getElementById('results-container');
    const titleEl = document.getElementById('quiz-title');
    const infoEl = document.getElementById('quiz-info');
    
    // Update title
    titleEl.textContent = quiz.quiz_title || 'Quiz Généré';
    infoEl.textContent = `${quiz.questions?.length || 0} questions • Difficulté: ${getDifficultyLabel(quiz.difficulty)}`;
    
    // Show actions, hide results
    actions.style.display = 'flex';
    results.style.display = 'none';
    
    // Render questions
    if (!quiz.questions || quiz.questions.length === 0) {
        container.innerHTML = `
            <div class="quiz-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Aucune question n'a pu être générée. Veuillez réessayer.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = quiz.questions.map((q, index) => renderQuestion(q, index)).join('');
    
    // Add event listeners for answers
    initAnswerListeners();
}

function renderQuestion(question, index) {
    const typeLabel = getTypeLabel(question.type);
    const diffLabel = getDifficultyLabel(question.difficulty);
    
    let answerSection = '';
    
    switch (question.type) {
        case 'qcm':
            answerSection = renderMCQOptions(question, index);
            break;
        case 'vrai_faux':
            answerSection = renderTrueFalseOptions(question, index);
            break;
        case 'comprehension':
        case 'memorisation':
        case 'reponse_courte':
        default:
            answerSection = renderOpenQuestion(question, index);
            break;
    }
    
    return `
        <div class="question-card" id="question-${index}">
            <div class="question-header">
                <div class="question-number">
                    <i class="fas fa-question-circle"></i>
                    Question ${index + 1}
                </div>
                <div class="question-badges">
                    <span class="badge badge-difficulty">${diffLabel}</span>
                    <span class="badge badge-type">${typeLabel}</span>
                </div>
            </div>
            <p class="question-text">${question.question}</p>
            ${answerSection}
            <div class="question-explanation" style="display: none;">
                <h5><i class="fas fa-lightbulb"></i> Explication</h5>
                <p>${question.explanation || 'Pas d\'explication disponible.'}</p>
                <p><strong>Réponse correcte:</strong> ${question.correct_answer}</p>
            </div>
        </div>
    `;
}

function renderMCQOptions(question, index) {
    const options = question.options || [];
    
    return `
        <div class="answer-options" data-question="${index}" data-type="mcq">
            ${options.map((opt, i) => {
                const letter = String.fromCharCode(65 + i);
                const optionText = opt.replace(/^[A-D][.)]\s*/, '');
                return `
                    <label class="answer-option" data-option="${letter}">
                        <input type="radio" name="q${index}" value="${letter}">
                        <div class="answer-content">
                            <span class="answer-marker">${letter}</span>
                            <span class="answer-text">${optionText}</span>
                        </div>
                    </label>
                `;
            }).join('')}
        </div>
    `;
}

function renderTrueFalseOptions(question, index) {
    return `
        <div class="answer-options true-false-options" data-question="${index}" data-type="tf">
            <label class="answer-option tf-option" data-option="Vrai">
                <input type="radio" name="q${index}" value="Vrai">
                <div class="answer-content tf-content">
                    <i class="fas fa-check"></i>
                    <span>Vrai</span>
                </div>
            </label>
            <label class="answer-option tf-option" data-option="Faux">
                <input type="radio" name="q${index}" value="Faux">
                <div class="answer-content tf-content">
                    <i class="fas fa-times"></i>
                    <span>Faux</span>
                </div>
            </label>
        </div>
    `;
}

function renderOpenQuestion(question, index) {
    return `
        <div class="answer-options" data-question="${index}" data-type="open">
            <textarea class="open-question-input" 
                      placeholder="Écrivez votre réponse ici..."
                      data-question="${index}"></textarea>
        </div>
    `;
}

function initAnswerListeners() {
    // Radio buttons
    document.querySelectorAll('.answer-options input[type="radio"]').forEach(input => {
        input.addEventListener('change', (e) => {
            const questionIndex = e.target.closest('.answer-options').dataset.question;
            state.userAnswers[questionIndex] = e.target.value;
        });
    });
    
    // Textareas
    document.querySelectorAll('.open-question-input').forEach(textarea => {
        textarea.addEventListener('input', (e) => {
            const questionIndex = e.target.dataset.question;
            state.userAnswers[questionIndex] = e.target.value;
        });
    });
}

function checkAnswers() {
    if (!state.currentQuiz || !state.currentQuiz.questions) return;
    
    let correctCount = 0;
    const totalQuestions = state.currentQuiz.questions.length;
    
    state.currentQuiz.questions.forEach((question, index) => {
        const questionCard = document.getElementById(`question-${index}`);
        const userAnswer = state.userAnswers[index];
        const correctAnswer = question.correct_answer;
        
        // Show explanation
        const explanation = questionCard.querySelector('.question-explanation');
        explanation.style.display = 'block';
        
        // Check answer based on type
        let isCorrect = false;
        
        if (question.type === 'qcm') {
            // Extract letter from correct answer
            const correctLetter = correctAnswer?.match(/^[A-D]/)?.[0] || correctAnswer;
            isCorrect = userAnswer === correctLetter;
            
            // Highlight options
            questionCard.querySelectorAll('.answer-option').forEach(opt => {
                const optLetter = opt.dataset.option;
                if (optLetter === correctLetter) {
                    opt.classList.add('correct');
                } else if (optLetter === userAnswer && !isCorrect) {
                    opt.classList.add('incorrect');
                }
            });
        } else if (question.type === 'vrai_faux') {
            const correctValue = correctAnswer?.toLowerCase().includes('vrai') ? 'Vrai' : 'Faux';
            isCorrect = userAnswer === correctValue;
            
            questionCard.querySelectorAll('.answer-option').forEach(opt => {
                const optValue = opt.dataset.option;
                if (optValue === correctValue) {
                    opt.classList.add('correct');
                } else if (optValue === userAnswer && !isCorrect) {
                    opt.classList.add('incorrect');
                }
            });
        } else {
            // For open questions, we can't automatically check
            // Just mark as reviewed
            isCorrect = null;
        }
        
        // Update card style
        if (isCorrect === true) {
            questionCard.classList.add('correct');
            correctCount++;
        } else if (isCorrect === false) {
            questionCard.classList.add('incorrect');
        }
    });
    
    // Show results
    showResults(correctCount, totalQuestions);
}

function showResults(correct, total) {
    const resultsContainer = document.getElementById('results-container');
    const scoreEl = document.getElementById('score');
    const totalEl = document.getElementById('total');
    const scoreFill = document.getElementById('score-fill');
    const scoreMessage = document.getElementById('score-message');
    
    resultsContainer.style.display = 'block';
    scoreEl.textContent = correct;
    totalEl.textContent = total;
    
    const percentage = (correct / total) * 100;
    scoreFill.style.width = `${percentage}%`;
    
    // Set message based on score
    if (percentage >= 80) {
        scoreMessage.textContent = 'Excellent travail! 🎉';
    } else if (percentage >= 60) {
        scoreMessage.textContent = 'Bon travail! Continuez ainsi. 👍';
    } else if (percentage >= 40) {
        scoreMessage.textContent = 'Pas mal! Quelques révisions seraient utiles. 📚';
    } else {
        scoreMessage.textContent = 'N\'abandonnez pas! Révisez et réessayez. 💪';
    }
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

function exportQuiz() {
    if (!state.currentQuiz) {
        showToast('Aucun quiz à exporter', 'error');
        return;
    }
    
    const quiz = state.currentQuiz;
    let content = `# ${quiz.quiz_title || 'Quiz'}\n\n`;
    content += `Difficulté: ${getDifficultyLabel(quiz.difficulty)}\n`;
    content += `Nombre de questions: ${quiz.questions?.length || 0}\n\n`;
    content += `---\n\n`;
    
    quiz.questions?.forEach((q, i) => {
        content += `## Question ${i + 1}\n\n`;
        content += `${q.question}\n\n`;
        
        if (q.options && q.options.length > 0) {
            q.options.forEach(opt => {
                content += `${opt}\n`;
            });
            content += '\n';
        }
        
        content += `**Réponse:** ${q.correct_answer}\n\n`;
        
        if (q.explanation) {
            content += `**Explication:** ${q.explanation}\n\n`;
        }
        
        content += `---\n\n`;
    });
    
    // Download
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `quiz-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Quiz exporté avec succès!', 'success');
}

// =====================================================
// Helper Functions
// =====================================================

function getDifficultyLabel(difficulty) {
    const labels = {
        'facile': 'Facile',
        'moyen': 'Moyen',
        'difficile': 'Difficile',
        'easy': 'Facile',
        'medium': 'Moyen',
        'hard': 'Difficile'
    };
    return labels[difficulty?.toLowerCase()] || difficulty || 'Moyen';
}

function getTypeLabel(type) {
    const labels = {
        'qcm': 'QCM',
        'comprehension': 'Compréhension',
        'memorisation': 'Mémorisation',
        'vrai_faux': 'Vrai/Faux',
        'reponse_courte': 'Réponse Courte',
        'multiple_choice': 'QCM',
        'true_false': 'Vrai/Faux',
        'short_answer': 'Réponse Courte'
    };
    return labels[type?.toLowerCase()] || type || 'Question';
}

// =====================================================
// Source Tabs (File, URL, YouTube)
// =====================================================

function initSourceTabs() {
    const tabs = document.querySelectorAll('.source-tab');
    const contents = document.querySelectorAll('.source-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const source = tab.dataset.source;
            
            // Update tabs
            tabs.forEach(t => t.classList.toggle('active', t === tab));
            
            // Update contents
            contents.forEach(c => {
                c.classList.toggle('active', c.id === `${source}-source`);
            });
        });
    });
    
    // URL fetch button
    const fetchUrlBtn = document.getElementById('fetch-url-btn');
    if (fetchUrlBtn) {
        fetchUrlBtn.addEventListener('click', async () => {
            const url = document.getElementById('url-input').value;
            if (!url) {
                showToast('Veuillez entrer une URL', 'error');
                return;
            }
            
            showLoading('Récupération du contenu...');
            try {
                const response = await fetch('/api/documents/from-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                const result = await response.json();
                
                if (result.success || result.document_id) {
                    showToast('Contenu récupéré avec succès', 'success');
                    state.uploadedFiles.push({
                        name: url,
                        type: 'url',
                        status: 'success'
                    });
                    updateFilesList();
                } else {
                    showToast(result.error || 'Erreur lors de la récupération', 'error');
                }
            } catch (error) {
                showToast('Erreur lors de la récupération', 'error');
            } finally {
                hideLoading();
            }
        });
    }
    
    // YouTube fetch button
    const fetchYoutubeBtn = document.getElementById('fetch-youtube-btn');
    if (fetchYoutubeBtn) {
        fetchYoutubeBtn.addEventListener('click', async () => {
            const videoUrl = document.getElementById('youtube-input').value;
            if (!videoUrl) {
                showToast('Veuillez entrer une URL YouTube', 'error');
                return;
            }
            
            showLoading('Extraction de la transcription...');
            try {
                const response = await fetch('/api/documents/from-youtube', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_url: videoUrl })
                });
                const result = await response.json();
                
                if (result.success || result.document_id) {
                    showToast('Transcription extraite avec succès', 'success');
                    state.uploadedFiles.push({
                        name: videoUrl,
                        type: 'youtube',
                        status: 'success'
                    });
                    updateFilesList();
                } else {
                    showToast(result.error || 'Erreur lors de l\'extraction', 'error');
                }
            } catch (error) {
                showToast('Erreur lors de l\'extraction', 'error');
            } finally {
                hideLoading();
            }
        });
    }
}

// =====================================================
// Flashcards Section
// =====================================================

const flashcardState = {
    cards: [],
    currentIndex: 0,
    isFlipped: false
};

function initFlashcardsSection() {
    const flashcard = document.getElementById('current-flashcard');
    const actionBtns = document.querySelectorAll('.flashcard-actions .btn');
    
    if (flashcard) {
        flashcard.addEventListener('click', () => {
            flashcard.classList.toggle('flipped');
            flashcardState.isFlipped = !flashcardState.isFlipped;
        });
    }
    
    actionBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const quality = parseInt(btn.dataset.quality);
            await submitFlashcardReview(quality);
        });
    });
    
    // Create flashcards from quiz results
    const createFlashcardsBtn = document.getElementById('create-flashcards-btn');
    if (createFlashcardsBtn) {
        createFlashcardsBtn.addEventListener('click', () => {
            createFlashcardsFromQuiz();
        });
    }
    
    loadDueFlashcards();
}

async function loadDueFlashcards() {
    try {
        const response = await fetch('/api/flashcards/user/guest/due');
        if (response.ok) {
            const result = await response.json();
            flashcardState.cards = result.cards || [];
            updateFlashcardDisplay();
            updateFlashcardStats();
        }
    } catch (error) {
        console.log('Flashcards API not available');
    }
}

function updateFlashcardDisplay() {
    const questionEl = document.getElementById('flashcard-question');
    const answerEl = document.getElementById('flashcard-answer');
    const actionsEl = document.getElementById('flashcard-actions');
    const flashcard = document.getElementById('current-flashcard');
    
    if (flashcardState.cards.length === 0) {
        questionEl.textContent = 'Aucune carte à réviser';
        answerEl.textContent = '';
        actionsEl.style.display = 'none';
        return;
    }
    
    const card = flashcardState.cards[flashcardState.currentIndex];
    questionEl.textContent = card.front || card.question;
    answerEl.textContent = card.back || card.answer;
    actionsEl.style.display = 'flex';
    
    // Reset flip state
    flashcard.classList.remove('flipped');
    flashcardState.isFlipped = false;
}

function updateFlashcardStats() {
    const dueToday = document.getElementById('due-today');
    const totalCards = document.getElementById('total-cards');
    
    if (dueToday) dueToday.textContent = flashcardState.cards.length;
    if (totalCards) totalCards.textContent = flashcardState.cards.length;
}

async function submitFlashcardReview(quality) {
    const card = flashcardState.cards[flashcardState.currentIndex];
    if (!card) return;
    
    try {
        await fetch(`/api/flashcards/${card.id}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quality })
        });
    } catch (error) {
        console.log('Review API not available');
    }
    
    // Move to next card
    flashcardState.cards.splice(flashcardState.currentIndex, 1);
    if (flashcardState.currentIndex >= flashcardState.cards.length) {
        flashcardState.currentIndex = 0;
    }
    updateFlashcardDisplay();
    updateFlashcardStats();
    
    if (flashcardState.cards.length === 0) {
        showToast('Félicitations! Toutes les cartes ont été révisées!', 'success');
    }
}

function createFlashcardsFromQuiz() {
    if (!state.currentQuiz || !state.currentQuiz.questions) {
        showToast('Aucun quiz disponible', 'error');
        return;
    }
    
    const wrongAnswers = [];
    state.currentQuiz.questions.forEach((q, i) => {
        const userAnswer = state.userAnswers[i];
        if (userAnswer !== q.correct_answer && userAnswer !== q.correctAnswer) {
            wrongAnswers.push({
                front: q.question,
                back: `Réponse: ${q.correct_answer || q.correctAnswer}\n\n${q.explanation || ''}`
            });
        }
    });
    
    if (wrongAnswers.length === 0) {
        showToast('Aucune erreur à réviser!', 'success');
        return;
    }
    
    flashcardState.cards = [...flashcardState.cards, ...wrongAnswers];
    updateFlashcardDisplay();
    updateFlashcardStats();
    showToast(`${wrongAnswers.length} flashcards créées`, 'success');
    navigateToSection('flashcards');
}

// =====================================================
// Stats Section
// =====================================================

const userStats = {
    totalQuizzes: 0,
    correctAnswers: 0,
    level: 1,
    xp: 0
};

function initStatsSection() {
    loadUserStats();
}

async function loadUserStats() {
    try {
        const response = await fetch('/api/user/guest/stats');
        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        // Use local stats
        updateStatsDisplay(userStats);
    }
}

function updateStatsDisplay(stats) {
    const globalScore = document.getElementById('global-score');
    const totalQuizzes = document.getElementById('total-quizzes');
    const correctAnswers = document.getElementById('correct-answers');
    const userLevel = document.getElementById('user-level');
    const currentXp = document.getElementById('current-xp');
    const nextLevelXp = document.getElementById('next-level-xp');
    const xpFill = document.getElementById('xp-fill');
    
    const total = (stats.totalQuizzes || 0);
    const correct = (stats.correctAnswers || stats.total_correct || 0);
    const wrong = (stats.total_wrong || 0);
    const scorePercent = total > 0 ? Math.round((correct / (correct + wrong)) * 100) : 0;
    
    if (globalScore) globalScore.textContent = `${scorePercent}%`;
    if (totalQuizzes) totalQuizzes.textContent = total;
    if (correctAnswers) correctAnswers.textContent = correct;
    if (userLevel) userLevel.textContent = stats.level || 1;
    if (currentXp) currentXp.textContent = stats.xp || stats.xp_points || 0;
    if (nextLevelXp) nextLevelXp.textContent = ((stats.level || 1) + 1) * 100;
    
    if (xpFill) {
        const xp = stats.xp || stats.xp_points || 0;
        const level = stats.level || 1;
        const xpForLevel = xp % 100;
        xpFill.style.width = `${xpForLevel}%`;
    }
    
    // Update difficulty chart
    updateDifficultyChart(stats.performance_by_difficulty || {});
}

function updateDifficultyChart(performance) {
    const chartBars = document.querySelectorAll('.chart-bar');
    
    chartBars.forEach(bar => {
        const difficulty = bar.dataset.difficulty;
        const data = performance[difficulty] || { success_rate: 0 };
        const percent = Math.round(data.success_rate || 0);
        
        const fill = bar.querySelector('.bar-fill');
        const value = bar.querySelector('.bar-value');
        
        if (fill) fill.style.height = `${percent}%`;
        if (value) value.textContent = `${percent}%`;
    });
}

function updateLocalStats(score, total) {
    userStats.totalQuizzes++;
    userStats.correctAnswers += score;
    
    // Award XP
    const xpEarned = score * 10 + (score === total ? 50 : 0);
    userStats.xp += xpEarned;
    
    // Level up check
    while (userStats.xp >= (userStats.level + 1) * 100) {
        userStats.level++;
        showToast(`🎉 Niveau ${userStats.level} atteint!`, 'success');
    }
    
    updateStatsDisplay(userStats);
    
    // Try to save to server
    try {
        fetch('/api/gamification/award-points', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                activity_type: 'quiz_complete',
                score: score,
                perfect: score === total
            })
        });
    } catch (error) {
        console.log('Gamification API not available');
    }
}

// =====================================================
// Share Quiz
// =====================================================

function initShareFeature() {
    const shareBtn = document.getElementById('share-quiz-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            shareQuiz();
        });
    }
}

async function shareQuiz() {
    if (!state.currentQuiz) {
        showToast('Aucun quiz à partager', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/collaboration/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                quiz_id: state.currentQuiz.id || 'temp',
                allow_review: true,
                show_leaderboard: true
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            const shareUrl = window.location.origin + result.share_url;
            
            if (navigator.share) {
                navigator.share({
                    title: 'Quiz RAG Generator',
                    text: 'Essayez ce quiz!',
                    url: shareUrl
                });
            } else {
                navigator.clipboard.writeText(shareUrl);
                showToast('Lien copié dans le presse-papier!', 'success');
            }
        } else {
            // Fallback: copy current URL
            navigator.clipboard.writeText(window.location.href);
            showToast('Lien copié!', 'success');
        }
    } catch (error) {
        navigator.clipboard.writeText(window.location.href);
        showToast('Lien copié!', 'success');
    }
}

// =====================================================
// Initialization
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initUploadSection();
    initGenerateSection();
    initQuizSection();
    initSourceTabs();
    initFlashcardsSection();
    initStatsSection();
    initShareFeature();
    initAuth();
    
    // Check if user is logged in
    checkAuthStatus();
    
    // Check for existing documents
    getDocumentStats().then(result => {
        if (result.success && result.data.total_chunks > 0) {
            showToast('Documents existants détectés', 'info');
        }
    }).catch(() => {});
});

// =====================================================
// Authentication
// =====================================================

const authState = {
    isLoggedIn: false,
    user: null,
    accessToken: null,
    refreshToken: null
};

function initAuth() {
    // Login/Register button clicks
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const closeAuthModal = document.getElementById('close-auth-modal');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const authModal = document.getElementById('auth-modal');
    
    // Open modal for login
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            showAuthModal('login');
        });
    }
    
    // Open modal for register
    if (registerBtn) {
        registerBtn.addEventListener('click', () => {
            showAuthModal('register');
        });
    }
    
    // Close modal
    if (closeAuthModal) {
        closeAuthModal.addEventListener('click', () => {
            hideAuthModal();
        });
    }
    
    // Click outside to close
    if (authModal) {
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) {
                hideAuthModal();
            }
        });
    }
    
    // Switch between login and register
    if (showRegister) {
        showRegister.addEventListener('click', (e) => {
            e.preventDefault();
            switchAuthForm('register');
        });
    }
    
    if (showLogin) {
        showLogin.addEventListener('click', (e) => {
            e.preventDefault();
            switchAuthForm('login');
        });
    }
    
    // Handle login form
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Handle register form
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Handle logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

function showAuthModal(formType = 'login') {
    const authModal = document.getElementById('auth-modal');
    authModal.style.display = 'flex';
    switchAuthForm(formType);
}

function hideAuthModal() {
    const authModal = document.getElementById('auth-modal');
    authModal.style.display = 'none';
    clearAuthForms();
}

function switchAuthForm(formType) {
    const loginContainer = document.getElementById('login-form-container');
    const registerContainer = document.getElementById('register-form-container');
    
    if (formType === 'register') {
        loginContainer.style.display = 'none';
        registerContainer.style.display = 'block';
    } else {
        loginContainer.style.display = 'block';
        registerContainer.style.display = 'none';
    }
    clearAuthForms();
}

function clearAuthForms() {
    document.getElementById('login-form')?.reset();
    document.getElementById('register-form')?.reset();
    document.getElementById('login-error').style.display = 'none';
    document.getElementById('register-error').style.display = 'none';
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    
    showLoading('Connexion en cours...');
    
    try {
        const response = await fetch('/api/user/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Save tokens
            saveAuthData(result);
            updateUIForLoggedInUser(result.user);
            hideAuthModal();
            showToast(`Bienvenue, ${result.user.display_name || result.user.username}!`, 'success');
        } else {
            errorEl.textContent = result.error || 'Identifiants invalides';
            errorEl.style.display = 'block';
        }
    } catch (error) {
        errorEl.textContent = 'Erreur de connexion au serveur';
        errorEl.style.display = 'block';
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-confirm').value;
    const errorEl = document.getElementById('register-error');
    
    // Validate password match
    if (password !== confirm) {
        errorEl.textContent = 'Les mots de passe ne correspondent pas';
        errorEl.style.display = 'block';
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        errorEl.textContent = 'Le mot de passe doit contenir au moins 6 caractères';
        errorEl.style.display = 'block';
        return;
    }
    
    showLoading('Création du compte...');
    
    try {
        const response = await fetch('/api/user/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                username, 
                email, 
                password,
                display_name: username 
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Save tokens
            saveAuthData(result);
            updateUIForLoggedInUser(result.user);
            hideAuthModal();
            showToast('Compte créé avec succès! Bienvenue!', 'success');
        } else {
            errorEl.textContent = result.error || 'Erreur lors de l\'inscription';
            errorEl.style.display = 'block';
        }
    } catch (error) {
        errorEl.textContent = 'Erreur de connexion au serveur';
        errorEl.style.display = 'block';
    } finally {
        hideLoading();
    }
}

async function handleLogout() {
    showLoading('Déconnexion...');
    
    try {
        const token = localStorage.getItem('access_token');
        
        await fetch('/api/user/logout', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
    } catch (error) {
        console.log('Logout API error:', error);
    } finally {
        clearAuthData();
        updateUIForLoggedOutUser();
        hideLoading();
        showToast('Vous êtes déconnecté', 'info');
    }
}

function saveAuthData(result) {
    authState.isLoggedIn = true;
    authState.user = result.user;
    authState.accessToken = result.session?.access_token || result.token;
    authState.refreshToken = result.session?.refresh_token;
    
    localStorage.setItem('access_token', authState.accessToken);
    if (authState.refreshToken) {
        localStorage.setItem('refresh_token', authState.refreshToken);
    }
    localStorage.setItem('user', JSON.stringify(result.user));
}

function clearAuthData() {
    authState.isLoggedIn = false;
    authState.user = null;
    authState.accessToken = null;
    authState.refreshToken = null;
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

function updateUIForLoggedInUser(user) {
    authState.isLoggedIn = true;
    authState.user = user;
    
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    const displayName = document.getElementById('user-display-name');
    
    if (authButtons) authButtons.style.display = 'none';
    if (userMenu) userMenu.style.display = 'flex';
    if (displayName) displayName.textContent = user.display_name || user.username || user.email;
}

function updateUIForLoggedOutUser() {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (authButtons) authButtons.style.display = 'flex';
    if (userMenu) userMenu.style.display = 'none';
}

async function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    
    if (!token) {
        updateUIForLoggedOutUser();
        return;
    }
    
    try {
        // Verify token with server
        const response = await fetch('/api/user/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            authState.accessToken = token;
            updateUIForLoggedInUser(user);
        } else {
            // Token is invalid, try to refresh
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                await refreshAuthToken(refreshToken);
            } else {
                clearAuthData();
                updateUIForLoggedOutUser();
            }
        }
    } catch (error) {
        // Use saved user data if available
        if (savedUser) {
            try {
                const user = JSON.parse(savedUser);
                authState.accessToken = token;
                updateUIForLoggedInUser(user);
            } catch {
                clearAuthData();
                updateUIForLoggedOutUser();
            }
        } else {
            clearAuthData();
            updateUIForLoggedOutUser();
        }
    }
}

async function refreshAuthToken(refreshToken) {
    try {
        const response = await fetch('/api/user/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success && result.session) {
                localStorage.setItem('access_token', result.session.access_token);
                localStorage.setItem('refresh_token', result.session.refresh_token);
                authState.accessToken = result.session.access_token;
                authState.refreshToken = result.session.refresh_token;
                
                // Re-check auth status with new token
                await checkAuthStatus();
            }
        } else {
            clearAuthData();
            updateUIForLoggedOutUser();
        }
    } catch (error) {
        clearAuthData();
        updateUIForLoggedOutUser();
    }
}

// Helper function to get auth headers for API calls
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}
