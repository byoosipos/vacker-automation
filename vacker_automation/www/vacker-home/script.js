// ================ HEADER & SCROLL EFFECTS ================
document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('.header');
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.main-nav');
    
    // Header scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Reveal elements on scroll
        revealElements();
    });
    
    // Mobile menu toggle
    menuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        menuToggle.classList.toggle('active');
        
        if (menuToggle.classList.contains('active')) {
            menuToggle.innerHTML = '<i class="fas fa-times"></i>';
        } else {
            menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
        }
    });
    
    // Close mobile menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            menuToggle.classList.remove('active');
            menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
        });
    });
    
    // Portfolio filter
    const filterButtons = document.querySelectorAll('.filter-btn');
    const workItems = document.querySelectorAll('.work-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            const filterValue = button.getAttribute('data-filter');
            
            workItems.forEach(item => {
                if (filterValue === 'all' || item.classList.contains(filterValue)) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
    
    // Initialize particles
    initParticles();
    
    // Add reveal classes to elements
    addRevealClasses();
    
    // Trigger initial check for visible elements
    revealElements();
});

// ================ PARTICLES ANIMATION ================
function initParticles() {
    const particlesContainer = document.querySelector('.hero-particles');
    
    // Create particles
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random position, size, and animation delay
        const size = Math.random() * 5 + 1;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        
        // Add random animation delay and duration
        const delay = Math.random() * 5;
        const duration = Math.random() * 10 + 5;
        
        particle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
        
        // Add glowing effect with random color
        const colors = ['#00c3ff', '#6a11cb', '#ff006a'];
        const colorIndex = Math.floor(Math.random() * colors.length);
        particle.style.backgroundColor = colors[colorIndex];
        particle.style.boxShadow = `0 0 5px ${colors[colorIndex]}, 0 0 10px ${colors[colorIndex]}`;
        
        // Append particle to container
        particlesContainer.appendChild(particle);
    }
    
    // Add floating animation keyframes
    if (!document.getElementById('particle-style')) {
        const style = document.createElement('style');
        style.id = 'particle-style';
        style.textContent = `
            .particle {
                position: absolute;
                border-radius: 50%;
                opacity: 0.6;
                pointer-events: none;
            }
            
            @keyframes float {
                0% {
                    transform: translateY(0) translateX(0);
                }
                25% {
                    transform: translateY(-20px) translateX(10px);
                }
                50% {
                    transform: translateY(0) translateX(20px);
                }
                75% {
                    transform: translateY(20px) translateX(10px);
                }
                100% {
                    transform: translateY(0) translateX(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// ================ SCROLL REVEAL ANIMATION ================
function addRevealClasses() {
    // Add reveal classes to elements
    document.querySelectorAll('.section-header').forEach(element => {
        element.classList.add('reveal-fade');
    });
    
    document.querySelectorAll('.service-card, .specialty-item, .work-item, .client-logo, .blog-card').forEach(element => {
        element.classList.add('reveal-scale');
    });
    
    document.querySelectorAll('.about-text, .contact-info').forEach(element => {
        element.classList.add('reveal-left');
    });
    
    document.querySelectorAll('.about-video, .contact-form').forEach(element => {
        element.classList.add('reveal-right');
    });
    
    // Add CSS for reveal animations if not already present
    if (!document.getElementById('reveal-style')) {
        const style = document.createElement('style');
        style.id = 'reveal-style';
        style.textContent = `
            .reveal-fade,
            .reveal-scale,
            .reveal-left,
            .reveal-right {
                opacity: 0;
                transition: all 0.8s ease;
            }
            
            .reveal-scale {
                transform: scale(0.9);
            }
            
            .reveal-left {
                transform: translateX(-50px);
            }
            
            .reveal-right {
                transform: translateX(50px);
            }
            
            .reveal-fade.active,
            .reveal-scale.active,
            .reveal-left.active,
            .reveal-right.active {
                opacity: 1;
                transform: translateX(0) scale(1);
            }
        `;
        document.head.appendChild(style);
    }
}

function revealElements() {
    const windowHeight = window.innerHeight;
    const revealPoint = 150; // Distance from the bottom of viewport to trigger reveal
    
    const elements = document.querySelectorAll('.reveal-fade, .reveal-scale, .reveal-left, .reveal-right');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        
        if (elementTop < windowHeight - revealPoint) {
            element.classList.add('active');
        } else {
            element.classList.remove('active');
        }
    });
}

// ================ FORM HANDLING ================
document.addEventListener('DOMContentLoaded', () => {
    // Contact form handling
    const contactForm = document.querySelector('.contact-form form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Get form inputs
            const nameInput = contactForm.querySelector('input[type="text"]');
            const emailInput = contactForm.querySelector('input[type="email"]');
            const subjectInput = contactForm.querySelector('input[placeholder="Subject"]');
            const messageInput = contactForm.querySelector('textarea');
            
            // Basic form validation
            if (!nameInput.value || !emailInput.value || !messageInput.value) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Simulate form submission
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            
            // Simulate API call (would be replaced with actual form submission)
            setTimeout(() => {
                alert('Thank you for your message! We will get back to you soon.');
                contactForm.reset();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Message';
            }, 1500);
        });
    }
    
    // Newsletter form handling
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const emailInput = newsletterForm.querySelector('input[type="email"]');
            
            if (!emailInput.value) {
                alert('Please enter your email address.');
                return;
            }
            
            // Simulate form submission
            const submitBtn = newsletterForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Subscribing...';
            
            // Simulate API call
            setTimeout(() => {
                alert('Thank you for subscribing to our newsletter!');
                newsletterForm.reset();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Subscribe';
            }, 1500);
        });
    }
}); 