document.addEventListener('DOMContentLoaded', function() {
    console.log("DNA Script Initialized with Persistence");

    const questions = [
        { id: 'style', text: 'Choose your visual mood:', options: ['Luxury', 'Emotional', 'Artistic', 'Minimalist', 'Vintage'] },
        { id: 'vibe', text: 'Preferred photographer style:', options: ['Guided (Posed)', 'Candid (Natural)', 'Editorial', 'Storytelling'] },
        { id: 'lighting', text: 'Preferred lighting style:', options: ['Bright & Airy', 'Dark & Moody', 'Natural Light', 'Studio Flash'] },
        { id: 'editing', text: 'Desired Editing Tone:', options: ['True to Color', 'Film-like', 'High Contrast', 'Soft & Warm'] },
        { id: 'usage', text: 'Primary use for photos:', options: ['Magazine/Print', 'Physical Album', 'Instagram/Social', 'Professional Brand'] },
        { id: 'setting', text: 'Ideal Shooting Location:', options: ['Grand Architecture', 'Nature/Outdoor', 'Urban/Cityscape', 'Private Studio'] }
    ];

    let currentStep = 0;
    let answers = {};

    // --- NEW: PERSISTENCE LOGIC ---
    // Check if we have saved results from a previous session
    const savedResults = sessionStorage.getItem('photographyMatches');
    if (savedResults) {
        displayResults(JSON.parse(savedResults));
    } else {
        showQuestion(); // Only start the quiz if no saved results exist
    }

    function showQuestion() {
        const q = questions[currentStep];
        const titleElement = document.getElementById('q-title');
        const optDiv = document.getElementById('options');
        
        const subtitle = document.querySelector('#quiz-container p');
        if (subtitle) subtitle.style.display = 'none';

        if (!titleElement || !optDiv) return;

        const progress = `Question ${currentStep + 1} of ${questions.length}`;
        titleElement.innerHTML = `
            <span style="font-size: 0.8rem; color: #C09853; text-transform: uppercase; letter-spacing: 2px;">${progress}</span><br>
            <div style="margin-top:10px;">${q.text}</div>
        `;
        
        optDiv.innerHTML = '';
        const grid = document.createElement('div');
        grid.style.display = "grid";
        grid.style.gridTemplateColumns = "1fr";
        grid.style.gap = "10px";
        grid.style.width = "100%";

        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.innerText = opt;
            btn.className = "dna-btn"; 
            
            btn.onclick = () => {
                answers[q.id] = opt;
                currentStep++;
                
                if (currentStep < questions.length) {
                    showQuestion();
                } else {
                    fetchResults();
                }
            };
            grid.appendChild(btn);
        });
        optDiv.appendChild(grid);
    }

    function fetchResults() {
        const container = document.getElementById('quiz-container');
        
        container.innerHTML = `
            <div style="text-align:center; padding: 50px;">
                <h2 style="color: #C09853; font-family: 'Playfair Display', serif; font-size: 2rem;">Analyzing Your DNA...</h2>
                <p style="color: #EAD8B1; margin-top: 10px;">Curating your perfect photography matches.</p>
            </div>`;

        fetch('/calculate-match', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(answers)
        })
        .then(res => res.json())
        .then(data => {
            // Save the data to session storage so the "Back" button works
            sessionStorage.setItem('photographyMatches', JSON.stringify(data));
            displayResults(data);
        })
        .catch(err => {
            console.error("Error fetching results:", err);
            container.innerHTML = `<h3 style="color: #ff4d4d; text-align:center;">Connection Error. Please try again.</h3>`;
        });
    }

    // --- RECTIFIED: SEPARATE DISPLAY FUNCTION ---
    function displayResults(data) {
        const container = document.getElementById('quiz-container');
        container.style.maxWidth = "800px";
        container.innerHTML = `<h2 style="color: #C09853; margin-bottom: 30px; text-align: center; font-family: 'Playfair Display', serif; font-size: 2.5rem;">Your Curated Matches</h2>`;
        
        data.forEach(p => {
            const card = document.createElement('div');
            card.style.cssText = "background: #1A1A1A; padding: 30px; border: 1px solid #333; border-top: 4px solid #C09853; margin-bottom: 25px; text-align: center; border-radius: 5px;";
            
            card.innerHTML = `
                <span style="color: #EAD8B1; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;">Match Score: ${p.match}%</span>
                <h3 style="color: #C09853; margin: 15px 0; font-size: 2rem; font-family: 'Playfair Display', serif;">${p.name}</h3>
                <p style="color: #FFFFFF; font-size: 1rem; opacity: 0.8; margin-bottom: 25px; line-height: 1.6;">${p.reason}</p>
                <a href="/portfolio/${encodeURIComponent(p.name)}" 
                   style="display: inline-block; padding: 15px 35px; background: #C09853; color: #1a1a1a; text-decoration: none; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; border-radius: 2px;">
                   View Full Portfolio
                </a>
            `;
            container.appendChild(card);
        });
        
        // Re-take Quiz Link (Also clears the storage)
        const retryDiv = document.createElement('div');
        retryDiv.style.textAlign = "center";
        const retryLink = document.createElement('a');
        retryLink.href = "#";
        retryLink.innerText = "← START OVER / CLEAR DNA";
        retryLink.style.cssText = "color: #C09853; text-decoration: none; font-size: 0.9rem; letter-spacing: 1px; border-bottom: 1px solid #C09853;";
        retryLink.onclick = () => {
            sessionStorage.removeItem('photographyMatches');
            window.location.reload();
        };
        retryDiv.appendChild(retryLink);
        container.appendChild(retryDiv);
    }
});