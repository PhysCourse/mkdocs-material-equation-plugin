class FormulaSlider {
    constructor(container) {
        this.container = container;
        this.track = container.querySelector('.formula-track');
        this.slides = Array.from(container.querySelectorAll('.formula-slide'));
        this.prevBtn = container.querySelector('.left-arrow');
        this.nextBtn = container.querySelector('.right-arrow');
        this.progressFill = container.querySelector('.progress-fill');
        
        this.currentIndex = 0;
        this.isAnimating = false;
        
        this.init();
    }
    
    init() {
        this.prevBtn.addEventListener('click', () => this.prev());
        this.nextBtn.addEventListener('click', () => this.next());
        
        // Добавляем обработчики для свайпов (опционально)
        this.addSwipeSupport();
        
        this.updateProgress();
        this.adjustHeight();
    }
    
    goToSlide(index) {
        if (this.isAnimating || index < 0 || index >= this.slides.length || index === this.currentIndex) return;
        
        this.isAnimating = true;
        const currentSlide = this.slides[this.currentIndex];
        const nextSlide = this.slides[index];
        
        // Добавляем классы для анимации
        currentSlide.classList.add('sliding-out');
        nextSlide.classList.add('sliding-in');
        
        setTimeout(() => {
            currentSlide.classList.remove('active', 'sliding-out');
            nextSlide.classList.add('active');
            nextSlide.classList.remove('sliding-in');
            
            this.currentIndex = index;
            this.isAnimating = false;
            this.updateProgress();
            this.adjustHeight();
            
        }, 400);
    }
    
    next() {
        const nextIndex = (this.currentIndex + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }
    
    prev() {
        const prevIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
        this.goToSlide(prevIndex);
    }
    
    updateProgress() {
        const progress = ((this.currentIndex + 1) / this.slides.length) * 100;
        this.progressFill.style.width = `${progress}%`;
    }
    
    adjustHeight() {
        const activeSlide = this.slides[this.currentIndex];
        const activeContent = activeSlide.querySelector('.slide-content');
        const contentHeight = activeContent.scrollHeight;
        
        // Устанавливаем минимальную высоту на основе контента
        //this.track.style.minHeight = `${contentHeight + 80}px`; // + отступы
    }
    
    addSwipeSupport() {
        let startX = 0;
        let endX = 0;
        
        this.container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });
        
        this.container.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            this.handleSwipe();
        });
        
        this.handleSwipe = () => {
            const diff = startX - endX;
            const swipeThreshold = 50;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    this.next();
                } else {
                    this.prev();
                }
            }
        };
    }
}

// Инициализация всех слайдеров

document.addEventListener('DOMContentLoaded', function() {
    const sliders = document.querySelectorAll('.formula-slider');
    
    sliders.forEach((slider) => {
        slider.setAttribute('tabindex', '0');
        new FormulaSlider(slider);
    });
    
});

// Автоматическая подстройка высоты при изменении размера окна
/*
window.addEventListener('resize', function() {
    document.querySelectorAll('.formula-slider').forEach(slider => {
        const instance = slider._formulaSliderInstance;
        if (instance) {
            instance.adjustHeight();
        }
    });
});*/