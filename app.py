# app.py
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Современный веб-дизайн</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        /* Навигация */
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #333;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #667eea;
        }
        
        /* Главный блок */
        .hero {
            text-align: center;
            padding: 4rem 2rem;
            color: white;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: fadeInUp 0.8s ease;
        }
        
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            animation: fadeInUp 0.8s ease 0.2s both;
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: transform 0.3s, box-shadow 0.3s;
            animation: fadeInUp 0.8s ease 0.4s both;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        /* Карточки */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 4rem 2rem;
        }
        
        .section-title {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: white;
        }
        
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
            animation: fadeInUp 0.8s ease;
        }
        
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .card-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .card h3 {
            margin-bottom: 1rem;
            color: #667eea;
        }
        
        /* Форма */
        .contact-form {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        input, textarea {
            width: 100%;
            padding: 0.8rem;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            width: 100%;
            transition: transform 0.3s;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
        }
        
        /* Футер */
        .footer {
            background: rgba(0,0,0,0.8);
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
        }
        
        /* Анимации */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Адаптивность */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }
            
            .nav-links {
                display: none;
            }
            
            .cards {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">DesignHub</div>
            <div class="nav-links">
                <a href="#home">Главная</a>
                <a href="#services">Услуги</a>
                <a href="#contact">Контакты</a>
            </div>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <h1>Современный веб-дизайн</h1>
        <p>Создаем красивые и функциональные сайты</p>
        <a href="#contact" class="btn">Связаться</a>
    </section>
    
    <div class="container" id="services">
        <h2 class="section-title">Наши услуги</h2>
        <div class="cards">
            <div class="card">
                <div class="card-icon">🎨</div>
                <h3>Веб-дизайн</h3>
                <p>Создаем уникальный дизайн, который отражает вашу индивидуальность</p>
            </div>
            <div class="card">
                <div class="card-icon">💻</div>
                <h3>Разработка</h3>
                <p>Современные технологии для вашего бизнеса</p>
            </div>
            <div class="card">
                <div class="card-icon">📱</div>
                <h3>Адаптивность</h3>
                <p>Идеальное отображение на всех устройствах</p>
            </div>
        </div>
    </div>
    
    <div class="container" id="contact">
        <h2 class="section-title">Свяжитесь с нами</h2>
        <form class="contact-form" method="POST">
            <div class="form-group">
                <input type="text" name="name" placeholder="Ваше имя" required>
            </div>
            <div class="form-group">
                <input type="email" name="email" placeholder="Email" required>
            </div>
            <div class="form-group">
                <textarea name="message" rows="4" placeholder="Сообщение" required></textarea>
            </div>
            <button type="submit" class="submit-btn">Отправить</button>
        </form>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 DesignHub. Все права защищены.</p>
    </footer>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Здесь можно добавить отправку email или сохранение в файл
        print(f"Новое сообщение от {name} ({email}): {message}")
        
        # Возвращаем страницу с сообщением об успехе (можно добавить уведомление)
        return render_template_string(HTML_TEMPLATE)
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)